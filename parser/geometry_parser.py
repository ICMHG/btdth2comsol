"""
几何解析器
负责解析几何区域定义，创建Section和SectionComponent对象
"""

from typing import List, Dict, Any, Optional
from loguru import logger

from core.thermal_info import ThermalInfo
from models.geometry import Section, SectionComponent
from models.shape import Vector3D
from models.pkg_die import PkgComponent
from models.stacked_die import StackedDieSection
from models.bump_section import BumpSection
from parser.shape_parser import ShapeParser, ShapeParsingError


class GeometryParsingError(Exception):
    """几何解析错误"""
    pass


class GeometryParser:
    """几何解析器"""
    
    def __init__(self, thermal_info: ThermalInfo):
        """
        初始化几何解析器
        
        Args:
            thermal_info: ThermalInfo对象
        """
        self.thermal_info = thermal_info
        self.shape_parser = ShapeParser()
        logger.debug("GeometryParser initialized")
    
    def parse_sections(self, sections_data: List[Dict[str, Any]]) -> None:
        """
        解析几何区域列表
        
        Args:
            sections_data: 几何区域数据列表
            
        Raises:
            GeometryParsingError: 解析失败时抛出
        """
        logger.info(f"Parsing {len(sections_data)} sections")
        
        for section_data in sections_data:
            try:
                section = self._parse_single_section(section_data)
                self.thermal_info.add_section(section)
                logger.debug(f"Added section: {section.name}")
            except Exception as e:
                logger.error(f"Failed to parse section: {e}")
                raise GeometryParsingError(f"Section parsing failed: {e}")
    
    def _parse_single_section(self, section_data: Dict[str, Any]) -> Section:
        """
        解析单个几何区域
        
        Args:
            section_data: 单个几何区域数据
            
        Returns:
            Section: 几何区域对象
            
        Raises:
            GeometryParsingError: 解析失败时抛出
        """
        # 验证必要字段
        required_fields = ["name"]
        for field in required_fields:
            if field not in section_data:
                raise GeometryParsingError(f"Missing required field: {field}")
        
        # 创建Section对象
        section_name = section_data["name"]
        section = Section(name=section_name)
        
        # 设置层信息
        if "layer" in section_data:
            section.layer = section_data["layer"]
        
        # 设置类型字符串
        if "type" in section_data:
            section.type_str = section_data["type"]
        
        # 设置厚度
        if "thickness" in section_data:
            thickness = float(section_data["thickness"])
            if thickness <= 0:
                raise GeometryParsingError(f"Invalid thickness for section {section_name}: {thickness}")
            section.thickness = thickness
        
        # 设置偏移量
        if "offset" in section_data:
            offset_data = section_data["offset"]
            if isinstance(offset_data, list) and len(offset_data) >= 3:
                # 如果是列表格式 [x, y, z]
                section.position = offset_data
            elif isinstance(offset_data, dict):
                # 如果是字典格式 {"x": x, "y": y, "z": z}
                offset_x = float(offset_data.get("x", 0.0))
                offset_y = float(offset_data.get("y", 0.0))
                offset_z = float(offset_data.get("z", 0.0))
                section.position = [offset_x, offset_y, offset_z]
        
        # 设置旋转角度
        if "rotation" in section_data:
            rotation = float(section_data["rotation"])
            section.rotation = rotation
        
        # 解析形状
        if "shape" in section_data:
            try:
                shape_string = section_data["shape"]
                shape = self.shape_parser.parse_shape_string(shape_string)
                section.shape = shape
            except ShapeParsingError as e:
                raise GeometryParsingError(f"Failed to parse shape for section {section_name}: {e}")
        
        # 解析材料
        if "materials" in section_data:
            materials_data = section_data["materials"]
            if isinstance(materials_data, list) and materials_data:
                # 处理复合材料
                if len(materials_data) > 1:
                    from models.material import CompositeMaterial
                    composite_material = CompositeMaterial()
                    
                    for mat_data in materials_data:
                        if isinstance(mat_data, dict):
                            material_name = mat_data.get("name", "")
                            percentage = float(mat_data.get("percentage", 1.0))
                            
                            if material_name:
                                material_info = self.thermal_info.get_materials_mgr().get_material(material_name)
                                if material_info:
                                    composite_material.add_material(material_info, percentage)
                                else:
                                    logger.warning(f"Material not found: {material_name}")
                    
                    if composite_material.materials:
                        section.material = composite_material
                else:
                    # 单一材料
                    material_name = materials_data[0].get("name", "") if isinstance(materials_data[0], dict) else str(materials_data[0])
                    if material_name:
                        material_info = self.thermal_info.get_materials_mgr().get_material(material_name)
                        if material_info:
                            section.material = material_info
                        else:
                            logger.warning(f"Material not found: {material_name}")
        
        # 解析子组件
        if "children" in section_data:
            children_data = section_data["children"]
            if isinstance(children_data, list):
                for child_data in children_data:
                    try:
                        child = self._parse_section_component(child_data)
                        section.add_component(child)
                    except Exception as e:
                        logger.warning(f"Failed to parse child component: {e}")
        
        # 注意：Section类目前不支持description和visible属性
        # 如果需要这些属性，可以在Section类中添加
        
        # 设置透明度（如果有）
        if "transparency" in section_data:
            transparency = float(section_data["transparency"])
            if 0 <= transparency <= 1:
                section.set_transparency(transparency)
        
        logger.debug(f"Successfully parsed section: {section_name}")
        return section
    
    def _parse_section_component(self, component_data: Dict[str, Any]) -> SectionComponent:
        """
        解析区域组件
        
        Args:
            component_data: 组件数据
            
        Returns:
            SectionComponent: 区域组件对象
            
        Raises:
            GeometryParsingError: 解析失败时抛出
        """
        # 验证必要字段
        required_fields = ["name"]
        for field in required_fields:
            if field not in component_data:
                raise GeometryParsingError(f"Missing required field: {field}")
        
        # 创建SectionComponent对象
        component_name = component_data["name"]
        component = SectionComponent()
        component.set_name(component_name)
        
        # 设置模板名称（如果有）
        if "template_name" in component_data:
            component.set_template_name(component_data["template_name"])
        
        # 设置类型
        if "type" in component_data:
            component.set_type(component_data["type"])
        
        # 设置位置
        if "position" in component_data:
            pos_data = component_data["position"]
            if isinstance(pos_data, dict):
                x = float(pos_data.get("x", 0.0))
                y = float(pos_data.get("y", 0.0))
                z = float(pos_data.get("z", 0.0))
                component.set_position(Vector3D(x, y, z))
        
        # 设置旋转
        if "rotation" in component_data:
            rotation = float(component_data["rotation"])
            component.set_rotation(rotation)
        
        # 设置缩放
        if "scale" in component_data:
            scale_data = component_data["scale"]
            if isinstance(scale_data, dict):
                scale_x = float(scale_data.get("x", 1.0))
                scale_y = float(scale_data.get("y", 1.0))
                scale_z = float(scale_data.get("z", 1.0))
                component.set_scale(scale_x, scale_y, scale_z)
        
        # 设置材料
        if "material" in component_data:
            material_name = component_data["material"]
            if isinstance(material_name, str):
                material_info = self.thermal_info.get_materials_mgr().get_material(material_name)
                if material_info:
                    component.set_material(material_info)
                else:
                    logger.warning(f"Material not found for component {component_name}: {material_name}")
        
        # 设置布尔运算类型
        if "boolean_operation" in component_data:
            operation = component_data["boolean_operation"]
            if operation in ["union", "difference", "intersection"]:
                component.set_boolean_operation(operation)
        
        # 设置描述
        if "description" in component_data:
            component.set_description(component_data["description"])
        
        logger.debug(f"Successfully parsed component: {component_name}")
        return component
    
    def parse_stacked_die_sections(self, stacked_die_data: List[Dict[str, Any]]) -> None:
        """
        解析堆叠芯片区域
        
        Args:
            stacked_die_data: 堆叠芯片数据列表
            
        Raises:
            GeometryParsingError: 解析失败时抛出
        """
        logger.info(f"Parsing {len(stacked_die_data)} stacked die sections")
        
        for die_data in stacked_die_data:
            try:
                # 创建堆叠芯片区域
                from models.geometry import StackedDieSection
                stacked_die = StackedDieSection()
                
                # 设置基本信息
                if "name" in die_data:
                    stacked_die.set_name(die_data["name"])
                
                if "layer" in die_data:
                    stacked_die.set_layer(die_data["layer"])
                
                if "type" in die_data:
                    stacked_die.set_type_str(die_data["type"])
                
                # 设置功率类型
                if "power_type" in die_data:
                    power_type = die_data["power_type"]
                    stacked_die.set_power_type(power_type)
                
                # 设置功率映射文件
                if "power_map_file" in die_data:
                    power_map_file = die_data["power_map_file"]
                    stacked_die.set_power_map_file(power_map_file)
                
                # 设置堆叠层级
                if "stack_tier" in die_data:
                    stack_tier = int(die_data["stack_tier"])
                    stacked_die.set_stack_tier(stack_tier)
                
                # 设置bump信息
                if "bump" in die_data:
                    bump_data = die_data["bump"]
                    if isinstance(bump_data, dict):
                        from models.geometry import Bump
                        bump = Bump()
                        
                        if "diameter" in bump_data:
                            bump.set_diameter(float(bump_data["diameter"]))
                        
                        if "height" in bump_data:
                            bump.set_height(float(bump_data["height"]))
                        
                        if "material" in bump_data:
                            material_name = bump_data["material"]
                            material_info = self.thermal_info.get_materials_mgr().get_material(material_name)
                            if material_info:
                                bump.set_material(material_info)
                        
                        stacked_die.set_bump(bump)
                
                # 设置子芯片
                if "dies" in die_data:
                    dies_data = die_data["dies"]
                    if isinstance(dies_data, list):
                        for die_info in dies_data:
                            if isinstance(die_info, dict):
                                from models.geometry import Die
                                die = Die()
                                
                                if "name" in die_info:
                                    die.set_name(die_info["name"])
                                
                                if "thickness" in die_info:
                                    die.set_thickness(float(die_info["thickness"]))
                                
                                if "material" in die_info:
                                    material_name = die_info["material"]
                                    material_info = self.thermal_info.get_materials_mgr().get_material(material_name)
                                    if material_info:
                                        die.set_material(material_info)
                                
                                stacked_die.add_die(die)
                
                # 添加到ThermalInfo
                self.thermal_info.add_section(stacked_die)
                logger.debug(f"Added stacked die section: {stacked_die.name}")
                
            except Exception as e:
                logger.error(f"Failed to parse stacked die section: {e}")
                raise GeometryParsingError(f"Stacked die parsing failed: {e}")
    
    def parse_package_components(self, package_data: List[Dict[str, Any]]) -> None:
        """
        解析封装组件
        
        Args:
            package_data: 封装组件数据列表
            
        Raises:
            GeometryParsingError: 解析失败时抛出
        """
        logger.info(f"Parsing {len(package_data)} package components")
        
        for pkg_data in package_data:
            try:
                # 创建封装组件
                from models.geometry import PkgComponent
                pkg_component = PkgComponent()
                
                # 设置基本信息
                if "name" in pkg_data:
                    pkg_component.set_name(pkg_data["name"])
                
                if "ref_des" in pkg_data:
                    pkg_component.set_ref_des(pkg_data["ref_des"])
                
                if "model_name" in pkg_data:
                    pkg_component.set_model_name(pkg_data["model_name"])
                
                if "attach_layer" in pkg_data:
                    pkg_component.set_attach_layer(pkg_data["attach_layer"])
                
                # 设置封装参数
                if "package_parameters" in pkg_data:
                    pkg_params = pkg_data["package_parameters"]
                    if isinstance(pkg_params, dict):
                        from models.geometry import PackageParameters
                        package_params = PackageParameters()
                        
                        if "length" in pkg_params:
                            package_params.set_length(float(pkg_params["length"]))
                        
                        if "width" in pkg_params:
                            package_params.set_width(float(pkg_params["width"]))
                        
                        if "height" in pkg_params:
                            package_params.set_height(float(pkg_params["height"]))
                        
                        if "ball_pitch" in pkg_params:
                            package_params.set_ball_pitch(float(pkg_params["ball_pitch"]))
                        
                        pkg_component.set_package_parameters(package_params)
                
                # 添加到ThermalInfo
                self.thermal_info.add_section(pkg_component)
                logger.debug(f"Added package component: {pkg_component.name}")
                
            except Exception as e:
                logger.error(f"Failed to parse package component: {e}")
                raise GeometryParsingError(f"Package component parsing failed: {e}")
    
    def validate_geometry_consistency(self) -> bool:
        """
        验证几何一致性
        
        Returns:
            bool: 验证是否通过
        """
        logger.info("Validating geometry consistency")
        
        sections = self.thermal_info.get_all_sections()
        
        for section in sections:
            # 检查形状是否存在
            if not section.shape:
                logger.error(f"Section {section.name} has no shape")
                return False
            
            # 检查厚度是否有效
            if section.thickness <= 0:
                logger.error(f"Section {section.name} has invalid thickness: {section.thickness}")
                return False
            
            # 检查材料是否存在
            if section.material:
                if hasattr(section.material, 'name'):
                    material_name = section.material.name
                    if not self.thermal_info.get_materials_mgr().has_material(material_name):
                        logger.error(f"Section {section.name} references missing material: {material_name}")
                        return False
                elif hasattr(section.material, 'materials'):
                    # 复合材料
                    for material, _ in section.material.materials:
                        if not self.thermal_info.get_materials_mgr().has_material(material.name):
                            logger.error(f"Section {section.name} references missing material: {material.name}")
                            return False
        
        logger.info("Geometry consistency validation passed")
        return True
    
    def create_geometry_summary(self) -> Dict[str, Any]:
        """
        创建几何摘要信息
        
        Returns:
            Dict[str, Any]: 几何摘要
        """
        sections = self.thermal_info.get_all_sections()
        
        summary = {
            "total_sections": len(sections),
            "section_types": {},
            "shape_types": {},
            "material_usage": {},
            "thickness_stats": {
                "min": float('inf'),
                "max": 0.0,
                "total": 0.0
            }
        }
        
        for section in sections:
            # 统计区域类型
            section_type = section.type_str or "unknown"
            summary["section_types"][section_type] = summary["section_types"].get(section_type, 0) + 1
            
            # 统计形状类型
            if section.shape:
                if hasattr(section.shape, 'type') and hasattr(section.shape.type, 'value'):
                    shape_type = section.shape.type.value
                elif hasattr(section.shape, 'shape_type') and hasattr(section.shape.shape_type, 'value'):
                    shape_type = section.shape.shape_type.value
                else:
                    shape_type = type(section.shape).__name__
                summary["shape_types"][shape_type] = summary["shape_types"].get(shape_type, 0) + 1
            
            # 统计材料使用
            if section.material:
                if hasattr(section.material, 'name'):
                    material_name = section.material.name
                    summary["material_usage"][material_name] = summary["material_usage"].get(material_name, 0) + 1
                elif hasattr(section.material, 'materials'):
                    # 复合材料
                    for material, _ in section.material.materials:
                        material_name = material.name
                        summary["material_usage"][material_name] = summary["material_usage"].get(material_name, 0) + 1
            
            # 统计厚度
            thickness = section.thickness
            summary["thickness_stats"]["min"] = min(summary["thickness_stats"]["min"], thickness)
            summary["thickness_stats"]["max"] = max(summary["thickness_stats"]["max"], thickness)
            summary["thickness_stats"]["total"] += thickness
        
        # 计算平均厚度
        if summary["thickness_stats"]["total"] > 0:
            summary["thickness_stats"]["average"] = summary["thickness_stats"]["total"] / len(sections)
        
        return summary
    
    def export_geometry_to_dict(self) -> List[Dict[str, Any]]:
        """
        导出几何数据到字典格式
        
        Returns:
            List[Dict[str, Any]]: 几何数据列表
        """
        sections = self.thermal_info.get_all_sections()
        
        exported_sections = []
        for section in sections:
            section_dict = section.to_dict()
            exported_sections.append(section_dict)
        
        return exported_sections
    
    def import_geometry_from_dict(self, geometry_data: List[Dict[str, Any]]) -> None:
        """
        从字典格式导入几何数据
        
        Args:
            geometry_data: 几何数据列表
        """
        logger.info(f"Importing {len(geometry_data)} sections from dictionary")
        
        for section_data in geometry_data:
            try:
                section = Section.from_dict(section_data)
                self.thermal_info.add_section(section)
                logger.debug(f"Imported section: {section.name}")
            except Exception as e:
                logger.error(f"Failed to import section: {e}")
                raise GeometryParsingError(f"Geometry import failed: {e}")
    
    def parse_pkg_components(self, pkg_components_data: List[Dict[str, Any]]) -> None:
        """
        解析封装芯片组件列表
        
        Args:
            pkg_components_data: 封装芯片组件数据列表
        """
        logger.info(f"Parsing {len(pkg_components_data)} package components")
        
        for pkg_data in pkg_components_data:
            try:
                pkg_component = PkgComponent(pkg_data)
                self.thermal_info.add_pkg_component(pkg_component)
                logger.debug(f"Added package component: {pkg_component.get_mdl_name()}")
            except Exception as e:
                logger.error(f"Failed to parse package component: {e}")
                raise GeometryParsingError(f"Package component parsing failed: {e}")
    
    def parse_stacked_die_sections(self, stacked_die_data: List[Dict[str, Any]]) -> None:
        """
        解析堆叠芯片区域列表
        
        Args:
            stacked_die_data: 堆叠芯片区域数据列表
        """
        logger.info(f"Parsing {len(stacked_die_data)} stacked die sections")
        
        for stacked_die in stacked_die_data:
            try:
                stacked_die_section = StackedDieSection(stacked_die)
                self.thermal_info.add_stacked_die_section(stacked_die_section)
                logger.debug(f"Added stacked die section: {stacked_die_section.name}")
            except Exception as e:
                logger.error(f"Failed to parse stacked die section: {e}")
                raise GeometryParsingError(f"Stacked die section parsing failed: {e}")
    
    def parse_bump_sections(self, bump_sections_data: List[Dict[str, Any]]) -> None:
        """
        解析凸点区域列表
        
        Args:
            bump_sections_data: 凸点区域数据列表
        """
        logger.info(f"Parsing {len(bump_sections_data)} bump sections")
        
        for bump_data in bump_sections_data:
            try:
                bump_section = BumpSection(bump_data)
                self.thermal_info.add_bump_section(bump_section)
                logger.debug(f"Added bump section: {bump_section.name}")
            except Exception as e:
                logger.error(f"Failed to parse bump section: {e}")
                raise GeometryParsingError(f"Bump section parsing failed: {e}")

