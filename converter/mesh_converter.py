"""
网格转换器
负责生成COMSOL网格
"""

from typing import Any, Dict, List, Optional
from loguru import logger


class MeshConverter:
    """网格转换器"""
    
    def __init__(self):
        """初始化网格转换器"""
        logger.debug("MeshConverter initialized")
    
    def generate_mesh(self, model: Any, thermal_info: Any, mesh_parameters: Optional[Dict] = None) -> Any:
        """
        生成COMSOL网格
        
        Args:
            model: COMSOL模型对象
            thermal_info: 热分析信息对象
            mesh_parameters: 网格参数
            
        Returns:
            Any: 网格对象
        """
        logger.debug("Generating COMSOL mesh")
        
        try:
            # 获取网格管理器
            mesh = model.mesh()
            
            # 设置网格参数
            if mesh_parameters:
                self._setup_mesh_parameters(mesh, mesh_parameters)
            else:
                self._setup_default_mesh_parameters(mesh)
            
            # 创建网格特征
            self._create_mesh_features(mesh, thermal_info)
            
            # 生成网格
            mesh.run()
            
            logger.info("COMSOL mesh generation completed")
            return mesh
            
        except Exception as e:
            logger.error(f"Failed to generate COMSOL mesh: {e}")
            return None
    
    def _setup_mesh_parameters(self, mesh: Any, mesh_parameters: Dict) -> None:
        """
        设置网格参数
        
        Args:
            mesh: 网格对象
            mesh_parameters: 网格参数字典
        """
        try:
            # 设置全局网格参数
            if 'element_size' in mesh_parameters:
                mesh.set("elementSize", mesh_parameters['element_size'])
            
            if 'min_element_size' in mesh_parameters:
                mesh.set("minElementSize", mesh_parameters['min_element_size'])
            
            if 'max_element_size' in mesh_parameters:
                mesh.set("maxElementSize", mesh_parameters['max_element_size'])
            
            if 'element_quality' in mesh_parameters:
                mesh.set("elementQuality", mesh_parameters['element_quality'])
            
            if 'mesh_algorithm' in mesh_parameters:
                mesh.set("algorithm", mesh_parameters['mesh_algorithm'])
            
            logger.debug("Mesh parameters set successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup mesh parameters: {e}")
    
    def _setup_default_mesh_parameters(self, mesh: Any) -> None:
        """
        设置默认网格参数
        
        Args:
            mesh: 网格对象
        """
        try:
            # 设置默认参数
            mesh.set("elementSize", "normal")
            mesh.set("minElementSize", "0.001")
            mesh.set("maxElementSize", "0.1")
            mesh.set("elementQuality", "0.3")
            mesh.set("algorithm", "free")
            
            logger.debug("Default mesh parameters set")
            
        except Exception as e:
            logger.error(f"Failed to setup default mesh parameters: {e}")
    
    def _create_mesh_features(self, mesh: Any, thermal_info: Any) -> None:
        """
        创建网格特征
        
        Args:
            mesh: 网格对象
            thermal_info: 热分析信息对象
        """
        try:
            # 创建自由四面体网格
            self._create_free_tetrahedral_mesh(mesh)
            
            # 创建边界层网格（如果需要）
            self._create_boundary_layer_mesh(mesh, thermal_info)
            
            # 创建尺寸函数（如果需要）
            self._create_size_functions(mesh, thermal_info)
            
            # 创建网格控制
            self._create_mesh_controls(mesh, thermal_info)
            
        except Exception as e:
            logger.error(f"Failed to create mesh features: {e}")
    
    def _create_free_tetrahedral_mesh(self, mesh: Any) -> None:
        """
        创建自由四面体网格
        
        Args:
            mesh: 网格对象
        """
        try:
            # 创建自由四面体网格特征
            free_tet = mesh.feature().create("FreeTetrahedral1", "FreeTetrahedral")
            
            # 设置选择
            free_tet.set("selection", "all")
            
            # 设置网格尺寸
            free_tet.set("elementSize", "normal")
            
            logger.debug("Free tetrahedral mesh feature created")
            
        except Exception as e:
            logger.error(f"Failed to create free tetrahedral mesh: {e}")
    
    def _create_boundary_layer_mesh(self, mesh: Any, thermal_info: Any) -> None:
        """
        创建边界层网格
        
        Args:
            mesh: 网格对象
            thermal_info: 热分析信息对象
        """
        try:
            # 检查是否需要边界层网格
            if hasattr(thermal_info, 'parameters') and 'boundary_layer' in thermal_info.parameters:
                boundary_layer = thermal_info.parameters['boundary_layer']
                
                if boundary_layer.get('enabled', False):
                    # 创建边界层网格特征
                    bl_mesh = mesh.feature().create("BoundaryLayer1", "BoundaryLayer")
                    
                    # 设置选择
                    if 'surfaces' in boundary_layer:
                        bl_mesh.set("selection", boundary_layer['surfaces'])
                    
                    # 设置边界层参数
                    if 'thickness' in boundary_layer:
                        bl_mesh.set("hwall", str(boundary_layer['thickness']))
                    
                    if 'growth_rate' in boundary_layer:
                        bl_mesh.set("hgrad", str(boundary_layer['growth_rate']))
                    
                    if 'layers' in boundary_layer:
                        bl_mesh.set("nlayers", str(boundary_layer['layers']))
                    
                    logger.debug("Boundary layer mesh feature created")
                    
        except Exception as e:
            logger.error(f"Failed to create boundary layer mesh: {e}")
    
    def _create_size_functions(self, mesh: Any, thermal_info: Any) -> None:
        """
        创建尺寸函数
        
        Args:
            mesh: 网格对象
            thermal_info: 热分析信息对象
        """
        try:
            # 检查是否有尺寸函数定义
            if hasattr(thermal_info, 'mesh_parameters') and 'size_functions' in thermal_info.mesh_parameters:
                size_functions = thermal_info.mesh_parameters['size_functions']
                
                for i, size_func in enumerate(size_functions):
                    # 创建尺寸函数
                    func = mesh.feature().create(f"SizeFunction{i+1}", "Size")
                    
                    # 设置函数类型
                    if 'type' in size_func:
                        func.set("custom", size_func['type'])
                    
                    # 设置表达式
                    if 'expression' in size_func:
                        func.set("expr", size_func['expression'])
                    
                    # 设置选择
                    if 'selection' in size_func:
                        func.set("selection", size_func['selection'])
                    
                    logger.debug(f"Size function {i+1} created")
                    
        except Exception as e:
            logger.error(f"Failed to create size functions: {e}")
    
    def _create_mesh_controls(self, mesh: Any, thermal_info: Any) -> None:
        """
        创建网格控制
        
        Args:
            mesh: 网格对象
            thermal_info: 热分析信息对象
        """
        try:
            # 检查是否有网格控制定义
            if hasattr(thermal_info, 'mesh_parameters') and 'mesh_controls' in thermal_info.mesh_parameters:
                mesh_controls = thermal_info.mesh_parameters['mesh_controls']
                
                for i, control in enumerate(mesh_controls):
                    # 创建网格控制
                    mesh_control = mesh.feature().create(f"MeshControl{i+1}", "Size")
                    
                    # 设置控制类型
                    if 'type' in control:
                        mesh_control.set("custom", control['type'])
                    
                    # 设置参数
                    if 'parameters' in control:
                        for param_name, param_value in control['parameters'].items():
                            mesh_control.set(param_name, str(param_value))
                    
                    # 设置选择
                    if 'selection' in control:
                        mesh_control.set("selection", control['selection'])
                    
                    logger.debug(f"Mesh control {i+1} created")
                    
        except Exception as e:
            logger.error(f"Failed to create mesh controls: {e}")
    
    def setup_mesh_refinement(self, mesh: Any, refinement_areas: List[Dict]) -> None:
        """
        设置网格细化
        
        Args:
            mesh: 网格对象
            refinement_areas: 细化区域列表
        """
        try:
            for i, refinement in enumerate(refinement_areas):
                # 创建细化特征
                refine = mesh.feature().create(f"Refine{i+1}", "Refine")
                
                # 设置选择
                if 'selection' in refinement:
                    refine.set("selection", refinement['selection'])
                
                # 设置细化级别
                if 'level' in refinement:
                    refine.set("level", str(refinement['level']))
                
                logger.debug(f"Mesh refinement {i+1} created")
                
        except Exception as e:
            logger.error(f"Failed to setup mesh refinement: {e}")
    
    def setup_mesh_import(self, mesh: Any, import_file: str) -> None:
        """
        设置网格导入
        
        Args:
            mesh: 网格对象
            import_file: 导入文件路径
        """
        try:
            # 创建导入特征
            import_feature = mesh.feature().create("Import1", "Import")
            
            # 设置文件路径
            import_feature.set("filename", import_file)
            
            # 设置文件格式
            import_feature.set("filetype", "auto")
            
            logger.debug(f"Mesh import feature created for file: {import_file}")
            
        except Exception as e:
            logger.error(f"Failed to setup mesh import: {e}")
    
    def validate_mesh(self, mesh: Any) -> bool:
        """
        验证网格
        
        Args:
            mesh: 网格对象
            
        Returns:
            bool: 验证是否通过
        """
        try:
            if not mesh:
                logger.error("Mesh object is None")
                return False
            
            # 检查网格统计信息
            mesh_stats = mesh.stat()
            
            if not mesh_stats:
                logger.error("Failed to get mesh statistics")
                return False
            
            # 检查网格质量
            element_quality = mesh_stats.get("quality", 0)
            if element_quality < 0.1:
                logger.warning(f"Low mesh quality: {element_quality}")
            
            # 检查网格数量
            num_elements = mesh_stats.get("elements", 0)
            if num_elements == 0:
                logger.error("No mesh elements generated")
                return False
            
            logger.info(f"Mesh validation passed. Elements: {num_elements}, Quality: {element_quality}")
            return True
            
        except Exception as e:
            logger.error(f"Mesh validation failed: {e}")
            return False
    
    def get_mesh_statistics(self, mesh: Any) -> Dict:
        """
        获取网格统计信息
        
        Args:
            mesh: 网格对象
            
        Returns:
            Dict: 网格统计信息
        """
        try:
            if not mesh:
                return {}
            
            mesh_stats = mesh.stat()
            if not mesh_stats:
                return {}
            
            return {
                'elements': mesh_stats.get("elements", 0),
                'nodes': mesh_stats.get("nodes", 0),
                'quality': mesh_stats.get("quality", 0),
                'min_element_size': mesh_stats.get("minElementSize", 0),
                'max_element_size': mesh_stats.get("maxElementSize", 0)
            }
            
        except Exception as e:
            logger.error(f"Failed to get mesh statistics: {e}")
            return {}

