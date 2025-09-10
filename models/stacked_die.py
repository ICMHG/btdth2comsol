"""
StackedDie模型类
对应C++的StackedDieSection类，管理堆叠芯片区域
"""

from typing import Optional, Dict, Any, List
from enum import Enum
from pathlib import Path
from loguru import logger

from .geometry import Section
from .power_map import PowerMap, DieStackPowerMap
from .bump_section import BumpSection


class PowerType(Enum):
    """功率类型枚举，对应C++的PowerType"""
    TOTAL_POWER = 1
    POWER_MAP = 2


class StackedDieSection(Section):
    """堆叠芯片区域类，对应C++的StackedDieSection"""
    
    def __init__(self, json_data: Optional[Dict[str, Any]] = None):
        """
        初始化StackedDieSection
        
        Args:
            json_data: JSON数据字典
        """
        super().__init__()
        
        # 功率类型
        self.power_type: PowerType = PowerType.TOTAL_POWER
        
        # 功率映射文件
        self.powermap_file: str = ""
        
        # 是否使用GDS
        self.use_gds: bool = False
        
        # GDS文件路径
        self.gds_file: str = ""
        
        # 堆叠层数
        self.stack_tier: int = 1
        
        # 临时文件
        self.temp_file: str = ""
        
        # 是否翻转
        self.is_flip: bool = False
        
        # 凸点区域
        self.bump: Optional[BumpSection] = None
        
        # 材料字符串
        self.material_string: str = ""
        
        # TIM材料
        self.tim_material: str = ""
        
        # 标签
        self.tags: str = ""
        
        # 总功率
        self.total_power: float = 0.0
        
        # 最大芯片温度
        self.max_die_temp: float = 0.0
        
        # 缩放因子
        self.scale_factor: float = 1.0
        
        # TIM尺寸X
        self.tim_size_x: float = 0.0
        
        # TIM尺寸Y
        self.tim_size_y: float = 0.0
        
        # 芯片堆叠功率映射
        self.powermap: DieStackPowerMap = DieStackPowerMap()
        
        # XML映射字段
        self.face_up: bool = True
        
        # 功率缩放
        self.power_scale: float = 1.0
        
        # 基础目录
        self.base_dir: Optional[Path] = None
        
        # 从JSON加载数据
        if json_data:
            self.from_json(json_data)
    
    def get_power_map(self) -> PowerMap:
        """获取功率映射"""
        return self.powermap
    
    def get_power_type(self) -> PowerType:
        """获取功率类型"""
        return self.power_type
    
    def get_powermap_file(self) -> str:
        """获取功率映射文件"""
        return self.powermap_file
    
    def get_use_gds(self) -> bool:
        """获取是否使用GDS"""
        return self.use_gds
    
    def get_gds_file(self) -> str:
        """获取GDS文件"""
        return self.gds_file
    
    def get_stack_tier(self) -> int:
        """获取堆叠层数"""
        return self.stack_tier
    
    def get_temp_file(self) -> str:
        """获取临时文件"""
        return self.temp_file
    
    def get_is_flip(self) -> bool:
        """获取是否翻转"""
        return self.is_flip
    
    def get_bump(self) -> Optional[BumpSection]:
        """获取凸点区域"""
        return self.bump
    
    def get_material_string(self) -> str:
        """获取材料字符串"""
        return self.material_string
    
    def get_tim_material(self) -> str:
        """获取TIM材料"""
        return self.tim_material
    
    def get_tags(self) -> str:
        """获取标签"""
        return self.tags
    
    def get_total_power(self) -> float:
        """获取总功率"""
        return self.total_power
    
    def get_max_die_temp(self) -> float:
        """获取最大芯片温度"""
        return self.max_die_temp
    
    def get_scale_factor(self) -> float:
        """获取缩放因子"""
        return self.scale_factor
    
    def get_tim_size_x(self) -> float:
        """获取TIM尺寸X"""
        return self.tim_size_x
    
    def get_tim_size_y(self) -> float:
        """获取TIM尺寸Y"""
        return self.tim_size_y
    
    def get_die_stack_power_map(self) -> DieStackPowerMap:
        """获取芯片堆叠功率映射"""
        return self.powermap
    
    def get_face_up(self) -> bool:
        """获取是否面朝上"""
        return self.face_up
    
    def get_power_scale(self) -> float:
        """获取功率缩放"""
        return self.power_scale
    
    # Setter方法
    def set_power_type(self, pt: PowerType) -> None:
        """设置功率类型"""
        self.power_type = pt
    
    def set_powermap_file(self, file: str) -> None:
        """设置功率映射文件"""
        self.powermap_file = file
    
    def set_use_gds(self, use: bool) -> None:
        """设置是否使用GDS"""
        self.use_gds = use
    
    def set_gds_file(self, file: str) -> None:
        """设置GDS文件"""
        self.gds_file = file
    
    def set_stack_tier(self, tier: int) -> None:
        """设置堆叠层数"""
        self.stack_tier = tier
    
    def set_temp_file(self, file: str) -> None:
        """设置临时文件"""
        self.temp_file = file
    
    def setIs_flip(self, is_flip: bool) -> None:
        """设置是否翻转"""
        self.is_flip = is_flip
    
    def set_bump(self, bump: BumpSection) -> None:
        """设置凸点区域"""
        self.bump = bump
    
    def set_material_string(self, mat: str) -> None:
        """设置材料字符串"""
        self.material_string = mat
    
    def set_tim_material(self, mat: str) -> None:
        """设置TIM材料"""
        self.tim_material = mat
    
    def set_tags(self, tags: str) -> None:
        """设置标签"""
        self.tags = tags
    
    def set_total_power(self, total_power: float) -> None:
        """设置总功率"""
        self.total_power = total_power
    
    def set_scale_factor(self, scale_factor: float) -> None:
        """设置缩放因子"""
        self.scale_factor = scale_factor
    
    def set_max_die_temp(self, max_die_temp: float) -> None:
        """设置最大芯片温度"""
        self.max_die_temp = max_die_temp
    
    def set_tim_size_x(self, tim_size_x: float) -> None:
        """设置TIM尺寸X"""
        self.tim_size_x = tim_size_x
    
    def set_tim_size_y(self, tim_size_y: float) -> None:
        """设置TIM尺寸Y"""
        self.tim_size_y = tim_size_y
    
    def set_die_stack_power_map(self, powermap: DieStackPowerMap) -> None:
        """设置芯片堆叠功率映射"""
        self.powermap = powermap
    
    def set_face_up(self, face_up: bool) -> None:
        """设置是否面朝上"""
        self.face_up = face_up
    
    def set_power_scale(self, power_scale: float) -> None:
        """设置功率缩放"""
        self.power_scale = power_scale
    
    def set_base_dir(self, base_dir: Path) -> None:
        """设置基础目录"""
        self.base_dir = base_dir
    
    def resolve_relative_path(self, relative_path: str) -> str:
        """解析相对路径为绝对路径"""
        if self.base_dir:
            return str(self.base_dir / relative_path)
        return relative_path
    
    def get_runtime_sections(self) -> List['Section']:
        """获取运行时区域"""
        # 这里需要实现具体的逻辑
        return [self]
    
    def from_json(self, json_data: Dict[str, Any]) -> None:
        """从JSON数据加载"""
        try:
            super().from_json(json_data)
            
            # 加载堆叠芯片特有属性
            if "powerType" in json_data:
                power_type_val = json_data["powerType"]
                if power_type_val == 1:
                    self.power_type = PowerType.TOTAL_POWER
                elif power_type_val == 2:
                    self.power_type = PowerType.POWER_MAP
            
            self.powermap_file = json_data.get("powermapFile", "")
            self.use_gds = json_data.get("useGDS", False)
            self.gds_file = json_data.get("gdsFile", "")
            self.stack_tier = json_data.get("stackTier", 1)
            self.temp_file = json_data.get("tempFile", "")
            self.is_flip = json_data.get("isFlip", False)
            self.material_string = json_data.get("materialString", "")
            self.tim_material = json_data.get("timMaterial", "")
            self.tags = json_data.get("tags", "")
            self.total_power = json_data.get("totalPower", 0.0)
            self.max_die_temp = json_data.get("maxDieTemp", 0.0)
            self.scale_factor = json_data.get("scaleFactor", 1.0)
            self.tim_size_x = json_data.get("timSizeX", 0.0)
            self.tim_size_y = json_data.get("timSizeY", 0.0)
            self.face_up = json_data.get("faceUp", True)
            self.power_scale = json_data.get("powerScale", 1.0)
            
            # 加载凸点区域
            if "bump" in json_data:
                self.bump = BumpSection(json_data["bump"])
            
            # 加载功率映射
            if "powermap" in json_data:
                self.powermap.from_json(json_data["powermap"])
            
            logger.debug(f"Loaded StackedDieSection: {self.name}")
            
        except Exception as e:
            logger.error(f"Failed to load StackedDieSection from JSON: {e}")
            raise
    
    def to_json(self) -> Dict[str, Any]:
        """转换为JSON数据"""
        try:
            data = super().to_json()
            
            # 添加堆叠芯片特有属性
            data.update({
                "powerType": self.power_type.value,
                "powermapFile": self.powermap_file,
                "useGDS": self.use_gds,
                "gdsFile": self.gds_file,
                "stackTier": self.stack_tier,
                "tempFile": self.temp_file,
                "isFlip": self.is_flip,
                "materialString": self.material_string,
                "timMaterial": self.tim_material,
                "tags": self.tags,
                "totalPower": self.total_power,
                "maxDieTemp": self.max_die_temp,
                "scaleFactor": self.scale_factor,
                "timSizeX": self.tim_size_x,
                "timSizeY": self.tim_size_y,
                "faceUp": self.face_up,
                "powerScale": self.power_scale,
                "bump": self.bump.to_json() if self.bump else None,
                "powermap": self.powermap.to_json()
            })
            
            return data
            
        except Exception as e:
            logger.error(f"Failed to convert StackedDieSection to JSON: {e}")
            raise
