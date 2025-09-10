"""
装配体转换器
负责创建COMSOL装配体
"""

from typing import Any, Dict, List, Optional
from loguru import logger

from models.geometry import Section, BaseComponent
from models.material import MaterialInfo


class AssemblyConverter:
    """装配体转换器"""
    
    def __init__(self):
        """初始化装配体转换器"""
        logger.debug("AssemblyConverter initialized")
    
    def create_assembly(self, model: Any, thermal_info: Any) -> Any:
        """
        创建COMSOL装配体
        
        Args:
            model: COMSOL模型对象
            thermal_info: 热分析信息对象
            
        Returns:
            Any: 装配体对象
        """
        logger.debug("Creating COMSOL assembly")
        
        try:
            # 获取装配体管理器
            assembly = model.geom("assembly")
            
            # 设置装配体参数
            self._setup_assembly_parameters(assembly, thermal_info)
            
            # 添加几何组件到装配体
            self._add_components_to_assembly(assembly, thermal_info)
            
            # 设置装配体关系
            self._setup_assembly_relationships(assembly, thermal_info)
            
            # 构建装配体
            assembly.run()
            
            logger.info("COMSOL assembly creation completed")
            return assembly
            
        except Exception as e:
            logger.error(f"Failed to create COMSOL assembly: {e}")
            return None
    
    def _setup_assembly_parameters(self, assembly: Any, thermal_info: Any) -> None:
        """
        设置装配体参数
        
        Args:
            assembly: 装配体对象
            thermal_info: 热分析信息对象
        """
        try:
            # 设置装配体名称
            assembly.set("name", "Assembly")
            
            # 设置装配体类型
            assembly.set("type", "assembly")
            
            # 设置装配体参数
            if hasattr(thermal_info, 'assembly_parameters'):
                params = thermal_info.assembly_parameters
                
                if 'tolerance' in params:
                    assembly.set("tolerance", str(params['tolerance']))
                
                if 'auto_repair' in params:
                    assembly.set("autoRepair", "on" if params['auto_repair'] else "off")
                
                if 'form_assembly' in params:
                    assembly.set("formAssembly", "on" if params['form_assembly'] else "off")
            
            logger.debug("Assembly parameters set successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup assembly parameters: {e}")
    
    def _add_components_to_assembly(self, assembly: Any, thermal_info: Any) -> None:
        """
        添加几何组件到装配体
        
        Args:
            assembly: 装配体对象
            thermal_info: 热分析信息对象
        """
        try:
            # 添加几何区域
            if hasattr(thermal_info, 'sections') and thermal_info.sections:
                self._add_sections_to_assembly(assembly, thermal_info.sections)
            
            # 添加封装组件
            if hasattr(thermal_info, 'pkg_components') and thermal_info.pkg_components:
                self._add_pkg_components_to_assembly(assembly, thermal_info.pkg_components)
            
            # 添加堆叠芯片区域
            if hasattr(thermal_info, 'stacked_die_sections') and thermal_info.stacked_die_sections:
                self._add_stacked_die_sections_to_assembly(assembly, thermal_info.stacked_die_sections)
            
            # 添加凸点区域
            if hasattr(thermal_info, 'bump_sections') and thermal_info.bump_sections:
                self._add_bump_sections_to_assembly(assembly, thermal_info.bump_sections)
            
        except Exception as e:
            logger.error(f"Failed to add components to assembly: {e}")
    
    def _add_sections_to_assembly(self, assembly: Any, sections: List[Section]) -> None:
        """
        添加几何区域到装配体
        
        Args:
            assembly: 装配体对象
            sections: 几何区域列表
        """
        try:
            for section in sections:
                if section.shape:
                    # 创建几何对象
                    geom_obj = self._create_geometry_object(assembly, section)
                    
                    if geom_obj:
                        # 设置材料
                        if section.material:
                            self._assign_material_to_geometry(assembly, geom_obj, section.material)
                        
                        # 设置位置和变换
                        self._apply_transformations(assembly, geom_obj, section)
                        
                        logger.debug(f"Added section {section.name} to assembly")
                        
        except Exception as e:
            logger.error(f"Failed to add sections to assembly: {e}")
    
    def _add_pkg_components_to_assembly(self, assembly: Any, pkg_components: List[Any]) -> None:
        """
        添加封装组件到装配体
        
        Args:
            assembly: 装配体对象
            pkg_components: 封装组件列表
        """
        try:
            for pkg_component in pkg_components:
                # 创建封装组件几何
                geom_obj = self._create_pkg_component_geometry(assembly, pkg_component)
                
                if geom_obj:
                    # 设置材料
                    if hasattr(pkg_component, 'material') and pkg_component.material:
                        self._assign_material_to_geometry(assembly, geom_obj, pkg_component.material)
                    
                    # 设置位置和变换
                    self._apply_pkg_component_transformations(assembly, geom_obj, pkg_component)
                    
                    logger.debug(f"Added package component {pkg_component.get_mdl_name()} to assembly")
                    
        except Exception as e:
            logger.error(f"Failed to add package components to assembly: {e}")
    
    def _add_stacked_die_sections_to_assembly(self, assembly: Any, stacked_die_sections: List[Any]) -> None:
        """
        添加堆叠芯片区域到装配体
        
        Args:
            assembly: 装配体对象
            stacked_die_sections: 堆叠芯片区域列表
        """
        try:
            for stacked_die in stacked_die_sections:
                # 创建堆叠芯片几何
                geom_obj = self._create_stacked_die_geometry(assembly, stacked_die)
                
                if geom_obj:
                    # 设置材料
                    if hasattr(stacked_die, 'material') and stacked_die.material:
                        self._assign_material_to_geometry(assembly, geom_obj, stacked_die.material)
                    
                    # 设置位置和变换
                    self._apply_stacked_die_transformations(assembly, geom_obj, stacked_die)
                    
                    logger.debug(f"Added stacked die section {stacked_die.name} to assembly")
                    
        except Exception as e:
            logger.error(f"Failed to add stacked die sections to assembly: {e}")
    
    def _add_bump_sections_to_assembly(self, assembly: Any, bump_sections: List[Any]) -> None:
        """
        添加凸点区域到装配体
        
        Args:
            assembly: 装配体对象
            bump_sections: 凸点区域列表
        """
        try:
            for bump_section in bump_sections:
                # 创建凸点几何
                geom_obj = self._create_bump_section_geometry(assembly, bump_section)
                
                if geom_obj:
                    # 设置材料
                    if hasattr(bump_section, 'underfill_material') and bump_section.underfill_material:
                        self._assign_material_to_geometry(assembly, geom_obj, bump_section.underfill_material)
                    
                    # 设置位置和变换
                    self._apply_bump_section_transformations(assembly, geom_obj, bump_section)
                    
                    logger.debug(f"Added bump section {bump_section.name} to assembly")
                    
        except Exception as e:
            logger.error(f"Failed to add bump sections to assembly: {e}")
    
    def _create_geometry_object(self, assembly: Any, section: Section) -> Optional[Any]:
        """
        创建几何对象
        
        Args:
            assembly: 装配体对象
            section: 几何区域对象
            
        Returns:
            Optional[Any]: 几何对象
        """
        try:
            # 根据形状类型创建相应的几何对象
            if hasattr(section.shape, 'shape_type'):
                shape_type = section.shape.shape_type.value
            else:
                shape_type = type(section.shape).__name__.lower()
            
            # 创建几何特征
            geom_feature = assembly.feature().create(f"{section.name}_geom", "Import")
            
            # 设置几何类型
            geom_feature.set("type", shape_type)
            
            # 设置几何参数
            self._set_geometry_parameters(geom_feature, section.shape)
            
            return geom_feature
            
        except Exception as e:
            logger.error(f"Failed to create geometry object for section {section.name}: {e}")
            return None
    
    def _create_pkg_component_geometry(self, assembly: Any, pkg_component: Any) -> Optional[Any]:
        """
        创建封装组件几何
        
        Args:
            assembly: 装配体对象
            pkg_component: 封装组件对象
            
        Returns:
            Optional[Any]: 几何对象
        """
        try:
            # 创建封装组件几何特征
            geom_feature = assembly.feature().create(f"{pkg_component.get_mdl_name()}_geom", "Import")
            
            # 设置几何类型
            geom_feature.set("type", "package")
            
            # 设置几何参数
            if hasattr(pkg_component, 'dimensions'):
                dims = pkg_component.dimensions
                geom_feature.set("size", [dims.get('length', 1), dims.get('width', 1), dims.get('height', 1)])
            
            return geom_feature
            
        except Exception as e:
            logger.error(f"Failed to create package component geometry: {e}")
            return None
    
    def _create_stacked_die_geometry(self, assembly: Any, stacked_die: Any) -> Optional[Any]:
        """
        创建堆叠芯片几何
        
        Args:
            assembly: 装配体对象
            stacked_die: 堆叠芯片对象
            
        Returns:
            Optional[Any]: 几何对象
        """
        try:
            # 创建堆叠芯片几何特征
            geom_feature = assembly.feature().create(f"{stacked_die.name}_geom", "Import")
            
            # 设置几何类型
            geom_feature.set("type", "stacked_die")
            
            # 设置几何参数
            if hasattr(stacked_die, 'thickness'):
                geom_feature.set("thickness", str(stacked_die.thickness))
            
            return geom_feature
            
        except Exception as e:
            logger.error(f"Failed to create stacked die geometry: {e}")
            return None
    
    def _create_bump_section_geometry(self, assembly: Any, bump_section: Any) -> Optional[Any]:
        """
        创建凸点区域几何
        
        Args:
            assembly: 装配体对象
            bump_section: 凸点区域对象
            
        Returns:
            Optional[Any]: 几何对象
        """
        try:
            # 创建凸点区域几何特征
            geom_feature = assembly.feature().create(f"{bump_section.name}_geom", "Import")
            
            # 设置几何类型
            geom_feature.set("type", "bump_array")
            
            # 设置几何参数
            if hasattr(bump_section, 'bump_array') and bump_section.bump_array:
                bump_array = bump_section.bump_array
                if hasattr(bump_array, 'pitch'):
                    geom_feature.set("pitch", str(bump_array.pitch))
                
                if hasattr(bump_array, 'diameter'):
                    geom_feature.set("diameter", str(bump_array.diameter))
            
            return geom_feature
            
        except Exception as e:
            logger.error(f"Failed to create bump section geometry: {e}")
            return None
    
    def _set_geometry_parameters(self, geom_feature: Any, shape: Any) -> None:
        """
        设置几何参数
        
        Args:
            geom_feature: 几何特征对象
            shape: 形状对象
        """
        try:
            # 根据形状类型设置参数
            if hasattr(shape, 'position'):
                geom_feature.set("pos", [shape.position.x, shape.position.y, shape.position.z])
            
            if hasattr(shape, 'length') and hasattr(shape, 'width') and hasattr(shape, 'height'):
                geom_feature.set("size", [shape.length, shape.width, shape.height])
            
            if hasattr(shape, 'radius'):
                geom_feature.set("r", str(shape.radius))
            
            if hasattr(shape, 'thickness'):
                geom_feature.set("h", str(shape.thickness))
            
        except Exception as e:
            logger.error(f"Failed to set geometry parameters: {e}")
    
    def _assign_material_to_geometry(self, assembly: Any, geom_obj: Any, material: MaterialInfo) -> None:
        """
        将材料分配给几何对象
        
        Args:
            assembly: 装配体对象
            geom_obj: 几何对象
            material: 材料对象
        """
        try:
            # 设置材料
            geom_obj.set("material", material.name)
            
            logger.debug(f"Assigned material {material.name} to geometry")
            
        except Exception as e:
            logger.error(f"Failed to assign material to geometry: {e}")
    
    def _apply_transformations(self, assembly: Any, geom_obj: Any, section: Section) -> None:
        """
        应用变换到几何对象
        
        Args:
            assembly: 装配体对象
            geom_obj: 几何对象
            section: 几何区域对象
        """
        try:
            # 应用旋转
            if hasattr(section, 'rotation') and section.rotation:
                geom_obj.set("rot", section.rotation)
            
            # 应用偏移
            if hasattr(section, 'offset'):
                offset = section.offset
                if hasattr(offset, 'x') and hasattr(offset, 'y') and hasattr(offset, 'z'):
                    geom_obj.set("pos", [offset.x, offset.y, offset.z])
            
        except Exception as e:
            logger.error(f"Failed to apply transformations: {e}")
    
    def _apply_pkg_component_transformations(self, assembly: Any, geom_obj: Any, pkg_component: Any) -> None:
        """
        应用变换到封装组件
        
        Args:
            assembly: 装配体对象
            geom_obj: 几何对象
            pkg_component: 封装组件对象
        """
        try:
            # 应用位置变换
            if hasattr(pkg_component, 'position'):
                pos = pkg_component.position
                if hasattr(pos, 'x') and hasattr(pos, 'y') and hasattr(pos, 'z'):
                    geom_obj.set("pos", [pos.x, pos.y, pos.z])
            
            # 应用旋转
            if hasattr(pkg_component, 'rotation') and pkg_component.rotation:
                geom_obj.set("rot", pkg_component.rotation)
            
        except Exception as e:
            logger.error(f"Failed to apply package component transformations: {e}")
    
    def _apply_stacked_die_transformations(self, assembly: Any, geom_obj: Any, stacked_die: Any) -> None:
        """
        应用变换到堆叠芯片
        
        Args:
            assembly: 装配体对象
            geom_obj: 几何对象
            stacked_die: 堆叠芯片对象
        """
        try:
            # 应用位置变换
            if hasattr(stacked_die, 'position'):
                pos = stacked_die.position
                if hasattr(pos, 'x') and hasattr(pos, 'y') and hasattr(pos, 'z'):
                    geom_obj.set("pos", [pos.x, pos.y, pos.z])
            
            # 应用旋转
            if hasattr(stacked_die, 'rotation') and stacked_die.rotation:
                geom_obj.set("rot", stacked_die.rotation)
            
        except Exception as e:
            logger.error(f"Failed to apply stacked die transformations: {e}")
    
    def _apply_bump_section_transformations(self, assembly: Any, geom_obj: Any, bump_section: Any) -> None:
        """
        应用变换到凸点区域
        
        Args:
            assembly: 装配体对象
            geom_obj: 几何对象
            bump_section: 凸点区域对象
        """
        try:
            # 应用位置变换
            if hasattr(bump_section, 'position'):
                pos = bump_section.position
                if hasattr(pos, 'x') and hasattr(pos, 'y') and hasattr(pos, 'z'):
                    geom_obj.set("pos", [pos.x, pos.y, pos.z])
            
            # 应用旋转
            if hasattr(bump_section, 'rotation') and bump_section.rotation:
                geom_obj.set("rot", bump_section.rotation)
            
        except Exception as e:
            logger.error(f"Failed to apply bump section transformations: {e}")
    
    def _setup_assembly_relationships(self, assembly: Any, thermal_info: Any) -> None:
        """
        设置装配体关系
        
        Args:
            assembly: 装配体对象
            thermal_info: 热分析信息对象
        """
        try:
            # 设置接触关系
            self._setup_contact_relationships(assembly, thermal_info)
            
            # 设置连接关系
            self._setup_connection_relationships(assembly, thermal_info)
            
            # 设置约束关系
            self._setup_constraint_relationships(assembly, thermal_info)
            
        except Exception as e:
            logger.error(f"Failed to setup assembly relationships: {e}")
    
    def _setup_contact_relationships(self, assembly: Any, thermal_info: Any) -> None:
        """
        设置接触关系
        
        Args:
            assembly: 装配体对象
            thermal_info: 热分析信息对象
        """
        try:
            # 检查是否有接触定义
            if hasattr(thermal_info, 'contact_relationships'):
                contacts = thermal_info.contact_relationships
                
                for i, contact in enumerate(contacts):
                    # 创建接触特征
                    contact_feature = assembly.feature().create(f"Contact{i+1}", "Contact")
                    
                    # 设置接触参数
                    if 'source' in contact:
                        contact_feature.set("source", contact['source'])
                    
                    if 'destination' in contact:
                        contact_feature.set("destination", contact['destination'])
                    
                    if 'type' in contact:
                        contact_feature.set("type", contact['type'])
                    
                    logger.debug(f"Contact relationship {i+1} created")
                    
        except Exception as e:
            logger.error(f"Failed to setup contact relationships: {e}")
    
    def _setup_connection_relationships(self, assembly: Any, thermal_info: Any) -> None:
        """
        设置连接关系
        
        Args:
            assembly: 装配体对象
            thermal_info: 热分析信息对象
        """
        try:
            # 检查是否有连接定义
            if hasattr(thermal_info, 'component_connect'):
                connections = thermal_info.component_connect
                
                for i, connection in enumerate(connections):
                    # 创建连接特征
                    connection_feature = assembly.feature().create(f"Connection{i+1}", "Connection")
                    
                    # 设置连接参数
                    if 'source' in connection:
                        connection_feature.set("source", connection['source'])
                    
                    if 'destination' in connection:
                        connection_feature.set("destination", connection['destination'])
                    
                    if 'type' in connection:
                        connection_feature.set("type", connection['type'])
                    
                    logger.debug(f"Connection relationship {i+1} created")
                    
        except Exception as e:
            logger.error(f"Failed to setup connection relationships: {e}")
    
    def _setup_constraint_relationships(self, assembly: Any, thermal_info: Any) -> None:
        """
        设置约束关系
        
        Args:
            assembly: 装配体对象
            thermal_info: 热分析信息对象
        """
        try:
            # 检查是否有约束定义
            if hasattr(thermal_info, 'constraints') and thermal_info.constraints:
                # 如果constraints是对象，尝试获取其属性
                if hasattr(thermal_info.constraints, 'constraints'):
                    constraints_list = thermal_info.constraints.constraints
                else:
                    # 尝试将对象转换为列表
                    try:
                        constraints_list = list(thermal_info.constraints)
                    except:
                        constraints_list = []
                
                for i, constraint in enumerate(constraints_list):
                    # 创建约束特征
                    constraint_feature = assembly.feature().create(f"Constraint{i+1}", "Constraint")
                    
                    # 设置约束参数
                    if hasattr(constraint, 'type'):
                        constraint_feature.set("type", constraint.type)
                    elif isinstance(constraint, dict) and 'type' in constraint:
                        constraint_feature.set("type", constraint['type'])
                    
                    if hasattr(constraint, 'selection'):
                        constraint_feature.set("selection", constraint.selection)
                    elif isinstance(constraint, dict) and 'selection' in constraint:
                        constraint_feature.set("selection", constraint['selection'])
                    
                    if hasattr(constraint, 'parameters'):
                        for param_name, param_value in constraint.parameters.items():
                            constraint_feature.set(param_name, str(param_value))
                    elif isinstance(constraint, dict) and 'parameters' in constraint:
                        for param_name, param_value in constraint['parameters'].items():
                            constraint_feature.set(param_name, str(param_value))
                    
                    logger.debug(f"Constraint relationship {i+1} created")
                    
        except Exception as e:
            logger.error(f"Failed to setup constraint relationships: {e}")
    
    def validate_assembly(self, assembly: Any) -> bool:
        """
        验证装配体
        
        Args:
            assembly: 装配体对象
            
        Returns:
            bool: 验证是否通过
        """
        try:
            if not assembly:
                logger.error("Assembly object is None")
                return False
            
            # 检查装配体状态
            assembly_status = assembly.status()
            
            if not assembly_status:
                logger.error("Failed to get assembly status")
                return False
            
            # 检查是否有错误
            if assembly_status.get("error", False):
                logger.error(f"Assembly has errors: {assembly_status.get('errorMessage', 'Unknown error')}")
                return False
            
            logger.info("Assembly validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Assembly validation failed: {e}")
            return False
    
    def get_assembly_info(self, assembly: Any) -> Dict:
        """
        获取装配体信息
        
        Args:
            assembly: 装配体对象
            
        Returns:
            Dict: 装配体信息
        """
        try:
            if not assembly:
                return {}
            
            # 获取装配体信息
            assembly_info = assembly.info()
            if not assembly_info:
                return {}
            
            return {
                'name': assembly_info.get("name", ""),
                'type': assembly_info.get("type", ""),
                'components': assembly_info.get("components", 0),
                'status': assembly_info.get("status", "unknown"),
                'error': assembly_info.get("error", False),
                'error_message': assembly_info.get("errorMessage", "")
            }
            
        except Exception as e:
            logger.error(f"Failed to get assembly info: {e}")
            return {}

