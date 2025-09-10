"""
PackagePara模型类
对应C++的PackagePara类，管理封装参数
"""

from typing import Dict, Any, Optional
from loguru import logger


class PackagePara:
    """封装参数类，对应C++的PackagePara"""
    
    def __init__(self, json_data: Optional[Dict[str, Any]] = None):
        """
        初始化PackagePara
        
        Args:
            json_data: JSON数据字典
        """
        # 这里需要根据C++的PackagePara类添加具体的属性
        # 由于没有看到具体的C++代码，我先创建一个基础结构
        self.parameters: Dict[str, Any] = {}
        
        # 从JSON加载数据
        if json_data:
            self.from_json(json_data)
    
    def from_json(self, json_data: Dict[str, Any]) -> None:
        """从JSON数据加载"""
        try:
            self.parameters = json_data.copy()
            logger.debug("Loaded PackagePara from JSON")
            
        except Exception as e:
            logger.error(f"Failed to load PackagePara from JSON: {e}")
            raise
    
    def to_json(self) -> Dict[str, Any]:
        """转换为JSON数据"""
        try:
            return self.parameters.copy()
            
        except Exception as e:
            logger.error(f"Failed to convert PackagePara to JSON: {e}")
            raise
