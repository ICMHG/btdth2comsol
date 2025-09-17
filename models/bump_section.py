"""
BumpSection模型类
对应C++的BumpSection类，管理凸点区域
现在使用BallBumpInfo来替代原来的BumpSection类
"""

from typing import Optional, Dict, Any, List
from loguru import logger

from .geometry import Section
# 避免循环导入，使用字符串类型注解
from .vertical_interconnect_components import BallBumpInfo


class BumpArray:
    """凸点阵列类，对应C++的BumpArray"""
    
    def __init__(self, json_data: Optional[Dict[str, Any]] = None):
        """
        初始化BumpArray
        
        Args:
            json_data: JSON数据字典
        """
        self.name: str = ""
        self.offset_x: float = 0.0
        self.offset_y: float = 0.0
        self.length: float = 0.0
        self.width: float = 0.0
        self.material: str = ""
        
        # 从JSON加载数据
        if json_data:
            self.from_json(json_data)
    
    def from_json(self, json_data: Dict[str, Any]) -> None:
        """从JSON数据加载"""
        try:
            self.name = json_data.get("name", "")
            self.offset_x = json_data.get("offsetX", 0.0)
            self.offset_y = json_data.get("offsetY", 0.0)
            self.length = json_data.get("length", 0.0)
            self.width = json_data.get("width", 0.0)
            self.material = json_data.get("material", "")
            
            logger.debug(f"Loaded BumpArray: {self.name}")
            
        except Exception as e:
            logger.error(f"Failed to load BumpArray from JSON: {e}")
            raise
    
    def to_json(self) -> Dict[str, Any]:
        """转换为JSON数据"""
        try:
            data = {
                "name": self.name,
                "offsetX": self.offset_x,
                "offsetY": self.offset_y,
                "length": self.length,
                "width": self.width,
                "material": self.material
            }
            return data
            
        except Exception as e:
            logger.error(f"Failed to convert BumpArray to JSON: {e}")
            raise


class BumpSection(Section):
    """凸点区域类，对应C++的BumpSection，现在继承自Section并使用BallBumpInfo"""
    
    def __init__(self, json_data: Optional[Dict[str, Any]] = None):
        """
        初始化BumpSection
        
        Args:
            json_data: JSON数据字典
        """
        super().__init__()
        
        # 常量定义
        self.BUMP_ARRAY = "STACKED_DIE_BUMP_ARRAY"
        self.BUMP_FILE = "STACKED_DIE_BUMP_FILE"
        
        # 下层芯片
        self.lower_die: str = ""
        
        # 凸点类型
        self.bump_type: int = 0
        
        # 凸点文件
        self.bump_file: str = ""
        
        # 关联的芯片
        self.die: Optional['StackedDieSection'] = None
        
        # 凸点阵列
        self.bump_array: Optional[BumpArray] = None
        
        # 底部填充材料
        self.underfill_material: str = ""
        
        # 连接类型
        self.connection_type: str = ""
        
        # 是否已修改
        self.is_modify: bool = False
        
        # 从JSON加载数据
        if json_data:
            self.from_json(json_data)
    
    def get_lower_die(self) -> str:
        """获取下层芯片"""
        return self.lower_die
    
    def get_bump_type(self) -> int:
        """获取凸点类型"""
        return self.bump_type
    
    def get_bump_file(self) -> str:
        """获取凸点文件"""
        return self.bump_file
    
    def get_die(self) -> Optional['StackedDieSection']:
        """获取关联的芯片"""
        return self.die
    
    def get_bump_array(self) -> Optional[BumpArray]:
        """获取凸点阵列"""
        return self.bump_array
    
    def get_underfill_material(self) -> str:
        """获取底部填充材料"""
        return self.underfill_material
    
    def get_connection_type(self) -> str:
        """获取连接类型"""
        return self.connection_type
    
    def is_modified(self) -> bool:
        """获取是否已修改"""
        return self.is_modify
    
    # Setter方法
    def set_lower_die(self, lower_die: str) -> None:
        """设置下层芯片"""
        self.lower_die = lower_die
    
    def set_bump_type(self, bump_type: int) -> None:
        """设置凸点类型"""
        self.bump_type = bump_type
    
    def set_bump_file(self, bump_file_path: str) -> None:
        """设置凸点文件"""
        self.set_is_modify(True)
        self.bump_file = bump_file_path
    
    def set_die(self, die: 'StackedDieSection') -> None:
        """设置关联的芯片"""
        self.die = die
    
    def set_bump_array(self, bump_array: BumpArray) -> None:
        """设置凸点阵列"""
        self.bump_array = bump_array
    
    def set_underfill_material(self, underfill_material: str) -> None:
        """设置底部填充材料"""
        self.underfill_material = underfill_material
    
    def set_connection_type(self, connection_type: str) -> None:
        """设置连接类型"""
        self.connection_type = connection_type
    
    def set_is_modify(self, value: bool) -> None:
        """设置是否已修改"""
        self.is_modify = value
    
    def get_runtime_section(self) -> 'Section':
        """获取运行时区域"""
        # 这里需要实现具体的逻辑
        return self
    
    def from_json(self, json_data: Dict[str, Any]) -> None:
        """从JSON数据加载，支持BTD格式"""
        try:
            # 设置基本信息
            self.name = json_data.get("name", "")
            self.layer = json_data.get("layer", "")
            type_str = json_data.get("type", "")
            if type_str:
                try:
                    from .geometry import ComponentType
                    self.type = ComponentType(type_str)
                except ValueError:
                    logger.warning(f"Unknown component type: {type_str}, using UNKNOWN")
                    self.type = ComponentType.UNKNOWN
            else:
                self.type = ComponentType.UNKNOWN
            
            # 加载凸点区域特有属性，支持BTD格式的字段名
            self.lower_die = json_data.get("lower_die", json_data.get("lowerDie", ""))
            self.bump_type = json_data.get("bump_type", json_data.get("bumpType", 0))
            self.bump_file = json_data.get("bump_file", json_data.get("bumpFile", ""))
            self.underfill_material = json_data.get("underfill_material", json_data.get("underfillMaterial", ""))
            self.connection_type = json_data.get("connection_type", json_data.get("connectionType", ""))
            self.is_modify = json_data.get("is_modify", json_data.get("isModify", False))
            
            # 加载凸点阵列
            if "bump_array" in json_data or "bumpArray" in json_data:
                bump_array_data = json_data.get("bump_array", json_data.get("bumpArray", {}))
                self.bump_array = BumpArray(bump_array_data)
            
            logger.debug(f"Loaded BumpSection: {self.name}")
            
        except Exception as e:
            logger.error(f"Failed to load BumpSection from JSON: {e}")
            raise
    
    def to_json(self) -> Dict[str, Any]:
        """转换为JSON数据"""
        try:
            data = super().to_json()
            
            # 添加凸点区域特有属性
            data.update({
                "lowerDie": self.lower_die,
                "bumpType": self.bump_type,
                "bumpFile": self.bump_file,
                "underfillMaterial": self.underfill_material,
                "connectionType": self.connection_type,
                "isModify": self.is_modify,
                "bumpArray": self.bump_array.to_json() if self.bump_array else None
            })
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to convert BumpSection to JSON: {e}")
            raise
