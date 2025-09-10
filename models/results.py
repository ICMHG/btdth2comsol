"""
Results模型类
对应C++的Results类，管理计算结果
"""

from typing import Dict, Any, Optional, List
from loguru import logger


class TemperatureResult:
    """温度结果类，对应C++的TemperatureResult"""
    
    def __init__(self, json_data: Optional[Dict[str, Any]] = None):
        """
        初始化TemperatureResult
        
        Args:
            json_data: JSON数据字典
        """
        self.component_name: str = ""
        self.node_id: str = ""
        self.temperature: float = 0.0
        self.unit: str = "K"
        
        # 从JSON加载数据
        if json_data:
            self.from_json(json_data)
    
    def get_component_name(self) -> str:
        """获取组件名称"""
        return self.component_name
    
    def get_node_id(self) -> str:
        """获取节点ID"""
        return self.node_id
    
    def get_temperature(self) -> float:
        """获取温度"""
        return self.temperature
    
    def get_unit(self) -> str:
        """获取单位"""
        return self.unit
    
    def from_json(self, json_data: Dict[str, Any]) -> None:
        """从JSON数据加载"""
        try:
            self.component_name = json_data.get("componentName", "")
            self.node_id = json_data.get("nodeId", "")
            self.temperature = json_data.get("temperature", 0.0)
            self.unit = json_data.get("unit", "K")
            
            logger.debug(f"Loaded TemperatureResult: {self.component_name}")
            
        except Exception as e:
            logger.error(f"Failed to load TemperatureResult from JSON: {e}")
            raise
    
    def to_json(self) -> Dict[str, Any]:
        """转换为JSON数据"""
        try:
            data = {
                "componentName": self.component_name,
                "nodeId": self.node_id,
                "temperature": self.temperature,
                "unit": self.unit
            }
            return data
            
        except Exception as e:
            logger.error(f"Failed to convert TemperatureResult to JSON: {e}")
            raise


class HeatFluxResult:
    """热流密度结果类，对应C++的HeatFluxResult"""
    
    def __init__(self, json_data: Optional[Dict[str, Any]] = None):
        """
        初始化HeatFluxResult
        
        Args:
            json_data: JSON数据字典
        """
        self.component_name: str = ""
        self.surface_name: str = ""
        self.heat_flux_x: float = 0.0
        self.heat_flux_y: float = 0.0
        self.heat_flux_z: float = 0.0
        self.unit: str = "W/m²"
        
        # 从JSON加载数据
        if json_data:
            self.from_json(json_data)
    
    def get_component_name(self) -> str:
        """获取组件名称"""
        return self.component_name
    
    def get_surface_name(self) -> str:
        """获取表面名称"""
        return self.surface_name
    
    def get_heat_flux_x(self) -> float:
        """获取X方向热流密度"""
        return self.heat_flux_x
    
    def get_heat_flux_y(self) -> float:
        """获取Y方向热流密度"""
        return self.heat_flux_y
    
    def get_heat_flux_z(self) -> float:
        """获取Z方向热流密度"""
        return self.heat_flux_z
    
    def get_unit(self) -> str:
        """获取单位"""
        return self.unit
    
    def from_json(self, json_data: Dict[str, Any]) -> None:
        """从JSON数据加载"""
        try:
            self.component_name = json_data.get("componentName", "")
            self.surface_name = json_data.get("surfaceName", "")
            self.heat_flux_x = json_data.get("heatFluxX", 0.0)
            self.heat_flux_y = json_data.get("heatFluxY", 0.0)
            self.heat_flux_z = json_data.get("heatFluxZ", 0.0)
            self.unit = json_data.get("unit", "W/m²")
            
            logger.debug(f"Loaded HeatFluxResult: {self.component_name}")
            
        except Exception as e:
            logger.error(f"Failed to load HeatFluxResult from JSON: {e}")
            raise
    
    def to_json(self) -> Dict[str, Any]:
        """转换为JSON数据"""
        try:
            data = {
                "componentName": self.component_name,
                "surfaceName": self.surface_name,
                "heatFluxX": self.heat_flux_x,
                "heatFluxY": self.heat_flux_y,
                "heatFluxZ": self.heat_flux_z,
                "unit": self.unit
            }
            return data
            
        except Exception as e:
            logger.error(f"Failed to convert HeatFluxResult to JSON: {e}")
            raise


class Results:
    """结果管理器类，对应C++的Results"""
    
    def __init__(self):
        """初始化Results"""
        self.temperature_results: List[TemperatureResult] = []
        self.heat_flux_results: List[HeatFluxResult] = []
        self.simulation_time: float = 0.0
        self.convergence_status: str = "unknown"
    
    def add_temperature_result(self, result: TemperatureResult) -> None:
        """添加温度结果"""
        self.temperature_results.append(result)
        logger.debug(f"Added temperature result: {result.get_component_name()}")
    
    def add_heat_flux_result(self, result: HeatFluxResult) -> None:
        """添加热流密度结果"""
        self.heat_flux_results.append(result)
        logger.debug(f"Added heat flux result: {result.get_component_name()}")
    
    def get_temperature_results(self) -> List[TemperatureResult]:
        """获取所有温度结果"""
        return self.temperature_results
    
    def get_heat_flux_results(self) -> List[HeatFluxResult]:
        """获取所有热流密度结果"""
        return self.heat_flux_results
    
    def get_simulation_time(self) -> float:
        """获取仿真时间"""
        return self.simulation_time
    
    def get_convergence_status(self) -> str:
        """获取收敛状态"""
        return self.convergence_status
    
    def set_simulation_time(self, time: float) -> None:
        """设置仿真时间"""
        self.simulation_time = time
    
    def set_convergence_status(self, status: str) -> None:
        """设置收敛状态"""
        self.convergence_status = status
    
    def from_json(self, json_data: Dict[str, Any]) -> None:
        """从JSON数据加载"""
        try:
            self.simulation_time = json_data.get("simulationTime", 0.0)
            self.convergence_status = json_data.get("convergenceStatus", "unknown")
            
            # 加载温度结果
            if "temperatureResults" in json_data:
                temp_results_data = json_data["temperatureResults"]
                for result_data in temp_results_data:
                    result = TemperatureResult(result_data)
                    self.add_temperature_result(result)
            
            # 加载热流密度结果
            if "heatFluxResults" in json_data:
                flux_results_data = json_data["heatFluxResults"]
                for result_data in flux_results_data:
                    result = HeatFluxResult(result_data)
                    self.add_heat_flux_result(result)
            
            logger.debug(f"Loaded Results with {len(self.temperature_results)} temperature results and {len(self.heat_flux_results)} heat flux results")
            
        except Exception as e:
            logger.error(f"Failed to load Results from JSON: {e}")
            raise
    
    def to_json(self) -> Dict[str, Any]:
        """转换为JSON数据"""
        try:
            data = {
                "simulationTime": self.simulation_time,
                "convergenceStatus": self.convergence_status,
                "temperatureResults": [result.to_json() for result in self.temperature_results],
                "heatFluxResults": [result.to_json() for result in self.heat_flux_results]
            }
            return data
            
        except Exception as e:
            logger.error(f"Failed to convert Results to JSON: {e}")
            raise
