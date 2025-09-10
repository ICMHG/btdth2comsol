"""
Constraints模型类
对应C++的Constraints类，管理约束条件
"""

from typing import Dict, Any, Optional, List
from loguru import logger


class Constraint:
    """约束条件类，对应C++的Constraint"""
    
    def __init__(self, json_data: Optional[Dict[str, Any]] = None):
        """
        初始化Constraint
        
        Args:
            json_data: JSON数据字典
        """
        self.name: str = ""
        self.constraint_type: str = ""
        self.target_component: str = ""
        self.parameter_name: str = ""
        self.value: float = 0.0
        self.unit: str = ""
        self.description: str = ""
        
        # 从JSON加载数据
        if json_data:
            self.from_json(json_data)
    
    def get_name(self) -> str:
        """获取名称"""
        return self.name
    
    def get_constraint_type(self) -> str:
        """获取约束类型"""
        return self.constraint_type
    
    def get_target_component(self) -> str:
        """获取目标组件"""
        return self.target_component
    
    def get_parameter_name(self) -> str:
        """获取参数名称"""
        return self.parameter_name
    
    def get_value(self) -> float:
        """获取值"""
        return self.value
    
    def get_unit(self) -> str:
        """获取单位"""
        return self.unit
    
    def get_description(self) -> str:
        """获取描述"""
        return self.description
    
    def from_json(self, json_data: Dict[str, Any]) -> None:
        """从JSON数据加载"""
        try:
            self.name = json_data.get("name", "")
            self.constraint_type = json_data.get("constraintType", "")
            self.target_component = json_data.get("targetComponent", "")
            self.parameter_name = json_data.get("parameterName", "")
            self.value = json_data.get("value", 0.0)
            self.unit = json_data.get("unit", "")
            self.description = json_data.get("description", "")
            
            logger.debug(f"Loaded Constraint: {self.name}")
            
        except Exception as e:
            logger.error(f"Failed to load Constraint from JSON: {e}")
            raise
    
    def to_json(self) -> Dict[str, Any]:
        """转换为JSON数据"""
        try:
            data = {
                "name": self.name,
                "constraintType": self.constraint_type,
                "targetComponent": self.target_component,
                "parameterName": self.parameter_name,
                "value": self.value,
                "unit": self.unit,
                "description": self.description
            }
            return data
            
        except Exception as e:
            logger.error(f"Failed to convert Constraint to JSON: {e}")
            raise


class Constraints:
    """约束条件管理器类，对应C++的Constraints"""
    
    def __init__(self):
        """初始化Constraints"""
        self.constraints: List[Constraint] = []
    
    def add_constraint(self, constraint: Constraint) -> None:
        """添加约束条件"""
        self.constraints.append(constraint)
        logger.debug(f"Added constraint: {constraint.get_name()}")
    
    def get_constraints(self) -> List[Constraint]:
        """获取所有约束条件"""
        return self.constraints
    
    def get_constraint_by_name(self, name: str) -> Optional[Constraint]:
        """根据名称获取约束条件"""
        for constraint in self.constraints:
            if constraint.get_name() == name:
                return constraint
        return None
    
    def get_constraints_by_type(self, constraint_type: str) -> List[Constraint]:
        """根据类型获取约束条件"""
        return [c for c in self.constraints if c.get_constraint_type() == constraint_type]
    
    def from_json(self, json_data: Dict[str, Any]) -> None:
        """从JSON数据加载"""
        try:
            if "constraints" in json_data:
                constraints_data = json_data["constraints"]
                for constraint_data in constraints_data:
                    constraint = Constraint(constraint_data)
                    self.add_constraint(constraint)
            
            logger.debug(f"Loaded Constraints with {len(self.constraints)} constraints")
            
        except Exception as e:
            logger.error(f"Failed to load Constraints from JSON: {e}")
            raise
    
    def to_json(self) -> Dict[str, Any]:
        """转换为JSON数据"""
        try:
            data = {
                "constraints": [constraint.to_json() for constraint in self.constraints]
            }
            return data
            
        except Exception as e:
            logger.error(f"Failed to convert Constraints to JSON: {e}")
            raise
