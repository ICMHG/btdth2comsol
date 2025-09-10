"""
VerticalInterconnectManager模型类
对应C++的VerticalInterconnectManager类，管理垂直互连管理器
"""

from typing import Dict, Any, Optional, List
from loguru import logger

from .vertical_interconnect_components import BallBumpsMgr, BallBumpInfo


class VerticalInterconnectManager:
    """垂直互连管理器类，对应C++的VerticalInterconnectManager"""
    
    def __init__(self):
        """初始化VerticalInterconnectManager"""
        self.ball_bumps_mgr: BallBumpsMgr = BallBumpsMgr()
        self.vertical_interconnect_components: Dict[str, Any] = {}
    
    def get_ball_bumps_mgr(self) -> BallBumpsMgr:
        """获取球状凸点管理器"""
        return self.ball_bumps_mgr
    
    def set_ball_bumps_mgr(self, mgr: BallBumpsMgr) -> None:
        """设置球状凸点管理器"""
        self.ball_bumps_mgr = mgr
        logger.debug("Set ball bumps manager")
    
    def add_vertical_interconnect_component(self, name: str, component: Any) -> None:
        """添加垂直互连组件"""
        self.vertical_interconnect_components[name] = component
        logger.debug(f"Added vertical interconnect component: {name}")
    
    def get_vertical_interconnect_component(self, name: str) -> Optional[Any]:
        """获取垂直互连组件"""
        return self.vertical_interconnect_components.get(name)
    
    def get_all_vertical_interconnect_components(self) -> Dict[str, Any]:
        """获取所有垂直互连组件"""
        return self.vertical_interconnect_components
    
    def from_json(self, json_data: Dict[str, Any]) -> None:
        """从JSON数据加载"""
        try:
            # 加载球状凸点管理器
            if "ballBumpsMgr" in json_data:
                self.ball_bumps_mgr.from_json(json_data["ballBumpsMgr"])
            
            # 加载垂直互连组件
            if "verticalInterconnectComponents" in json_data:
                components_data = json_data["verticalInterconnectComponents"]
                for name, component_data in components_data.items():
                    # 这里需要根据组件类型创建相应的对象
                    # 暂时存储为字典
                    self.vertical_interconnect_components[name] = component_data
            
            logger.debug("Loaded VerticalInterconnectManager")
            
        except Exception as e:
            logger.error(f"Failed to load VerticalInterconnectManager from JSON: {e}")
            raise
    
    def to_json(self) -> Dict[str, Any]:
        """转换为JSON数据"""
        try:
            data = {
                "ballBumpsMgr": self.ball_bumps_mgr.to_json(),
                "verticalInterconnectComponents": self.vertical_interconnect_components
            }
            return data
            
        except Exception as e:
            logger.error(f"Failed to convert VerticalInterconnectManager to JSON: {e}")
            raise
