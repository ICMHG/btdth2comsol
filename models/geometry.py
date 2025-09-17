"""
几何模型
包含Section、BaseComponent、SectionComponent等几何相关类
"""

from typing import List, Dict, Optional, Any, Tuple
from enum import Enum
from loguru import logger


class ComponentType(Enum):
    """组件类型枚举"""
    BGA = "bga"
    SUBSTRATE = "substrate"
    MIDDLE = "middle"
    INTERPOSER = "interposer"
    DIE = "die"
    TSV = "tsv"
    VIA = "via"
    BUMP = "bump"
    TRACE = "trace"
    POWERCUBE = "powerCube"
    UNKNOWN = "unknown"


class BaseComponent:
    """基础组件类"""
    
    def __init__(self, name: str = ""):
        self.name = name
        self.shape = None
        self.material = None
        self.position = None
        self.type = ComponentType.UNKNOWN
    
    def get_offset_z(self) -> float:
        """获取Z偏移量"""
        if self.position:
            return self.position[2] if len(self.position) > 2 else 0.0
        return 0.0
    
    def get_bounding_box(self) -> Tuple[float, float, float, float, float, float]:
        """获取边界框"""
        return (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)


class Section(BaseComponent):
    """几何区域类"""
    
    def __init__(self, name: str = ""):
        super().__init__(name)
        self.layer = ""
        self.children: List['SectionComponent'] = []
        self.thickness = 0.0
        self.rotation = 0
        self.has_power = False
        self.total_power = 0.0
    
    def get_name(self) -> str:
        """获取区域名称"""
        return self.name
    
    def get_offset_z(self) -> float:
        """获取Z偏移量"""
        if self.position:
            return self.position[2] if len(self.position) > 2 else 0.0
        return 0.0
    
    def add_component(self, component: 'SectionComponent') -> None:
        """添加子组件"""
        self.children.append(component)
    
    def add_child_with_operation(self, child: 'SectionComponent', operation: str) -> None:
        """添加子组件并设置布尔运算"""
        child.boolean_operation = operation
        self.children.append(child)
    
    def get_children_bounding_box_union(self) -> Tuple[float, float, float, float, float, float]:
        """
        计算所有子组件的bounding box并集
        
        Returns:
            Tuple[float, float, float, float, float, float]: (min_x, min_y, min_z, max_x, max_y, max_z)
        """
        if not self.children:
            return (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        
        # 初始化边界框
        min_x = float('inf')
        min_y = float('inf')
        min_z = float('inf')
        max_x = float('-inf')
        max_y = float('-inf')
        max_z = float('-inf')
        
        for child in self.children:
            if hasattr(child, 'shape') and child.shape:
                # 获取子组件的bounding box
                bbox = child.shape.get_bounding_box()
                
                # 更新边界框
                min_x = min(min_x, bbox.min_x)
                min_y = min(min_y, bbox.min_y)
                min_z = min(min_z, bbox.min_z)
                max_x = max(max_x, bbox.max_x)
                max_y = max(max_y, bbox.max_y)
                max_z = max(max_z, bbox.max_z)
        
        # 如果没有有效的bounding box，返回默认值
        if min_x == float('inf'):
            return (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        
        return (min_x, min_y, min_z, max_x, max_y, max_z)
    
    def get_effective_dimensions(self) -> Tuple[float, float, float]:
        """
        获取有效的尺寸（长、宽、高）
        如果主形状的尺寸为0，则使用子组件的bounding box并集
        
        Returns:
            Tuple[float, float, float]: (length, width, height)
        """
        # 如果主形状存在且尺寸不为0，使用主形状的尺寸
        if hasattr(self, 'shape') and self.shape:
            if hasattr(self.shape, 'length') and hasattr(self.shape, 'width') and hasattr(self.shape, 'height'):
                if self.shape.length > 0 and self.shape.width > 0 and self.shape.height > 0:
                    return (self.shape.length, self.shape.width, self.shape.height)
        
        # 否则使用子组件的bounding box并集
        bbox = self.get_children_bounding_box_union()
        length = bbox[3] - bbox[0]  # max_x - min_x
        width = bbox[4] - bbox[1]   # max_y - min_y
        height = bbox[5] - bbox[2]  # max_z - min_z
        
        return (length, width, height)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "name": self.name,
            "layer": self.layer,
            "type": self.type.value if self.type else ComponentType.UNKNOWN.value,
            "thickness": self.thickness
        }
    
    def from_json(self, data: Dict[str, Any], materials_mgr=None, original_data=None, thermal_info=None) -> None:
        """从JSON数据加载，包含完整的解析逻辑"""
        # 设置基本信息
        self.name = data.get("name", "")
        self.layer = data.get("layer", "")
        type_str = data.get("type", "")
        if type_str:
            try:
                self.type = ComponentType(type_str)
            except ValueError:
                logger.warning(f"Unknown component type: {type_str}, using UNKNOWN")
                self.type = ComponentType.UNKNOWN
        else:
            self.type = ComponentType.UNKNOWN
        self.thickness = float(data.get("thickness", 0.0))
        
        # 设置偏移量
        if "offset" in data:
            offset_data = data["offset"]
            if isinstance(offset_data, list) and len(offset_data) >= 3:
                self.position = offset_data
            elif isinstance(offset_data, dict):
                offset_x = float(offset_data.get("x", 0.0))
                offset_y = float(offset_data.get("y", 0.0))
                offset_z = float(offset_data.get("z", 0.0))
                self.position = [offset_x, offset_y, offset_z]
        
        # 设置旋转角度
        if "rotation" in data:
            self.rotation = float(data["rotation"])
        
        # 解析形状
        if "shape" in data:
            from parser.shape_parser import ShapeParser
            shape_parser = ShapeParser()
            try:
                shape_string = data["shape"]
                self.shape = shape_parser.parse_shape_string(shape_string)
            except Exception as e:
                logger.warning(f"Failed to parse shape for section {self.name}: {e}")
        
        # 解析子组件
        if "children" in data:
            children_data = data["children"]
            if isinstance(children_data, list):
                for child_data in children_data:
                    try:
                        logger.info(f"Creating child component in section: {self.name}")
                        child = SectionComponent()
                        child.from_json(child_data, self.name, materials_mgr, original_data, thermal_info)
                        self.add_component(child)
                    except Exception as e:
                        logger.warning(f"Failed to parse child component: {e}")
        
        # 如果主形状的尺寸为0，使用子组件的bounding box并集
        if hasattr(self, 'shape') and self.shape:
            if hasattr(self.shape, 'length') and hasattr(self.shape, 'width') and hasattr(self.shape, 'height'):
                if self.shape.length == 0 or self.shape.width == 0 or self.shape.height == 0:
                    # 计算子组件的有效尺寸
                    effective_dims = self.get_effective_dimensions()
                    if effective_dims[0] > 0 and effective_dims[1] > 0 and effective_dims[2] > 0:
                        # 更新主形状的尺寸
                        self.shape.length = effective_dims[0]
                        self.shape.width = effective_dims[1]
                        self.shape.height = effective_dims[2]
                        logger.debug(f"Updated section {self.name} dimensions from children: {effective_dims}")
        
        # 解析材料
        if "materials" in data:
            materials_data = data["materials"]
            if isinstance(materials_data, list) and materials_data:
                # 处理复合材料
                if len(materials_data) > 1:
                    from models.composite import CompositeMaterial
                    composite_material = CompositeMaterial()
                    
                    for mat_data in materials_data:
                        if isinstance(mat_data, dict):
                            material_name = mat_data.get("name", "")
                            percentage = float(mat_data.get("percentage", 1.0))
                            
                            if material_name:
                                composite_material.add_material(material_name, percentage)
                    
                    if composite_material.materials:
                        self.material = composite_material
                else:
                    # 单一材料
                    material_name = materials_data[0].get("name", "") if isinstance(materials_data[0], dict) else str(materials_data[0])
                    if material_name and materials_mgr:
                        material_info = materials_mgr.get_material(material_name)
                        if material_info:
                            self.material = material_info
                        else:
                            logger.warning(f"Material not found: {material_name}")
        
        # 设置透明度（如果有）
        if "transparency" in data:
            transparency = float(data["transparency"])
            if 0 <= transparency <= 1:
                self.set_transparency(transparency)


class SectionComponent(BaseComponent):
    """区域组件类"""
    
    def __init__(self, name: str = ""):
        super().__init__(name)
        self.template_name = ""
        self.boolean_operation = "difference"
    
    def set_name(self, name: str) -> None:
        """设置组件名称"""
        self.name = name
    
    def set_template_name(self, template_name: str) -> None:
        """设置模板名称"""
        self.template_name = template_name
    
    def set_type(self, component_type: ComponentType) -> None:
        """设置类型"""
        self.type = component_type
    
    def set_position(self, position) -> None:
        """设置位置"""
        self.position = position
    
    def set_rotation(self, rotation: float) -> None:
        """设置旋转角度"""
        self.rotation = rotation
    
    def set_scale(self, scale_x: float, scale_y: float, scale_z: float) -> None:
        """设置缩放"""
        self.scale = [scale_x, scale_y, scale_z]
    
    def set_material(self, material) -> None:
        """设置材料"""
        self.material = material
    
    def set_boolean_operation(self, operation: str) -> None:
        """设置布尔运算类型"""
        self.boolean_operation = operation
    
    def set_description(self, description: str) -> None:
        """设置描述"""
        self.description = description
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "name": self.name,
            "template_name": self.template_name
        }
    
    def from_json(self, data: Dict[str, Any], parent_section_name: str = None, materials_mgr=None, original_data=None, thermal_info=None) -> None:
        """从JSON数据加载，包含完整的解析逻辑"""
        # 处理name字段，如果缺失则生成默认名称
        if "name" not in data or not data["name"]:
            import uuid
            component_name = f"component_{uuid.uuid4().hex[:8]}"
            logger.debug(f"Generated default name for component: {component_name}")
        else:
            component_name = data["name"]
        
        self.name = component_name
        
        # 设置模板名称（如果有）
        if "template_name" in data:
            self.set_template_name(data["template_name"])
        
        # 设置类型
        if "type" in data:
            self.set_type(data["type"])
        
        # 设置位置
        if "position" in data:
            pos_data = data["position"]
            if isinstance(pos_data, dict):
                from models.shape import Vector3D
                x = float(pos_data.get("x", 0.0))
                y = float(pos_data.get("y", 0.0))
                z = float(pos_data.get("z", 0.0))
                self.set_position(Vector3D(x, y, z))
        
        # 设置旋转
        if "rotation" in data:
            rotation = float(data["rotation"])
            self.set_rotation(rotation)
        
        # 设置缩放
        if "scale" in data:
            scale_data = data["scale"]
            if isinstance(scale_data, dict):
                scale_x = float(scale_data.get("x", 1.0))
                scale_y = float(scale_data.get("y", 1.0))
                scale_z = float(scale_data.get("z", 1.0))
                self.set_scale(scale_x, scale_y, scale_z)
        
        # 设置材料
        if "material" in data:
            material_name = data["material"]
            if isinstance(material_name, str) and material_name and materials_mgr:
                material_info = materials_mgr.get_material(material_name)
                if material_info:
                    self.set_material(material_info)
                    logger.debug(f"Set material for component {component_name}: {material_name}")
                else:
                    logger.warning(f"Material not found for component {component_name}: {material_name}")
        elif "materials" in data:
            # 处理materials字段（可能是列表格式）
            materials_data = data["materials"]
            if isinstance(materials_data, list) and materials_data and materials_mgr:
                # 取第一个材料
                material_data = materials_data[0]
                if isinstance(material_data, dict) and "name" in material_data:
                    material_name = material_data["name"]
                    if material_name:
                        material_info = materials_mgr.get_material(material_name)
                        if material_info:
                            self.set_material(material_info)
                            logger.debug(f"Set material for component {component_name}: {material_name}")
                        else:
                            logger.warning(f"Material not found for component {component_name}: {material_name}")
                elif isinstance(material_data, str) and material_data and materials_mgr:
                    material_info = materials_mgr.get_material(material_data)
                    if material_info:
                        self.set_material(material_info)
                        logger.debug(f"Set material for component {component_name}: {material_data}")
                    else:
                        logger.warning(f"Material not found for component {component_name}: {material_data}")
        else:
            # 子组件可能通过template引用，需要从template中获取完整信息
            logger.info(f"Looking for template info for component {component_name} in parent section: {parent_section_name}")
            template_info = self._get_template_info(data, component_name, parent_section_name, materials_mgr, original_data, thermal_info)
            if template_info:
                # 设置材料
                if template_info.get('material'):
                    self.set_material(template_info['material'])
                    logger.debug(f"Set material for component {component_name} from template: {template_info['material'].name}")
                
                # 设置形状
                if template_info.get('shape'):
                    self.shape = template_info['shape']
                    logger.debug(f"Set shape for component {component_name} from template")
                
                # 设置位置（从template字符串中提取）
                if template_info.get('position'):
                    self.set_position(template_info['position'])
                    logger.debug(f"Set position for component {component_name} from template: {template_info['position']}")
            else:
                logger.debug(f"Component {component_name} has no material or materials field (may be template-based)")
        
        # 设置布尔运算类型
        if "boolean_operation" in data:
            operation = data["boolean_operation"]
            if operation in ["union", "difference", "intersection"]:
                self.set_boolean_operation(operation)
        
        # 设置描述
        if "description" in data:
            self.set_description(data["description"])
    
    @classmethod
    def _get_template_info(cls, component_data: Dict[str, Any], component_name: str, parent_section_name: str = None, materials_mgr=None, original_data=None, thermal_info=None):
        """
        从template中获取完整信息（材料、形状、位置）
        
        Args:
            component_data: 组件数据
            component_name: 组件名称
            parent_section_name: 父section名称
            materials_mgr: 材料管理器
            original_data: 原始JSON数据
            thermal_info: 热信息对象
            
        Returns:
            Dict: 包含material、shape、position的字典，如果未找到返回None
        """
        # 检查是否有template字段
        if "template" not in component_data:
            logger.debug(f"Component {component_name} has no template field")
            return None
        else:
            logger.info(f"Component {component_name} has template field: {component_data['template']}")
        
        template_string = component_data["template"]
        if not isinstance(template_string, str):
            return None
        
        # 解析template字符串，提取template名称和位置
        # 格式: "GeneratedByC4bump_BUMP([-405000.000000,1458000.000000,1208880.000000])"
        import re
        match = re.match(r'^([^(]+)\(\[([^\]]+)\]\)', template_string)
        if not match:
            logger.debug(f"Failed to parse template string: {template_string}")
            return None
        
        template_name = match.group(1)
        position_str = match.group(2)
        
        # 解析位置
        try:
            position_values = [float(x.strip()) for x in position_str.split(',')]
            if len(position_values) >= 3:
                # 直接使用nm单位，不进行转换
                position = position_values[:3]
            else:
                position = [0.0, 0.0, 0.0]
        except ValueError:
            logger.warning(f"Failed to parse position from template: {position_str}")
            position = [0.0, 0.0, 0.0]
        
        logger.info(f"Extracting info from template: {template_name} for section: '{parent_section_name}', position: {position}")
        logger.info(f"Template string: {template_string}")
        
        # 从原始数据中查找template定义
        if not original_data:
            logger.debug(f"No original data available for template lookup")
            return None
        
        # 查找template定义
        template_def = None
        
        # 首先尝试从thermal_info的templates中查找
        if thermal_info and hasattr(thermal_info, 'templates'):
            logger.info(f"Looking for template {template_name} in thermal_info.templates: {list(thermal_info.templates.keys()) if thermal_info.templates else 'None'}")
            if template_name in thermal_info.templates:
                template_info = thermal_info.templates[template_name]
                # 将VerticalInterconnectInfo转换为字典格式
                template_def = template_info.to_json()
                logger.info(f"Found template {template_name} in thermal_info.templates")
        
        # 如果没找到，从原始数据中查找
        if not template_def and "templates" in original_data:
            for template_comp in original_data["templates"]:
                if template_comp.get("name") == template_name:
                    template_def = template_comp
                    break
        
        if not template_def:
            logger.warning(f"Template {template_name} not found in templates")
            return None
        
        # 从template的shapes中查找匹配的section
        if "shapes" in template_def:
            logger.info(f"Template {template_name} has {len(template_def['shapes'])} shapes")
            # 先打印所有可用的section
            available_sections = [shape.get("section", "unknown") for shape in template_def["shapes"]]
            logger.info(f"Template {template_name} available sections: {available_sections}")
            logger.info(f"Looking for parent_section_name: '{parent_section_name}'")
            
            for i, shape in enumerate(template_def["shapes"]):
                shape_section = shape.get("section", "unknown")
                logger.info(f"Template {template_name} shape {i}: section='{shape_section}', parent_section='{parent_section_name}'")
                logger.info(f"Section comparison: '{shape_section}' == '{parent_section_name}' ? {shape_section == parent_section_name}")
                if "section" in shape and shape["section"] == parent_section_name:
                    # 找到匹配的section，获取完整信息
                    result = {}
                    
                    # 获取材料信息
                    if "materials" in shape and shape["materials"]:
                        material_data = shape["materials"][0]
                        if isinstance(material_data, dict) and "name" in material_data:
                            material_name = material_data["name"]
                            if material_name and materials_mgr:
                                material_info = materials_mgr.get_material(material_name)
                                if material_info:
                                    result['material'] = material_info
                                    logger.debug(f"Found material {material_name} for template {template_name} in section {parent_section_name}")
                                else:
                                    logger.warning(f"Material {material_name} not found for template {template_name}")
                    
                    # 获取形状信息
                    if "shape" in shape:
                        shape_string = shape["shape"]
                        # 替换位置信息
                        # 格式: "cylinder([0,0,0],86000,92000)" -> "cylinder([-405000.000000,1458000.000000,1208880.000000],86000,92000)"
                        import re
                        shape_with_position = re.sub(r'\[0,0,0\]', f'[{position_str}]', shape_string)
                        
                        # 解析形状
                        try:
                            from parser.shape_parser import ShapeParser
                            shape_parser = ShapeParser()
                            parsed_shape = shape_parser.parse_shape_string(shape_with_position)
                            result['shape'] = parsed_shape
                            logger.debug(f"Parsed shape for template {template_name}: {shape_with_position}")
                        except Exception as e:
                            logger.warning(f"Failed to parse shape for template {template_name}: {e}")
                    
                    # 设置位置
                    result['position'] = position
                    
                    if result:
                        logger.info(f"Found complete template info for {template_name} in section {parent_section_name}")
                        logger.info(f"Template info: material={result.get('material', 'None')}, shape={result.get('shape', 'None')}, position={result.get('position', 'None')}")
                        return result
                    else:
                        logger.warning(f"No valid info found in template {template_name} for section {parent_section_name}")
                else:
                    logger.debug(f"Template {template_name} shape section {shape.get('section', 'unknown')} does not match {parent_section_name}")
        
        logger.warning(f"Template {template_name} found but no matching info for section {parent_section_name}")
        return None

