"""
材料管理器
负责管理所有材料定义和属性
"""

from typing import List, Dict, Optional
from loguru import logger

from models.material import MaterialInfo


class MaterialInfosMgr:
    """
    材料信息管理器
    
    负责管理所有材料定义，提供材料的增删改查功能
    """
    
    def __init__(self):
        """初始化材料管理器"""
        self.materials: Dict[str, MaterialInfo] = {}
        logger.debug("MaterialInfosMgr initialized")
    
    def add_material(self, material: MaterialInfo) -> None:
        """
        添加材料
        
        Args:
            material: 材料信息对象
        """
        if material.name in self.materials:
            logger.warning(f"Material {material.name} already exists, overwriting")
        
        self.materials[material.name] = material
        logger.debug(f"Added material: {material.name}")
    
    def get_material(self, name: str) -> Optional[MaterialInfo]:
        """
        根据名称获取材料
        
        Args:
            name: 材料名称
            
        Returns:
            Optional[MaterialInfo]: 材料对象，未找到返回None
        """
        return self.materials.get(name)
    
    def has_material(self, name: str) -> bool:
        """
        检查材料是否存在
        
        Args:
            name: 材料名称
            
        Returns:
            bool: 材料是否存在
        """
        return name in self.materials
    
    def get_materials(self) -> List[MaterialInfo]:
        """
        获取所有材料
        
        Returns:
            List[MaterialInfo]: 所有材料列表
        """
        return list(self.materials.values())
    
    def get_material_names(self) -> List[str]:
        """
        获取所有材料名称
        
        Returns:
            List[str]: 材料名称列表
        """
        return list(self.materials.keys())
    
    def remove_material(self, name: str) -> bool:
        """
        删除材料
        
        Args:
            name: 材料名称
            
        Returns:
            bool: 删除是否成功
        """
        if name in self.materials:
            del self.materials[name]
            logger.debug(f"Removed material: {name}")
            return True
        else:
            logger.warning(f"Material {name} not found")
            return False
    
    def clear_materials(self) -> None:
        """清空所有材料"""
        self.materials.clear()
        logger.debug("Cleared all materials")
    
    def get_materials_count(self) -> int:
        """
        获取材料数量
        
        Returns:
            int: 材料数量
        """
        return len(self.materials)
    
    def validate_materials(self) -> bool:
        """
        验证所有材料的完整性
        
        Returns:
            bool: 验证是否通过
        """
        for name, material in self.materials.items():
            if not material.validate():
                logger.error(f"Material {name} validation failed")
                return False
        
        logger.info("All materials validation passed")
        return True
    
    def get_temperature_dependent_materials(self) -> List[MaterialInfo]:
        """
        获取温度依赖性材料
        
        Returns:
            List[MaterialInfo]: 温度依赖性材料列表
        """
        return [material for material in self.materials.values() 
                if material.is_temperature_dependent()]
    
    def get_constant_materials(self) -> List[MaterialInfo]:
        """
        获取常数材料（非温度依赖性）
        
        Returns:
            List[MaterialInfo]: 常数材料列表
        """
        return [material for material in self.materials.values() 
                if not material.is_temperature_dependent()]
    
    def find_materials_by_type(self, material_type: str) -> List[MaterialInfo]:
        """
        根据类型查找材料
        
        Args:
            material_type: 材料类型
            
        Returns:
            List[MaterialInfo]: 匹配的材料列表
        """
        return [material for material in self.materials.values() 
                if material.material_type == material_type]
    
    def get_materials_summary(self) -> Dict[str, int]:
        """
        获取材料统计摘要
        
        Returns:
            Dict[str, int]: 材料统计信息
        """
        total = len(self.materials)
        temperature_dependent = len(self.get_temperature_dependent_materials())
        constant = len(self.get_constant_materials())
        
        return {
            "total": total,
            "temperature_dependent": temperature_dependent,
            "constant": constant
        }
    
    def print_summary(self) -> None:
        """打印材料摘要信息"""
        summary = self.get_materials_summary()
        
        logger.info("=" * 40)
        logger.info("Materials Summary")
        logger.info("=" * 40)
        logger.info(f"Total materials: {summary['total']}")
        logger.info(f"Temperature dependent: {summary['temperature_dependent']}")
        logger.info(f"Constant: {summary['constant']}")
        
        for name, material in self.materials.items():
            logger.info(f"  - {name}: {material.material_type}")
        
        logger.info("=" * 40)

