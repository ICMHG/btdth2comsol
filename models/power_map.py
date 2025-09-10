"""
PowerMap模型类
对应C++的PowerMap类，管理功率映射
"""

from typing import List, Dict, Any, Optional
from loguru import logger


class Area:
    """区域类，对应C++的Area"""
    
    def __init__(self, json_data: Optional[Dict[str, Any]] = None):
        """
        初始化Area
        
        Args:
            json_data: JSON数据字典
        """
        self.area_name: str = ""
        self.llx: float = 0.0  # 左下角X坐标
        self.lly: float = 0.0  # 左下角Y坐标
        self.lrx: float = 0.0  # 右上角X坐标
        self.lry: float = 0.0  # 右上角Y坐标
        self.s_layer: str = ""  # 起始层
        self.e_layer: str = ""  # 结束层
        self.metal_factor: float = 0.0  # 金属因子
        self.dy_pwr_factor: float = 0.0  # 动态功率因子
        self.lkg_pwr_factor: float = 0.0  # 漏电功率因子
        
        # 从JSON加载数据
        if json_data:
            self.from_json(json_data)
    
    def from_json(self, json_data: Dict[str, Any]) -> None:
        """从JSON数据加载"""
        try:
            self.area_name = json_data.get("areaName", "")
            self.llx = json_data.get("llx", 0.0)
            self.lly = json_data.get("lly", 0.0)
            self.lrx = json_data.get("lrx", 0.0)
            self.lry = json_data.get("lry", 0.0)
            self.s_layer = json_data.get("sLayer", "")
            self.e_layer = json_data.get("eLayer", "")
            self.metal_factor = json_data.get("metalFactor", 0.0)
            self.dy_pwr_factor = json_data.get("dyPwrFactor", 0.0)
            self.lkg_pwr_factor = json_data.get("lkgPwrFactor", 0.0)
            
            logger.debug(f"Loaded Area: {self.area_name}")
            
        except Exception as e:
            logger.error(f"Failed to load Area from JSON: {e}")
            raise
    
    def to_json(self) -> Dict[str, Any]:
        """转换为JSON数据"""
        try:
            data = {
                "areaName": self.area_name,
                "llx": self.llx,
                "lly": self.lly,
                "lrx": self.lrx,
                "lry": self.lry,
                "sLayer": self.s_layer,
                "eLayer": self.e_layer,
                "metalFactor": self.metal_factor,
                "dyPwrFactor": self.dy_pwr_factor,
                "lkgPwrFactor": self.lkg_pwr_factor
            }
            return data
            
        except Exception as e:
            logger.error(f"Failed to convert Area to JSON: {e}")
            raise


class PowerMap:
    """功率映射类，对应C++的PowerMap"""
    
    def __init__(self, json_data: Optional[Dict[str, Any]] = None):
        """
        初始化PowerMap
        
        Args:
            json_data: JSON数据字典
        """
        self.xcoor: List[float] = []  # X坐标数组
        self.ycoor: List[float] = []  # Y坐标数组
        self.power: List[List[float]] = []  # 功率数组
        self.volumetric_power: List[List[float]] = []  # 体积功率数组
        self.metal_density: List[List[float]] = []  # 金属密度数组
        self.has_metal: bool = False  # 是否有金属
        
        # 从JSON加载数据
        if json_data:
            self.from_json(json_data)
    
    def get_grid_power(self, bottom_left_x: float, bottom_left_y: float, 
                       top_right_x: float, top_right_y: float) -> float:
        """获取网格功率（平均功率）"""
        # 这里需要实现具体的逻辑
        return 0.0
    
    def compute_volumetric_power(self, thickness: float) -> None:
        """计算体积功率"""
        # 这里需要实现具体的逻辑
        pass
    
    def print(self) -> None:
        """打印功率映射信息"""
        logger.info(f"PowerMap: {len(self.xcoor)}x{len(self.ycoor)} grid")
        logger.info(f"Has metal: {self.has_metal}")
    
    def from_json(self, json_data: Dict[str, Any]) -> None:
        """从JSON数据加载"""
        try:
            self.xcoor = json_data.get("xcoor", [])
            self.ycoor = json_data.get("ycoor", [])
            self.power = json_data.get("power", [])
            self.volumetric_power = json_data.get("volumetricPower", [])
            self.metal_density = json_data.get("metalDensity", [])
            self.has_metal = json_data.get("hasMetal", False)
            
            logger.debug(f"Loaded PowerMap: {len(self.xcoor)}x{len(self.ycoor)} grid")
            
        except Exception as e:
            logger.error(f"Failed to load PowerMap from JSON: {e}")
            raise
    
    def to_json(self) -> Dict[str, Any]:
        """转换为JSON数据"""
        try:
            data = {
                "xcoor": self.xcoor,
                "ycoor": self.ycoor,
                "power": self.power,
                "volumetricPower": self.volumetric_power,
                "metalDensity": self.metal_density,
                "hasMetal": self.has_metal
            }
            return data
            
        except Exception as e:
            logger.error(f"Failed to convert PowerMap to JSON: {e}")
            raise


