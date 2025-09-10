"""
BumpFileInfo模型类
对应C++的BumpFileInfo类，管理凸点文件信息
"""

from typing import Dict, Any, Optional, List
from loguru import logger


class BumpModel:
    """凸点模型类，对应C++的BumpModel"""
    
    def __init__(self, json_data: Optional[Dict[str, Any]] = None):
        """
        初始化BumpModel
        
        Args:
            json_data: JSON数据字典
        """
        self.name: str = ""
        self.diameter: float = 0.0
        self.height: float = 0.0
        self.material: str = ""
        
        # 从JSON加载数据
        if json_data:
            self.from_json(json_data)
    
    def get_name(self) -> str:
        """获取名称"""
        return self.name
    
    def get_diameter(self) -> float:
        """获取直径"""
        return self.diameter
    
    def get_height(self) -> float:
        """获取高度"""
        return self.height
    
    def get_material(self) -> str:
        """获取材料"""
        return self.material
    
    def from_json(self, json_data: Dict[str, Any]) -> None:
        """从JSON数据加载"""
        try:
            self.name = json_data.get("name", "")
            self.diameter = json_data.get("diameter", 0.0)
            self.height = json_data.get("height", 0.0)
            self.material = json_data.get("material", "")
            
            logger.debug(f"Loaded BumpModel: {self.name}")
            
        except Exception as e:
            logger.error(f"Failed to load BumpModel from JSON: {e}")
            raise
    
    def to_json(self) -> Dict[str, Any]:
        """转换为JSON数据"""
        try:
            data = {
                "name": self.name,
                "diameter": self.diameter,
                "height": self.height,
                "material": self.material
            }
            return data
            
        except Exception as e:
            logger.error(f"Failed to convert BumpModel to JSON: {e}")
            raise


class BumpInstance:
    """凸点实例类，对应C++的BumpInstance"""
    
    def __init__(self, json_data: Optional[Dict[str, Any]] = None):
        """
        初始化BumpInstance
        
        Args:
            json_data: JSON数据字典
        """
        self.name: str = ""
        self.x: float = 0.0
        self.y: float = 0.0
        self.bump_model: Optional[BumpModel] = None
        
        # 从JSON加载数据
        if json_data:
            self.from_json(json_data)
    
    def get_name(self) -> str:
        """获取名称"""
        return self.name
    
    def get_x(self) -> float:
        """获取X坐标"""
        return self.x
    
    def get_y(self) -> float:
        """获取Y坐标"""
        return self.y
    
    def get_bump_model(self) -> Optional[BumpModel]:
        """获取凸点模型"""
        return self.bump_model
    
    def from_json(self, json_data: Dict[str, Any]) -> None:
        """从JSON数据加载"""
        try:
            self.name = json_data.get("name", "")
            self.x = json_data.get("x", 0.0)
            self.y = json_data.get("y", 0.0)
            
            # 加载凸点模型
            if "bumpModel" in json_data:
                self.bump_model = BumpModel(json_data["bumpModel"])
            
            logger.debug(f"Loaded BumpInstance: {self.name}")
            
        except Exception as e:
            logger.error(f"Failed to load BumpInstance from JSON: {e}")
            raise
    
    def to_json(self) -> Dict[str, Any]:
        """转换为JSON数据"""
        try:
            data = {
                "name": self.name,
                "x": self.x,
                "y": self.y,
                "bumpModel": self.bump_model.to_json() if self.bump_model else None
            }
            return data
            
        except Exception as e:
            logger.error(f"Failed to convert BumpInstance to JSON: {e}")
            raise


class BumpFileInfo:
    """凸点文件信息类，对应C++的BumpFileInfo"""
    
    def __init__(self, json_data: Optional[Dict[str, Any]] = None):
        """
        初始化BumpFileInfo
        
        Args:
            json_data: JSON数据字典
        """
        self.file_path: str = ""
        self.unit: str = ""
        self.die_area: Dict[str, float] = {}
        self.bump_models: List[BumpModel] = []
        self.instances: List[BumpInstance] = []
        
        # 从JSON加载数据
        if json_data:
            self.from_json(json_data)
    
    def get_unit(self) -> str:
        """获取单位"""
        return self.unit
    
    def get_die_area(self) -> Dict[str, float]:
        """获取芯片区域"""
        return self.die_area
    
    def get_bump_models(self) -> List[BumpModel]:
        """获取凸点模型列表"""
        return self.bump_models
    
    def get_instances(self) -> List[BumpInstance]:
        """获取实例列表"""
        return self.instances
    
    def from_json(self, json_data: Dict[str, Any]) -> None:
        """从JSON数据加载"""
        try:
            self.file_path = json_data.get("filePath", "")
            self.unit = json_data.get("unit", "")
            self.die_area = json_data.get("dieArea", {})
            
            # 加载凸点模型
            if "bumpModels" in json_data:
                models_data = json_data["bumpModels"]
                for model_data in models_data:
                    model = BumpModel(model_data)
                    self.bump_models.append(model)
            
            # 加载实例
            if "instances" in json_data:
                instances_data = json_data["instances"]
                for instance_data in instances_data:
                    instance = BumpInstance(instance_data)
                    self.instances.append(instance)
            
            logger.debug(f"Loaded BumpFileInfo: {len(self.bump_models)} models, {len(self.instances)} instances")
            
        except Exception as e:
            logger.error(f"Failed to load BumpFileInfo from JSON: {e}")
            raise
    
    def to_json(self) -> Dict[str, Any]:
        """转换为JSON数据"""
        try:
            data = {
                "filePath": self.file_path,
                "unit": self.unit,
                "dieArea": self.die_area,
                "bumpModels": [model.to_json() for model in self.bump_models],
                "instances": [instance.to_json() for instance in self.instances]
            }
            return data
            
        except Exception as e:
            logger.error(f"Failed to convert BumpFileInfo to JSON: {e}")
            raise
