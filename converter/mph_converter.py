"""
COMSOL MPH转换器
负责将ThermalInfo对象转换为COMSOL MPH文件
"""

from pathlib import Path
from typing import Optional, Dict, Any
from loguru import logger

from core.thermal_info import ThermalInfo


class ComsolCreationError(Exception):
    """COMSOL创建错误"""
    pass


class MPHConverter:
    """COMSOL MPH转换器"""
    
    def __init__(self):
        """初始化转换器"""
        self.model = None
        self.thermal_info = None
        self.geometry_objects = {}  # 保存几何体对象的字典
        self.material_objects = {}  # 保存材料对象的字典
        self.material_selection_inputs = {}  # material_name -> set of geom selection names
        logger.debug("MPHConverter initialized")
    
    def convert(self, thermal_info: ThermalInfo, output_file: Path) -> bool:
        """
        将ThermalInfo对象转换为COMSOL MPH文件
        
        Args:
            thermal_info: ThermalInfo对象
            output_file: 输出MPH文件路径
            
        Returns:
            bool: 转换是否成功
            
        Raises:
            ComsolCreationError: 转换失败时抛出
        """
        try:
            logger.info(f"Starting conversion to: {output_file}")
            
            self.thermal_info = thermal_info
            thermal_info.init_runtime_sections()
            # 验证输入数据
            if not thermal_info.validate():
                logger.error("ThermalInfo validation failed")
                raise ComsolCreationError("ThermalInfo validation failed")
            
            # 创建COMSOL模型
            self._create_model()
            
            # 从ThermalInfo中获取sections并创建几何
            self._create_geometry_from_sections(thermal_info)
            
            # 设置材料
            self._setup_materials(thermal_info)
            
            # 设置热物理场（包括边界条件）
            self._setup_heat_transfer(thermal_info)
            
            # 生成网格
            self._generate_mesh(thermal_info)
            
            # 设置稳态热研究
            self._setup_steady_heat_study()
            
            # 设置求解器并求解 - 暂时注释掉，手动执行求解
            # self._setup_solver(thermal_info)
            
            # 保存文件
            self._save_file(output_file)
            
            logger.info("Conversion completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Conversion1 failed: {e}")
            if isinstance(e, ComsolCreationError):
                raise
            raise ComsolCreationError(f"Conversion failed: {e}")
    
    def _create_model(self) -> None:
        """创建COMSOL模型"""
        logger.debug("Creating COMSOL model")
        
        try:
            # 尝试导入MPh库
            import mph
            logger.debug("MPh library imported successfully")
            
            # 启动COMSOL客户端
            self.client = mph.start(cores=1)
            logger.debug(f"COMSOL client started successfully: {type(self.client)}")
            
            # 创建新模型
            self.model = self.client.create('Model')
            logger.debug(f"COMSOL model created successfully: {type(self.model)}")
            logger.debug(f"Model name: {self.model.name()}")
            logger.debug(f"Model attributes: {[attr for attr in dir(self.model) if not attr.startswith('_')]}")
            
            # 创建组件
            components = self.model/'components'
            components.create(True, name='component')
            
            # 创建几何容器 - 使用正确的MPh API
            geometries = self.model/'geometries'
            self.geometry = geometries.create(3, name='geometry')  # 3D几何
            logger.debug(f"Geometry container created successfully: {type(self.geometry)}")
            
            # 设置几何长度单位为纳米(nm) —— 仅按参考实现
            try:
                j = self.model.java
                j.component('comp1').geom('geom1').lengthUnit('nm')
                logger.debug("Set geometry length unit to nm via Java API (comp1/geom1)")
            except Exception as e:
                logger.warning(f"Failed to set geometry length unit: {e}")
            
            # 添加参数d设置为1 [nm]
            try:
                self.model.parameter('d', '1 [nm]')
                logger.debug("Added parameter d = 1 [nm]")
            except Exception as e:
                logger.warning(f"Failed to add parameter d: {e}")
            
        except ImportError:
            raise ComsolCreationError("MPh library not available. Please install it with: pip install mph")
        except Exception as e:
            raise ComsolCreationError(f"Failed to create COMSOL model: {e}")
    
    def _create_geometry_from_sections(self, thermal_info: ThermalInfo) -> None:
        """从ThermalInfo中的sections创建几何"""
        logger.debug("Creating geometry from sections")
        
        try:
            # 从ThermalInfo中获取sections
            sections = thermal_info.init_runtime_sections()
            logger.debug(f"Found {len(sections)} sections to process")
            
            # 存储每个section的几何对象
            section_geometries = {}
            
            # 为每个section创建几何体
            for section_index, section in enumerate(sections):
                logger.debug(f"Processing section {section_index}: {section.get_name()}")
                section_geom = self._create_section_geometry(section, section_index)
                if section_geom:
                    section_geometries[section.get_name()] = section_geom
                
            # 创建装配体，将所有section的几何体组装起来
            if section_geometries:
                self._create_assembly_from_geometries(section_geometries)
                
            logger.debug(f"Successfully created geometry from {len(sections)} sections")
            
        except Exception as e:
            logger.error(f"Failed to create geometry from sections: {e}")
            raise ComsolCreationError(f"Failed to create geometry from sections: {e}")
    
    
    def _create_section_geometry(self, section, section_index: int):
        """为单个section创建几何体，返回创建的几何对象"""
        try:
            # 验证section对象
            if not self._validate_section(section):
                logger.warning(f"Section {section.get_name()} validation failed, skipping")
                return None
            
            logger.debug(f"Creating geometry for section: {section.get_name()}")
            
            # 1. 首先创建section本身的shape（如果存在）
            section_shape_geometry = None
            if hasattr(section, 'shape') and section.shape:
                logger.debug(f"Section {section.get_name()} has its own shape, creating section shape geometry")
                section_shape_geometry = self._create_shape_from_section(section, section_index)
                if section_shape_geometry:
                    logger.debug(f"Created section shape geometry for {section.get_name()}")
                else:
                    logger.warning(f"Failed to create section shape geometry for {section.get_name()}")
            
            # 2. 创建所有components的几何
            component_geometries = []
            if hasattr(section, 'children') and section.children:
                logger.debug(f"Section {section.get_name()} has {len(section.children)} children")
                
                # 逐一处理每个child，创建几何对象
                for comp_index, child in enumerate(section.children):
                    logger.debug(f"Processing child {comp_index}: {type(child).__name__}")
                    logger.debug(f"  - Has shape: {hasattr(child, 'shape') and child.shape is not None}")
                    logger.debug(f"  - Template name: {getattr(child, 'template_name', 'None')}")
                    
                    # 根据child的shape类型生成不同的几何形状
                    if hasattr(child, 'shape') and child.shape:
                        comp_geom = self._create_shape_from_component(child, section_index, section.get_name(), comp_index)
                        if comp_geom:
                            component_geometries.append(comp_geom)
                    else:
                        logger.warning(f"Child {comp_index} has no shape, skipping")
                        # 尝试手动解析模板
                        if hasattr(child, 'template_name') and child.template_name:
                            logger.debug(f"Attempting to parse template: {child.template_name}")
            else:
                logger.debug(f"Section {section.get_name()} has no children")
            
            # 3. 根据section shape和components的情况决定最终的几何
            if section_shape_geometry and component_geometries:
                # 有section shape和components，需要做布尔运算：section shape - components
                logger.debug(f"Section {section.get_name()} has both shape and components, performing boolean operations")
                return self._create_section_with_boolean_operations(section, section_shape_geometry, component_geometries, section_index)
            elif section_shape_geometry:
                # 只有section shape，没有components
                logger.debug(f"Section {section.get_name()} has only shape, no components")
                return section_shape_geometry
            elif component_geometries:
                # 只有components，没有section shape，使用原来的逻辑
                logger.debug(f"Section {section.get_name()} has only components, no section shape")
                return self._create_components_union(component_geometries, section.get_name(), section_index)
            else:
                # 既没有section shape也没有components
                logger.debug(f"Section {section.get_name()} has no shape and no components, no geometry created")
                return None
                
        except Exception as e:
            logger.error(f"Failed to create section geometry {section.get_name()}: {e}")
            raise ComsolCreationError(f"Failed to create section geometry: {e}")
    
    def _create_shape_from_section(self, section, section_index: int):
        """从section的shape创建几何对象"""
        try:
            shape = section.shape
            shape_type = type(shape).__name__.lower()
            geom_name = self._get_section_geom_name(section_index, section.get_name())
            
            logger.debug(f"Creating section shape geometry: {geom_name}, type: {shape_type}")
            
            # 根据shape类型创建相应的几何
            if shape_type == "cube":
                return self._create_cube_geometry(shape, geom_name, section)
            elif shape_type == "cylinder":
                return self._create_cylinder_geometry(shape, geom_name, section)
            elif shape_type == "sphere":
                return self._create_sphere_geometry(shape, geom_name, section)
            else:
                logger.warning(f"Unknown section shape type: {shape_type}, using generic method")
                return self._create_generic_geometry(shape, geom_name, section)
                
        except Exception as e:
            logger.error(f"Failed to create shape from section: {e}")
            raise ComsolCreationError(f"Failed to create shape from section: {e}")
    
    def _create_section_with_boolean_operations(self, section, section_shape_geometry, component_geometries, section_index):
        """创建section几何，执行布尔运算：section shape - components"""
        try:
            section_name = section.get_name()
            logger.debug(f"Creating boolean operations for section {section_name}")
            
            # 如果有多个components，先创建它们的Union
            if len(component_geometries) > 1:
                components_union_name = f"components_union_{section_name}_{section_index}"
                components_union = self.geometry.create('Union', name=components_union_name)
                components_union.java.selection('input').set(*[geom.tag() for geom in component_geometries])
                components_geometry = components_union
                logger.debug(f"Created components union for section {section_name}")
            else:
                components_geometry = component_geometries[0]
                logger.debug(f"Using single component for section {section_name}")
            
            # 按需求：跳过Difference操作（section_diff_*），直接使用已创建的Union结果
            logger.debug(f"Skip difference operation for section {section_name}; use components union directly")
            return components_geometry
            
        except Exception as e:
            logger.error(f"Failed to create boolean operations for section: {e}")
            raise ComsolCreationError(f"Failed to create boolean operations for section: {e}")
    
    def _create_components_union(self, component_geometries, section_name, section_index):
        """创建components的联合几何"""
        try:
            if len(component_geometries) > 1:
                # 有多个component，创建Union将它们组合
                section_geom_name = f"section_union_{section_name}_{section_index}"
                section_geometry = self.geometry.create('Union', name=section_geom_name)
                section_geometry.java.selection('input').set(*[geom.tag() for geom in component_geometries])
                
                # 为联合几何创建材料选择组（使用第一个component的材料作为代表）
                if component_geometries and hasattr(component_geometries[0], 'material'):
                    # 创建一个虚拟的component对象来传递材料信息
                    class VirtualComponent:
                        def __init__(self, material):
                            self.material = material
                    
                    # 使用第一个component的材料
                    virtual_component = VirtualComponent(component_geometries[0].material)
                    self._create_material_selection(section_geom_name, virtual_component)
                
                logger.debug(f"Created union geometry for section {section_name} with {len(component_geometries)} components")
                return section_geometry
            elif len(component_geometries) == 1:
                # 只有一个component，直接使用它
                logger.debug(f"Section {section_name} has single component geometry")
                return component_geometries[0]
            else:
                # 没有components
                logger.debug(f"Section {section_name} has no components")
                return None
                
        except Exception as e:
            logger.error(f"Failed to create components union: {e}")
            raise ComsolCreationError(f"Failed to create components union: {e}")
    
    def _create_assembly_from_geometries(self, section_geometries) -> None:
        """将多个section的几何体组装成装配体"""
        try:
            logger.debug("Creating assembly from section geometries")
            
            if not section_geometries:
                logger.debug("No section geometries to assemble")
                return
            
            # 获取所有section几何对象
            geometry_list = list(section_geometries.values())
            
            if len(geometry_list) == 1:
                logger.debug("Only one section geometry, no assembly needed")
                return
            
            # 创建装配体 - 使用Union操作将所有section几何体组合
            assembly_name = "assembly"
            try:
                assembly = self.geometry.create('Union', name=assembly_name)
                # 设置输入几何对象 - 使用selection方式
                assembly.java.selection('input').set(*[geom.tag() for geom in geometry_list])
                logger.debug(f"Created assembly with {len(geometry_list)} section geometries")
            except Exception as e:
                logger.warning(f"Failed to create assembly Union: {e}")
                logger.debug("Skipping assembly creation due to Union error")
            
        except Exception as e:
            logger.error(f"Failed to create assembly from geometries: {e}")
            raise ComsolCreationError(f"Failed to create assembly from geometries: {e}")
    
    def _create_shape_from_component(self, component, section_index: int, section_name: str, comp_index: int):
        """根据component的shape类型创建不同的几何形状，返回创建的几何对象"""
        try:
            shape = component.shape
            shape_type = type(shape).__name__
            logger.debug(f"Creating shape of type: {shape_type}")
            
            # 创建几何对象名称
            geom_name = self._get_component_geom_name(section_index, section_name, comp_index)
            
            # 根据不同的shape类型创建不同的几何对象
            if shape_type == "Cube":
                return self._create_cube_geometry(shape, geom_name, component)
            elif shape_type == "Cylinder":
                return self._create_cylinder_geometry(shape, geom_name, component)
            elif shape_type == "Sphere":
                return self._create_sphere_geometry(shape, geom_name, component)
            else:
                logger.warning(f"Unknown shape type: {shape_type}, using generic method")
                return self._create_generic_geometry(shape, geom_name, component)
                
        except Exception as e:
            logger.error(f"Failed to create shape from component: {e}")
            raise ComsolCreationError(f"Failed to create shape from component: {e}")
    
    def _create_cube_geometry(self, shape, geom_name: str, component):
        """创建立方体几何，返回创建的几何对象"""
        try:
            logger.debug(f"Creating cube geometry: {geom_name}")
            
            # 创建Block几何对象 - 使用正确的MPh API
            block = self.geometry.create('Block', name=geom_name)
            
            # 设置立方体参数
            if hasattr(shape, 'length') and hasattr(shape, 'width') and hasattr(shape, 'height'):
                block.property('size', [shape.length, shape.width, shape.height])
            
            # 设置位置
            if hasattr(shape, 'position') and shape.position:
                pos = shape.position
                block.property('pos', [pos.x, pos.y, pos.z])
            
            # 启用结果选择输出到域
            try:
                block.property('selresult', 'on')
                block.property('selresultshow', 'dom')
            except Exception:
                pass
            
            # 为材料创建对应的选择组
            self._create_material_selection(geom_name, component)
            
            # 保存几何体对象到字典中
            self.geometry_objects[geom_name] = block
            
            logger.debug(f"Created cube geometry: {geom_name}")
            return block
            
        except Exception as e:
            logger.error(f"Failed to create cube geometry: {e}")
            raise
    
    def _create_cylinder_geometry(self, shape, geom_name: str, component):
        """创建圆柱体几何，返回创建的几何对象"""
        try:
            logger.debug(f"Creating cylinder geometry: {geom_name}")
            
            # 创建Cylinder几何对象 - 使用正确的MPh API
            cylinder = self.geometry.create('Cylinder', name=geom_name)
            
            # 设置圆柱体参数
            if hasattr(shape, 'radius') and shape.radius:
                cylinder.property('r', shape.radius)
            
            if hasattr(shape, 'height') and shape.height:
                cylinder.property('h', shape.height)
            
            # 设置位置
            if hasattr(shape, 'position') and shape.position:
                pos = shape.position
                cylinder.property('pos', [pos.x, pos.y, pos.z])
            
            # 启用结果选择输出到域
            try:
                cylinder.property('selresult', 'on')
                cylinder.property('selresultshow', 'dom')
            except Exception:
                pass
            
            # 为材料创建对应的选择组
            self._create_material_selection(geom_name, component)
            
            # 保存几何体对象到字典中
            self.geometry_objects[geom_name] = cylinder
            
            logger.debug(f"Created cylinder geometry: {geom_name}")
            return cylinder
            
        except Exception as e:
            logger.error(f"Failed to create cylinder geometry: {e}")
            raise
    
    def _create_sphere_geometry(self, shape, geom_name: str, component):
        """创建球体几何，返回创建的几何对象"""
        try:
            logger.debug(f"Creating sphere geometry: {geom_name}")
            
            # 创建Sphere几何对象 - 使用正确的MPh API
            sphere = self.geometry.create('Sphere', name=geom_name)
            
            # 设置球体参数
            if hasattr(shape, 'radius') and shape.radius:
                sphere.property('r', shape.radius)
            
            # 设置位置
            if hasattr(shape, 'position') and shape.position:
                pos = shape.position
                sphere.property('pos', [pos.x, pos.y, pos.z])
            
            # 启用结果选择输出到域
            try:
                sphere.property('selresult', 'on')
                sphere.property('selresultshow', 'dom')
            except Exception:
                pass
            
            # 为材料创建对应的选择组
            self._create_material_selection(geom_name, component)
            
            # 保存几何体对象到字典中
            self.geometry_objects[geom_name] = sphere
            
            logger.debug(f"Created sphere geometry: {geom_name}")
            return sphere
            
        except Exception as e:
            logger.error(f"Failed to create sphere geometry: {e}")
            raise
    
    def _create_generic_geometry(self, shape, geom_name: str, component):
        """创建通用几何对象，返回创建的几何对象"""
        try:
            logger.debug(f"Creating generic geometry: {geom_name}")
            
            # 默认创建Block几何对象 - 使用正确的MPh API
            block = self.geometry.create('Block', name=geom_name)
            
            # 设置默认参数
            block.property('size', [1, 1, 1])
            block.property('pos', [0, 0, 0])
            
            # 启用结果选择输出到域
            try:
                block.property('selresult', 'on')
                block.property('selresultshow', 'dom')
            except Exception:
                pass
            
            # 为材料创建对应的选择组
            self._create_material_selection(geom_name, component)
            
            # 保存几何体对象到字典中
            self.geometry_objects[geom_name] = block
            
            logger.debug(f"Created generic geometry: {geom_name}")
            return block
            
        except Exception as e:
            logger.error(f"Failed to create generic geometry: {e}")
            raise
    
    def _validate_section(self, section) -> bool:
        """验证Section对象"""
        try:
            # 检查必需属性
            if not hasattr(section, 'name') or not section.name:
                logger.warning("Section missing name")
                return False
            
            # 检查形状
            if section.shape:
                if not self._validate_shape(section.shape):
                    logger.warning(f"Section {section.name} has invalid shape")
                    return False
            
            # 检查材料
            if section.material:
                if not self._validate_material(section.material):
                    logger.warning(f"Section {section.name} has invalid material")
                    return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Section validation failed: {e}")
            return False
    
    def _validate_shape(self, shape) -> bool:
        """验证Shape对象"""
        try:
            # 检查必需属性
            if not hasattr(shape, 'shape_type') or not shape.shape_type:
                logger.warning("Shape missing shape_type")
                return False
            
            if not hasattr(shape, 'position') or not shape.position:
                logger.warning("Shape missing position")
                return False
            
            # 检查位置坐标
            if hasattr(shape.position, 'x') and hasattr(shape.position, 'y') and hasattr(shape.position, 'z'):
                if not (isinstance(shape.position.x, (int, float)) and 
                       isinstance(shape.position.y, (int, float)) and 
                       isinstance(shape.position.z, (int, float))):
                    logger.warning("Shape position coordinates must be numeric")
                    return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Shape validation failed: {e}")
            return False
    
    def _validate_material(self, material) -> bool:
        """验证Material对象"""
        try:
            # 检查必需属性
            if not hasattr(material, 'name') or not material.name:
                logger.warning("Material missing name")
                return False
            
            # 检查温度相关属性
            if hasattr(material, 'temperature_map') and material.temperature_map:
                for temp, point in material.temperature_map.items():
                    if not isinstance(temp, (int, float)) or temp < 0:
                        logger.warning(f"Material {material.name} has invalid temperature: {temp}")
                        return False
                    
                    if not self._validate_temperature_point(point):
                        logger.warning(f"Material {material.name} has invalid temperature point at {temp}")
                        return False
            
            return True
            
        except Exception as e:
            logger.warning(f"Material validation failed: {e}")
            return False
    
    def _validate_temperature_point(self, point) -> bool:
        """验证TemperaturePoint对象"""
        try:
            # 检查必需属性
            if not hasattr(point, 'conductivity') or not point.conductivity:
                logger.warning("TemperaturePoint missing conductivity")
                return False
            
            if not hasattr(point, 'density') or not isinstance(point.density, (int, float)) or point.density <= 0:
                logger.warning("TemperaturePoint has invalid density")
                return False
            
            if not hasattr(point, 'heat_capacity') or not isinstance(point.heat_capacity, (int, float)) or point.heat_capacity <= 0:
                logger.warning("TemperaturePoint has invalid heat capacity")
                return False
            
            return True
            
        except Exception as e:
            logger.warning(f"TemperaturePoint validation failed: {e}")
            return False
    
    def _add_shape_to_geometry(self, geom, shape) -> None:
        """将Shape对象添加到COMSOL几何"""
        try:
            shape_type = shape.shape_type.value
            
            # 3D形状处理
            if shape_type == "cube":
                self._add_cube_to_geometry(geom, shape)
            elif shape_type == "cylinder":
                self._add_cylinder_to_geometry(geom, shape)
            elif shape_type == "hexagonal_prism":
                self._add_hexagonal_prism_to_geometry(geom, shape)
            elif shape_type == "oblique_cube":
                self._add_oblique_cube_to_geometry(geom, shape)
            elif shape_type == "rect_prism":
                self._add_rect_prism_to_geometry(geom, shape)
            elif shape_type == "square_prism":
                self._add_square_prism_to_geometry(geom, shape)
            elif shape_type == "oblong_x_prism":
                self._add_oblong_x_prism_to_geometry(geom, shape)
            elif shape_type == "oblong_y_prism":
                self._add_oblong_y_prism_to_geometry(geom, shape)
            elif shape_type == "rounded_rect_prism":
                self._add_rounded_rect_prism_to_geometry(geom, shape)
            elif shape_type == "chamfered_rect_prism":
                self._add_chamfered_rect_prism_to_geometry(geom, shape)
            elif shape_type == "n_sided_polygon_prism":
                self._add_n_sided_polygon_prism_to_geometry(geom, shape)
            elif shape_type == "prism":
                self._add_prism_to_geometry(geom, shape)
            elif shape_type == "trace":
                self._add_trace_to_geometry(geom, shape)
            # 2D形状处理
            elif shape_type == "circle":
                self._add_circle_to_geometry(geom, shape)
            elif shape_type == "rectangle":
                self._add_rectangle_to_geometry(geom, shape)
            elif shape_type == "square":
                self._add_square_to_geometry(geom, shape)
            elif shape_type == "oblong_x":
                self._add_oblong_x_to_geometry(geom, shape)
            elif shape_type == "oblong_y":
                self._add_oblong_y_to_geometry(geom, shape)
            elif shape_type == "rounded_rectangle":
                self._add_rounded_rectangle_to_geometry(geom, shape)
            elif shape_type == "chamfered_rectangle":
                self._add_chamfered_rectangle_to_geometry(geom, shape)
            elif shape_type == "n_sided_polygon":
                self._add_n_sided_polygon_to_geometry(geom, shape)
            else:
                logger.warning(f"Unsupported shape type: {shape_type}")
                # 使用通用方法
                self._add_generic_shape_to_geometry(geom, shape)
                
        except Exception as e:
            raise ComsolCreationError(f"Failed to add shape to geometry: {e}")
    
    def _add_cube_to_geometry(self, geom, cube) -> None:
        """添加立方体到COMSOL几何"""
        try:
            block = geom.feature().create("block", "Block")
            
            # 设置尺寸
            block.set("size", [cube.length, cube.width, cube.height])
            
            # 设置位置
            position = cube.position
            block.set("pos", [position.x, position.y, position.z])
            
            # 设置旋转
            if cube.rotation != 0:
                block.set("rot", cube.rotation)
            
            logger.debug("Added cube to geometry")
            
        except Exception as e:
            raise ComsolCreationError(f"Failed to add cube: {e}")
    
    def _add_cylinder_to_geometry(self, geom, cylinder) -> None:
        """添加圆柱体到COMSOL几何"""
        try:
            cyl = geom.feature().create("cyl", "Cylinder")
            
            # 设置半径和高度
            cyl.set("r", cylinder.radius)
            cyl.set("h", cylinder.height)
            
            # 设置位置
            position = cylinder.position
            cyl.set("pos", [position.x, position.y, position.z])
            
            # 设置旋转
            if cylinder.rotation != 0:
                cyl.set("rot", cylinder.rotation)
            
            logger.debug("Added cylinder to geometry")
            
        except Exception as e:
            raise ComsolCreationError(f"Failed to add cylinder: {e}")
    
    def _add_hexagonal_prism_to_geometry(self, geom, hex_prism) -> None:
        """添加六棱柱到COMSOL几何"""
        try:
            # 使用多边形棱柱
            poly = geom.feature().create("poly", "Polygon")
            
            # 设置边数
            poly.set("n", 6)
            
            # 设置半径
            poly.set("r", hex_prism.radius)
            
            # 设置高度
            poly.set("h", hex_prism.height)
            
            # 设置位置
            position = hex_prism.position
            poly.set("pos", [position.x, position.y, position.z])
            
            # 设置旋转
            if hex_prism.rotation != 0:
                poly.set("rot", hex_prism.rotation)
            
            logger.debug("Added hexagonal prism to geometry")
            
        except Exception as e:
            raise ComsolCreationError(f"Failed to add hexagonal prism: {e}")
    
    def _add_rect_prism_to_geometry(self, geom, rect_prism) -> None:
        """添加矩形棱柱到COMSOL几何"""
        try:
            block = geom.feature().create("block", "Block")
            
            # 设置尺寸
            block.set("size", [rect_prism.width, rect_prism.depth, rect_prism.height])
            
            # 设置位置
            position = rect_prism.position
            block.set("pos", [position.x, position.y, position.z])
            
            # 设置旋转
            if rect_prism.rotation != 0:
                block.set("rot", rect_prism.rotation)
            
            logger.debug("Added rectangular prism to geometry")
            
        except Exception as e:
            raise ComsolCreationError(f"Failed to add rectangular prism: {e}")
    
    def _add_square_prism_to_geometry(self, geom, square_prism) -> None:
        """添加正方形棱柱到COMSOL几何"""
        try:
            block = geom.feature().create("block", "Block")
            
            # 设置尺寸
            block.set("size", [square_prism.side, square_prism.side, square_prism.height])
            
            # 设置位置
            position = square_prism.position
            block.set("pos", [position.x, position.y, position.z])
            
            # 设置旋转
            if square_prism.rotation != 0:
                block.set("rot", square_prism.rotation)
            
            logger.debug("Added square prism to geometry")
            
        except Exception as e:
            raise ComsolCreationError(f"Failed to add square prism: {e}")
    
    def _add_oblique_cube_to_geometry(self, geom, oblique_cube) -> None:
        """添加斜立方体到COMSOL几何"""
        try:
            # 使用通用块，然后应用倾斜变换
            block = geom.feature().create("block", "Block")
            
            # 设置尺寸
            block.set("size", [oblique_cube.length, oblique_cube.width, oblique_cube.height])
            
            # 设置位置
            position = oblique_cube.position
            block.set("pos", [position.x, position.y, position.z])
            
            # 设置倾斜角度
            if hasattr(oblique_cube, 'tilt_x') and oblique_cube.tilt_x != 0:
                block.set("tiltx", oblique_cube.tilt_x)
            if hasattr(oblique_cube, 'tilt_y') and oblique_cube.tilt_y != 0:
                block.set("tilty", oblique_cube.tilt_y)
            
            # 设置旋转
            if oblique_cube.rotation != 0:
                block.set("rot", oblique_cube.rotation)
            
            logger.debug("Added oblique cube to geometry")
            
        except Exception as e:
            raise ComsolCreationError(f"Failed to add oblique cube: {e}")
    
    def _add_oblong_x_prism_to_geometry(self, geom, oblong_x_prism) -> None:
        """添加X方向椭圆形棱柱到COMSOL几何"""
        try:
            # 使用椭圆棱柱
            ellipsoid = geom.feature().create("ellipsoid", "Ellipsoid")
            
            # 设置尺寸
            ellipsoid.set("a", oblong_x_prism.length_x / 2)  # X方向半轴
            ellipsoid.set("b", oblong_x_prism.width_y / 2)   # Y方向半轴
            ellipsoid.set("c", oblong_x_prism.height / 2)    # Z方向半轴
            
            # 设置位置
            position = oblong_x_prism.position
            ellipsoid.set("pos", [position.x, position.y, position.z])
            
            # 设置旋转
            if oblong_x_prism.rotation != 0:
                ellipsoid.set("rot", oblong_x_prism.rotation)
            
            logger.debug("Added oblong X prism to geometry")
            
        except Exception as e:
            raise ComsolCreationError(f"Failed to add oblong X prism: {e}")
    
    def _add_oblong_y_prism_to_geometry(self, geom, oblong_y_prism) -> None:
        """添加Y方向椭圆形棱柱到COMSOL几何"""
        try:
            # 使用椭圆棱柱
            ellipsoid = geom.feature().create("ellipsoid", "Ellipsoid")
            
            # 设置尺寸
            ellipsoid.set("b", oblong_y_prism.length_y / 2)  # Y方向半轴
            ellipsoid.set("a", oblong_y_prism.width_x / 2)   # X方向半轴
            ellipsoid.set("c", oblong_y_prism.height / 2)    # Z方向半轴
            
            # 设置位置
            position = oblong_y_prism.position
            ellipsoid.set("pos", [position.x, position.y, position.z])
            
            # 设置旋转
            if oblong_y_prism.rotation != 0:
                ellipsoid.set("rot", oblong_y_prism.rotation)
            
            logger.debug("Added oblong Y prism to geometry")
            
        except Exception as e:
            raise ComsolCreationError(f"Failed to add oblong Y prism: {e}")
    
    def _add_rounded_rect_prism_to_geometry(self, geom, rounded_rect_prism) -> None:
        """添加圆角矩形棱柱到COMSOL几何"""
        try:
            # 使用圆角块
            rounded_block = geom.feature().create("rounded_block", "RoundedBlock")
            
            # 设置尺寸
            rounded_block.set("size", [rounded_rect_prism.width, rounded_rect_prism.depth, rounded_rect_prism.height])
            
            # 设置圆角半径
            if hasattr(rounded_rect_prism, 'corner_radius'):
                rounded_block.set("r", rounded_rect_prism.corner_radius)
            else:
                rounded_block.set("r", min(rounded_rect_prism.width, rounded_rect_prism.depth) * 0.1)
            
            # 设置位置
            position = rounded_rect_prism.position
            rounded_block.set("pos", [position.x, position.y, position.z])
            
            # 设置旋转
            if rounded_rect_prism.rotation != 0:
                rounded_block.set("rot", rounded_rect_prism.rotation)
            
            logger.debug("Added rounded rectangular prism to geometry")
            
        except Exception as e:
            raise ComsolCreationError(f"Failed to add rounded rectangular prism: {e}")
    
    def _add_chamfered_rect_prism_to_geometry(self, geom, chamfered_rect_prism) -> None:
        """添加倒角矩形棱柱到COMSOL几何"""
        try:
            # 使用倒角块
            chamfered_block = geom.feature().create("chamfered_block", "ChamferedBlock")
            
            # 设置尺寸
            chamfered_block.set("size", [chamfered_rect_prism.width, chamfered_rect_prism.depth, chamfered_rect_prism.height])
            
            # 设置倒角距离
            if hasattr(chamfered_rect_prism, 'chamfer_distance'):
                chamfered_block.set("d", chamfered_rect_prism.chamfer_distance)
            else:
                chamfered_block.set("d", min(chamfered_rect_prism.width, chamfered_rect_prism.depth) * 0.1)
            
            # 设置位置
            position = chamfered_rect_prism.position
            chamfered_block.set("pos", [position.x, position.y, position.z])
            
            # 设置旋转
            if chamfered_rect_prism.rotation != 0:
                chamfered_block.set("rot", chamfered_rect_prism.rotation)
            
            logger.debug("Added chamfered rectangular prism to geometry")
            
        except Exception as e:
            raise ComsolCreationError(f"Failed to add chamfered rectangular prism: {e}")
    
    def _add_n_sided_polygon_prism_to_geometry(self, geom, n_sided_prism) -> None:
        """添加N边形棱柱到COMSOL几何"""
        try:
            # 使用多边形棱柱
            poly_prism = geom.feature().create("poly_prism", "Polygon")
            
            # 设置边数
            poly_prism.set("n", n_sided_prism.n_sides)
            
            # 设置半径
            poly_prism.set("r", n_sided_prism.radius)
            
            # 设置高度
            poly_prism.set("h", n_sided_prism.height)
            
            # 设置位置
            position = n_sided_prism.position
            poly_prism.set("pos", [position.x, position.y, position.z])
            
            # 设置旋转
            if n_sided_prism.rotation != 0:
                poly_prism.set("rot", n_sided_prism.rotation)
            
            logger.debug("Added N-sided polygon prism to geometry")
            
        except Exception as e:
            raise ComsolCreationError(f"Failed to add N-sided polygon prism: {e}")
    
    def _add_prism_to_geometry(self, geom, prism) -> None:
        """添加通用棱柱到COMSOL几何"""
        try:
            # 使用多边形棱柱
            poly_prism = geom.feature().create("poly_prism", "Polygon")
            
            # 设置边数
            poly_prism.set("n", prism.n_sides)
            
            # 设置半径
            poly_prism.set("r", prism.radius)
            
            # 设置高度
            poly_prism.set("h", prism.height)
            
            # 设置位置
            position = prism.position
            poly_prism.set("pos", [position.x, position.y, position.z])
            
            # 设置旋转
            if prism.rotation != 0:
                poly_prism.set("rot", prism.rotation)
            
            logger.debug("Added generic prism to geometry")
            
        except Exception as e:
            raise ComsolCreationError(f"Failed to add generic prism: {e}")
    
    def _add_trace_to_geometry(self, geom, trace) -> None:
        """添加轨迹到COMSOL几何"""
        try:
            # 使用曲线特征
            curve = geom.feature().create("curve", "Curve")
            
            # 设置轨迹点
            if hasattr(trace, 'points') and trace.points:
                curve.set("points", trace.points)
            
            # 设置轨迹宽度
            if hasattr(trace, 'width'):
                curve.set("width", trace.width)
            
            # 设置轨迹高度
            if hasattr(trace, 'height'):
                curve.set("height", trace.height)
            
            # 设置位置
            position = trace.position
            curve.set("pos", [position.x, position.y, position.z])
            
            # 设置旋转
            if trace.rotation != 0:
                curve.set("rot", trace.rotation)
            
            logger.debug("Added trace to geometry")
            
        except Exception as e:
            raise ComsolCreationError(f"Failed to add trace: {e}")
    
    def _add_circle_to_geometry(self, geom, circle) -> None:
        """添加圆形到COMSOL几何"""
        try:
            # 使用圆形特征
            circle_feature = geom.feature().create("circle", "Circle")
            
            # 设置半径
            circle_feature.set("r", circle.radius)
            
            # 设置位置
            position = circle.position
            circle_feature.set("pos", [position.x, position.y])
            
            # 设置旋转
            if circle.rotation != 0:
                circle_feature.set("rot", circle.rotation)
            
            logger.debug("Added circle to geometry")
            
        except Exception as e:
            raise ComsolCreationError(f"Failed to add circle: {e}")
    
    def _add_rectangle_to_geometry(self, geom, rectangle) -> None:
        """添加矩形到COMSOL几何"""
        try:
            # 使用矩形特征
            rect_feature = geom.feature().create("rectangle", "Rectangle")
            
            # 设置尺寸
            rect_feature.set("size", [rectangle.width, rectangle.height])
            
            # 设置位置
            position = rectangle.position
            rect_feature.set("pos", [position.x, position.y])
            
            # 设置旋转
            if rectangle.rotation != 0:
                rect_feature.set("rot", rectangle.rotation)
            
            logger.debug("Added rectangle to geometry")
            
        except Exception as e:
            raise ComsolCreationError(f"Failed to add rectangle: {e}")
    
    def _add_square_to_geometry(self, geom, square) -> None:
        """添加正方形到COMSOL几何"""
        try:
            # 使用正方形特征
            square_feature = geom.feature().create("square", "Square")
            
            # 设置边长
            square_feature.set("size", square.side)
            
            # 设置位置
            position = square.position
            square_feature.set("pos", [position.x, position.y])
            
            # 设置旋转
            if square.rotation != 0:
                square_feature.set("rot", square.rotation)
            
            logger.debug("Added square to geometry")
            
        except Exception as e:
            raise ComsolCreationError(f"Failed to add square: {e}")
    
    def _add_oblong_x_to_geometry(self, geom, oblong_x) -> None:
        """添加X方向椭圆形到COMSOL几何"""
        try:
            # 使用椭圆特征
            ellipse_feature = geom.feature().create("ellipse", "Ellipse")
            
            # 设置尺寸
            ellipse_feature.set("a", oblong_x.length_x / 2)  # X方向半轴
            ellipse_feature.set("b", oblong_x.width_y / 2)   # Y方向半轴
            
            # 设置位置
            position = oblong_x.position
            ellipse_feature.set("pos", [position.x, position.y])
            
            # 设置旋转
            if oblong_x.rotation != 0:
                ellipse_feature.set("rot", oblong_x.rotation)
            
            logger.debug("Added oblong X to geometry")
            
        except Exception as e:
            raise ComsolCreationError(f"Failed to add oblong X: {e}")
    
    def _add_oblong_y_to_geometry(self, geom, oblong_y) -> None:
        """添加Y方向椭圆形到COMSOL几何"""
        try:
            # 使用椭圆特征
            ellipse_feature = geom.feature().create("ellipse", "Ellipse")
            
            # 设置尺寸
            ellipse_feature.set("b", oblong_y.length_y / 2)  # Y方向半轴
            ellipse_feature.set("a", oblong_y.width_x / 2)   # X方向半轴
            
            # 设置位置
            position = oblong_y.position
            ellipse_feature.set("pos", [position.x, position.y])
            
            # 设置旋转
            if oblong_y.rotation != 0:
                ellipse_feature.set("rot", oblong_y.rotation)
            
            logger.debug("Added oblong Y to geometry")
            
        except Exception as e:
            raise ComsolCreationError(f"Failed to add oblong Y: {e}")
    
    def _add_rounded_rectangle_to_geometry(self, geom, rounded_rectangle) -> None:
        """添加圆角矩形到COMSOL几何"""
        try:
            # 使用圆角矩形特征
            rounded_rect_feature = geom.feature().create("rounded_rect", "RoundedRectangle")
            
            # 设置尺寸
            rounded_rect_feature.set("size", [rounded_rectangle.width, rounded_rectangle.height])
            
            # 设置圆角半径
            if hasattr(rounded_rectangle, 'corner_radius'):
                rounded_rect_feature.set("r", rounded_rectangle.corner_radius)
            else:
                rounded_rect_feature.set("r", min(rounded_rectangle.width, rounded_rectangle.height) * 0.1)
            
            # 设置位置
            position = rounded_rectangle.position
            rounded_rect_feature.set("pos", [position.x, position.y])
            
            # 设置旋转
            if rounded_rectangle.rotation != 0:
                rounded_rect_feature.set("rot", rounded_rectangle.rotation)
            
            logger.debug("Added rounded rectangle to geometry")
            
        except Exception as e:
            raise ComsolCreationError(f"Failed to add rounded rectangle: {e}")
    
    def _add_chamfered_rectangle_to_geometry(self, geom, chamfered_rectangle) -> None:
        """添加倒角矩形到COMSOL几何"""
        try:
            # 使用倒角矩形特征
            chamfered_rect_feature = geom.feature().create("chamfered_rect", "ChamferedRectangle")
            
            # 设置尺寸
            chamfered_rect_feature.set("size", [chamfered_rectangle.width, chamfered_rectangle.height])
            
            # 设置倒角距离
            if hasattr(chamfered_rectangle, 'chamfer_distance'):
                chamfered_rect_feature.set("d", chamfered_rectangle.chamfer_distance)
            else:
                chamfered_rect_feature.set("d", min(chamfered_rectangle.width, chamfered_rectangle.height) * 0.1)
            
            # 设置位置
            position = chamfered_rectangle.position
            chamfered_rect_feature.set("pos", [position.x, position.y])
            
            # 设置旋转
            if chamfered_rectangle.rotation != 0:
                chamfered_rect_feature.set("rot", chamfered_rectangle.rotation)
            
            logger.debug("Added chamfered rectangle to geometry")
            
        except Exception as e:
            raise ComsolCreationError(f"Failed to add chamfered rectangle: {e}")
    
    def _add_n_sided_polygon_to_geometry(self, geom, n_sided_polygon) -> None:
        """添加N边形到COMSOL几何"""
        try:
            # 使用多边形特征
            polygon_feature = geom.feature().create("polygon", "Polygon")
            
            # 设置边数
            polygon_feature.set("n", n_sided_polygon.n_sides)
            
            # 设置半径
            polygon_feature.set("r", n_sided_polygon.radius)
            
            # 设置位置
            position = n_sided_polygon.position
            polygon_feature.set("pos", [position.x, position.y])
            
            # 设置旋转
            if n_sided_polygon.rotation != 0:
                polygon_feature.set("rot", n_sided_polygon.rotation)
            
            logger.debug("Added N-sided polygon to geometry")
            
        except Exception as e:
            raise ComsolCreationError(f"Failed to add N-sided polygon: {e}")
    
    def _add_generic_shape_to_geometry(self, geom, shape) -> None:
        """添加通用形状到COMSOL几何"""
        try:
            # 使用边界框创建通用形状
            bbox = shape.get_bounding_box()
            
            # 创建矩形块
            block = geom.feature().create("block", "Block")
            
            # 设置尺寸
            width = bbox.width()
            depth = bbox.depth()
            height = bbox.height()
            block.set("size", [width, depth, height])
            
            # 设置位置
            center_x = (bbox.min_x + bbox.max_x) / 2
            center_y = (bbox.min_y + bbox.max_y) / 2
            center_z = (bbox.min_z + bbox.max_z) / 2
            block.set("pos", [center_x, center_y, center_z])
            
            # 设置旋转
            if shape.rotation != 0:
                block.set("rot", shape.rotation)
            
            logger.debug(f"Added generic shape {shape.shape_type.value} to geometry")
            
        except Exception as e:
            raise ComsolCreationError(f"Failed to add generic shape: {e}")
    
    def _add_child_to_geometry(self, geom, child) -> None:
        """添加子组件到几何"""
        try:
            # 创建子几何对象
            child_geom = geom.create(f"child_{child.name}", "Block")
            
            # 添加形状（如果有）
            if hasattr(child, 'shape') and child.shape:
                self._add_shape_to_geometry(child_geom, child.shape)
            
            # 设置材料
            if child.material:
                self._assign_material_to_geometry(child_geom, child.material)
            
            logger.debug(f"Added child component {child.name}")
            
        except Exception as e:
            logger.warning(f"Failed to add child component {child.name}: {e}")
    
    def _setup_boolean_operations(self, geom, children) -> None:
        """设置布尔运算"""
        try:
            for i, child in enumerate(children):
                # 创建布尔运算特征
                boolean_feature = geom.feature().create(f"bool_{i}", "BooleanOperation")
                
                # 设置布尔运算类型（默认为差集）
                operation = getattr(child, 'boolean_operation', 'difference')
                boolean_feature.set("operation", operation)
                
                # 添加子几何
                boolean_feature.set("input", [f"child_{child.name}"])
                
            logger.debug("Boolean operations setup completed")
            
        except Exception as e:
            logger.warning(f"Failed to setup boolean operations: {e}")
    
    def _assign_material_to_geometry(self, geom, material) -> None:
        """将材料分配给几何对象"""
        try:
            # 获取几何对象的选择
            selection = geom.selection()
            
            # 设置材料
            geom.material().set("material", f"mat_{material.name}")
            
            logger.debug(f"Assigned material {material.name} to geometry")
            
        except Exception as e:
            logger.warning(f"Failed to assign material: {e}")
    
    def _setup_materials(self, thermal_info: ThermalInfo) -> None:
        """设置材料，使用自定义材料并从materialmgr获取材料信息"""
        logger.debug("Setting up custom materials from material manager")
        
        try:
            # 获取材料管理器
            materials_mgr = thermal_info.get_materials_mgr()
            
            # 获取所有使用的材料名称
            used_material_names = thermal_info.get_all_used_material_names()
            logger.debug(f"Found {len(used_material_names)} unique materials to create")
            
            # 创建所有使用的材料
            created_materials = {}
            for material_name in used_material_names:
                material_info = materials_mgr.get_material(material_name)
                if material_info:
                    # 创建COMSOL自定义材料
                    comsol_material_name = self._create_comsol_material(material_info)
                    if comsol_material_name:  # 只有成功创建的材料才添加到字典中
                        created_materials[material_name] = comsol_material_name
                        logger.debug(f"Created COMSOL material: {comsol_material_name} for {material_name}")
                    else:
                        logger.warning(f"Skipped material creation for: {material_name}")
                else:
                    logger.warning(f"Material {material_name} not found in material manager")
            
            # 统一创建材料对应的选择组（Union）
            self._build_material_selection_groups()
            
            # 将材料应用到几何对象
            self._apply_materials_to_geometry(thermal_info, created_materials)
            
            logger.debug("Successfully set up all custom materials")
            
        except Exception as e:
            raise ComsolCreationError(f"Failed to setup materials: {e}")
    
    def _get_section_geom_name(self, section_index: int, section_name: str) -> str:
        """生成section几何体名称"""
        return f"section_{section_name}_{section_index}"
    
    def _get_component_geom_name(self, section_index: int, section_name: str, comp_index: int) -> str:
        """获取（并在创建时使用）component几何体的规范名称"""
        return f"{self._get_section_geom_name(section_index, section_name)}_comp_{comp_index}"
    
    def _get_pkg_component_geom_name(self, comp_index: int, component_name: str) -> str:
        """生成PkgComponent几何体名称"""
        return f"pkg_component_{comp_index}_{component_name}"
    
    def _create_material_selection(self, geom_name: str, component) -> None:
        """为材料创建对应的选择组（延后统一构建）"""
        try:
            # 检查component是否有材料
            if not hasattr(component, 'material') or not component.material:
                logger.debug(f"Component {geom_name} has no material, skipping selection creation queueing")
                return
            
            # 获取材料名称（原始名，如 FR4）
            material_name = self._get_material_name(component.material)
            logger.debug(f"Queue material selection for {material_name} on geometry {geom_name}")
            
            # 记录到缓冲映射，稍后统一创建Union选择组
            name_set = self.material_selection_inputs.get(material_name)
            if name_set is None:
                name_set = set()
                self.material_selection_inputs[material_name] = name_set
            name_set.add(geom_name)
        except Exception as e:
            logger.warning(f"Failed to queue material selection for {geom_name}: {e}")
    
    def _build_material_selection_groups(self) -> None:
        """根据已记录的映射为每种材料创建/更新Union选择组"""
        try:
            if not self.material_selection_inputs:
                return
            selections = self.model/'selections'
            for material_name, geom_names in self.material_selection_inputs.items():
                if not geom_names:
                    continue
                sel_name = f"sel_{material_name}"
                try:
                    if sel_name in selections:
                        sel_node = selections/sel_name
                    else:
                        sel_node = selections.create('Union', name=sel_name)
                    # 将名称转换为可用的选择节点 tag 列表
                    input_tags = []
                    for name in geom_names:
                        if name in selections:
                            try:
                                input_tags.append((selections/name).tag())
                            except Exception:
                                pass
                    if not input_tags:
                        logger.debug(f"No valid inputs for selection {sel_name} yet; skip")
                        continue
                    # 优先使用 java.selection 接口
                    try:
                        sel_node.java.selection('input').set(*input_tags)
                    except Exception:
                        # 回退到 property 接口
                        try:
                            sel_node.property('input', input_tags)
                        except Exception:
                            logger.warning(f"Failed to set inputs for selection {sel_name}")
                    # 尝试设置为3D域
                    try:
                        sel_node.property('entitydim', 3)
                    except Exception:
                        pass
                    logger.debug(f"Built/updated material selection group {sel_name} with {len(input_tags)} inputs")
                except Exception as ie:
                    logger.warning(f"Failed to build selection group for material {material_name}: {ie}")
        except Exception as e:
            logger.warning(f"Failed to build material selection groups: {e}")
    
    def _apply_materials_to_geometry(self, thermal_info: ThermalInfo, created_materials: Dict[str, str]) -> None:
        """将创建的材料应用到对应的几何对象"""
        try:
            logger.debug("Applying materials to geometry objects")
            
            # 获取运行时sections
            sections = thermal_info.get_runtime_sections()
            
            for section_index, section in enumerate(sections):
                logger.debug(f"Applying materials for section: {section.get_name()}")
                
                # 处理section本身的材料
                if hasattr(section, 'material') and section.material:
                    material_name = self._get_material_name(section.material)
                    if material_name in created_materials:
                        comsol_material_name = created_materials[material_name]
                        section_geom_name = self._get_section_geom_name(section_index, section.get_name())
                        self._apply_material_to_geometry(comsol_material_name, section_geom_name)
                
                # 处理section的components
                if hasattr(section, 'children') and section.children:
                    for comp_index, component in enumerate(section.children):
                        if hasattr(component, 'material') and component.material:
                            material_name = self._get_material_name(component.material)
                            if material_name in created_materials:
                                comsol_material_name = created_materials[material_name]
                                geom_name = self._get_component_geom_name(section_index, section.get_name(), comp_index)
                                self._apply_material_to_geometry(comsol_material_name, geom_name)
            
            # 处理PkgDie中的PkgComponent材料
            if thermal_info.parts:
                logger.debug("Applying materials for PkgDie components")
                for comp_index, component in enumerate(thermal_info.parts.get_components()):
                    if hasattr(component, 'material') and component.material:
                        material_name = self._get_material_name(component.material)
                        if material_name in created_materials:
                            comsol_material_name = created_materials[material_name]
                            # 使用宏生成PkgComponent的几何体名称
                            geom_name = self._get_pkg_component_geom_name(comp_index, component.get_mdl_name())
                            self._apply_material_to_geometry(comsol_material_name, geom_name)
                            logger.debug(f"Applied material {material_name} to PkgComponent {component.get_mdl_name()}")
            
            logger.debug("Successfully applied all materials to geometry")
            
        except Exception as e:
            raise ComsolCreationError(f"Failed to apply materials to geometry: {e}")
    
    def _get_material_name(self, material) -> str:
        """获取材料名称，支持MaterialInfo和CompositeMaterial"""
        if hasattr(material, 'name'):
            return material.name
        elif isinstance(material, str):
            return material
        else:
            return str(material)
    
    def _apply_material_to_geometry(self, material_name: str, geom_name: str) -> None:
        """将材料应用到对应的几何对象（使用材料对应的选择组）"""
        try:
            logger.debug(f"Applying material {material_name} to geometry {geom_name}")
            
            material = self.material_objects.get(material_name)
            if not material:
                logger.warning(f"Material object {material_name} not found in saved objects")
                return
            
            # 从COMSOL材料名称中提取原始材料名称
            # material_name格式为 "mat_原始材料名"，需要提取原始材料名
            if material_name.startswith('mat_'):
                original_material_name = material_name[4:]  # 去掉 "mat_" 前缀
            else:
                original_material_name = material_name
            
            # 使用原始材料名称创建选择组名称
            material_selection_name = f"sel_{original_material_name}"
            selections = self.model/'selections'
            
            if material_selection_name in selections:
                # 直接使用材料对应的选择组
                sel_node = selections/material_selection_name
                material.select(sel_node)
                logger.debug(f"Material {material_name} bound to material selection {material_selection_name}")
            else:
                # 回退到原来的逻辑：按几何名匹配 selection
                logger.warning(f"Material selection {material_selection_name} not found, falling back to geometry-based selection")
                sel_node = None
                
                # 直接按几何名匹配 selection
                if geom_name in selections:
                    sel_node = selections/geom_name
                else:
                    # 模糊匹配：在所有 selection 名称里查包含几何名的项，优先 entitydim=3（如果存在）
                    try:
                        candidate_names = [name for name in self.model.selections() if geom_name in name]
                    except Exception:
                        candidate_names = []
                    for name in candidate_names:
                        node = selections/name
                        try:
                            props = node.properties()
                            ent = props.get('entitydim', None)
                            if ent in (3, '3', 3.0):
                                sel_node = node
                                break
                            if sel_node is None:
                                sel_node = node
                        except Exception:
                            sel_node = node
                            break
                
                if not sel_node:
                    logger.warning(f"No selection node found for geometry {geom_name}; skip material apply")
                    return
                
                material.select(sel_node)
                logger.debug(f"Material {material_name} bound to geometry-based selection for {geom_name}")
            
        except Exception as e:
            logger.warning(f"Failed to apply material {material_name} to geometry {geom_name}: {e}")
    
    def _create_comsol_material(self, material_info) -> str:
        """创建COMSOL自定义材料"""
        try:
            # 创建自定义材料对象 - 使用正确的MPh API
            material_name = f"mat_{material_info.name}"
            materials = self.model/'materials'
            material = materials.create('Common', name=material_name)
            
            # 所有材料都作为基础材料处理，material_type都是"thermal"
            if material_info.is_temperature_dependent():
                self._setup_temperature_dependent_material(material, material_info)
            else:
                self._setup_constant_material(material, material_info)
            
            # 保存材料对象到字典中
            self.material_objects[material_name] = material
            
            logger.debug(f"Created custom material: {material_name}")
            return material_name
            
        except Exception as e:
            raise ComsolCreationError(f"Failed to create material {material_info.name}: {e}")
    
    def _setup_temperature_dependent_material(self, material, material_info) -> None:
        """设置温度依赖性材料（当前禁用温变：使用首个温度点常数属性）"""
        try:
            # 用户要求：暂不处理温度依赖，取第一个温度点作为常数属性
            if not getattr(material_info, 'temperature_map', None):
                # 若无温度点，则回退到默认常数流程
                logger.debug(f"No temperature map for {material_info.name}, fallback to default constant setup")
                return self._setup_constant_material(material, material_info)

            # 选取最小温度对应的点
            try:
                first_temp = sorted(material_info.temperature_map.keys())[0]
            except Exception:
                first_temp = list(material_info.temperature_map.keys())[0]
            point = material_info.temperature_map[first_temp]

            conductivity = point.conductivity  # Conductivity 对象（含x,y,z/is_isotropic等）
            density = point.density
            heat_capacity = point.heat_capacity

            # 设置材料属性 - 使用COMSOL热传导模块属性
            if hasattr(conductivity, 'is_isotropic') and conductivity.is_isotropic():
                (material/'Basic').property("thermalconductivity", getattr(conductivity, 'get_average', lambda: conductivity.x)())
            else:
                (material/'Basic').property(
                    "thermalconductivity",
                    [str(conductivity.x), '0', '0', '0', str(getattr(conductivity, 'y', conductivity.x)), '0', '0', '0', str(getattr(conductivity, 'z', conductivity.x))]
                )
                (material/'Basic').property("thermalconductivity_symmetry", '0')

            (material/'Basic').property("density", density)
            (material/'Basic').property("heatcapacity", heat_capacity)

            logger.debug(f"Setup material as constant using first temperature point: {material_info.name} @ {first_temp}K")

        except Exception as e:
            raise ComsolCreationError(f"Failed to setup temperature dependent material (use first point): {e}")
    
    def _setup_constant_material(self, material, material_info) -> None:
        """设置常数材料"""
        try:
            # 获取默认温度下的属性
            default_temp = 293.15  # 20°C
            
            conductivity = material_info.get_conductivity(default_temp)
            density = material_info.get_density(default_temp)
            heat_capacity = material_info.get_heat_capacity(default_temp)
            
            # 设置材料属性 - 使用COMSOL热传导模块的正确属性名称
            if conductivity.is_isotropic():
                # 各向同性材料，使用热导率
                (material/'Basic').property("thermalconductivity", conductivity.get_average())
            else:
                # 各向异性材料，使用张量形式
                (material/'Basic').property("thermalconductivity", 
                    [str(conductivity.x), '0', '0', 
                     '0', str(conductivity.y), '0', 
                     '0', '0', str(conductivity.z)])
                (material/'Basic').property("thermalconductivity_symmetry", '0')
            
            (material/'Basic').property("density", density)
            (material/'Basic').property("heatcapacity", heat_capacity)
            
            logger.debug(f"Setup constant material: {material_info.name}")
            
        except Exception as e:
            raise ComsolCreationError(f"Failed to setup constant material: {e}")
    
    def _setup_composite_material(self, material, composite_material) -> None:
        """设置复合材料，使用优化后的CompositeMaterial类"""
        try:
            # 获取材料管理器
            materials_mgr = self.thermal_info.get_materials_mgr()
            
            # 获取默认温度下的有效属性
            default_temp = 293.15  # 20°C
            
            # 使用CompositeMaterial的方法计算有效属性
            conductivity = composite_material.get_effective_conductivity(materials_mgr, default_temp)
            density = composite_material.get_effective_density(materials_mgr, default_temp)
            heat_capacity = composite_material.get_effective_heat_capacity(materials_mgr, default_temp)
            
            # 设置材料属性 - 使用COMSOL热传导模块的正确属性名称
            if conductivity.is_isotropic():
                # 各向同性材料，使用k_iso
                material.property("k_iso", conductivity.get_average())
            else:
                # 各向异性材料，使用kii设置对角线元素
                material.property("kii", conductivity.x)  # 主对角线元素
                # 对于各向异性材料，可以设置kij=0（非对角线元素）
            
            material.property("rho", density)
            material.property("cp", heat_capacity)
            
            logger.debug(f"Setup composite material: {composite_material.name}")
            logger.debug(f"Effective properties - k: {conductivity}, rho: {density}, cp: {heat_capacity}")
                
        except Exception as e:
            raise ComsolCreationError(f"Failed to setup composite material: {e}")
    
    def _setup_object_material(self, material, object_material) -> None:
        """设置对象材料"""
        try:
            # 获取对象材料的基础材料
            base_material = object_material.get_base_material()
            
            if base_material:
                # 使用基础材料的属性
                if base_material.is_temperature_dependent():
                    self._setup_temperature_dependent_material(material, base_material)
                else:
                    self._setup_constant_material(material, base_material)
                
                # 应用对象特定的修改
                if hasattr(object_material, 'modifications'):
                    for mod in object_material.modifications:
                        if mod.property == "thermal_conductivity":
                            material.property("thermal_conductivity", mod.value)
                        elif mod.property == "density":
                            material.property("density", mod.value)
                        elif mod.property == "heat_capacity":
                            material.property("heat_capacity", mod.value)
                
                logger.debug(f"Setup object material: {object_material.name}")
            else:
                logger.warning(f"Object material {object_material.name} has no base material")
                
        except Exception as e:
            raise ComsolCreationError(f"Failed to setup object material: {e}")
    
    def _create_conductivity_function(self, material_info, func_name: str):
        """创建热导率函数"""
        try:
            # 创建插值函数 - 使用正确的MPh API
            functions = self.model/'functions'
            k_func = functions.create('Interpolation', name=func_name)
            
            # 获取温度点和热导率值
            temperatures = []
            conductivities = []
            
            for temp, point in material_info.temperature_map.items():
                temperatures.append(temp)
                conductivities.append(point.conductivity.x)  # 使用X方向热导率
            
            # 设置插值数据
            k_func.set("table", temperatures)
            k_func.set("values", conductivities)
            
            return k_func
            
        except Exception as e:
            raise ComsolCreationError(f"Failed to create conductivity function: {e}")
    
    def _create_density_function(self, material_info, func_name: str):
        """创建密度函数"""
        try:
            # 创建插值函数 - 使用正确的MPh API
            functions = self.model/'functions'
            rho_func = functions.create('Interpolation', name=func_name)
            
            # 获取插值数据
            temperatures = []
            densities = []
            
            for temp, point in material_info.temperature_map.items():
                temperatures.append(temp)
                densities.append(point.density)
            
            # 设置插值数据
            rho_func.set("table", temperatures)
            rho_func.set("values", densities)
            
            return rho_func
            
        except Exception as e:
            raise ComsolCreationError(f"Failed to create density function: {e}")
    
    def _create_heat_capacity_function(self, material_info, func_name: str):
        """创建比热容函数"""
        try:
            # 创建插值函数 - 使用正确的MPh API
            functions = self.model/'functions'
            cp_func = functions.create('Interpolation', name=func_name)
            
            # 获取插值数据
            temperatures = []
            heat_capacities = []
            
            for temp, point in material_info.temperature_map.items():
                temperatures.append(temp)
                heat_capacities.append(point.heat_capacity)
            
            # 设置插值数据
            cp_func.set("table", temperatures)
            cp_func.set("values", heat_capacities)
            
            return cp_func
            
        except Exception as e:
            raise ComsolCreationError(f"Failed to create heat capacity function: {e}")
    
    def _setup_heat_transfer(self, thermal_info: ThermalInfo) -> None:
        """设置热传递物理场"""
        logger.debug("Setting up heat transfer physics")
        
        try:
            # 创建热传递物理场 - 使用正确的MPh API
            physics = self.model/'physics'
            try:
                # 创建热传导（固体）物理场，命名为 heat
                heat_transfer = physics.create('HeatTransfer', self.geometry, name="heat")
                logger.debug("Successfully created HeatTransfer physics")
            except Exception as e:
                logger.warning(f"Failed to create HeatTransfer physics: {e}")
                logger.warning("Skipping heat transfer physics setup")
                return
            
            # 设置热源
            self._setup_heat_sources(heat_transfer, thermal_info)
            
            # 设置边界条件
            self._setup_boundary_conditions(heat_transfer, thermal_info)
            
            logger.debug("Heat transfer physics setup completed")
            
        except Exception as e:
            raise ComsolCreationError(f"Failed to setup heat transfer physics: {e}")
    
    def _setup_heat_sources(self, heat_transfer, thermal_info: ThermalInfo) -> None:
        """设置热源"""
        try:
            # 先处理基于参数的简单面热流（保留原逻辑）
            surface_heat_flux = thermal_info.parameters.get("surface_heat_flux", 0.0)
            if surface_heat_flux > 0:
                surface_source = heat_transfer.create("HeatFlux", name="surf_heat")
                # 使用 property 而不是 set
                try:
                    surface_source.property("Q0", surface_heat_flux)
                except Exception:
                    pass
                # 设置选择为装配体（若不支持则忽略）
                try:
                    surface_source.property("selection", "assembly")
                except Exception:
                    try:
                        surface_source.selection().property("selection", "assembly")
                    except Exception:
                        pass

            # 遍历运行时区域：若是StackedDieSection（或含total_power）则在对应域添加总功率热源
            for idx, section in enumerate(thermal_info.get_runtime_sections()):
                total_power = getattr(section, 'total_power', 0.0)
                if total_power and total_power > 0:
                    # 获取该区域的几何选择名
                    if hasattr(section, 'get_name'):
                        base_name = section.get_name()
                        geom_name = self._get_section_geom_name(idx, base_name)
                    else:
                        base_name = f"section_{idx}"
                        geom_name = base_name

                    # 为该区域创建（或更新）专用选择组（Union），后续由物理场引用
                    power_sel_name = f"selpow_{geom_name}"
                    try:
                        self._create_union_selection(power_sel_name, [geom_name])
                    except Exception:
                        pass

                    # 创建总功率热源（HeatRate）
                    hs_name = f"hs_{geom_name}"
                    hs_node = heat_transfer.create("HeatSource", name=hs_name)
                    try:
                        hs_node.property("heatSourceType", "HeatRate")
                    except Exception as e:
                        logger.warning(f"Failed to set heatSourceType for {hs_name}: {e}")
                    try:
                        hs_node.property("P0", total_power)
                    except Exception as e:
                        logger.warning(f"Failed to set P0 for {hs_name}: {e}")
                    # 绑定到命名选择节点，避免"手动"
                    try:
                        selections = self.model/'selections'
                        if power_sel_name in selections:
                            sel_node = selections/power_sel_name
                            logger.debug(f"Binding heat source {hs_name} to selection {power_sel_name}")
                            hs_node.select(sel_node)
                        else:
                            logger.warning(f"Selection {power_sel_name} not found when binding heat source {hs_name}")
                    except Exception as e:
                        logger.warning(f"Failed to bind heat source {hs_name} to selection {power_sel_name}: {e}")

            logger.debug("Heat sources setup completed")
        except Exception as e:
            logger.warning(f"Failed to setup heat sources: {e}")

    def _create_union_selection(self, selection_name: str, input_selection_names: list) -> None:
        """创建或更新一个Union类型的选择，其输入为已有的选择节点名称列表"""
        try:
            selections = self.model/'selections'
            if selection_name in selections:
                sel_node = selections/selection_name
            else:
                sel_node = selections.create('Union', name=selection_name)
            input_tags = []
            for name in input_selection_names:
                if name in selections:
                    try:
                        input_tags.append((selections/name).tag())
                    except Exception:
                        pass
            if not input_tags:
                logger.debug(f"No valid inputs found for union selection {selection_name}")
                return
            try:
                sel_node.java.selection('input').set(*input_tags)
            except Exception:
                try:
                    sel_node.property('input', input_tags)
                except Exception:
                    logger.warning(f"Failed to set inputs for union selection {selection_name}")
            try:
                sel_node.property('entitydim', 3)
            except Exception:
                pass
        except Exception as e:
            logger.warning(f"Failed to create union selection {selection_name}: {e}")
    
    def _setup_directional_heat_flux(self, heat_transfer, thermal_info: ThermalInfo) -> None:
        """设置方向性热流密度"""
        try:
            # 获取各个方向的热流密度参数
            heat_flux_params = {
                "air_heat_flux": thermal_info.parameters.get("air_heat_flux", 0.0),
                "top_heat_flux": thermal_info.parameters.get("top_heat_flux", 0.0),
                "side_heat_flux": thermal_info.parameters.get("side_heat_flux", 0.0),
                "bottom_heat_flux": thermal_info.parameters.get("bottom_heat_flux", 0.0)
            }
            
            # 为每个有热流密度的方向创建边界条件
            for direction, heat_flux in heat_flux_params.items():
                if heat_flux > 0:
                    # 创建热流边界条件
                    heat_flux_bc = heat_transfer.feature().create(f"heat_flux_{direction}", "HeatFlux")
                    heat_flux_bc.set("Q0", heat_flux)
                    heat_flux_bc.set("unit", "W/m^2")
                    
                    # 根据方向选择相应的表面
                    # 这里需要根据实际的几何结构来设置选择
                    # 暂时使用通用选择
                    heat_flux_bc.selection().set("assembly")
                    
                    logger.debug(f"Set {direction}: {heat_flux} W/m^2")
            
            logger.debug("Directional heat flux setup completed")
            
        except Exception as e:
            logger.warning(f"Failed to setup directional heat flux: {e}")
    
    def _setup_power_map_source(self, section, heat_transfer) -> None:
        """设置功率映射热源"""
        try:
            # 创建体积热源
            volume_source = heat_transfer.feature().create("vol_heat", "HeatSource")
            
            # 获取功率映射信息
            power_map_info = getattr(section, 'power_map', {})
            
            if power_map_info:
                # 从功率映射中获取功率密度
                if 'power_density' in power_map_info:
                    power_density = power_map_info['power_density']
                elif 'total_power' in power_map_info and 'volume' in power_map_info:
                    # 计算功率密度
                    power_density = power_map_info['total_power'] / power_map_info['volume']
                else:
                    # 使用默认功率密度
                    power_density = 1e6  # 默认功率密度
                
                volume_source.set("Q", power_density)
                
                # 设置功率映射函数（如果有）
                if 'function' in power_map_info:
                    functions = self.model/'functions'
                    power_func = functions.create('Analytic', name=f"power_map_{section.get_name()}")
                    power_func.set("expr", power_map_info['function'])
                    volume_source.set("Q", power_func)
                
                # 设置空间分布（如果有）
                if 'spatial_distribution' in power_map_info:
                    functions = self.model/'functions'
                    spatial_func = functions.create('Analytic', name=f"spatial_{section.get_name()}")
                    spatial_func.set("expr", power_map_info['spatial_distribution'])
                    volume_source.set("spatial", spatial_func)
            else:
                # 使用默认功率密度
                volume_source.set("Q", 1e6)
            
            # 选择对应的几何区域
            volume_source.selection().set(f"geom_{section.get_name()}")
            
            logger.debug(f"Setup power map source for {section.get_name()}")
            
        except Exception as e:
            logger.warning(f"Failed to setup power map source: {e}")
    
    def _setup_total_power_source(self, section, heat_transfer) -> None:
        """设置总功率热源"""
        try:
            # 创建体积热源
            volume_source = heat_transfer.feature().create("vol_heat", "HeatSource")
            
            # 获取总功率信息
            total_power = getattr(section, 'total_power', 0.0)
            
            if total_power > 0:
                # 计算功率密度
                if hasattr(section, 'volume') and section.volume > 0:
                    power_density = total_power / section.volume
                else:
                    # 使用形状的边界框计算体积
                    if section.shape:
                        bbox = section.shape.get_bounding_box()
                        volume = bbox.width() * bbox.depth() * bbox.height()
                        if volume > 0:
                            power_density = total_power / volume
                        else:
                            power_density = total_power  # 直接使用总功率
                    else:
                        power_density = total_power
                
                volume_source.set("Q", power_density)
                
                # 设置功率分布函数（如果有）
                if hasattr(section, 'power_distribution'):
                    functions = self.model/'functions'
                    power_func = functions.create('Analytic', name=f"power_dist_{section.get_name()}")
                    power_func.set("expr", section.power_distribution)
                    volume_source.set("Q", power_func)
            else:
                # 使用默认功率密度
                volume_source.set("Q", 1e6)
            
            # 选择对应的几何区域
            volume_source.selection().set(f"geom_{section.get_name()}")
            
            logger.debug(f"Setup total power source for {section.get_name()}")
            
        except Exception as e:
            logger.warning(f"Failed to setup total power source: {e}")
    
    def _setup_boundary_conditions(self, heat_transfer, thermal_info: ThermalInfo) -> None:
        """设置边界条件"""
        logger.debug("Setting up boundary conditions")
        try:
            # 环境温度
            ambient_temp = 293.15

            # 参考用户代码：使用Java API在ht物理场下创建hf1并选择所有边界
            j = self.model.java
            # 创建 feature
            try:
                j.component('comp1').physics('ht').create('hf1', 'HeatFluxBoundary', 2)
            except Exception:
                # 如果已存在则忽略
                pass
            # 配置参数
            try:
                j.component('comp1').physics('ht').feature('hf1').set('HeatFluxType', 'ConvectiveHeatFlux')
            except Exception:
                pass
            try:
                j.component('comp1').physics('ht').feature('hf1').set('h', '30')
            except Exception:
                pass
            try:
                j.component('comp1').physics('ht').feature('hf1').set('Tinf', str(ambient_temp))
            except Exception:
                pass
            # 选择全部边界
            try:
                j.component('comp1').physics('ht').feature('hf1').selection().all()
            except Exception:
                logger.warning("Failed to set selection().all() for hf1")
 
            logger.debug("Boundary conditions setup completed")
        except Exception as e:
            logger.warning(f"Failed to setup boundary conditions: {e}")
    
    def _setup_convection_boundary(self, heat_transfer, heat_sink_para: dict) -> None:
        """设置对流边界条件"""
        try:
            # 创建对流边界条件
            conv_bc = heat_transfer.feature().create("conv_bc", "ConvectiveHeatFlux")
            
            # 设置对流系数
            h_coeff = heat_sink_para.get("convection_coefficient", 10.0)
            conv_bc.set("h", h_coeff)
            
            # 设置环境温度
            T_inf = heat_sink_para.get("ambient_temperature", 293.15)
            conv_bc.set("Tinf", T_inf)
            
            # 选择散热器表面
            conv_bc.set("selection", "heat_sink_surface")
            
            logger.debug("Convection boundary condition setup completed")
            
        except Exception as e:
            logger.warning(f"Failed to setup convection boundary: {e}")
    
    def _setup_radiation_boundary(self, heat_transfer, radiation_para: dict) -> None:
        """设置辐射边界条件"""
        try:
            # 创建辐射边界条件
            rad_bc = heat_transfer.feature().create("rad_bc", "Radiation")
            
            # 设置发射率
            emissivity = radiation_para.get("emissivity", 0.8)
            rad_bc.set("epsilon", emissivity)
            
            # 设置环境温度
            T_amb = radiation_para.get("ambient_temperature", 293.15)
            rad_bc.set("Tamb", T_amb)
            
            # 设置辐射系数
            if "radiation_coefficient" in radiation_para:
                rad_coeff = radiation_para["radiation_coefficient"]
                rad_bc.set("hrad", rad_coeff)
            
            # 选择辐射表面
            rad_bc.set("selection", "radiation_surface")
            
            logger.debug("Radiation boundary condition setup completed")
            
        except Exception as e:
            logger.warning(f"Failed to setup radiation boundary: {e}")
    
    def _setup_adiabatic_boundary(self, heat_transfer, adiabatic_para: dict) -> None:
        """设置绝热边界条件"""
        try:
            # 创建绝热边界条件
            adia_bc = heat_transfer.feature().create("adia_bc", "ThermalInsulation")
            
            # 选择绝热表面
            adia_bc.set("selection", "adiabatic_surface")
            
            logger.debug("Adiabatic boundary condition setup completed")
            
        except Exception as e:
            logger.warning(f"Failed to setup adiabatic boundary: {e}")
    
    def _setup_heat_flux_boundary(self, heat_transfer, heat_flux_para: dict) -> None:
        """设置热流边界条件"""
        try:
            # 创建热流边界条件
            flux_bc = heat_transfer.feature().create("flux_bc", "HeatFlux")
            
            # 设置热流密度
            q0 = heat_flux_para.get("heat_flux_density", 0.0)
            flux_bc.set("Q0", q0)
            
            # 设置热流函数（如果有）
            if "heat_flux_function" in heat_flux_para:
                functions = self.model/'functions'
                flux_func = functions.create('Analytic', name="heat_flux_func")
                flux_func.set("expr", heat_flux_para["heat_flux_function"])
                flux_bc.set("Q0", flux_func)
            
            # 选择热流表面
            flux_bc.set("selection", "heat_flux_surface")
            
            logger.debug("Heat flux boundary condition setup completed")
            
        except Exception as e:
            logger.warning(f"Failed to setup heat flux boundary: {e}")
    
    def _generate_mesh(self, thermal_info: ThermalInfo) -> None:
        """生成网格"""
        logger.debug("Generating mesh")
        
        try:
            # 创建网格
            meshes = self.model/'meshes'
            mesh = meshes.create(self.geometry, name="mesh")
            
            # 获取网格参数
            mesh_params = thermal_info.parameters.get("mesh_parameters", {})
            
            # 设置网格尺寸
            mesh_size = mesh_params.get("mesh_size", "normal")
            mesh.set("size", mesh_size)
            
            # 设置网格类型
            mesh_type = mesh_params.get("mesh_type", "tetrahedral")
            if mesh_type == "hexahedral":
                mesh.set("method", "hexahedral")
            elif mesh_type == "prismatic":
                mesh.set("method", "prismatic")
            else:
                mesh.set("method", "tetrahedral")
            
            # 设置网格阶数
            element_order = mesh_params.get("element_order", "quadratic")
            mesh.set("elementorder", element_order)
            
            # 设置网格细化
            if "refinement" in mesh_params:
                refinement = mesh_params["refinement"]
                if refinement.get("use_refinement", False):
                    self._setup_mesh_refinement(mesh, refinement)
            
            # 设置网格质量
            if "quality" in mesh_params:
                quality = mesh_params["quality"]
                mesh.set("quality", quality.get("target_quality", 0.3))
            
            # 生成网格 - 暂时注释掉，手动执行网格生成
            # mesh.run()
            
            logger.debug("Mesh setup completed (manual mesh generation required)")
            
        except Exception as e:
            logger.warning(f"Failed to generate mesh: {e}")
    
    def _setup_mesh_refinement(self, mesh, refinement: dict) -> None:
        """设置网格细化"""
        try:
            # 创建网格细化特征
            refine_feature = mesh.feature().create("refine", "Refine")
            
            # 设置细化方法
            refine_method = refinement.get("method", "global")
            refine_feature.set("method", refine_method)
            
            # 设置细化次数
            refine_times = refinement.get("times", 1)
            refine_feature.set("times", refine_times)
            
            # 设置细化选择
            if "selection" in refinement:
                refine_feature.set("selection", refinement["selection"])
            
            logger.debug("Mesh refinement setup completed")
            
        except Exception as e:
            logger.warning(f"Failed to setup mesh refinement: {e}")
    
    def _setup_solver(self, thermal_info: ThermalInfo) -> None:
        """设置求解器"""
        logger.debug("Setting up solver")
        
        try:
            # 仅运行稳态研究，不做回退 - 暂时注释掉，手动执行求解
            # self.model.solve('static')
            logger.debug("Solver setup completed (manual solve required)")
            
        except Exception as e:
            # 不回退，直接抛出
            raise ComsolCreationError(f"Failed to setup solver: {e}")
    
    def _save_file(self, output_file: Path) -> None:
        """保存文件"""
        logger.debug(f"Saving file to: {output_file}")
        
        try:
            # 保存MPH文件
            self.model.save(str(output_file))
            logger.info(f"File saved successfully to: {output_file}")
            
        except Exception as e:
            raise ComsolCreationError(f"Failed to save file: {e}")
    
    def create_conversion_summary(self) -> Dict[str, Any]:
        """
        创建转换摘要信息
        
        Returns:
            Dict[str, Any]: 转换摘要
        """
        if not self.thermal_info:
            return {"error": "No data converted yet"}
        
        summary = {
            "model_name": self.thermal_info.name,
            "total_sections": len(self.thermal_info.get_runtime_sections()),
            "total_materials": len(self.thermal_info.get_materials_mgr().get_materials()),
            "conversion_status": "completed",
            "output_format": "COMSOL MPH"
        }
        
        return summary
    
    def get_conversion_statistics(self) -> Dict[str, Any]:
        """
        获取转换统计信息
        
        Returns:
            Dict[str, Any]: 转换统计
        """
        if not self.thermal_info:
            return {"error": "No data converted yet"}
        
        stats = {
            "geometry_objects": 0,
            "materials_created": 0,
            "physics_fields": 0,
            "boundary_conditions": 0,
            "mesh_elements": 0
        }
        
        try:
            # 统计几何对象
            if self.model and hasattr(self.model, 'geometries'):
                geometries = self.model.geometries()
                if geometries:
                    stats["geometry_objects"] = len(geometries)
                else:
                    stats["geometry_objects"] = 0
            
            # 统计材料
            if self.model:
                materials = self.model/'materials'
                stats["materials_created"] = len(materials.children())
            
            # 统计物理场
            if self.model:
                physics = self.model/'physics'
                stats["physics_fields"] = len(physics.children())
            
        except Exception:
            pass
        
        return stats
    
    def _setup_steady_heat_study(self) -> None:
        """设置稳态热单场研究（Stationary）并关联heat物理场"""
        try:
            studies = self.model/'studies'
            # 创建或获取研究
            if 'static' in self.model.studies():
                study = studies/'static'
            else:
                study = studies.create(name='static')
            
            # 创建或获取稳态步骤
            if 'stationary' in study:
                step = study/'stationary'
            else:
                step = study.create('Stationary', name='stationary')
            
            # 激活heat物理场
            physics = self.model/'physics'
            try:
                step.property('activate', [physics/'heat', 'on', 'frame:spatial1', 'on', 'frame:material1', 'on'])
            except Exception:
                # 兼容不同版本的激活格式
                pass
            
            logger.debug("Steady-state heat study setup completed")
        except Exception as e:
            logger.warning(f"Failed to setup steady-state study: {e}")

    def _ensure_all_boundary_selection(self):
        """确保存在一个选择所有边界的命名选择，返回该选择节点"""
        try:
            selections = self.model/'selections'
            sel_name = 'sel_all_boundaries'
            if sel_name in selections:
                return selections/sel_name
            node = selections.create('All', name=sel_name)
            try:
                node.property('entitydim', 2)
            except Exception:
                pass
            return node
        except Exception as e:
            logger.warning(f"Failed to ensure all-boundaries selection: {e}")
            return None

