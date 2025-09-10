"""
BallsBumps模型类
对应C++的BallsBumps类，管理球状凸点
"""

from typing import Dict, Any, Optional, List
from loguru import logger


class BallBump:
    """球状凸点类，对应C++的BallBump"""
    
    def __init__(self, json_data: Optional[Dict[str, Any]] = None):
        """
        初始化BallBump
        
        Args:
            json_data: JSON数据字典
        """
        # 这里需要根据C++的BallBump类添加具体的属性
        # 由于没有看到具体的C++代码，我先创建一个基础结构
        self.name: str = ""
        self.parameters: Dict[str, Any] = {}
        
        # 从JSON加载数据
        if json_data:
            self.from_json(json_data)
    
    def from_json(self, json_data: Dict[str, Any]) -> None:
        """从JSON数据加载"""
        try:
            self.name = json_data.get("name", "")
            self.parameters = json_data.copy()
            logger.debug(f"Loaded BallBump: {self.name}")
            
        except Exception as e:
            logger.error(f"Failed to load BallBump from JSON: {e}")
            raise
    
    def to_json(self) -> Dict[str, Any]:
        """转换为JSON数据"""
        try:
            data = {"name": self.name}
            data.update(self.parameters)
            return data
            
        except Exception as e:
            logger.error(f"Failed to convert BallBump to JSON: {e}")
            raise


class BallsBumps:
    """球状凸点管理器类，对应C++的BallsBumps"""
    
    def __init__(self):
        """初始化BallsBumps"""
        self.ball_bumps: List[BallBump] = []
    
    def add_ball_bump(self, ball_bump: BallBump) -> None:
        """添加球状凸点"""
        self.ball_bumps.append(ball_bump)
        logger.debug(f"Added ball bump: {ball_bump.name}")
    
    def get_ball_bumps(self) -> List[BallBump]:
        """获取所有球状凸点"""
        return self.ball_bumps
    
    def from_json(self, json_data: Dict[str, Any]) -> None:
        """从JSON数据加载"""
        try:
            if "ballBumps" in json_data:
                bumps_data = json_data["ballBumps"]
                for bump_data in bumps_data:
                    bump = BallBump(bump_data)
                    self.add_ball_bump(bump)
            
            logger.debug(f"Loaded BallsBumps with {len(self.ball_bumps)} bumps")
            
        except Exception as e:
            logger.error(f"Failed to load BallsBumps from JSON: {e}")
            raise
    
    def to_json(self) -> Dict[str, Any]:
        """转换为JSON数据"""
        try:
            data = {
                "ballBumps": [bump.to_json() for bump in self.ball_bumps]
            }
            return data
            
        except Exception as e:
            logger.error(f"Failed to convert BallsBumps to JSON: {e}")
            raise
