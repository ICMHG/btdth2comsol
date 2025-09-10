"""
JSON解析器
负责解析BTD Thermal格式的JSON文件
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger

from core.thermal_info import ThermalInfo
from parser.material_parser import MaterialParser, MaterialParsingError
from parser.geometry_parser import GeometryParser, GeometryParsingError
from parser.shape_parser import ShapeParser, ShapeParsingError
from models.thermal_netlist import ThermalNetList
from models.thermal_para import ThermalPara
from models.constraints import Constraints
from models.vertical_interconnect_manager import VerticalInterconnectManager


class BTDJsonParsingError(Exception):
    """BTD JSON解析错误"""
    pass


class BTDJsonParser:
    """BTD Thermal JSON解析器"""
    
    def __init__(self):
        """初始化解析器"""
        self.thermal_info = None
        self.material_parser = None
        self.geometry_parser = None
        self.shape_parser = None
        logger.debug("BTDJsonParser initialized")
    
    def parse_file(self, json_file_path: Path) -> Optional[ThermalInfo]:
        """
        解析JSON文件
        
        Args:
            json_file_path: JSON文件路径
            
        Returns:
            Optional[ThermalInfo]: 解析后的ThermalInfo对象
            
        Raises:
            BTDJsonParsingError: 解析失败时抛出
        """
        try:
            logger.info(f"Parsing JSON file: {json_file_path}")
            
            # 确保文件路径是Path对象
            if isinstance(json_file_path, str):
                json_file_path = Path(json_file_path)
            
            # 验证文件存在
            if not json_file_path.exists():
                raise BTDJsonParsingError(f"JSON file not found: {json_file_path}")
            
            # 读取JSON文件
            with open(json_file_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            # 解析JSON数据
            return self.parse(json_data, json_file_path)
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format: {e}")
            raise BTDJsonParsingError(f"Invalid JSON format: {e}")
        except Exception as e:
            logger.error(f"Failed to parse JSON file: {e}")
            raise BTDJsonParsingError(f"Failed to parse JSON file: {e}")
    
    def parse(self, json_data: Dict[str, Any], json_file_path: Path = None) -> Optional[ThermalInfo]:
        """
        解析JSON数据
        
        Args:
            json_data: JSON数据字典
            json_file_path: JSON文件路径（可选）
            
        Returns:
            Optional[ThermalInfo]: 解析后的ThermalInfo对象
            
        Raises:
            BTDJsonParsingError: 解析失败时抛出
        """
        try:
            # 创建ThermalInfo对象
            self.thermal_info = ThermalInfo()
            
            # 设置JSON文件目录（用于相对路径解析）
            if json_file_path:
                self.thermal_info.set_json_file_dir(json_file_path)
            
            # 设置模型名称
            if "model_name" in json_data:
                self.thermal_info.name = json_data["model_name"]
            
            # 初始化专用解析器
            self.material_parser = MaterialParser(self.thermal_info)
            self.geometry_parser = GeometryParser(self.thermal_info)
            self.shape_parser = ShapeParser()
            
            # 按顺序解析各个部分
            self._parse_materials(json_data.get("materials", []))
            self._parse_templates(json_data.get("templates", []))
            self._parse_sections(json_data.get("sections", []))
            self._parse_parts(json_data.get("parts", []))
            
            # 解析新组件类型
            self._parse_pkg_components(json_data.get("pkg_components", []))
            self._parse_stacked_die_sections(json_data.get("stacked_die_sections", []))
            self._parse_bump_sections(json_data.get("bump_sections", []))
            
            self._parse_parameters(json_data.get("parameters", {}))
            self._parse_thermal_parameters(json_data.get("thermal", {}))
            self._parse_netlist(json_data.get("netlist", {}))
            self._parse_component_connect(json_data.get("ComponentConnect", []))
            self._parse_part_info(json_data.get("Part", []))
            self._parse_constraints(json_data.get("Constraints", {}))
            self._parse_power_maps(json_data.get("power_maps", {}))
            
            # 验证解析结果
            self._validate_parsed_data()
            
            logger.info("JSON parsing completed successfully")
            return self.thermal_info
            
        except Exception as e:
            logger.error(f"Failed to parse JSON data: {e}")
            if isinstance(e, (MaterialParsingError, GeometryParsingError, ShapeParsingError)):
                raise BTDJsonParsingError(f"Parsing error: {e}")
            raise BTDJsonParsingError(f"Unexpected error during parsing: {e}")
    
    def _parse_materials(self, materials_data: list) -> None:
        """解析材料定义"""
        if not materials_data:
            logger.debug("No materials data found")
            return
        
        try:
            self.material_parser.parse_materials(materials_data)
            logger.info(f"Successfully parsed {len(materials_data)} materials")
        except MaterialParsingError as e:
            logger.error(f"Material parsing failed: {e}")
            raise
    
    def _parse_templates(self, templates_data: list) -> None:
        """解析模板定义"""
        if not templates_data:
            logger.debug("No templates data found")
            return
        
        logger.info(f"Parsing {len(templates_data)} templates")
        
        try:
            # 解析垂直互连模板
            for template_data in templates_data:
                if isinstance(template_data, dict):
                    template_name = template_data.get("name", "")
                    template_type = template_data.get("type", "")
                    
                    if template_type == "vertical_interconnect":
                        self._parse_vertical_interconnect_template(template_data)
                    else:
                        logger.debug(f"Skipping template of type: {template_type}")
            
            logger.info("Templates parsing completed")
        except Exception as e:
            logger.error(f"Template parsing failed: {e}")
            raise BTDJsonParsingError(f"Template parsing failed: {e}")
    
    def _parse_vertical_interconnect_template(self, template_data: Dict[str, Any]) -> None:
        """解析垂直互连模板"""
        template_name = template_data.get("name", "")
        logger.debug(f"Parsing vertical interconnect template: {template_name}")
        
        # 创建垂直互连管理器（如果不存在）
        if not hasattr(self.thermal_info, 'vertical_interconnect_manager'):
            from core.vertical_interconnect_manager import VerticalInterconnectManager
            self.thermal_info.vertical_interconnect_manager = VerticalInterconnectManager()
        
        # 解析PadStack信息
        if "padstack" in template_data:
            padstack_data = template_data["padstack"]
            if isinstance(padstack_data, dict):
                from models.geometry import PadStack
                padstack = PadStack(template_name)
                
                # 设置参数
                if "diameter" in padstack_data:
                    padstack.set_diameter(float(padstack_data["diameter"]))
                
                if "height" in padstack_data:
                    padstack.set_height(float(padstack_data["height"]))
                
                if "material" in padstack_data:
                    material_name = padstack_data["material"]
                    material_info = self.thermal_info.get_materials_mgr().get_material(material_name)
                    if material_info:
                        padstack.set_material(material_info)
                
                # 添加到管理器
                self.thermal_info.vertical_interconnect_manager.add_padstack(padstack)
    
    def _parse_sections(self, sections_data: list) -> None:
        """解析几何区域"""
        if not sections_data:
            logger.debug("No sections data found")
            return
        
        try:
            self.geometry_parser.parse_sections(sections_data)
            logger.info(f"Successfully parsed {len(sections_data)} sections")
        except GeometryParsingError as e:
            logger.error(f"Geometry parsing failed: {e}")
            raise
    
    def _parse_parts(self, parts_data: list) -> None:
        """解析部件定义"""
        if not parts_data:
            logger.debug("No parts data found")
            return
        
        logger.info(f"Parsing {len(parts_data)} parts")
        
        try:
            for part_data in parts_data:
                if isinstance(part_data, dict):
                    part_name = part_data.get("name", "")
                    part_type = part_data.get("type", "")
                    
                    if part_type == "stacked_die":
                        # 解析堆叠芯片
                        self.geometry_parser.parse_stacked_die_sections([part_data])
                    elif part_type == "package":
                        # 解析封装组件
                        self.geometry_parser.parse_pkg_components([part_data])
                    elif part_type == "bump":
                        # 解析凸点区域
                        self.geometry_parser.parse_bump_sections([part_data])
                    else:
                        logger.debug(f"Skipping part of type: {part_type}")
            
            logger.info("Parts parsing completed")
        except Exception as e:
            logger.error(f"Parts parsing failed: {e}")
            raise BTDJsonParsingError(f"Parts parsing failed: {e}")
    
    def _parse_pkg_components(self, pkg_components_data: list) -> None:
        """解析封装芯片组件"""
        if not pkg_components_data:
            logger.debug("No package components data found")
            return
        
        logger.info(f"Parsing {len(pkg_components_data)} package components")
        try:
            self.geometry_parser.parse_pkg_components(pkg_components_data)
            logger.info("Package components parsing completed")
        except Exception as e:
            logger.error(f"Package components parsing failed: {e}")
            raise BTDJsonParsingError(f"Package components parsing failed: {e}")
    
    def _parse_stacked_die_sections(self, stacked_die_data: list) -> None:
        """解析堆叠芯片区域"""
        if not stacked_die_data:
            logger.debug("No stacked die sections data found")
            return
        
        logger.info(f"Parsing {len(stacked_die_data)} stacked die sections")
        try:
            self.geometry_parser.parse_stacked_die_sections(stacked_die_data)
            logger.info("Stacked die sections parsing completed")
        except Exception as e:
            logger.error(f"Stacked die sections parsing failed: {e}")
            raise BTDJsonParsingError(f"Stacked die sections parsing failed: {e}")
    
    def _parse_bump_sections(self, bump_sections_data: list) -> None:
        """解析凸点区域"""
        if not bump_sections_data:
            logger.debug("No bump sections data found")
            return
        
        logger.info(f"Parsing {len(bump_sections_data)} bump sections")
        try:
            self.geometry_parser.parse_bump_sections(bump_sections_data)
            logger.info("Bump sections parsing completed")
        except Exception as e:
            logger.error(f"Bump sections parsing failed: {e}")
            raise BTDJsonParsingError(f"Bump sections parsing failed: {e}")
    
    def _parse_parameters(self, parameters_data: dict) -> None:
        """解析参数"""
        if not parameters_data:
            logger.debug("No parameters data found")
            return
        
        logger.info("Parsing parameters")
        
        try:
            # 设置环境参数
            if "ambient_temperature" in parameters_data:
                ambient_temp = float(parameters_data["ambient_temperature"])
                self.thermal_info.parameters["ambient_temperature"] = ambient_temp
            
            if "surface_heat_flux" in parameters_data:
                surface_heat_flux = float(parameters_data["surface_heat_flux"])
                self.thermal_info.parameters["surface_heat_flux"] = surface_heat_flux
            
            # 设置单位参数
            if "units" in parameters_data:
                units_data = parameters_data["units"]
                if isinstance(units_data, dict):
                    self.thermal_info.parameters["units"] = units_data
            
            # 设置其他参数
            for key, value in parameters_data.items():
                if key not in ["ambient_temperature", "surface_heat_flux", "units"]:
                    self.thermal_info.parameters[key] = value
            
            logger.info("Parameters parsing completed")
        except Exception as e:
            logger.error(f"Parameters parsing failed: {e}")
            raise BTDJsonParsingError(f"Parameters parsing failed: {e}")
    
    def _parse_thermal_parameters(self, thermal_data: dict) -> None:
        """解析热分析参数"""
        if not thermal_data:
            logger.debug("No thermal parameters data found")
            return
        
        logger.info("Parsing thermal parameters")
        
        try:
            # 设置封装参数
            if "package" in thermal_data:
                package_data = thermal_data["package"]
                if isinstance(package_data, dict):
                    self.thermal_info.thermal_parameters["package"] = package_data
            
            # 设置散热器参数
            if "heat_sink" in thermal_data:
                heat_sink_data = thermal_data["heat_sink"]
                if isinstance(heat_sink_data, dict):
                    self.thermal_info.thermal_parameters["heat_sink"] = heat_sink_data
            
            # 设置测试板参数
            if "test_board" in thermal_data:
                test_board_data = thermal_data["test_board"]
                if isinstance(test_board_data, dict):
                    self.thermal_info.thermal_parameters["test_board"] = test_board_data
            
            # 设置其他热参数
            for key, value in thermal_data.items():
                if key not in ["package", "heat_sink", "test_board"]:
                    self.thermal_info.thermal_parameters[key] = value
            
            logger.info("Thermal parameters parsing completed")
        except Exception as e:
            logger.error(f"Thermal parameters parsing failed: {e}")
            raise BTDJsonParsingError(f"Thermal parameters parsing failed: {e}")
    
    def _parse_netlist(self, netlist_data: dict) -> None:
        """解析网络列表"""
        if not netlist_data:
            logger.debug("No netlist data found")
            return
        
        logger.info("Parsing netlist")
        
        try:
            # 设置网络列表数据
            self.thermal_info.netlist = netlist_data
            logger.info("Netlist parsing completed")
        except Exception as e:
            logger.error(f"Netlist parsing failed: {e}")
            raise BTDJsonParsingError(f"Netlist parsing failed: {e}")
    
    def _parse_component_connect(self, component_connect_data: list) -> None:
        """解析组件连接信息"""
        if not component_connect_data:
            logger.debug("No component connect data found")
            return
        
        logger.info(f"Parsing {len(component_connect_data)} component connections")
        
        try:
            # 设置组件连接数据
            self.thermal_info.component_connect = component_connect_data
            logger.info("Component connect parsing completed")
        except Exception as e:
            logger.error(f"Component connect parsing failed: {e}")
            raise BTDJsonParsingError(f"Component connect parsing failed: {e}")
    
    def _parse_part_info(self, part_info_data: list) -> None:
        """解析部件信息"""
        if not part_info_data:
            logger.debug("No part info data found")
            return
        
        logger.info(f"Parsing {len(part_info_data)} part info")
        
        try:
            # 设置部件信息数据
            self.thermal_info.part_info = part_info_data
            logger.info("Part info parsing completed")
        except Exception as e:
            logger.error(f"Part info parsing failed: {e}")
            raise BTDJsonParsingError(f"Part info parsing failed: {e}")
    
    def _parse_constraints(self, constraints_data: dict) -> None:
        """解析约束条件"""
        if not constraints_data:
            logger.debug("No constraints data found")
            return
        
        logger.info("Parsing constraints")
        
        try:
            # 设置约束条件数据
            self.thermal_info.constraints = constraints_data
            logger.info("Constraints parsing completed")
        except Exception as e:
            logger.error(f"Constraints parsing failed: {e}")
            raise BTDJsonParsingError(f"Constraints parsing failed: {e}")
    
    def _parse_power_maps(self, power_maps_data: dict) -> None:
        """解析功率映射"""
        if not power_maps_data:
            logger.debug("No power maps data found")
            return
        
        logger.info("Parsing power maps")
        
        try:
            # 设置功率映射数据
            self.thermal_info.power_maps = power_maps_data
            logger.info("Power maps parsing completed")
        except Exception as e:
            logger.error(f"Power maps parsing failed: {e}")
            raise BTDJsonParsingError(f"Power maps parsing failed: {e}")
    
    def _validate_parsed_data(self) -> None:
        """验证解析后的数据"""
        logger.info("Validating parsed data")
        
        try:
            # 验证材料引用
            if self.material_parser:
                if not self.material_parser.validate_material_references():
                    raise BTDJsonParsingError("Material reference validation failed")
            
            # 验证几何一致性
            if self.geometry_parser:
                if not self.geometry_parser.validate_geometry_consistency():
                    raise BTDJsonParsingError("Geometry consistency validation failed")
            
            # 验证ThermalInfo
            if not self.thermal_info.validate():
                raise BTDJsonParsingError("ThermalInfo validation failed")
            
            logger.info("Data validation completed successfully")
        except Exception as e:
            logger.error(f"Data validation failed: {e}")
            raise BTDJsonParsingError(f"Data validation failed: {e}")
    
    def create_parsing_summary(self) -> Dict[str, Any]:
        """
        创建解析摘要信息
        
        Returns:
            Dict[str, Any]: 解析摘要
        """
        if not self.thermal_info:
            return {"error": "No data parsed yet"}
        
        summary = {
            "model_name": self.thermal_info.name,
            "materials": {},
            "geometry": {},
            "parameters": len(self.thermal_info.parameters),
            "thermal_parameters": len(self.thermal_info.thermal_parameters),
            "netlist": len(self.thermal_info.netlist) if self.thermal_info.netlist else 0,
            "component_connect": len(self.thermal_info.component_connect),
            "part_info": len(self.thermal_info.part_info),
            "constraints": len(self.thermal_info.constraints) if hasattr(self.thermal_info.constraints, '__len__') else 0,
            "power_maps": len(self.thermal_info.power_maps)
        }
        
        # 材料摘要
        if self.material_parser:
            summary["materials"] = self.material_parser.create_material_summary()
        
        # 几何摘要
        if self.geometry_parser:
            summary["geometry"] = self.geometry_parser.create_geometry_summary()
        
        return summary
    
    def export_parsed_data(self, output_file: Path) -> None:
        """
        导出解析后的数据到JSON文件
        
        Args:
            output_file: 输出文件路径
        """
        if not self.thermal_info:
            raise BTDJsonParsingError("No data to export")
        
        try:
            data = self.thermal_info.to_dict()
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Exported parsed data to: {output_file}")
        except Exception as e:
            logger.error(f"Failed to export data: {e}")
            raise BTDJsonParsingError(f"Export failed: {e}")
    
    def get_parsing_statistics(self) -> Dict[str, Any]:
        """
        获取解析统计信息
        
        Returns:
            Dict[str, Any]: 解析统计
        """
        if not self.thermal_info:
            return {"error": "No data parsed yet"}
        
        stats = {
            "total_materials": len(self.thermal_info.get_materials_mgr().get_materials()),
            "total_sections": len(self.thermal_info.get_all_sections()),
            "total_parameters": len(self.thermal_info.parameters),
            "total_thermal_parameters": len(self.thermal_info.thermal_parameters),
            "validation_status": "unknown"
        }
        
        try:
            if self.thermal_info.validate():
                stats["validation_status"] = "passed"
            else:
                stats["validation_status"] = "failed"
        except Exception:
            stats["validation_status"] = "error"
        
        return stats

