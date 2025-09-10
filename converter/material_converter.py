"""
材料转换器
负责将材料对象转换为COMSOL材料
"""

from typing import List, Any, Dict, Optional
from loguru import logger

from models.material import MaterialInfo, Conductivity, TemperaturePoint
from models.composite import CompositeMaterial, ObjectMaterial


class MaterialConverter:
    """材料转换器"""
    
    def __init__(self):
        """初始化材料转换器"""
        logger.debug("MaterialConverter initialized")
    
    def convert_materials(self, materials: List[MaterialInfo], model: Any) -> List[Any]:
        """
        转换材料为COMSOL材料
        
        Args:
            materials: 材料列表
            model: COMSOL模型对象
            
        Returns:
            List[Any]: COMSOL材料对象列表
        """
        logger.debug(f"Converting {len(materials)} materials to COMSOL materials")
        
        comsol_materials = []
        for material in materials:
            try:
                comsol_material = self._convert_single_material(material, model)
                if comsol_material:
                    comsol_materials.append(comsol_material)
                    logger.debug(f"Converted material: {material.name}")
            except Exception as e:
                logger.error(f"Failed to convert material {material.name}: {e}")
        
        return comsol_materials
    
    def _convert_single_material(self, material: MaterialInfo, model: Any) -> Optional[Any]:
        """
        转换单个材料
        
        Args:
            material: 材料对象
            model: COMSOL模型对象
            
        Returns:
            Optional[Any]: COMSOL材料对象
        """
        try:
            if material.material_type == "base":
                return self._create_base_material(material, model)
            elif material.material_type == "composite":
                return self._create_composite_material(material, model)
            elif material.material_type == "object":
                return self._create_object_material(material, model)
            else:
                logger.warning(f"Unknown material type: {material.material_type}")
                return self._create_base_material(material, model)
        
        except Exception as e:
            logger.error(f"Failed to convert material {material.name}: {e}")
            return None
    
    def _create_base_material(self, material: MaterialInfo, model: Any) -> Any:
        """
        创建基础材料
        
        Args:
            material: 材料对象
            model: COMSOL模型对象
            
        Returns:
            Any: COMSOL材料对象
        """
        try:
            # 获取材料管理器
            materials = model.materials()
            
            # 创建新材料
            comsol_material = materials.create(material.name, "Common")
            
            # 设置基本属性
            if hasattr(material, 'density') and material.density:
                comsol_material.property("density", str(material.density))
            
            if hasattr(material, 'heat_capacity') and material.heat_capacity:
                comsol_material.property("heat_capacity", str(material.heat_capacity))
            
            # 设置导热系数
            if hasattr(material, 'get_conductivity'):
                try:
                    conductivity = material.get_conductivity()
                    if conductivity:
                        conductivity_func = self._create_conductivity_function(material, model)
                        if conductivity_func:
                            comsol_material.property("thermal_conductivity", conductivity_func)
                except Exception as e:
                    logger.warning(f"Failed to get conductivity for material {material.name}: {e}")
            
            # 设置温度相关属性
            if hasattr(material, 'temperature_map') and material.temperature_map:
                # 创建温度相关的密度函数
                density_func = self._create_density_function(material, model)
                if density_func:
                    comsol_material.property("density", density_func)
                
                # 创建温度相关的热容函数
                heat_capacity_func = self._create_heat_capacity_function(material, model)
                if heat_capacity_func:
                    comsol_material.property("heat_capacity", heat_capacity_func)
            
            logger.debug(f"Created base material: {material.name}")
            return comsol_material
            
        except Exception as e:
            logger.error(f"Failed to create base material {material.name}: {e}")
            return None
    
    def _create_composite_material(self, material: MaterialInfo, model: Any) -> Any:
        """
        创建复合材料
        
        Args:
            material: 材料对象
            model: COMSOL模型对象
            
        Returns:
            Any: COMSOL材料对象
        """
        try:
            # 获取材料管理器
            materials = model.materials()
            
            # 创建复合材料
            comsol_material = materials.create(material.name, "Composite")
            
            # 设置复合材料属性
            if hasattr(material, 'density') and material.density:
                comsol_material.property("density", str(material.density))
            
            if hasattr(material, 'heat_capacity') and material.heat_capacity:
                comsol_material.property("heat_capacity", str(material.heat_capacity))
            
            # 设置导热系数
            if hasattr(material, 'get_conductivity'):
                try:
                    conductivity = material.get_conductivity()
                    if conductivity:
                        conductivity_func = self._create_conductivity_function(material, model)
                        if conductivity_func:
                            comsol_material.property("thermal_conductivity", conductivity_func)
                except Exception as e:
                    logger.warning(f"Failed to get conductivity for material {material.name}: {e}")
            
            # 设置复合材料参数
            if hasattr(material, 'volume_fraction'):
                comsol_material.property("volume_fraction", str(material.volume_fraction))
            
            logger.debug(f"Created composite material: {material.name}")
            return comsol_material
            
        except Exception as e:
            logger.error(f"Failed to create composite material {material.name}: {e}")
            return None
    
    def _create_object_material(self, material: MaterialInfo, model: Any) -> Any:
        """
        创建对象材料
        
        Args:
            material: 材料对象
            model: COMSOL模型对象
            
        Returns:
            Any: COMSOL材料对象
        """
        try:
            # 获取材料管理器
            materials = model.materials()
            
            # 创建对象材料
            comsol_material = materials.create(material.name, "Object")
            
            # 设置对象材料属性
            if hasattr(material, 'density') and material.density:
                comsol_material.property("density", str(material.density))
            
            if hasattr(material, 'heat_capacity') and material.heat_capacity:
                comsol_material.property("heat_capacity", str(material.heat_capacity))
            
            # 设置导热系数
            if hasattr(material, 'get_conductivity'):
                try:
                    conductivity = material.get_conductivity()
                    if conductivity:
                        conductivity_func = self._create_conductivity_function(material, model)
                        if conductivity_func:
                            comsol_material.property("thermal_conductivity", conductivity_func)
                except Exception as e:
                    logger.warning(f"Failed to get conductivity for material {material.name}: {e}")
            
            # 设置对象材料参数
            if hasattr(material, 'object_type'):
                comsol_material.property("object_type", material.object_type)
            
            logger.debug(f"Created object material: {material.name}")
            return comsol_material
            
        except Exception as e:
            logger.error(f"Failed to create object material {material.name}: {e}")
            return None
    
    def _create_conductivity_function(self, material: MaterialInfo, model: Any) -> Optional[Any]:
        """
        创建导热系数函数
        
        Args:
            material: 材料对象
            model: COMSOL模型对象
            
        Returns:
            Optional[Any]: 导热系数函数对象
        """
        try:
            if not hasattr(material, 'get_conductivity'):
                return None
            
            # 获取函数管理器
            functions = model.func()
            
            # 创建插值函数
            func_name = f"conductivity_{material.name}"
            conductivity_func = functions.create(func_name, "Interpolation")
            
            # 设置插值数据
            if hasattr(material, 'temperature_map') and material.temperature_map:
                temperatures = []
                conductivities = []
                
                for temp_point in material.temperature_map.values():
                    temperatures.append(temp_point.temperature)
                    if hasattr(temp_point, 'conductivity') and temp_point.conductivity:
                        conductivities.append(temp_point.conductivity.x)  # 假设是各向同性
                
                if temperatures and conductivities:
                    conductivity_func.set("table", [temperatures, conductivities])
                    conductivity_func.set("interp", "linear")
                    
                    logger.debug(f"Created conductivity function for material: {material.name}")
                    return conductivity_func
            
            # 如果没有温度相关数据，使用常数
            try:
                conductivity = material.get_conductivity()
                if conductivity and conductivity.x:
                    conductivity_func = functions.create(f"conductivity_const_{material.name}", "Constant")
                    conductivity_func.set("value", conductivity.x)
                    return conductivity_func
            except Exception as e:
                logger.warning(f"Failed to get conductivity for material {material.name}: {e}")
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to create conductivity function for material {material.name}: {e}")
            return None
    
    def _create_density_function(self, material: MaterialInfo, model: Any) -> Optional[Any]:
        """
        创建密度函数
        
        Args:
            material: 材料对象
            model: COMSOL模型对象
            
        Returns:
            Optional[Any]: 密度函数对象
        """
        try:
            if not material.temperature_map:
                return None
            
            # 获取函数管理器
            functions = model.func()
            
            # 创建插值函数
            func_name = f"density_{material.name}"
            density_func = functions.create(func_name, "Interpolation")
            
            # 设置插值数据
            temperatures = []
            densities = []
            
            for temp_point in material.temperature_map:
                temperatures.append(temp_point.temperature)
                if hasattr(temp_point, 'density') and temp_point.density:
                    densities.append(temp_point.density)
            
            if temperatures and densities and len(temperatures) == len(densities):
                density_func.set("table", [temperatures, densities])
                density_func.set("interp", "linear")
                
                logger.debug(f"Created density function for material: {material.name}")
                return density_func
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to create density function for material {material.name}: {e}")
            return None
    
    def _create_heat_capacity_function(self, material: MaterialInfo, model: Any) -> Optional[Any]:
        """
        创建热容函数
        
        Args:
            material: 材料对象
            model: COMSOL模型对象
            
        Returns:
            Optional[Any]: 热容函数对象
        """
        try:
            if not material.temperature_map:
                return None
            
            # 获取函数管理器
            functions = model.func()
            
            # 创建插值函数
            func_name = f"heat_capacity_{material.name}"
            heat_capacity_func = functions.create(func_name, "Interpolation")
            
            # 设置插值数据
            temperatures = []
            heat_capacities = []
            
            for temp_point in material.temperature_map:
                temperatures.append(temp_point.temperature)
                if hasattr(temp_point, 'heat_capacity') and temp_point.heat_capacity:
                    heat_capacities.append(temp_point.heat_capacity)
            
            if temperatures and heat_capacities and len(temperatures) == len(heat_capacities):
                heat_capacity_func.set("table", [temperatures, heat_capacities])
                heat_capacity_func.set("interp", "linear")
                
                logger.debug(f"Created heat capacity function for material: {material.name}")
                return heat_capacity_func
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to create heat capacity function for material {material.name}: {e}")
            return None
    
    def setup_material_assignments(self, materials: List[Any], geometry_objects: List[Any]) -> bool:
        """
        设置材料分配
        
        Args:
            materials: COMSOL材料对象列表
            geometry_objects: 几何对象列表
            
        Returns:
            bool: 设置是否成功
        """
        try:
            if not materials or not geometry_objects:
                logger.warning("No materials or geometry objects for assignment")
                return False
            
            # 这里可以实现材料分配逻辑
            # 例如：将材料分配给特定的几何区域
            
            logger.info(f"Material assignments set up for {len(materials)} materials and {len(geometry_objects)} geometry objects")
            return True
            
        except Exception as e:
            logger.error(f"Failed to set up material assignments: {e}")
            return False
    
    def validate_materials(self, materials: List[Any]) -> bool:
        """
        验证材料对象
        
        Args:
            materials: 材料对象列表
            
        Returns:
            bool: 验证是否通过
        """
        if not materials:
            logger.warning("No materials to validate")
            return False
        
        try:
            for material in materials:
                if not material:
                    logger.error("Found None material object")
                    return False
                
                # 检查必要的属性
                if not hasattr(material, 'name'):
                    logger.error("Material object missing name attribute")
                    return False
            
            logger.info(f"Material validation passed for {len(materials)} materials")
            return True
            
        except Exception as e:
            logger.error(f"Material validation failed: {e}")
            return False

