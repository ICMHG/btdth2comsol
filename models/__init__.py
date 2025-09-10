"""
数据模型模块
包含材料、几何、形状和复合材料等数据模型
"""

from models.material import MaterialInfo, Conductivity, TemperaturePoint
from models.geometry import Section, BaseComponent, SectionComponent
from models.shape import Shape, Cube, Cylinder, HexagonalPrism, Shape2D
from models.composite import CompositeMaterial, ObjectMaterial
from models.pkg_die import PkgComponent, PkgDie
from models.stacked_die import StackedDieSection, PowerType
from models.bump_section import BumpSection, BumpArray
from models.power_map import PowerMap, PowerMapLayer, DieStackPowerMap, BoardDieStacks, Area
from models.balls_bumps import BallBump, BallsBumps
from models.bump_file_info import BumpModel, BumpInstance, BumpFileInfo
from models.vertical_interconnect_components import VerticalInterconnectShape, BallBumpShape, VerticalInterconnectInfo, BallBumpInfo, BallBumpsMgr, ComponentType
from models.vertical_interconnect_manager import VerticalInterconnectManager
from models.thermal_netlist import NetlistNode, NetlistConnection, ThermalNetList
from models.thermal_para import ThermalPara
from models.constraints import Constraint, Constraints
from models.results import TemperatureResult, HeatFluxResult, Results
from models.package_para import PackagePara

__all__ = [
    "MaterialInfo",
    "Conductivity", 
    "TemperaturePoint",
    "Section",
    "BaseComponent",
    "SectionComponent", 
    "Shape",
    "Cube",
    "Cylinder",
    "HexagonalPrism",
    "Shape2D",
    "CompositeMaterial",
    "ObjectMaterial",
    "PkgComponent",
    "PkgDie",
    "StackedDieSection",
    "PowerType",
    "BumpSection",
    "BumpArray",
    "PowerMap",
    "PowerMapLayer",
    "DieStackPowerMap",
    "BoardDieStacks",
    "Area",
    "BallBump",
    "BallsBumps",
    "BumpModel",
    "BumpInstance",
    "BumpFileInfo",
    "VerticalInterconnectShape",
    "BallBumpShape",
    "VerticalInterconnectInfo",
    "BallBumpInfo",
    "BallBumpsMgr",
    "ComponentType",
    "VerticalInterconnectManager",
    "NetlistNode",
    "NetlistConnection",
    "ThermalNetList",
    "ThermalPara",
    "Constraint",
    "Constraints",
    "TemperatureResult",
    "HeatFluxResult",
    "Results",
    "PackagePara",
]

