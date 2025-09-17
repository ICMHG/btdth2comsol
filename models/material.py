"""
材料模型
包含MaterialInfo、Conductivity、TemperaturePoint等材料相关类
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from loguru import logger


@dataclass
class Conductivity:
    """
    热导率类
    表示材料在x、y、z三个方向的热导率
    """
    x: float
    y: float
    z: float
    
    def __init__(self, x: float, y: float = None, z: float = None):
        """
        初始化热导率
        
        Args:
            x: x方向热导率
            y: y方向热导率，如果为None则使用x的值
            z: z方向热导率，如果为None则使用x的值
        """
        self.x = x
        self.y = y if y is not None else x
        self.z = z if z is not None else x
    
    def is_isotropic(self) -> bool:
        """
        检查是否为各向同性材料
        
        Returns:
            bool: 是否为各向同性
        """
        return abs(self.x - self.y) < 1e-6 and abs(self.x - self.z) < 1e-6
    
    def get_average(self) -> float:
        """
        获取平均热导率
        
        Returns:
            float: 平均热导率
        """
        return (self.x + self.y + self.z) / 3.0
    
    def to_dict(self) -> Dict[str, float]:
        """
        转换为字典格式
        
        Returns:
            Dict[str, float]: 字典格式的热导率
        """
        return {
            "x": self.x,
            "y": self.y,
            "z": self.z
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'Conductivity':
        """
        从字典格式创建热导率对象
        
        Args:
            data: 字典格式的数据
            
        Returns:
            Conductivity: 热导率对象
        """
        return cls(
            x=data.get("x", 0.0),
            y=data.get("y", data.get("x", 0.0)),
            z=data.get("z", data.get("x", 0.0))
        )


@dataclass
class TemperaturePoint:
    """
    温度点类
    表示在特定温度下的材料属性
    """
    temperature: float  # 温度 (K)
    conductivity: Conductivity  # 热导率
    density: float  # 密度 (kg/m³)
    heat_capacity: float  # 比热容 (J/(kg·K))
    electrical_migration: float  # 电迁移率
    solar_reflectance: float  # 太阳反射率
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式
        
        Returns:
            Dict[str, Any]: 字典格式的温度点数据
        """
        return {
            "temperature": self.temperature,
            "conductivity": self.conductivity.to_dict(),
            "density": self.density,
            "heat_capacity": self.heat_capacity,
            "electrical_migration": self.electrical_migration,
            "solar_reflectance": self.solar_reflectance
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TemperaturePoint':
        """
        从字典格式创建温度点对象
        
        Args:
            data: 字典格式的数据
            
        Returns:
            TemperaturePoint: 温度点对象
        """
        return cls(
            temperature=data["temperature"],
            conductivity=Conductivity.from_dict(data["conductivity"]),
            density=data["density"],
            heat_capacity=data["heat_capacity"],
            electrical_migration=data["electrical_migration"],
            solar_reflectance=data["solar_reflectance"]
        )


class MaterialInfo:
    """
    材料信息类
    表示一种材料的完整信息，包括温度依赖性属性
    """
    
    def __init__(self, name: str, material_type: str = "thermal"):
        """
        初始化材料信息
        
        Args:
            name: 材料名称
            material_type: 材料类型
        """
        self.name = name
        self.material_type = material_type
        self.temperature_map: Dict[float, TemperaturePoint] = {}
        
        logger.debug(f"Created MaterialInfo: {name}")
    
    def add_temperature_point(self, temperature: float, conductivity_x: float, 
                            conductivity_y: float = None, conductivity_z: float = None,
                            density: float = 0.0, heat_capacity: float = 0.0,
                            electrical_migration: float = 0.0, solar_reflectance: float = 0.0) -> None:
        """
        添加温度点数据
        
        Args:
            temperature: 温度 (K)
            conductivity_x: x方向热导率
            conductivity_y: y方向热导率
            conductivity_z: z方向热导率
            density: 密度
            heat_capacity: 比热容
            electrical_migration: 电迁移率
            solar_reflectance: 太阳反射率
        """
        conductivity = Conductivity(conductivity_x, conductivity_y, conductivity_z)
        point = TemperaturePoint(
            temperature=temperature,
            conductivity=conductivity,
            density=density,
            heat_capacity=heat_capacity,
            electrical_migration=electrical_migration,
            solar_reflectance=solar_reflectance
        )
        
        self.temperature_map[temperature] = point
        logger.debug(f"Added temperature point for {self.name} at {temperature}K")
    
    def get_conductivity(self, temperature: float = 293.15) -> Conductivity:
        """
        获取指定温度下的热导率（支持插值）
        
        Args:
            temperature: 目标温度 (K)
            
        Returns:
            Conductivity: 热导率
        """
        if not self.temperature_map:
            logger.warning(f"No temperature data for material {self.name}")
            return Conductivity(0.0)
        
        # 如果只有一个温度点，直接返回
        if len(self.temperature_map) == 1:
            return list(self.temperature_map.values())[0].conductivity
        
        # 线性插值
        return self._interpolate_property(temperature, lambda p: p.conductivity)
    
    def get_density(self, temperature: float = 293.15) -> float:
        """
        获取指定温度下的密度
        
        Args:
            temperature: 目标温度 (K)
            
        Returns:
            float: 密度
        """
        return self._interpolate_property(temperature, lambda p: p.density)
    
    def get_heat_capacity(self, temperature: float = 293.15) -> float:
        """
        获取指定温度下的比热容
        
        Args:
            temperature: 目标温度 (K)
            
        Returns:
            float: 比热容
        """
        return self._interpolate_property(temperature, lambda p: p.heat_capacity)
    
    def _interpolate_property(self, temperature: float, property_getter) -> Any:
        """
        线性插值算法
        
        Args:
            temperature: 目标温度
            property_getter: 属性获取函数
            
        Returns:
            Any: 插值结果
        """
        if not self.temperature_map:
            return None
        
        # 按温度排序
        sorted_points = sorted(self.temperature_map.items(), key=lambda x: x[0])
        
        # 边界检查
        min_temp = sorted_points[0][0]
        max_temp = sorted_points[-1][0]
        
        if temperature <= min_temp:
            return property_getter(sorted_points[0][1])
        elif temperature >= max_temp:
            return property_getter(sorted_points[-1][1])
        
        # 查找相邻温度点
        for i in range(len(sorted_points) - 1):
            temp1, point1 = sorted_points[i]
            temp2, point2 = sorted_points[i + 1]
            
            if temp1 <= temperature <= temp2:
                # 执行线性插值
                value1 = property_getter(point1)
                value2 = property_getter(point2)
                
                # 计算插值权重
                weight = (temperature - temp1) / (temp2 - temp1)
                
                # 线性插值
                if isinstance(value1, Conductivity):
                    # 热导率插值
                    interpolated_x = value1.x + weight * (value2.x - value1.x)
                    interpolated_y = value1.y + weight * (value2.y - value1.y)
                    interpolated_z = value1.z + weight * (value2.z - value1.z)
                    return Conductivity(interpolated_x, interpolated_y, interpolated_z)
                else:
                    # 标量插值
                    return value1 + weight * (value2 - value1)
        
        # 如果没找到合适的区间，返回最近的值
        return property_getter(sorted_points[-1][1])
    
    def is_temperature_dependent(self) -> bool:
        """
        检查是否为温度依赖性材料
        
        Returns:
            bool: 是否为温度依赖性
        """
        return len(self.temperature_map) > 1
    
    def get_temperature_range(self) -> tuple:
        """
        获取温度范围
        
        Returns:
            tuple: (最小温度, 最大温度)
        """
        if not self.temperature_map:
            return (0.0, 0.0)
        
        temperatures = list(self.temperature_map.keys())
        return (min(temperatures), max(temperatures))
    
    def validate(self) -> bool:
        """
        验证材料数据的完整性
        
        Returns:
            bool: 验证是否通过
        """
        if not self.name:
            logger.error("Material name is empty")
            return False
        
        if not self.temperature_map:
            logger.error(f"Material {self.name} has no temperature data")
            return False
        
        # 验证温度点数据
        for temp, point in self.temperature_map.items():
            if temp < 0:
                logger.error(f"Invalid temperature: {temp}K")
                return False
            
            if point.density <= 0:
                logger.warning(f"Material {self.name} has non-positive density at {temp}K")
            
            if point.heat_capacity <= 0:
                logger.warning(f"Material {self.name} has non-positive heat capacity at {temp}K")
        
        logger.debug(f"Material {self.name} validation passed")
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式
        
        Returns:
            Dict[str, Any]: 字典格式的材料数据
        """
        return {
            "name": self.name,
            "type": self.material_type,
            "temperature_points": [point.to_dict() for point in self.temperature_map.values()]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MaterialInfo':
        """
        从字典格式创建材料信息对象，支持BTD格式
        
        Args:
            data: 字典格式的数据
            
        Returns:
            MaterialInfo: 材料信息对象
        """
        material = cls(
            name=data["name"],
            material_type=data.get("type", "thermal")
        )
        
        # 检查是否是BTD格式的数据
        if "t_kx_ky_kz_rho_hc_em_ref_properties" in data:
            # BTD格式：处理温度依赖性属性
            properties_data = data["t_kx_ky_kz_rho_hc_em_ref_properties"]
            if isinstance(properties_data, list):
                for prop_data in properties_data:
                    if isinstance(prop_data, list) and len(prop_data) >= 7:
                        # 格式: [temperature, kx, ky, kz, density, heat_capacity, electrical_migration, solar_reflectance]
                        temperature = float(prop_data[0])
                        kx = float(prop_data[1])
                        ky = float(prop_data[2])
                        kz = float(prop_data[3])
                        density = float(prop_data[4])
                        heat_capacity = float(prop_data[5])
                        electrical_migration = float(prop_data[6]) if len(prop_data) > 6 else 0.0
                        solar_reflectance = float(prop_data[7]) if len(prop_data) > 7 else 0.0
                        
                        material.add_temperature_point(
                            temperature=temperature,
                            conductivity_x=kx,
                            conductivity_y=ky,
                            conductivity_z=kz,
                            density=density,
                            heat_capacity=heat_capacity,
                            electrical_migration=electrical_migration,
                            solar_reflectance=solar_reflectance
                        )
        else:
            # 标准格式：加载温度点数据
            temperature_points_data = data.get("temperature_points", [])
            for point_data in temperature_points_data:
                point = TemperaturePoint.from_dict(point_data)
                material.temperature_map[point.temperature] = point
        
        return material


# 导入复合材料类
from models.composite import CompositeMaterial, ObjectMaterial