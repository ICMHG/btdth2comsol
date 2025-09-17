"""
ThermalInfo核心类
整个系统的核心数据结构，统一管理所有热分析相关数据
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from loguru import logger

from models.material import MaterialInfo
from models.geometry import ComponentType, Section
from models.pkg_die import PkgComponent, PkgDie
from models.stacked_die import StackedDieSection
from models.bump_section import BumpSection
from models.thermal_netlist import ThermalNetList
from models.thermal_para import ThermalPara
from models.constraints import Constraints
from models.vertical_interconnect_manager import VerticalInterconnectManager
from models.power_map import DieStackPowerMap
from core.material_manager import MaterialInfosMgr
from parser.shape_parser import ShapeParser, ShapeParsingError


class BTDJsonParsingError(Exception):
    """BTD JSON解析错误"""
    pass


class ThermalInfo:
    """
    ThermalInfo是整个系统的核心数据结构

    它统一管理：
    1. 所有材料定义和属性
    2. 几何区域和层次结构
    3. 封装组件和堆叠芯片
    4. 热分析参数和约束条件
    """

    def __init__(self, name: str = ""):
        """
        初始化ThermalInfo

        Args:
            name: 热分析模型名称
        """
        self.name = name
        self.json_file_dir: Optional[Path] = None

        # 材料管理器
        self.materials_mgr = MaterialInfosMgr()

        # 几何区域列表
        self.sections: List[Section] = []

        # 参数系统
        self.parameters: Dict[str, Any] = {}

        # 热分析参数
        self.thermal_parameters: Dict[str, Any] = {}

        # 网络列表
        self.netlist: ThermalNetList = ThermalNetList()

        # 组件连接信息
        self.component_connect: List[Dict[str, Any]] = []

        # 部件信息
        self.parts: PkgDie = PkgDie()

        # 约束条件
        self.constraints: Constraints = Constraints()

        # 垂直互连管理器
        self.vertical_interconnect_manager: VerticalInterconnectManager = VerticalInterconnectManager()

        # 运行时区域列表
        self.runtime_sections: List[Section] = []

        logger.info(f"ThermalInfo initialized with name: {name}")

    def set_json_file_dir(self, json_file_path: Path) -> None:
        """
        设置JSON文件目录，用于相对路径解析

        Args:
            json_file_path: JSON文件路径
        """
        self.json_file_dir = json_file_path.parent
        logger.debug(f"Set JSON file directory: {self.json_file_dir}")

    def get_materials_mgr(self) -> MaterialInfosMgr:
        """
        获取材料管理器

        Returns:
            MaterialInfosMgr: 材料管理器实例
        """
        return self.materials_mgr

    def add_section(self, section: Section) -> None:
        """
        添加几何区域

        Args:
            section: 几何区域对象
        """
        self.sections.append(section)
        logger.debug(f"Added section: {section.name}")

    def set_part(self, part: PkgDie) -> None:
        """
        设置部件

        Args:
            part: 部件对象
        """
        self.parts = part
        logger.debug(f"Set part with {len(part.get_components())} components")

    def get_all_sections(self) -> List[Section]:
        """
        获取所有几何区域

        Returns:
            List[Section]: 所有几何区域列表
        """
        return self.sections

    def get_section_by_name(self, name: str) -> Optional[Section]:
        """
        根据名称获取几何区域

        Args:
            name: 区域名称

        Returns:
            Optional[Section]: 找到的区域对象，未找到返回None
        """
        for section in self.sections:
            if section.name == name:
                return section
        return None

    def get_pkg_section(self) -> List[Section]:
        """
        获取封装相关区域

        Returns:
            List[Section]: 封装相关区域列表
        """
        return [section for section in self.sections if section.type_str == "package"]

    def get_stack_dies_section(self) -> List[Section]:
        """
        获取堆叠芯片区域

        Returns:
            List[Section]: 堆叠芯片区域列表
        """
        return [section for section in self.sections if section.type_str == "stacked_die"]

    def init_runtime_sections(self) -> List[Section]:
        """
        获取运行时处理后的区域（按Z坐标排序）

        Returns:
            List[Section]: 排序后的区域列表
        """
        # 按Z坐标排序
        if self.runtime_sections:
            return self.runtime_sections

        self.runtime_sections = [section for section in self.sections]
        if self.parts:
            # self.parts 是 PkgDie 对象，从它的 components 中获取运行时区域
            for component in self.parts.get_components():
                runtime_sections = component.get_pkgdie_runtime_sections()
                self.runtime_sections.extend(runtime_sections)
        return self.runtime_sections

    def add_runtime_section(self, section: Section) -> None:
        """
        添加运行时处理后的区域
        """
        self.runtime_sections.append(section)

    def get_runtime_sections(self) -> List[Section]:
        """
        获取运行时处理后的区域（按Z坐标排序）

        Returns:
            List[Section]: 排序后的区域列表
        """
        return self.runtime_sections

    def get_part(self) -> PkgDie:
        """
        获取部件

        Returns:
            PkgDie: 部件对象
        """
        return self.parts

    def get_all_used_material_names(self) -> List[str]:
        """
        获取所有使用的材料名称

        Returns:
            List[str]: 材料名称列表
        """
        material_names = set()

        # 初始化runtime_sections
        runtime_sections = self.init_runtime_sections()

        # 从sections中收集材料名称
        for section in runtime_sections:
            if section.material:
                # section.material 是 MaterialInfo 对象
                try:
                    material_names.add(section.material.name)
                except Exception:
                    pass

            # 同时收集section内部component的材料
            if hasattr(section, 'children') and section.children:
                for comp in section.children:
                    if getattr(comp, 'material', None):
                        try:
                            material_names.add(comp.material.name)
                        except Exception:
                            pass

        # 从parts中收集材料名称
        if self.parts:
            # self.parts 是 PkgDie 对象，从它的 components 中收集材料
            for component in self.parts.get_components():
                if component.material:
                    # component.material 是 MaterialInfo 对象
                    material_names.add(component.material.name)

        return list(material_names)

    def validate_materials(self) -> bool:
        """
        验证材料完整性

        Returns:
            bool: 验证是否通过
        """
        material_names = self.get_all_used_material_names()

        for name in material_names:
            if not self.materials_mgr.has_material(name):
                logger.error(f"Missing material: {name}")
                return False

        logger.info("Material validation passed")
        return True

    def validate_geometry(self) -> bool:
        """
        验证几何一致性

        Returns:
            bool: 验证是否通过
        """
        for section in self.sections:
            if not section.shape:
                logger.error(f"Section {section.name} has no shape")
                return False

            if section.thickness <= 0:
                logger.error(
                    f"Section {section.name} has invalid thickness: {section.thickness}")
                return False

        logger.info("Geometry validation passed")
        return True

    def validate_parameters(self) -> bool:
        """
        验证参数合理性

        Returns:
            bool: 验证是否通过
        """
        # 检查必要的参数（这些参数有默认值，不是必需的）
        # required_params = ["ambient_temperature", "surface_heat_flux"]

        # 为缺失的参数设置默认值
        if "ambient_temperature" not in self.parameters:
            self.parameters["ambient_temperature"] = 293.15  # 默认环境温度 20°C
            logger.info("Set default ambient_temperature: 293.15 K")

        if "surface_heat_flux" not in self.parameters:
            self.parameters["surface_heat_flux"] = 0.0  # 默认表面热流密度
            logger.info("Set default surface_heat_flux: 0.0 W/m²")

        # 为各个方向的热流密度设置默认值
        heat_flux_params = ["air_heat_flux", "top_heat_flux",
                            "side_heat_flux", "bottom_heat_flux"]
        for param in heat_flux_params:
            if param not in self.parameters:
                self.parameters[param] = 0.0  # 默认热流密度
                logger.info(f"Set default {param}: 0.0 W/m²")

        # 为unit参数设置默认值
        if "unit" not in self.parameters:
            self.parameters["unit"] = "m"  # 默认单位
            logger.info("Set default unit: m")

        logger.info("Parameter validation passed")
        return True

    def validate_hierarchy(self) -> bool:
        """
        验证层次结构完整性

        Returns:
            bool: 验证是否通过
        """
        for section in self.sections:
            if section.children:
                for child in section.children:
                    if not child.material:
                        # 检查是否是template引用的组件（这些组件材料信息在template中定义）
                        if hasattr(child, 'template_name') and child.template_name:
                            logger.debug(
                                f"Child component {child.name} is template-based, material info in template")
                        else:
                            logger.warning(
                                f"Child component1 {child.name} has no material")

        logger.info("Hierarchy validation passed")
        return True

    def validate(self) -> bool:
        """
        执行完整验证

        Returns:
            bool: 验证是否通过
        """
        logger.info("Starting ThermalInfo validation...")

        validations = [
            self.validate_materials(),
            self.validate_geometry(),
            self.validate_parameters(),
            self.validate_hierarchy()
        ]

        all_valid = all(validations)

        if all_valid:
            logger.info("ThermalInfo validation passed")
        else:
            logger.error("ThermalInfo validation failed")

        return all_valid

    def to_dict(self) -> Dict[str, Any]:
        """
        转换为字典格式

        Returns:
            Dict[str, Any]: 字典格式的数据
        """
        return {
            "name": self.name,
            "materials": [material.to_dict() for material in self.materials_mgr.get_materials()],
            "sections": [section.to_dict() for section in self.sections],
            "parts": self.parts.to_dict() if self.parts else {},
            "parameters": self.parameters,
            "thermal_parameters": self.thermal_parameters,
            "netlist": self.netlist,
            "component_connect": self.component_connect,
            "constraints": self.constraints
        }

    def from_dict(self, data: Dict[str, Any], json_file_path: Path = None) -> None:
        """
        从字典格式加载数据

        Args:
            data: 字典格式的数据
            json_file_path: JSON文件路径（可选，用于相对路径解析）
        """
        # 设置JSON文件目录（用于相对路径解析）
        if json_file_path:
            self.set_json_file_dir(json_file_path)

        # 设置模型名称
        if "model_name" in data:
            self.name = data["model_name"]
        else:
            self.name = data.get("name", "")

        # 加载材料
        materials_data = data.get("materials", [])
        for material_data in materials_data:
            material = MaterialInfo.from_dict(material_data)
            self.materials_mgr.add_material(material)

        # 加载模板（templates）
        templates_data = data.get("templates", [])
        if templates_data:
            self.vertical_interconnect_manager.from_json(
                {"templates": templates_data})

        # 加载几何区域
        sections_data = data.get("sections", [])
        for section_data in sections_data:
            section = Section()
            section.from_json(
                section_data, self.get_materials_mgr(), data, self)
            self.add_section(section)

        # 加载部件
        parts_data = data.get("parts", [])
        if parts_data:
            # 创建PkgDie对象
            pkg_die = PkgDie()
            if isinstance(parts_data, list):
                # parts 是列表，每个元素都是PkgComponent的数据
                for part_data in parts_data:
                    if isinstance(part_data, dict):
                        # 创建PkgComponent对象
                        component = PkgComponent(part_data)
                        # 设置材料对象
                        material_name = part_data.get("material", "")
                        if material_name:
                            material_info = self.materials_mgr.get_material(material_name)
                            if material_info:
                                component.material = material_info
                            else:
                                logger.warning(f"Material not found for PkgComponent: {material_name}")
                        pkg_die.add_component(component)
            elif isinstance(parts_data, dict):
                # parts 是单个字典，直接创建PkgComponent
                component = PkgComponent(parts_data)
                # 设置材料对象
                material_name = parts_data.get("material", "")
                if material_name:
                    material_info = self.materials_mgr.get_material(material_name)
                    if material_info:
                        component.material = material_info
                    else:
                        logger.warning(f"Material not found for PkgComponent: {material_name}")
                pkg_die.add_component(component)
            self.set_part(pkg_die)

        # 加载其他数据
        parameters_data = data.get("parameters", {})
        # 确保parameters是字典类型，如果是列表则转换为空字典
        if isinstance(parameters_data, list):
            self.parameters = {}
            logger.warning("Parameters is a list, converting to empty dict")
        else:
            self.parameters = parameters_data

        self.thermal_parameters = data.get("thermal", {})

        # 加载网络列表
        netlist_data = data.get("netlist", {})
        if netlist_data:
            self.netlist.from_json(netlist_data)

        # 加载组件连接信息
        self.component_connect = data.get("ComponentConnect", [])

        logger.info(f"Loaded ThermalInfo from dict: {self.name}")

    def save_to_json(self, file_path: Path) -> None:
        """
        保存到JSON文件

        Args:
            file_path: 保存路径
        """
        data = self.to_dict()

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved ThermalInfo to: {file_path}")

    def load_from_json(self, file_path: Path) -> None:
        """
        从JSON文件加载

        Args:
            file_path: 加载路径
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.from_dict(data)
        self.set_json_file_dir(file_path)

        logger.info(f"Loaded ThermalInfo from: {file_path}")

    def print_summary(self) -> None:
        """
        打印摘要信息
        """
        logger.info("=" * 50)
        logger.info(f"ThermalInfo Summary: {self.name}")
        logger.info("=" * 50)
        logger.info(f"Materials: {len(self.materials_mgr.get_materials())}")
        logger.info(f"Sections: {len(self.sections)}")
        logger.info(f"Parts: {'1' if self.parts else '0'}")
        logger.info(f"Parameters: {len(self.parameters)}")
        logger.info(f"Thermal Parameters: {len(self.thermal_parameters)}")
        logger.info("=" * 50)
