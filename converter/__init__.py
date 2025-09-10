"""
转换器模块
负责将BTD Thermal数据转换为COMSOL MPH格式
"""

from .geometry_converter import GeometryConverter
from .material_converter import MaterialConverter
from .physics_converter import PhysicsConverter
from .mesh_converter import MeshConverter
from .solver_converter import SolverConverter
from .assembly_converter import AssemblyConverter
from .main_converter import MainConverter

__all__ = [
    "GeometryConverter",
    "MaterialConverter", 
    "PhysicsConverter",
    "MeshConverter",
    "SolverConverter",
    "AssemblyConverter",
    "MainConverter",
]