class PowerMapLayer:
    """功率映射层类，对应C++的PowerMapLayer"""
    
    def __init__(self, json_data: Optional[Dict[str, Any]] = None):
        """
        初始化PowerMapLayer
        
        Args:
            json_data: JSON数据字典
        """
        self.name: str = ""
        self.base_z: float = 0.0  # 基础Z坐标
        self.thickness: float = 0.0  # 厚度
        self.metal_thermal_conductivity: float = 0.0  # 金属热导率
        self.silicon_thermal_conductivity: float = 0.0  # 硅热导率
        self.powermap: PowerMap = PowerMap()  # 功率映射
        
        # 从JSON加载数据
        if json_data:
            self.from_json(json_data)
    
    def print(self) -> None:
        """打印功率映射层信息"""
        logger.info(f"PowerMapLayer: {self.name}, thickness: {self.thickness}")
        self.powermap.print()
    
    def from_json(self, json_data: Dict[str, Any]) -> None:
        """从JSON数据加载"""
        try:
            self.name = json_data.get("name", "")
            self.base_z = json_data.get("baseZ", 0.0)
            self.thickness = json_data.get("thickness", 0.0)
            self.metal_thermal_conductivity = json_data.get("metalThermalConductivity", 0.0)
            self.silicon_thermal_conductivity = json_data.get("siliconThermalConductivity", 0.0)
            
            # 加载功率映射
            if "powermap" in json_data:
                self.powermap.from_json(json_data["powermap"])
            
            logger.debug(f"Loaded PowerMapLayer: {self.name}")
            
        except Exception as e:
            logger.error(f"Failed to load PowerMapLayer from JSON: {e}")
            raise
    
    def to_json(self) -> Dict[str, Any]:
        """转换为JSON数据"""
        try:
            data = {
                "name": self.name,
                "baseZ": self.base_z,
                "thickness": self.thickness,
                "metalThermalConductivity": self.metal_thermal_conductivity,
                "siliconThermalConductivity": self.silicon_thermal_conductivity,
                "powermap": self.powermap.to_json()
            }
            return data
            
        except Exception as e:
            logger.error(f"Failed to convert PowerMapLayer to JSON: {e}")
            raise


