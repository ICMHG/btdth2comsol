"""
材料工具类
提供材料处理相关的工具函数
"""

from typing import List, Dict, Any
from loguru import logger

from models.material import MaterialInfo


class MaterialUtils:
    """材料工具类"""
    
    @staticmethod
    def validate_material_data(material: MaterialInfo) -> bool:
        """
        验证材料数据
        
        Args:
            material: 材料对象
            
        Returns:
            bool: 验证是否通过
        """
        logger.debug(f"Validating material: {material.name}")
        return material.validate()
    
    @staticmethod
    def get_material_properties(material: MaterialInfo, temperature: float = 293.15) -> Dict[str, Any]:
        """
        获取材料属性
        
        Args:
            material: 材料对象
            temperature: 温度 (K)
            
        Returns:
            Dict[str, Any]: 材料属性字典
        """
        logger.debug(f"Getting properties for material {material.name} at {temperature}K")
        
        return {
            "name": material.name,
            "conductivity": material.get_conductivity(temperature),
            "density": material.get_density(temperature),
            "heat_capacity": material.get_heat_capacity(temperature),
            "temperature_dependent": material.is_temperature_dependent()
        }

