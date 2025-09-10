"""
复合材料模型
包含CompositeMaterial、ObjectMaterial等复合材料相关类
"""

from typing import List, Dict, Optional, Any, Tuple
from loguru import logger

from models.material import MaterialInfo


class CompositeMaterial:
    """复合材料类"""
    
    def __init__(self):
        self.materials: List[Tuple[MaterialInfo, float]] = []  # [(material, percentage), ...]
        self.name = "Composite"
    
    def add_material(self, material: MaterialInfo, percentage: float) -> None:
        """
        添加材料及其体积分数
        
        Args:
            material: 材料对象
            percentage: 体积分数 (0.0-1.0)
        """
        self.materials.append((material, percentage))
        logger.debug(f"Added material {material.name} with percentage {percentage}")
    
    def get_effective_conductivity(self, temperature: float = 293.15) -> 'Conductivity':
        """
        计算有效热导率（体积加权平均）
        
        Args:
            temperature: 温度 (K)
            
        Returns:
            Conductivity: 有效热导率
        """
        if not self.materials:
            logger.warning("No materials in composite")
            from models.material import Conductivity
            return Conductivity(0.0)
        
        # 验证体积分数总和
        total_percentage = sum(mat[1] for mat in self.materials)
        if abs(total_percentage - 1.0) > 1e-6:
            logger.warning(f"Material percentages sum to {total_percentage}, not 1.0")
        
        # 计算有效热导率（体积加权平均）
        effective_x = 0.0
        effective_y = 0.0
        effective_z = 0.0
        
        for material, percentage in self.materials:
            conductivity = material.get_conductivity(temperature)
            effective_x += conductivity.x * percentage
            effective_y += conductivity.y * percentage
            effective_z += conductivity.z * percentage
        
        from models.material import Conductivity
        return Conductivity(effective_x, effective_y, effective_z)
    
    def get_effective_density(self, temperature: float = 293.15) -> float:
        """
        计算有效密度（体积加权平均）
        
        Args:
            temperature: 温度 (K)
            
        Returns:
            float: 有效密度
        """
        if not self.materials:
            return 0.0
        
        effective_density = 0.0
        for material, percentage in self.materials:
            density = material.get_density(temperature)
            effective_density += density * percentage
        
        return effective_density
    
    def get_effective_heat_capacity(self, temperature: float = 293.15) -> float:
        """
        计算有效比热容（体积加权平均）
        
        Args:
            temperature: 温度 (K)
            
        Returns:
            float: 有效比热容
        """
        if not self.materials:
            return 0.0
        
        effective_heat_capacity = 0.0
        for material, percentage in self.materials:
            heat_capacity = material.get_heat_capacity(temperature)
            effective_heat_capacity += heat_capacity * percentage
        
        return effective_heat_capacity
    
    def validate(self) -> bool:
        """
        验证复合材料数据
        
        Returns:
            bool: 验证是否通过
        """
        if not self.materials:
            logger.error("Composite material has no components")
            return False
        
        # 验证体积分数
        total_percentage = sum(mat[1] for mat in self.materials)
        if abs(total_percentage - 1.0) > 1e-6:
            logger.error(f"Material percentages must sum to 1.0, got {total_percentage}")
            return False
        
        # 验证每个材料
        for material, percentage in self.materials:
            if not material.validate():
                logger.error(f"Component material {material.name} validation failed")
                return False
            
            if percentage <= 0 or percentage > 1:
                logger.error(f"Invalid percentage {percentage} for material {material.name}")
                return False
        
        logger.debug(f"Composite material {self.name} validation passed")
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式
        
        Returns:
            Dict[str, Any]: 字典格式的复合材料数据
        """
        return {
            "name": self.name,
            "materials": [
                {
                    "material": material.name,
                    "percentage": percentage
                }
                for material, percentage in self.materials
            ]
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], materials_mgr) -> 'CompositeMaterial':
        """
        从字典格式创建复合材料对象
        
        Args:
            data: 字典格式的数据
            materials_mgr: 材料管理器
            
        Returns:
            CompositeMaterial: 复合材料对象
        """
        composite = cls()
        composite.name = data.get("name", "Composite")
        
        materials_data = data.get("materials", [])
        for mat_data in materials_data:
            material_name = mat_data["material"]
            percentage = mat_data["percentage"]
            
            material = materials_mgr.get_material(material_name)
            if material:
                composite.add_material(material, percentage)
            else:
                logger.warning(f"Material {material_name} not found in materials manager")
        
        return composite


class ObjectMaterial:
    """对象材料类"""
    
    def __init__(self, name: str = ""):
        self.name = name
        self.material = None
        self.composite_material = None
    
    def set_material(self, material: MaterialInfo) -> None:
        """设置材料"""
        self.material = material
    
    def set_composite_material(self, composite: CompositeMaterial) -> None:
        """设置复合材料"""
        self.composite_material = composite
    
    def get_effective_material(self) -> MaterialInfo:
        """获取有效材料（如果是复合材料，返回等效材料）"""
        if self.composite_material:
            # 创建等效材料
            effective_material = MaterialInfo(f"{self.name}_effective")
            # 这里需要实现从复合材料创建等效材料的逻辑
            return effective_material
        else:
            return self.material
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        if self.composite_material:
            return {
                "name": self.name,
                "type": "composite",
                "composite": self.composite_material.to_dict()
            }
        else:
            return {
                "name": self.name,
                "type": "single",
                "material": self.material.name if self.material else None
            }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], materials_mgr) -> 'ObjectMaterial':
        """从字典格式创建对象材料"""
        obj_material = cls(data.get("name", ""))
        
        material_type = data.get("type", "single")
        if material_type == "composite":
            composite_data = data.get("composite", {})
            obj_material.composite_material = CompositeMaterial.from_dict(composite_data, materials_mgr)
        else:
            material_name = data.get("material")
            if material_name:
                obj_material.material = materials_mgr.get_material(material_name)
        
        return obj_material

