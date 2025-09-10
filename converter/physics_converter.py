"""
物理场转换器
负责设置COMSOL物理场
"""

from typing import Any, Dict, List, Optional
from loguru import logger

from models.geometry import Section
from models.material import MaterialInfo


class PhysicsConverter:
    """物理场转换器"""
    
    def __init__(self):
        """初始化物理场转换器"""
        logger.debug("PhysicsConverter initialized")
    
    def setup_heat_transfer(self, model: Any, thermal_info: Any) -> Any:
        """
        设置热传递物理场
        
        Args:
            model: COMSOL模型对象
            thermal_info: 热分析信息对象
            
        Returns:
            Any: 热传递物理场对象
        """
        logger.debug("Setting up heat transfer physics")
        
        try:
            # 获取物理场管理器
            physics = model.physics()
            
            # 创建热传递物理场
            heat_transfer = physics.create("ht", "HeatTransferInSolids")
            
            # 设置基本参数
            self._setup_basic_heat_transfer_parameters(heat_transfer, thermal_info)
            
            # 设置热源
            self._setup_heat_sources(heat_transfer, thermal_info)
            
            # 设置边界条件
            self._setup_boundary_conditions(heat_transfer, thermal_info)
            
            logger.info("Heat transfer physics setup completed")
            return heat_transfer
            
        except Exception as e:
            logger.error(f"Failed to setup heat transfer physics: {e}")
            return None
    
    def _setup_basic_heat_transfer_parameters(self, heat_transfer: Any, thermal_info: Any) -> None:
        """
        设置基本热传递参数
        
        Args:
            heat_transfer: 热传递物理场对象
            thermal_info: 热分析信息对象
        """
        try:
            # 设置求解类型
            heat_transfer.feature("ht1").set("solvefor", "T")
            
            # 设置初始温度
            if hasattr(thermal_info, 'parameters') and 'ambient_temperature' in thermal_info.parameters:
                ambient_temp = thermal_info.parameters['ambient_temperature']
                heat_transfer.feature("ht1").set("T0", str(ambient_temp))
                logger.debug(f"Set initial temperature: {ambient_temp}")
            
            # 设置其他参数
            heat_transfer.feature("ht1").set("hteqtype", "hteq")
            
        except Exception as e:
            logger.error(f"Failed to setup basic heat transfer parameters: {e}")
    
    def _setup_heat_sources(self, heat_transfer: Any, thermal_info: Any) -> None:
        """
        设置热源
        
        Args:
            heat_transfer: 热传递物理场对象
            thermal_info: 热分析信息对象
        """
        try:
            # 设置表面热流
            if hasattr(thermal_info, 'parameters') and 'surface_heat_flux' in thermal_info.parameters:
                heat_flux = thermal_info.parameters['surface_heat_flux']
                self._setup_surface_heat_flux(heat_transfer, heat_flux)
            
            # 设置功率映射热源
            if hasattr(thermal_info, 'power_maps') and thermal_info.power_maps:
                self._setup_power_map_sources(heat_transfer, thermal_info.power_maps)
            
            # 设置总功率热源
            if hasattr(thermal_info, 'parameters') and 'total_power' in thermal_info.parameters:
                total_power = thermal_info.parameters['total_power']
                self._setup_total_power_source(heat_transfer, total_power)
                
        except Exception as e:
            logger.error(f"Failed to setup heat sources: {e}")
    
    def _setup_surface_heat_flux(self, heat_transfer: Any, heat_flux: float) -> None:
        """
        设置表面热流
        
        Args:
            heat_transfer: 热传递物理场对象
            heat_flux: 热流密度
        """
        try:
            # 创建表面热流边界条件
            heat_flux_bc = heat_transfer.feature().create("HeatFlux1", "HeatFlux")
            heat_flux_bc.set("q0", str(heat_flux))
            heat_flux_bc.set("unit", "W/m^2")
            
            logger.debug(f"Set surface heat flux: {heat_flux} W/m^2")
            
        except Exception as e:
            logger.error(f"Failed to setup surface heat flux: {e}")
    
    def _setup_power_map_sources(self, heat_transfer: Any, power_maps: List[Any]) -> None:
        """
        设置功率映射热源
        
        Args:
            heat_transfer: 热传递物理场对象
            power_maps: 功率映射列表
        """
        try:
            for i, power_map in enumerate(power_maps):
                if hasattr(power_map, 'power_density') and power_map.power_density:
                    # 创建热源
                    heat_source = heat_transfer.feature().create(f"HeatSource{i+1}", "HeatSource")
                    heat_source.set("Q0", str(power_map.power_density))
                    heat_source.set("unit", "W/m^3")
                    
                    # 设置选择
                    if hasattr(power_map, 'selection'):
                        heat_source.set("selection", power_map.selection)
                    
                    logger.debug(f"Set power map heat source {i+1}: {power_map.power_density} W/m^3")
                    
        except Exception as e:
            logger.error(f"Failed to setup power map sources: {e}")
    
    def _setup_total_power_source(self, heat_transfer: Any, total_power: float) -> None:
        """
        设置总功率热源
        
        Args:
            heat_transfer: 热传递物理场对象
            total_power: 总功率
        """
        try:
            # 创建热源
            heat_source = heat_transfer.feature().create("TotalPowerSource", "HeatSource")
            heat_source.set("Q0", str(total_power))
            heat_source.set("unit", "W")
            
            logger.debug(f"Set total power heat source: {total_power} W")
            
        except Exception as e:
            logger.error(f"Failed to setup total power source: {e}")
    
    def _setup_boundary_conditions(self, heat_transfer: Any, thermal_info: Any) -> None:
        """
        设置边界条件
        
        Args:
            heat_transfer: 热传递物理场对象
            thermal_info: 热分析信息对象
        """
        try:
            # 设置温度边界条件
            self._setup_temperature_boundary_conditions(heat_transfer, thermal_info)
            
            # 设置对流边界条件
            self._setup_convection_boundary_conditions(heat_transfer, thermal_info)
            
            # 设置辐射边界条件
            self._setup_radiation_boundary_conditions(heat_transfer, thermal_info)
            
            # 设置绝热边界条件
            self._setup_adiabatic_boundary_conditions(heat_transfer, thermal_info)
            
            # 设置热流边界条件
            self._setup_heat_flux_boundary_conditions(heat_transfer, thermal_info)
            
        except Exception as e:
            logger.error(f"Failed to setup boundary conditions: {e}")
    
    def _setup_temperature_boundary_conditions(self, heat_transfer: Any, thermal_info: Any) -> None:
        """
        设置温度边界条件
        
        Args:
            heat_transfer: 热传递物理场对象
            thermal_info: 热分析信息对象
        """
        try:
            if hasattr(thermal_info, 'parameters') and 'ambient_temperature' in thermal_info.parameters:
                ambient_temp = thermal_info.parameters['ambient_temperature']
                
                # 创建温度边界条件
                temp_bc = heat_transfer.feature().create("Temperature1", "Temperature")
                temp_bc.set("T0", str(ambient_temp))
                temp_bc.set("unit", "K")
                
                # 设置选择（这里需要根据实际情况设置）
                temp_bc.set("selection", "assembly")
                
                logger.debug(f"Set temperature boundary condition: {ambient_temp} K")
                
        except Exception as e:
            logger.error(f"Failed to setup temperature boundary conditions: {e}")
    
    def _setup_convection_boundary_conditions(self, heat_transfer: Any, thermal_info: Any) -> None:
        """
        设置对流边界条件
        
        Args:
            heat_transfer: 热传递物理场对象
            thermal_info: 热分析信息对象
        """
        try:
            # 创建对流边界条件
            conv_bc = heat_transfer.feature().create("Convection1", "Convection")
            
            # 设置对流系数
            conv_bc.set("h", "5")  # 默认对流系数
            conv_bc.set("unit", "W/(m^2*K)")
            
            # 设置环境温度
            if hasattr(thermal_info, 'parameters') and 'ambient_temperature' in thermal_info.parameters:
                ambient_temp = thermal_info.parameters['ambient_temperature']
                conv_bc.set("Text", str(ambient_temp))
                conv_bc.set("unit", "K")
            
            # 设置选择
            conv_bc.set("selection", "heat_sink_surface")
            
            logger.debug("Set convection boundary condition")
            
        except Exception as e:
            logger.error(f"Failed to setup convection boundary conditions: {e}")
    
    def _setup_radiation_boundary_conditions(self, heat_transfer: Any, thermal_info: Any) -> None:
        """
        设置辐射边界条件
        
        Args:
            heat_transfer: 热传递物理场对象
            thermal_info: 热分析信息对象
        """
        try:
            # 创建辐射边界条件
            rad_bc = heat_transfer.feature().create("Radiation1", "Radiation")
            
            # 设置发射率
            rad_bc.set("epsilon", "0.8")  # 默认发射率
            
            # 设置环境温度
            if hasattr(thermal_info, 'parameters') and 'ambient_temperature' in thermal_info.parameters:
                ambient_temp = thermal_info.parameters['ambient_temperature']
                rad_bc.set("Tamb", str(ambient_temp))
                rad_bc.set("unit", "K")
            
            # 设置选择
            rad_bc.set("selection", "radiation_surface")
            
            logger.debug("Set radiation boundary condition")
            
        except Exception as e:
            logger.error(f"Failed to setup radiation boundary conditions: {e}")
    
    def _setup_adiabatic_boundary_conditions(self, heat_transfer: Any, thermal_info: Any) -> None:
        """
        设置绝热边界条件
        
        Args:
            heat_transfer: 热传递物理场对象
            thermal_info: 热分析信息对象
        """
        try:
            # 创建绝热边界条件
            adiabatic_bc = heat_transfer.feature().create("Adiabatic1", "HeatFlux")
            
            # 设置热流为0（绝热）
            adiabatic_bc.set("q0", "0")
            adiabatic_bc.set("unit", "W/m^2")
            
            # 设置选择
            adiabatic_bc.set("selection", "adiabatic_surface")
            
            logger.debug("Set adiabatic boundary condition")
            
        except Exception as e:
            logger.error(f"Failed to setup adiabatic boundary conditions: {e}")
    
    def _setup_heat_flux_boundary_conditions(self, heat_transfer: Any, thermal_info: Any) -> None:
        """
        设置热流边界条件
        
        Args:
            heat_transfer: 热传递物理场对象
            thermal_info: 热分析信息对象
        """
        try:
            # 创建热流边界条件
            heat_flux_bc = heat_transfer.feature().create("HeatFluxBC1", "HeatFlux")
            
            # 设置热流
            if hasattr(thermal_info, 'parameters') and 'surface_heat_flux' in thermal_info.parameters:
                heat_flux = thermal_info.parameters['surface_heat_flux']
                heat_flux_bc.set("q0", str(heat_flux))
                heat_flux_bc.set("unit", "W/m^2")
            
            # 设置选择
            heat_flux_bc.set("selection", "heat_flux_surface")
            
            logger.debug("Set heat flux boundary condition")
            
        except Exception as e:
            logger.error(f"Failed to setup heat flux boundary conditions: {e}")
    
    def setup_thermal_contact(self, heat_transfer: Any, contact_pairs: List[Dict]) -> None:
        """
        设置热接触
        
        Args:
            heat_transfer: 热传递物理场对象
            contact_pairs: 接触对列表
        """
        try:
            for i, contact_pair in enumerate(contact_pairs):
                # 创建热接触
                thermal_contact = heat_transfer.feature().create(f"ThermalContact{i+1}", "ThermalContact")
                
                # 设置接触参数
                if 'contact_resistance' in contact_pair:
                    thermal_contact.set("Rc", str(contact_pair['contact_resistance']))
                
                if 'contact_conductance' in contact_pair:
                    thermal_contact.set("hc", str(contact_pair['contact_conductance']))
                
                # 设置选择
                if 'source' in contact_pair:
                    thermal_contact.set("source", contact_pair['source'])
                
                if 'destination' in contact_pair:
                    thermal_contact.set("destination", contact_pair['destination'])
                
                logger.debug(f"Set thermal contact {i+1}")
                
        except Exception as e:
            logger.error(f"Failed to setup thermal contact: {e}")
    
    def validate_physics_setup(self, heat_transfer: Any) -> bool:
        """
        验证物理场设置
        
        Args:
            heat_transfer: 热传递物理场对象
            
        Returns:
            bool: 验证是否通过
        """
        try:
            if not heat_transfer:
                logger.error("Heat transfer physics object is None")
                return False
            
            # 检查必要的特征
            required_features = ["ht1"]
            for feature_name in required_features:
                if not heat_transfer.feature(feature_name):
                    logger.error(f"Missing required feature: {feature_name}")
                    return False
            
            logger.info("Physics setup validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Physics setup validation failed: {e}")
            return False

