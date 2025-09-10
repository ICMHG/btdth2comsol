"""
VerticalInterconnectComponents模型类
对应C++的VerticalInterconnectComponents类，管理垂直互连组件
"""

from typing import Dict, Any, Optional, List
from enum import Enum
from loguru import logger


class ComponentType(Enum):
    """组件类型枚举，对应C++的ComponentType"""
    PAD_STACK = "PadStack"
    BALL_BUMP = "BallBump"


class VerticalInterconnectShape:
    """垂直互连形状基类，对应C++的VerticalInterconnectShape"""
    
    def __init__(self, json_data: Optional[Dict[str, Any]] = None):
        """
        初始化VerticalInterconnectShape
        
        Args:
            json_data: JSON数据字典
        """
        self.name: str = ""
        self.shape_type: str = ""
        
        # 从JSON加载数据
        if json_data:
            self.from_json(json_data)
    
    def from_json(self, json_data: Dict[str, Any]) -> None:
        """从JSON数据加载"""
        try:
            self.name = json_data.get("name", "")
            self.shape_type = json_data.get("shapeType", "")
            
            logger.debug(f"Loaded VerticalInterconnectShape: {self.name}")
            
        except Exception as e:
            logger.error(f"Failed to load VerticalInterconnectShape from JSON: {e}")
            raise
    
    def to_json(self) -> Dict[str, Any]:
        """转换为JSON数据"""
        try:
            data = {
                "name": self.name,
                "shapeType": self.shape_type
            }
            return data
            
        except Exception as e:
            logger.error(f"Failed to convert VerticalInterconnectShape to JSON: {e}")
            raise


class BallBumpShape(VerticalInterconnectShape):
    """球状凸点形状类，对应C++的BallBumpShape"""
    
    def __init__(self, json_data: Optional[Dict[str, Any]] = None):
        """
        初始化BallBumpShape
        
        Args:
            json_data: JSON数据字典
        """
        super().__init__(json_data)
        
        self.diameter: float = 0.0
        self.height: float = 0.0
        
        # 从JSON加载数据
        if json_data:
            self.from_json(json_data)
    
    def get_diameter(self) -> float:
        """获取直径"""
        return self.diameter
    
    def get_height(self) -> float:
        """获取高度"""
        return self.height
    
    def from_json(self, json_data: Dict[str, Any]) -> None:
        """从JSON数据加载"""
        try:
            super().from_json(json_data)
            
            self.diameter = json_data.get("diameter", 0.0)
            self.height = json_data.get("height", 0.0)
            
            logger.debug(f"Loaded BallBumpShape: {self.name}")
            
        except Exception as e:
            logger.error(f"Failed to load BallBumpShape from JSON: {e}")
            raise
    
    def to_json(self) -> Dict[str, Any]:
        """转换为JSON数据"""
        try:
            data = super().to_json()
            data.update({
                "diameter": self.diameter,
                "height": self.height
            })
            return data
            
        except Exception as e:
            logger.error(f"Failed to convert BallBumpShape to JSON: {e}")
            raise


class VerticalInterconnectInfo:
    """垂直互连信息基类，对应C++的VerticalInterconnectInfo"""
    
    def __init__(self, json_data: Optional[Dict[str, Any]] = None):
        """
        初始化VerticalInterconnectInfo
        
        Args:
            json_data: JSON数据字典
        """
        self.name: str = ""
        self.component_type: ComponentType = ComponentType.PAD_STACK
        self.shape: Optional[VerticalInterconnectShape] = None
        
        # 从JSON加载数据
        if json_data:
            self.from_json(json_data)
    
    def get_name(self) -> str:
        """获取名称"""
        return self.name
    
    def get_component_type(self) -> ComponentType:
        """获取组件类型"""
        return self.component_type
    
    def get_shape(self) -> Optional[VerticalInterconnectShape]:
        """获取形状"""
        return self.shape
    
    def from_json(self, json_data: Dict[str, Any]) -> None:
        """从JSON数据加载"""
        try:
            self.name = json_data.get("name", "")
            
            # 设置组件类型
            type_str = json_data.get("componentType", "PadStack")
            if type_str == "BallBump":
                self.component_type = ComponentType.BALL_BUMP
            else:
                self.component_type = ComponentType.PAD_STACK
            
            # 加载形状
            if "shape" in json_data:
                shape_data = json_data["shape"]
                if self.component_type == ComponentType.BALL_BUMP:
                    self.shape = BallBumpShape(shape_data)
                else:
                    self.shape = VerticalInterconnectShape(shape_data)
            
            logger.debug(f"Loaded VerticalInterconnectInfo: {self.name}")
            
        except Exception as e:
            logger.error(f"Failed to load VerticalInterconnectInfo from JSON: {e}")
            raise
    
    def to_json(self) -> Dict[str, Any]:
        """转换为JSON数据"""
        try:
            data = {
                "name": self.name,
                "componentType": self.component_type.value,
                "shape": self.shape.to_json() if self.shape else None
            }
            return data
            
        except Exception as e:
            logger.error(f"Failed to convert VerticalInterconnectInfo to JSON: {e}")
            raise


