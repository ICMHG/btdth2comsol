"""
ThermalPara模型类
对应C++的ThermalPara类，管理热参数
"""

from typing import Dict, Any, Optional, List
from loguru import logger


class ThermalPara:
    """热参数类，对应C++的ThermalPara"""
    
    def __init__(self, json_data: Optional[Dict[str, Any]] = None):
        """
        初始化ThermalPara
        
        Args:
            json_data: JSON数据字典
        """
        # 环境参数
        self.ambient_temperature: float = 298.15  # 环境温度 (K)
        self.surface_heat_flux: float = 0.0  # 表面热流密度 (W/m²)
        self.convection_coefficient: float = 0.0  # 对流系数 (W/m²·K)
        self.radiation_emissivity: float = 0.0  # 辐射发射率
        
        # 求解参数
        self.solver_type: str = "stationary"  # 求解器类型
        self.max_iterations: int = 100  # 最大迭代次数
        self.tolerance: float = 1e-6  # 收敛容差
        
        # 网格参数
        self.mesh_size: str = "normal"  # 网格尺寸
        self.mesh_type: str = "tetrahedral"  # 网格类型
        self.element_order: int = 2  # 单元阶数
        
        # 从JSON加载数据
        if json_data:
            self.from_json(json_data)
    
    def get_ambient_temperature(self) -> float:
        """获取环境温度"""
        return self.ambient_temperature
    
    def get_surface_heat_flux(self) -> float:
        """获取表面热流密度"""
        return self.surface_heat_flux
    
    def get_convection_coefficient(self) -> float:
        """获取对流系数"""
        return self.convection_coefficient
    
    def get_radiation_emissivity(self) -> float:
        """获取辐射发射率"""
        return self.radiation_emissivity
    
    def get_solver_type(self) -> str:
        """获取求解器类型"""
        return self.solver_type
    
    def get_max_iterations(self) -> int:
        """获取最大迭代次数"""
        return self.max_iterations
    
    def get_tolerance(self) -> float:
        """获取收敛容差"""
        return self.tolerance
    
    def get_mesh_size(self) -> str:
        """获取网格尺寸"""
        return self.mesh_size
    
    def get_mesh_type(self) -> str:
        """获取网格类型"""
        return self.mesh_type
    
    def get_element_order(self) -> int:
        """获取单元阶数"""
        return self.element_order
    
    def from_json(self, json_data: Dict[str, Any]) -> None:
        """从JSON数据加载"""
        try:
            self.ambient_temperature = json_data.get("ambientTemperature", 298.15)
            self.surface_heat_flux = json_data.get("surfaceHeatFlux", 0.0)
            self.convection_coefficient = json_data.get("convectionCoefficient", 0.0)
            self.radiation_emissivity = json_data.get("radiationEmissivity", 0.0)
            self.solver_type = json_data.get("solverType", "stationary")
            self.max_iterations = json_data.get("maxIterations", 100)
            self.tolerance = json_data.get("tolerance", 1e-6)
            self.mesh_size = json_data.get("meshSize", "normal")
            self.mesh_type = json_data.get("meshType", "tetrahedral")
            self.element_order = json_data.get("elementOrder", 2)
            
            logger.debug("Loaded ThermalPara from JSON")
            
        except Exception as e:
            logger.error(f"Failed to load ThermalPara from JSON: {e}")
            raise
    
    def to_json(self) -> Dict[str, Any]:
        """转换为JSON数据"""
        try:
            data = {
                "ambientTemperature": self.ambient_temperature,
                "surfaceHeatFlux": self.surface_heat_flux,
                "convectionCoefficient": self.convection_coefficient,
                "radiationEmissivity": self.radiation_emissivity,
                "solverType": self.solver_type,
                "maxIterations": self.max_iterations,
                "tolerance": self.tolerance,
                "meshSize": self.mesh_size,
                "meshType": self.mesh_type,
                "elementOrder": self.element_order
            }
            return data
            
        except Exception as e:
            logger.error(f"Failed to convert ThermalPara to JSON: {e}")
            raise
