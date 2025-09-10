"""
核心模块
包含ThermalInfo、材料管理器和几何管理器等核心类
"""

from . thermal_info import ThermalInfo
from . material_manager import MaterialInfosMgr
from . geometry_manager import GeometryManager

__all__ = [
    "ThermalInfo",
    "MaterialInfosMgr", 
    "GeometryManager",
]