class DieStackPowerMap:
    """芯片堆叠功率映射类，对应C++的DieStackPowerMap"""
    
    def __init__(self, json_data: Optional[Dict[str, Any]] = None):
        """
        初始化DieStackPowerMap
        
        Args:
            json_data: JSON数据字典
        """
        # 单位信息
        self.length_unit: str = ""
        self.power_unit: str = ""
        self.thermal_conductivity_unit: str = ""
        self.process_encryption: bool = False
        
        # 芯片信息
        self.die_name: str = ""
        self.die_area_min_x: float = 0.0
        self.die_area_min_y: float = 0.0
        self.die_area_max_x: float = 0.0
        self.die_area_max_y: float = 0.0
        self.die_area_nx: int = 0
        self.die_area_ny: int = 0
        self.number_of_layers: int = 0
        
        # 功率和层信息
        self.level_pwrs: List[Dict[str, Any]] = []  # 层级功率
        self.layers: List[PowerMapLayer] = []  # 功率映射层
        self.probes: List[Dict[str, Any]] = []  # 探针
        self.areas: List[Area] = []  # 区域
        
        # 其他参数
        self.temperature: float = 25.0
        self.gbl_x_len: float = 0.0
        self.gbl_y_len: float = 0.0
        
        # 从JSON加载数据
        if json_data:
            self.from_json(json_data)
    
    @staticmethod
    def parse_die_stack_power_map(file_path: str, die_thickness: int = 0) -> 'DieStackPowerMap':
        """解析芯片堆叠功率映射文件"""
        # 这里需要实现具体的文件解析逻辑
        return DieStackPowerMap()
    
    def set_base_z(self, base_z_start: float) -> None:
        """设置基础Z坐标"""
        # 这里需要实现具体的逻辑
        pass
    
    def get_power(self, centeroid: tuple) -> float:
        """获取功率值"""
        # 这里需要实现具体的逻辑
        return 0.0
    
    def process_layers_from_die_stack(self, dspm: 'DieStackPowerMap') -> None:
        """处理来自芯片堆叠的层"""
        # 这里需要实现具体的逻辑
        pass
    
    @staticmethod
    def read_file(file_path: str) -> str:
        """读取文件内容"""
        # 这里需要实现具体的文件读取逻辑
        return ""
    
    def print(self) -> None:
        """打印芯片堆叠功率映射信息"""
        logger.info(f"DieStackPowerMap: {self.die_name}")
        logger.info(f"Layers: {self.number_of_layers}")
        logger.info(f"Grid: {self.die_area_nx}x{self.die_area_ny}")
        logger.info(f"Temperature: {self.temperature}")
    
    def from_json(self, json_data: Dict[str, Any]) -> None:
        """从JSON数据加载"""
        try:
            # 加载单位信息
            self.length_unit = json_data.get("lengthUnit", "")
            self.power_unit = json_data.get("powerUnit", "")
            self.thermal_conductivity_unit = json_data.get("thermalConductivityUnit", "")
            self.process_encryption = json_data.get("processEncryption", False)
            
            # 加载芯片信息
            self.die_name = json_data.get("dieName", "")
            self.die_area_min_x = json_data.get("dieAreaMinx", 0.0)
            self.die_area_min_y = json_data.get("dieAreaMiny", 0.0)
            self.die_area_max_x = json_data.get("dieAreaMaxx", 0.0)
            self.die_area_max_y = json_data.get("dieAreaMaxy", 0.0)
            self.die_area_nx = json_data.get("dieAreaNx", 0)
            self.die_area_ny = json_data.get("dieAreaNy", 0)
            self.number_of_layers = json_data.get("numberOfLayers", 0)
            
            # 加载其他参数
            self.temperature = json_data.get("temperature", 25.0)
            self.gbl_x_len = json_data.get("gblXLen", 0.0)
            self.gbl_y_len = json_data.get("gblYLen", 0.0)
            
            # 加载层级功率
            self.level_pwrs = json_data.get("levelPwrs", [])
            
            # 加载功率映射层
            if "layers" in json_data:
                layers_data = json_data["layers"]
                for layer_data in layers_data:
                    layer = PowerMapLayer(layer_data)
                    self.layers.append(layer)
            
            # 加载探针
            self.probes = json_data.get("probes", [])
            
            # 加载区域
            if "areas" in json_data:
                areas_data = json_data["areas"]
                for area_data in areas_data:
                    area = Area(area_data)
                    self.areas.append(area)
            
            logger.debug(f"Loaded DieStackPowerMap: {self.die_name}")
            
        except Exception as e:
            logger.error(f"Failed to load DieStackPowerMap from JSON: {e}")
            raise
    
    def to_json(self) -> Dict[str, Any]:
        """转换为JSON数据"""
        try:
            data = {
                "lengthUnit": self.length_unit,
                "powerUnit": self.power_unit,
                "thermalConductivityUnit": self.thermal_conductivity_unit,
                "processEncryption": self.process_encryption,
                "dieName": self.die_name,
                "dieAreaMinx": self.die_area_min_x,
                "dieAreaMiny": self.die_area_min_y,
                "dieAreaMaxx": self.die_area_max_x,
                "dieAreaMaxy": self.die_area_max_y,
                "dieAreaNx": self.die_area_nx,
                "dieAreaNy": self.die_area_ny,
                "numberOfLayers": self.number_of_layers,
                "levelPwrs": self.level_pwrs,
                "layers": [layer.to_json() for layer in self.layers],
                "probes": self.probes,
                "areas": [area.to_json() for area in self.areas],
                "temperature": self.temperature,
                "gblXLen": self.gbl_x_len,
                "gblYLen": self.gbl_y_len
            }
            return data
            
        except Exception as e:
            logger.error(f"Failed to convert DieStackPowerMap to JSON: {e}")
            raise


class BoardDieStacks:
    """板级芯片堆叠类，对应C++的BoardDieStacks"""
    
    def __init__(self):
        """初始化BoardDieStacks"""
        self.die_stacks: List[DieStackPowerMap] = []
    
    def push_back(self, a_die_stack: DieStackPowerMap) -> None:
        """添加芯片堆叠"""
        self.die_stacks.append(a_die_stack)
    
    def write_csv4pi(self, file_path: str, nx: int, ny: int) -> None:
        """写入CSV文件用于PI分析"""
        # 这里需要实现具体的CSV写入逻辑
        pass
