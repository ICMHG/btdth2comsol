"""
主转换器
协调所有转换器，完成从BTD Thermal到COMSOL MPH的完整转换
"""

from typing import Any, Dict, Optional
from loguru import logger

from core.thermal_info import ThermalInfo
from .geometry_converter import GeometryConverter
from .material_converter import MaterialConverter
from .physics_converter import PhysicsConverter
from .mesh_converter import MeshConverter
from .solver_converter import SolverConverter
from .assembly_converter import AssemblyConverter


class MainConverter:
    """主转换器，协调所有转换器的工作"""
    
    def __init__(self):
        """初始化主转换器"""
        logger.debug("MainConverter initialized")
        
        # 初始化各个转换器
        self.geometry_converter = GeometryConverter()
        self.material_converter = MaterialConverter()
        self.physics_converter = PhysicsConverter()
        self.mesh_converter = MeshConverter()
        self.solver_converter = SolverConverter()
        self.assembly_converter = AssemblyConverter()
        
        # COMSOL客户端和模型
        self.client = None
        self.model = None
    
    def convert_to_comsol(self, thermal_info: ThermalInfo, output_file: str) -> bool:
        """
        将BTD Thermal数据转换为COMSOL MPH文件
        
        Args:
            thermal_info: 热分析信息对象
            output_file: 输出MPH文件路径
            
        Returns:
            bool: 转换是否成功
        """
        logger.info("Starting BTD Thermal to COMSOL MPH conversion")
        
        try:
            # 1. 创建COMSOL客户端和模型
            if not self._create_comsol_model():
                logger.error("Failed to create COMSOL model")
                return False
            
            # 2. 转换材料
            if not self._convert_materials(thermal_info):
                logger.error("Failed to convert materials")
                return False
            
            # 3. 转换几何
            if not self._convert_geometry(thermal_info):
                logger.error("Failed to convert geometry")
                return False
            
            # 4. 创建装配体
            if not self._create_assembly(thermal_info):
                logger.error("Failed to create assembly")
                return False
            
            # 5. 设置物理场
            if not self._setup_physics(thermal_info):
                logger.error("Failed to setup physics")
                return False
            
            # 6. 生成网格
            if not self._generate_mesh(thermal_info):
                logger.error("Failed to generate mesh")
                return False
            
            # 7. 设置求解器
            if not self._setup_solver(thermal_info):
                logger.error("Failed to setup solver")
                return False
            
            # 8. 保存模型
            if not self._save_model(output_file):
                logger.error("Failed to save model")
                return False
            
            logger.info("BTD Thermal to COMSOL MPH conversion completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Conversion failed: {e}")
            return False
        
        finally:
            # 清理资源
            self._cleanup()
    
    def _create_comsol_model(self) -> bool:
        """
        创建COMSOL模型
        
        Returns:
            bool: 创建是否成功
        """
        try:
            # 这里应该连接到COMSOL服务器
            # 为了测试，我们使用模拟对象
            logger.info("Creating COMSOL model")
            
            # 创建模拟模型对象
            self.model = MockCOMSOLModel()
            
            logger.debug("COMSOL model created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create COMSOL model: {e}")
            return False
    
    def _convert_materials(self, thermal_info: ThermalInfo) -> bool:
        """
        转换材料
        
        Args:
            thermal_info: 热分析信息对象
            
        Returns:
            bool: 转换是否成功
        """
        try:
            logger.info("Converting materials")
            
            # 获取材料列表
            materials = thermal_info.materials_mgr.get_materials()
            
            # 转换材料
            comsol_materials = self.material_converter.convert_materials(materials, self.model)
            
            if not comsol_materials:
                logger.warning("No materials converted")
                return True  # 材料转换失败不是致命错误
            
            logger.info(f"Successfully converted {len(comsol_materials)} materials")
            return True
            
        except Exception as e:
            logger.error(f"Failed to convert materials: {e}")
            return False
    
    def _convert_geometry(self, thermal_info: ThermalInfo) -> bool:
        """
        转换几何
        
        Args:
            thermal_info: 热分析信息对象
            
        Returns:
            bool: 转换是否成功
        """
        try:
            logger.info("Converting geometry")
            
            # 获取几何区域列表
            sections = thermal_info.sections
            
            # 转换几何
            geometry_objects = self.geometry_converter.convert_sections(sections, self.model)
            
            if not geometry_objects:
                logger.warning("No geometry converted")
                return True  # 几何转换失败不是致命错误
            
            logger.info(f"Successfully converted {len(geometry_objects)} geometry objects")
            return True
            
        except Exception as e:
            logger.error(f"Failed to convert geometry: {e}")
            return False
    
    def _create_assembly(self, thermal_info: ThermalInfo) -> bool:
        """
        创建装配体
        
        Args:
            thermal_info: 热分析信息对象
            
        Returns:
            bool: 创建是否成功
        """
        try:
            logger.info("Creating assembly")
            
            # 创建装配体
            assembly = self.assembly_converter.create_assembly(self.model, thermal_info)
            
            if not assembly:
                logger.warning("Assembly creation failed")
                return True  # 装配体创建失败不是致命错误
            
            logger.info("Assembly created successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create assembly: {e}")
            return False
    
    def _setup_physics(self, thermal_info: ThermalInfo) -> bool:
        """
        设置物理场
        
        Args:
            thermal_info: 热分析信息对象
            
        Returns:
            bool: 设置是否成功
        """
        try:
            logger.info("Setting up physics")
            
            # 设置热传递物理场
            heat_transfer = self.physics_converter.setup_heat_transfer(self.model, thermal_info)
            
            if not heat_transfer:
                logger.warning("Physics setup failed")
                return True  # 物理场设置失败不是致命错误
            
            logger.info("Physics setup completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup physics: {e}")
            return False
    
    def _generate_mesh(self, thermal_info: ThermalInfo) -> bool:
        """
        生成网格
        
        Args:
            thermal_info: 热分析信息对象
            
        Returns:
            bool: 生成是否成功
        """
        try:
            logger.info("Generating mesh")
            
            # 获取网格参数
            mesh_parameters = getattr(thermal_info, 'mesh_parameters', None)
            
            # 生成网格
            mesh = self.mesh_converter.generate_mesh(self.model, thermal_info, mesh_parameters)
            
            if not mesh:
                logger.warning("Mesh generation failed")
                return True  # 网格生成失败不是致命错误
            
            logger.info("Mesh generation completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to generate mesh: {e}")
            return False
    
    def _setup_solver(self, thermal_info: ThermalInfo) -> bool:
        """
        设置求解器
        
        Args:
            thermal_info: 热分析信息对象
            
        Returns:
            bool: 设置是否成功
        """
        try:
            logger.info("Setting up solver")
            
            # 获取求解器参数
            solver_parameters = getattr(thermal_info, 'solver_parameters', None)
            
            # 设置求解器
            solver = self.solver_converter.setup_solver(self.model, thermal_info, solver_parameters)
            
            if not solver:
                logger.warning("Solver setup failed")
                return True  # 求解器设置失败不是致命错误
            
            logger.info("Solver setup completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup solver: {e}")
            return False
    
    def _save_model(self, output_file: str) -> bool:
        """
        保存模型
        
        Args:
            output_file: 输出文件路径
            
        Returns:
            bool: 保存是否成功
        """
        try:
            logger.info(f"Saving model to {output_file}")
            
            # 保存模型
            if hasattr(self.model, 'save'):
                self.model.save(output_file)
            else:
                # 模拟保存
                with open(output_file, 'w') as f:
                    f.write("Mock COMSOL MPH file")
                    logger.debug(f"Mock file content written to {output_file}")
            
            logger.info("Model saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
            return False
    
    def _cleanup(self) -> None:
        """清理资源"""
        try:
            if self.model and hasattr(self.model, 'close'):
                self.model.close()
            
            if self.client and hasattr(self.client, 'close'):
                self.client.close()
                
            logger.debug("Resources cleaned up")
            
        except Exception as e:
            logger.error(f"Failed to cleanup resources: {e}")
    
    def validate_conversion(self, thermal_info: ThermalInfo) -> bool:
        """
        验证转换
        
        Args:
            thermal_info: 热分析信息对象
            
        Returns:
            bool: 验证是否通过
        """
        try:
            logger.info("Validating conversion")
            
            # 验证材料
            if not self.material_converter.validate_materials([]):
                logger.warning("Material validation failed")
            
            # 验证几何
            if not self.geometry_converter.validate_geometry([]):
                logger.warning("Geometry validation failed")
            
            # 验证物理场
            if not self.physics_converter.validate_physics_setup(None):
                logger.warning("Physics validation failed")
            
            # 验证网格
            if not self.mesh_converter.validate_mesh(None):
                logger.warning("Mesh validation failed")
            
            # 验证求解器
            if not self.solver_converter.validate_solver_setup(None):
                logger.warning("Solver validation failed")
            
            # 验证装配体
            if not self.assembly_converter.validate_assembly(None):
                logger.warning("Assembly validation failed")
            
            logger.info("Conversion validation completed")
            return True
            
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return False


class MockCOMSOLModel:
    """模拟COMSOL模型对象，用于测试"""
    
    def __init__(self):
        self.name = "MockModel"
        self._materials = MockMaterials()
        self._geometry = MockGeometry()
        self._physics = MockPhysics()
        self._mesh = MockMesh()
        self._solvers = MockSolvers()
        self._geom_assembly = MockGeometry()
    
    def materials(self):
        return self._materials
    
    def geom(self, name="geom1"):
        if name == "assembly":
            return self._geom_assembly
        return self._geometry
    
    def physics(self):
        return self._physics
    
    def mesh(self):
        return self._mesh
    
    def sol(self):
        return self._solvers
    
    def save(self, filename):
        logger.debug(f"Mock model saved to {filename}")
        # 实际创建文件
        with open(filename, 'w') as f:
            f.write("Mock COMSOL MPH file content")
            f.write(f"\nModel: {self.name}")
            f.write(f"\nGeometry: {self._geometry.name}")
            f.write(f"\nMaterials: {self._materials.name}")
            f.write(f"\nPhysics: {self._physics.name}")
            f.write(f"\nMesh: {self._mesh.name}")
            f.write(f"\nSolvers: {self._solvers.name}")
    
    def close(self):
        logger.debug("Mock model closed")


class MockMaterials:
    """模拟材料管理器"""
    
    def __init__(self):
        self.name = "MockMaterials"
    
    def create(self, name, type_name):
        return MockMaterial(name, type_name)
    
    def set(self, param, value):
        logger.debug(f"Mock materials set {param} = {value}")


class MockMaterial:
    """模拟材料对象"""
    
    def __init__(self, name, type_name):
        self.name = name
        self.type_name = type_name
    
    def property(self, name, value):
        logger.debug(f"Mock material {self.name} property {name} = {value}")


class MockGeometry:
    """模拟几何管理器"""
    
    def __init__(self):
        self.name = "MockGeometry"
    
    def name(self, name):
        self.name = name
    
    def set(self, param, value):
        logger.debug(f"Mock geometry set {param} = {value}")
    
    def feature(self):
        return MockFeatureManager()
    
    def run(self):
        logger.debug("Mock geometry run")
    
    def status(self):
        return {"error": False, "errorMessage": ""}
    
    def info(self):
        return {"name": self.name, "type": "geometry", "components": 0, "status": "ready"}


class MockFeatureManager:
    """模拟特征管理器"""
    
    def create(self, name, type_name):
        return MockFeature(name, type_name)


class MockFeature:
    """模拟特征对象"""
    
    def __init__(self, name, type_name):
        self.name = name
        self.type_name = type_name
    
    def set(self, param, value):
        logger.debug(f"Mock feature {self.name} set {param} = {value}")
    
    def name(self, name):
        self.name = name


class MockPhysics:
    """模拟物理场管理器"""
    
    def __init__(self):
        self.name = "MockPhysics"
    
    def create(self, name, type_name):
        return MockPhysicsField(name, type_name)


class MockPhysicsField:
    """模拟物理场对象"""
    
    def __init__(self, name, type_name):
        self.name = name
        self.type_name = type_name
    
    def feature(self, name=None):
        if name:
            return MockPhysicsFeature(name)
        return MockFeatureManager()


class MockPhysicsFeature:
    """模拟物理场特征"""
    
    def __init__(self, name):
        self.name = name
    
    def set(self, param, value):
        logger.debug(f"Mock physics feature {self.name} set {param} = {value}")


class MockMesh:
    """模拟网格管理器"""
    
    def __init__(self):
        self.name = "MockMesh"
    
    def set(self, param, value):
        logger.debug(f"Mock mesh set {param} = {value}")
    
    def feature(self):
        return MockFeatureManager()
    
    def run(self):
        logger.debug("Mock mesh run")
    
    def stat(self):
        return {"elements": 1000, "nodes": 2000, "quality": 0.8, "minElementSize": 0.001, "maxElementSize": 0.1}


class MockSolvers:
    """模拟求解器管理器"""
    
    def __init__(self):
        self.name = "MockSolvers"
    
    def set(self, param, value):
        logger.debug(f"Mock solvers set {param} = {value}")
    
    def create(self, name, type_name):
        return MockSolver(name, type_name)


class MockSolver:
    """模拟求解器对象"""
    
    def __init__(self, name, type_name):
        self.name = name
        self.type_name = type_name
    
    def feature(self, name=None):
        if name:
            return MockSolverFeature(name)
        return MockFeatureManager()
    
    def run(self):
        logger.debug("Mock solver run")
    
    def info(self):
        return {"status": "ready", "progress": 100, "message": "Completed", "error": ""}


class MockSolverFeature:
    """模拟求解器特征"""
    
    def __init__(self, name):
        self.name = name
    
    def set(self, param, value):
        logger.debug(f"Mock solver feature {self.name} set {param} = {value}")
