"""
材料解析器
负责解析材料定义，创建MaterialInfo和CompositeMaterial对象
"""

from typing import List, Dict, Any, Optional
from loguru import logger

from core.thermal_info import ThermalInfo
from models.material import MaterialInfo, CompositeMaterial, ObjectMaterial, TemperaturePoint, Conductivity


class MaterialParsingError(Exception):
    """材料解析错误"""
    pass


class MaterialParser:
    """材料解析器"""
    
    def __init__(self, thermal_info: ThermalInfo):
        """
        初始化材料解析器
        
        Args:
            thermal_info: ThermalInfo对象
        """
        self.thermal_info = thermal_info
        logger.debug("MaterialParser initialized")
    
    def parse_materials(self, materials_data: List[Dict[str, Any]]) -> None:
        """
        解析材料定义列表
        
        Args:
            materials_data: 材料数据列表
            
        Raises:
            MaterialParsingError: 解析失败时抛出
        """
        logger.info(f"Parsing {len(materials_data)} materials")
        
        for material_data in materials_data:
            try:
                material_info = self._parse_single_material(material_data)
                self.thermal_info.get_materials_mgr().add_material(material_info)
                logger.debug(f"Added material: {material_info.name}")
            except Exception as e:
                logger.error(f"Failed to parse material: {e}")
                raise MaterialParsingError(f"Material parsing failed: {e}")
    
    def _parse_single_material(self, material_data: Dict[str, Any]) -> MaterialInfo:
        """
        解析单个材料定义
        
        Args:
            material_data: 单个材料数据
            
        Returns:
            MaterialInfo: 材料信息对象
            
        Raises:
            MaterialParsingError: 解析失败时抛出
        """
        # 验证必要字段
        required_fields = ["name", "t_kx_ky_kz_rho_hc_em_ref_properties"]
        for field in required_fields:
            if field not in material_data:
                raise MaterialParsingError(f"Missing required field: {field}")
        
        # 创建MaterialInfo对象
        material_name = material_data["name"]
        material_info = MaterialInfo(material_name)
        
        # 解析温度依赖性属性
        properties_data = material_data["t_kx_ky_kz_rho_hc_em_ref_properties"]
        if not isinstance(properties_data, list):
            raise MaterialParsingError("Properties must be a list")
        
        for prop_data in properties_data:
            if not isinstance(prop_data, list) or len(prop_data) != 8:
                raise MaterialParsingError(f"Invalid property data format: {prop_data}")
            
            try:
                # 解析属性数组：[temperature, kx, ky, kz, rho, hc, em, ref]
                temperature = float(prop_data[0])
                conductivity_x = float(prop_data[1])
                conductivity_y = float(prop_data[2])
                conductivity_z = float(prop_data[3])
                density = float(prop_data[4])
                heat_capacity = float(prop_data[5])
                electrical_migration = float(prop_data[6])
                solar_reflectance = float(prop_data[7])
                
                # 验证数值合理性
                if temperature < 0:
                    logger.warning(f"Negative temperature for material {material_name}: {temperature}")
                
                if conductivity_x < 0 or conductivity_y < 0 or conductivity_z < 0:
                    logger.warning(f"Negative conductivity for material {material_name}")
                
                if density < 0:
                    logger.warning(f"Negative density for material {material_name}: {density}")
                
                if heat_capacity < 0:
                    logger.warning(f"Negative heat capacity for material {material_name}: {heat_capacity}")
                
                # 添加温度点
                material_info.add_temperature_point(
                    temperature, conductivity_x, conductivity_y, conductivity_z,
                    density, heat_capacity, electrical_migration, solar_reflectance
                )
                
            except (ValueError, TypeError) as e:
                raise MaterialParsingError(f"Invalid numeric value in properties: {e}")
        
        # 验证材料完整性
        if not material_info.temperature_map:
            raise MaterialParsingError(f"No valid temperature points for material: {material_name}")
        
        # 设置材料类型（如果有）
        if "type" in material_data:
            material_info.material_type = material_data["type"]
        
        # 注意：MaterialInfo类目前不支持description和color属性
        # 如果需要这些属性，可以在MaterialInfo类中添加
        
        logger.debug(f"Successfully parsed material: {material_name} with {len(material_info.temperature_map)} temperature points")
        return material_info
    
    def parse_composite_materials(self, composite_data: List[Dict[str, Any]]) -> List[CompositeMaterial]:
        """
        解析复合材料定义
        
        Args:
            composite_data: 复合材料数据列表
            
        Returns:
            List[CompositeMaterial]: 复合材料对象列表
            
        Raises:
            MaterialParsingError: 解析失败时抛出
        """
        logger.info(f"Parsing {len(composite_data)} composite materials")
        
        composite_materials = []
        for comp_data in composite_data:
            try:
                composite_material = self._parse_single_composite_material(comp_data)
                composite_materials.append(composite_material)
                logger.debug(f"Added composite material: {composite_material.name}")
            except Exception as e:
                logger.error(f"Failed to parse composite material: {e}")
                raise MaterialParsingError(f"Composite material parsing failed: {e}")
        
        return composite_materials
    
    def _parse_single_composite_material(self, comp_data: Dict[str, Any]) -> CompositeMaterial:
        """
        解析单个复合材料定义
        
        Args:
            comp_data: 单个复合材料数据
            
        Returns:
            CompositeMaterial: 复合材料对象
            
        Raises:
            MaterialParsingError: 解析失败时抛出
        """
        # 验证必要字段
        required_fields = ["name", "materials"]
        for field in required_fields:
            if field not in comp_data:
                raise MaterialParsingError(f"Missing required field: {field}")
        
        # 创建CompositeMaterial对象
        composite_name = comp_data["name"]
        composite_material = CompositeMaterial(composite_name)
        
        # 解析材料组成
        materials_data = comp_data["materials"]
        if not isinstance(materials_data, list):
            raise MaterialParsingError("Materials must be a list")
        
        total_percentage = 0.0
        for mat_data in materials_data:
            if not isinstance(mat_data, dict):
                raise MaterialParsingError("Material data must be a dictionary")
            
            required_mat_fields = ["name", "percentage"]
            for field in required_mat_fields:
                if field not in mat_data:
                    raise MaterialParsingError(f"Missing required material field: {field}")
            
            material_name = mat_data["name"]
            percentage = float(mat_data["percentage"])
            
            # 验证百分比
            if percentage < 0 or percentage > 1:
                raise MaterialParsingError(f"Invalid percentage for material {material_name}: {percentage}")
            
            # 获取材料对象
            material_info = self.thermal_info.get_materials_mgr().get_material(material_name)
            if not material_info:
                raise MaterialParsingError(f"Material not found: {material_name}")
            
            # 添加到复合材料
            composite_material.add_material(material_info, percentage)
            total_percentage += percentage
        
        # 验证百分比总和
        if abs(total_percentage - 1.0) > 1e-6:
            logger.warning(f"Composite material {composite_name} percentages sum to {total_percentage}, not 1.0")
        
        # 设置描述（如果有）
        if "description" in comp_data:
            composite_material.set_description(comp_data["description"])
        
        # 设置混合方法（如果有）
        if "mixing_method" in comp_data:
            composite_material.set_mixing_method(comp_data["mixing_method"])
        
        logger.debug(f"Successfully parsed composite material: {composite_name} with {len(composite_material.materials)} components")
        return composite_material
    
    def parse_object_materials(self, object_materials_data: List[Dict[str, Any]]) -> List[ObjectMaterial]:
        """
        解析对象材料定义
        
        Args:
            object_materials_data: 对象材料数据列表
            
        Returns:
            List[ObjectMaterial]: 对象材料对象列表
            
        Raises:
            MaterialParsingError: 解析失败时抛出
        """
        logger.info(f"Parsing {len(object_materials_data)} object materials")
        
        object_materials = []
        for obj_mat_data in object_materials_data:
            try:
                object_material = self._parse_single_object_material(obj_mat_data)
                object_materials.append(object_material)
                logger.debug(f"Added object material: {object_material.name}")
            except Exception as e:
                logger.error(f"Failed to parse object material: {e}")
                raise MaterialParsingError(f"Object material parsing failed: {e}")
        
        return object_materials
    
    def _parse_single_object_material(self, obj_mat_data: Dict[str, Any]) -> ObjectMaterial:
        """
        解析单个对象材料定义
        
        Args:
            obj_mat_data: 单个对象材料数据
            
        Returns:
            ObjectMaterial: 对象材料对象
            
        Raises:
            MaterialParsingError: 解析失败时抛出
        """
        # 验证必要字段
        required_fields = ["name", "material_name"]
        for field in required_fields:
            if field not in obj_mat_data:
                raise MaterialParsingError(f"Missing required field: {field}")
        
        # 创建ObjectMaterial对象
        object_name = obj_mat_data["name"]
        material_name = obj_mat_data["material_name"]
        
        # 获取基础材料
        material_info = self.thermal_info.get_materials_mgr().get_material(material_name)
        if not material_info:
            raise MaterialParsingError(f"Material not found: {material_name}")
        
        object_material = ObjectMaterial(object_name, material_info)
        
        # 设置厚度（如果有）
        if "thickness" in obj_mat_data:
            thickness = float(obj_mat_data["thickness"])
            if thickness <= 0:
                raise MaterialParsingError(f"Invalid thickness: {thickness}")
            object_material.set_thickness(thickness)
        
        # 设置位置（如果有）
        if "position" in obj_mat_data:
            pos_data = obj_mat_data["position"]
            if isinstance(pos_data, dict) and len(pos_data) >= 3:
                from models.shape import Vector3D
                position = Vector3D(
                    float(pos_data.get("x", 0.0)),
                    float(pos_data.get("y", 0.0)),
                    float(pos_data.get("z", 0.0))
                )
                object_material.set_position(position)
        
        # 设置旋转（如果有）
        if "rotation" in obj_mat_data:
            rotation = float(obj_mat_data["rotation"])
            object_material.set_rotation(rotation)
        
        # 设置描述（如果有）
        if "description" in obj_mat_data:
            object_material.set_description(obj_mat_data["description"])
        
        logger.debug(f"Successfully parsed object material: {object_name} using material: {material_name}")
        return object_material
    
    def validate_material_references(self) -> bool:
        """
        验证所有材料引用是否有效
        
        Returns:
            bool: 验证是否通过
        """
        logger.info("Validating material references")
        
        # 获取所有使用的材料名称
        used_material_names = self.thermal_info.get_all_used_material_names()
        
        # 检查每个材料是否存在
        missing_materials = []
        for material_name in used_material_names:
            if not self.thermal_info.get_materials_mgr().has_material(material_name):
                missing_materials.append(material_name)
        
        if missing_materials:
            logger.error(f"Missing materials: {missing_materials}")
            return False
        
        logger.info("Material reference validation passed")
        return True
    
    def create_material_summary(self) -> Dict[str, Any]:
        """
        创建材料摘要信息
        
        Returns:
            Dict[str, Any]: 材料摘要
        """
        materials_mgr = self.thermal_info.get_materials_mgr()
        materials = materials_mgr.get_materials()
        
        summary = {
            "total_materials": len(materials),
            "temperature_dependent": 0,
            "constant_properties": 0,
            "material_types": {},
            "temperature_ranges": {}
        }
        
        for material in materials:
            # 统计温度依赖性
            if len(material.temperature_map) > 1:
                summary["temperature_dependent"] += 1
            else:
                summary["constant_properties"] += 1
            
            # 统计材料类型
            material_type = getattr(material, 'type', 'unknown')
            summary["material_types"][material_type] = summary["material_types"].get(material_type, 0) + 1
            
            # 统计温度范围
            if material.temperature_map:
                temperatures = list(material.temperature_map.keys())
                min_temp = min(temperatures)
                max_temp = max(temperatures)
                summary["temperature_ranges"][material.name] = {
                    "min": min_temp,
                    "max": max_temp,
                    "points": len(temperatures)
                }
        
        return summary
    
    def export_materials_to_dict(self) -> List[Dict[str, Any]]:
        """
        导出材料数据到字典格式
        
        Returns:
            List[Dict[str, Any]]: 材料数据列表
        """
        materials_mgr = self.thermal_info.get_materials_mgr()
        materials = materials_mgr.get_materials()
        
        exported_materials = []
        for material in materials:
            material_dict = material.to_dict()
            exported_materials.append(material_dict)
        
        return exported_materials
    
    def import_materials_from_dict(self, materials_data: List[Dict[str, Any]]) -> None:
        """
        从字典格式导入材料数据
        
        Args:
            materials_data: 材料数据列表
        """
        logger.info(f"Importing {len(materials_data)} materials from dictionary")
        
        for material_data in materials_data:
            try:
                material_info = MaterialInfo.from_dict(material_data)
                self.thermal_info.get_materials_mgr().add_material(material_info)
                logger.debug(f"Imported material: {material_info.name}")
            except Exception as e:
                logger.error(f"Failed to import material: {e}")
                raise MaterialParsingError(f"Material import failed: {e}")