class BallBumpInfo(VerticalInterconnectInfo):
    """球状凸点信息类，对应C++的BallBumpInfo"""
    
    def __init__(self, json_data: Optional[Dict[str, Any]] = None):
        """
        初始化BallBumpInfo
        
        Args:
            json_data: JSON数据字典
        """
        super().__init__(json_data)
        
        # 强制设置为球状凸点类型
        self.component_type = ComponentType.BALL_BUMP
        
        # 球状凸点特有属性
        self.material: str = ""
        self.thermal_conductivity: float = 0.0
        
        # 从JSON加载数据
        if json_data:
            self.from_json(json_data)
    
    def get_material(self) -> str:
        """获取材料"""
        return self.material
    
    def get_thermal_conductivity(self) -> float:
        """获取热导率"""
        return self.thermal_conductivity
    
    def from_json(self, json_data: Dict[str, Any]) -> None:
        """从JSON数据加载"""
        try:
            super().from_json(json_data)
            
            self.material = json_data.get("material", "")
            self.thermal_conductivity = json_data.get("thermalConductivity", 0.0)
            
            logger.debug(f"Loaded BallBumpInfo: {self.name}")
            
        except Exception as e:
            logger.error(f"Failed to load BallBumpInfo from JSON: {e}")
            raise
    
    def to_json(self) -> Dict[str, Any]:
        """转换为JSON数据"""
        try:
            data = super().to_json()
            data.update({
                "material": self.material,
                "thermalConductivity": self.thermal_conductivity
            })
            return data
            
        except Exception as e:
            logger.error(f"Failed to convert BallBumpInfo to JSON: {e}")
            raise


class BallBumpsMgr:
    """球状凸点管理器类，对应C++的BallBumpsMgr"""
    
    def __init__(self):
        """初始化BallBumpsMgr"""
        self.ball_bumps: Dict[str, BallBumpInfo] = {}
    
    def add(self, ball_bump: BallBumpInfo) -> None:
        """添加球状凸点"""
        self.ball_bumps[ball_bump.get_name()] = ball_bump
        logger.debug(f"Added ball bump: {ball_bump.get_name()}")
    
    def get(self, name: str) -> Optional[BallBumpInfo]:
        """获取球状凸点"""
        return self.ball_bumps.get(name)
    
    def contains(self, name: str) -> bool:
        """检查是否包含指定名称的球状凸点"""
        return name in self.ball_bumps
    
    def delete_item(self, name: str) -> None:
        """删除球状凸点"""
        if name in self.ball_bumps:
            del self.ball_bumps[name]
            logger.debug(f"Deleted ball bump: {name}")
    
    def get_map(self) -> Dict[str, BallBumpInfo]:
        """获取球状凸点映射"""
        return self.ball_bumps
    
    def clear(self) -> None:
        """清空所有球状凸点"""
        self.ball_bumps.clear()
        logger.debug("Cleared all ball bumps")
    
    def from_json(self, json_data: Dict[str, Any]) -> None:
        """从JSON数据加载"""
        try:
            if "ballBumps" in json_data:
                bumps_data = json_data["ballBumps"]
                for bump_data in bumps_data:
                    bump = BallBumpInfo(bump_data)
                    self.add(bump)
            
            logger.debug(f"Loaded BallBumpsMgr with {len(self.ball_bumps)} bumps")
            
        except Exception as e:
            logger.error(f"Failed to load BallBumpsMgr from JSON: {e}")
            raise
    
    def to_json(self) -> Dict[str, Any]:
        """转换为JSON数据"""
        try:
            data = {
                "ballBumps": [bump.to_json() for bump in self.ball_bumps.values()]
            }
            return data
            
        except Exception as e:
            logger.error(f"Failed to convert BallBumpsMgr to JSON: {e}")
            raise
