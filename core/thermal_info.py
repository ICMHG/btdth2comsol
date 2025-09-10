"""
ThermalInfo核心类
整个系统的核心数据结构，统一管理所有热分析相关数据
"""

import json
from pathlib import Path
from typing import List, Dict, Optional, Any
from loguru import logger

from models.material import MaterialInfo
from models.geometry import Section
from models.pkg_die import PkgComponent, PkgDie
from models.stacked_die import StackedDieSection
from models.bump_section import BumpSection
from models.thermal_netlist import ThermalNetList
from models.thermal_para import ThermalPara
from models.constraints import Constraints
from models.vertical_interconnect_manager import VerticalInterconnectManager
from models.power_map import DieStackPowerMap
from core.material_manager import MaterialInfosMgr


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
        
        # 封装芯片组件
        self.pkg_components: List[PkgComponent] = []
        
        # 堆叠芯片区域
        self.stacked_die_sections: List[StackedDieSection] = []
        
        # 凸点区域
        self.bump_sections: List[BumpSection] = []
        
        # 参数系统
        self.parameters: Dict[str, Any] = {}
        
        # 热分析参数
        self.thermal_parameters: Dict[str, Any] = {}
        
        # 网络列表
        self.netlist: ThermalNetList = ThermalNetList()
        
        # 组件连接信息
        self.component_connect: List[Dict[str, Any]] = []
        
        # 部件信息
        self.part_info: List[Dict[str, Any]] = []
        
        # 约束条件
        self.constraints: Constraints = Constraints()
        
        # 垂直互连管理器
        self.vertical_interconnect_manager: VerticalInterconnectManager = VerticalInterconnectManager()
        
        # 功率映射
        self.power_maps: Dict[str, DieStackPowerMap] = {}
        
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
    
    def add_pkg_component(self, pkg_component: PkgComponent) -> None:
        """
        添加封装芯片组件
        
        Args:
            pkg_component: 封装芯片组件对象
        """
        self.pkg_components.append(pkg_component)
        logger.debug(f"Added pkg component: {pkg_component.get_mdl_name()}")
    
    def add_stacked_die_section(self, stacked_die: StackedDieSection) -> None:
        """
        添加堆叠芯片区域
        
        Args:
            stacked_die: 堆叠芯片区域对象
        """
        self.stacked_die_sections.append(stacked_die)
        logger.debug(f"Added stacked die section: {stacked_die.name}")
    
    def add_bump_section(self, bump_section: BumpSection) -> None:
        """
        添加凸点区域
        
        Args:
            bump_section: 凸点区域对象
        """
        self.bump_sections.append(bump_section)
        logger.debug(f"Added bump section: {bump_section.name}")
    
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
    
    def get_runtime_sections(self) -> List[Section]:
        """
        获取运行时处理后的区域（按Z坐标排序）
        
        Returns:
            List[Section]: 排序后的区域列表
        """
        # 按Z坐标排序
        sorted_sections = sorted(self.sections, key=lambda s: s.get_offset_z())
        return sorted_sections
    
    def get_pkg_components(self) -> List[Dict[str, Any]]:
        """
        获取所有封装芯片组件
        
        Returns:
            List[Dict[str, Any]]: 封装芯片组件列表
        """
        return self.pkg_components
    
    def get_stacked_die_sections(self) -> List[Dict[str, Any]]:
        """
        获取所有堆叠芯片区域
        
        Returns:
            List[Dict[str, Any]]: 堆叠芯片区域列表
        """
        return self.stacked_die_sections
    
    def get_bump_sections(self) -> List[BumpSection]:
        """
        获取所有凸点区域
        
        Returns:
            List[Dict[str, Any]]: 凸点区域列表
        """
        return self.bump_sections
    
    def get_all_used_material_names(self) -> List[str]:
        """
        获取所有使用的材料名称
        
        Returns:
            List[str]: 材料名称列表
        """
        material_names = set()
        
        # 从sections中收集材料名称
        for section in self.sections:
            if section.material:
                if hasattr(section.material, 'name'):
                    material_names.add(section.material.name)
                elif hasattr(section.material, 'materials'):
                    # 复合材料
                    for material, _ in section.material.materials:
                        material_names.add(material.name)
        
        # 从pkg_components中收集材料名称
        for pkg_comp in self.pkg_components:
            if 'material' in pkg_comp:
                material_names.add(pkg_comp['material'])
        
        # 从stacked_die_sections中收集材料名称
        for stacked_die in self.stacked_die_sections:
            if 'material' in stacked_die:
                material_names.add(stacked_die['material'])
        
        # 从bump_sections中收集材料名称
        for bump_section in self.bump_sections:
            if 'material' in bump_section:
                material_names.add(bump_section['material'])
        
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
                logger.error(f"Section {section.name} has invalid thickness: {section.thickness}")
                return False
        
        logger.info("Geometry validation passed")
        return True
    
    def validate_parameters(self) -> bool:
        """
        验证参数合理性
        
        Returns:
            bool: 验证是否通过
        """
        # 检查必要的参数
        required_params = ["ambient_temperature", "surface_heat_flux"]
        
        for param in required_params:
            if param not in self.parameters:
                logger.warning(f"Missing parameter: {param}")
        
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
                        logger.warning(f"Child component {child.name} has no material")
        
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
            "pkg_components": self.pkg_components,
            "stacked_die_sections": self.stacked_die_sections,
            "bump_sections": self.bump_sections,
            "parameters": self.parameters,
            "thermal_parameters": self.thermal_parameters,
            "netlist": self.netlist,
            "component_connect": self.component_connect,
            "part_info": self.part_info,
            "constraints": self.constraints,
            "power_maps": self.power_maps
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """
        从字典格式加载数据
        
        Args:
            data: 字典格式的数据
        """
        self.name = data.get("name", "")
        
        # 加载材料
        materials_data = data.get("materials", [])
        for material_data in materials_data:
            material = MaterialInfo.from_dict(material_data)
            self.materials_mgr.add_material(material)
        
        # 加载几何区域
        sections_data = data.get("sections", [])
        for section_data in sections_data:
            section = Section.from_dict(section_data)
            self.add_section(section)
        
        # 加载封装芯片组件
        pkg_components_data = data.get("pkg_components", [])
        for pkg_comp_data in pkg_components_data:
            self.add_pkg_component(pkg_comp_data)
        
        # 加载堆叠芯片区域
        stacked_die_data = data.get("stacked_die_sections", [])
        for stacked_die_data_item in stacked_die_data:
            self.add_stacked_die_section(stacked_die_data_item)
        
        # 加载凸点区域
        bump_sections_data = data.get("bump_sections", [])
        for bump_section_data in bump_sections_data:
            self.add_bump_section(bump_section_data)
        
        # 加载其他数据
        self.parameters = data.get("parameters", {})
        self.thermal_parameters = data.get("thermal_parameters", {})
        self.netlist = data.get("netlist", {})
        self.component_connect = data.get("component_connect", [])
        self.part_info = data.get("part_info", [])
        self.constraints = data.get("constraints", {})
        self.power_maps = data.get("power_maps", {})
        
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
        logger.info(f"Package Components: {len(self.pkg_components)}")
        logger.info(f"Stacked Die Sections: {len(self.stacked_die_sections)}")
        logger.info(f"Bump Sections: {len(self.bump_sections)}")
        logger.info(f"Parameters: {len(self.parameters)}")
        logger.info(f"Thermal Parameters: {len(self.thermal_parameters)}")
        logger.info(f"Power Maps: {len(self.power_maps)}")
        logger.info("=" * 50)

