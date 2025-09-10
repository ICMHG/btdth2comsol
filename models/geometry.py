"""
几何模型
包含Section、BaseComponent、SectionComponent等几何相关类
"""

from typing import List, Dict, Optional, Any, Tuple
from loguru import logger


class BaseComponent:
    """基础组件类"""
    
    def __init__(self, name: str = ""):
        self.name = name
        self.shape = None
        self.material = None
        self.position = None
        self.type = None
    
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
        self.type_str = ""
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
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "name": self.name,
            "layer": self.layer,
            "type": self.type_str,
            "thickness": self.thickness
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Section':
        """从字典格式创建"""
        section = cls(data.get("name", ""))
        section.layer = data.get("layer", "")
        section.type_str = data.get("type", "")
        section.thickness = data.get("thickness", 0.0)
        return section


class SectionComponent(BaseComponent):
    """区域组件类"""
    
    def __init__(self, name: str = ""):
        super().__init__(name)
        self.template_name = ""
        self.boolean_operation = "difference"
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "name": self.name,
            "template_name": self.template_name
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SectionComponent':
        """从字典格式创建"""
        component = cls(data.get("name", ""))
        component.template_name = data.get("template_name", "")
        return component

