"""
求解器转换器
负责设置COMSOL求解器
"""

from typing import Any, Dict, List, Optional
from loguru import logger


class SolverConverter:
    """求解器转换器"""
    
    def __init__(self):
        """初始化求解器转换器"""
        logger.debug("SolverConverter initialized")
    
    def setup_solver(self, model: Any, thermal_info: Any, solver_parameters: Optional[Dict] = None) -> Any:
        """
        设置COMSOL求解器
        
        Args:
            model: COMSOL模型对象
            thermal_info: 热分析信息对象
            solver_parameters: 求解器参数
            
        Returns:
            Any: 求解器对象
        """
        logger.debug("Setting up COMSOL solver")
        
        try:
            # 获取求解器管理器
            solvers = model.sol()
            
            # 设置求解器参数
            if solver_parameters:
                self._setup_solver_parameters(solvers, solver_parameters)
            else:
                self._setup_default_solver_parameters(solvers)
            
            # 创建求解器特征
            solver = self._create_solver_features(solvers, thermal_info)
            
            # 设置求解器配置
            self._configure_solver(solver, thermal_info)
            
            logger.info("COMSOL solver setup completed")
            return solver
            
        except Exception as e:
            logger.error(f"Failed to setup COMSOL solver: {e}")
            return None
    
    def _setup_solver_parameters(self, solvers: Any, solver_parameters: Dict) -> None:
        """
        设置求解器参数
        
        Args:
            solvers: 求解器管理器
            solver_parameters: 求解器参数字典
        """
        try:
            # 设置全局求解器参数
            if 'relative_tolerance' in solver_parameters:
                solvers.set("reltol", str(solver_parameters['relative_tolerance']))
            
            if 'absolute_tolerance' in solver_parameters:
                solvers.set("abstol", str(solver_parameters['absolute_tolerance']))
            
            if 'max_iterations' in solver_parameters:
                solvers.set("maxiter", str(solver_parameters['max_iterations']))
            
            if 'solver_type' in solver_parameters:
                solvers.set("solver", solver_parameters['solver_type'])
            
            logger.debug("Solver parameters set successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup solver parameters: {e}")
    
    def _setup_default_solver_parameters(self, solvers: Any) -> None:
        """
        设置默认求解器参数
        
        Args:
            solvers: 求解器管理器
        """
        try:
            # 设置默认参数
            solvers.set("reltol", "1e-6")
            solvers.set("abstol", "1e-8")
            solvers.set("maxiter", "100")
            solvers.set("solver", "pardiso")
            
            logger.debug("Default solver parameters set")
            
        except Exception as e:
            logger.error(f"Failed to setup default solver parameters: {e}")
    
    def _create_solver_features(self, solvers: Any, thermal_info: Any) -> Any:
        """
        创建求解器特征
        
        Args:
            solvers: 求解器管理器
            thermal_info: 热分析信息对象
            
        Returns:
            Any: 求解器对象
        """
        try:
            # 创建稳态求解器
            solver = solvers.create("Study1", "Study")
            
            # 创建求解步骤
            step = solver.feature().create("Step1", "Stationary")
            
            # 设置求解步骤参数
            step.set("activate", "on")
            step.set("usesol", "init")
            
            logger.debug("Solver features created successfully")
            return solver
            
        except Exception as e:
            logger.error(f"Failed to create solver features: {e}")
            return None
    
    def _configure_solver(self, solver: Any, thermal_info: Any) -> None:
        """
        配置求解器
        
        Args:
            solver: 求解器对象
            thermal_info: 热分析信息对象
        """
        try:
            # 配置求解器设置
            self._setup_solver_settings(solver, thermal_info)
            
            # 配置求解器选项
            self._setup_solver_options(solver, thermal_info)
            
            # 配置输出设置
            self._setup_output_settings(solver, thermal_info)
            
        except Exception as e:
            logger.error(f"Failed to configure solver: {e}")
    
    def _setup_solver_settings(self, solver: Any, thermal_info: Any) -> None:
        """
        设置求解器设置
        
        Args:
            solver: 求解器对象
            thermal_info: 热分析信息对象
        """
        try:
            # 获取求解步骤
            step = solver.feature("Step1")
            
            # 设置求解器类型
            step.set("solvertype", "Direct")
            
            # 设置求解器
            step.set("solver", "pardiso")
            
            # 设置收敛标准
            step.set("convergence", "strict")
            
            # 设置最大迭代次数
            if hasattr(thermal_info, 'solver_parameters') and 'max_iterations' in thermal_info.solver_parameters:
                max_iter = thermal_info.solver_parameters['max_iterations']
                step.set("maxiter", str(max_iter))
            else:
                step.set("maxiter", "100")
            
            # 设置容差
            if hasattr(thermal_info, 'solver_parameters') and 'relative_tolerance' in thermal_info.solver_parameters:
                rel_tol = thermal_info.solver_parameters['relative_tolerance']
                step.set("reltol", str(rel_tol))
            else:
                step.set("reltol", "1e-6")
            
            logger.debug("Solver settings configured")
            
        except Exception as e:
            logger.error(f"Failed to setup solver settings: {e}")
    
    def _setup_solver_options(self, solver: Any, thermal_info: Any) -> None:
        """
        设置求解器选项
        
        Args:
            solver: 求解器对象
            thermal_info: 热分析信息对象
        """
        try:
            # 获取求解步骤
            step = solver.feature("Step1")
            
            # 设置求解器选项
            step.set("usesol", "init")
            step.set("notsolmethod", "auto")
            step.set("notsol", "auto")
            step.set("pardisomaxthrds", "0")
            step.set("pardisomtr", "auto")
            step.set("pardisopivtol", "0.001")
            step.set("pardisopivtolmax", "0.999999999")
            step.set("pardisosym", "auto")
            step.set("pardisoref", "auto")
            step.set("pardisoadaptiv", "auto")
            step.set("pardisoperf", "auto")
            step.set("pardisomemory", "auto")
            step.set("pardisocorefactor", "auto")
            
            logger.debug("Solver options configured")
            
        except Exception as e:
            logger.error(f"Failed to setup solver options: {e}")
    
    def _setup_output_settings(self, solver: Any, thermal_info: Any) -> None:
        """
        设置输出设置
        
        Args:
            solver: 求解器对象
            thermal_info: 热分析信息对象
        """
        try:
            # 获取求解步骤
            step = solver.feature("Step1")
            
            # 设置输出设置
            step.set("out", "on")
            step.set("outref", "hide")
            step.set("plot", "on")
            step.set("plotsel", "all")
            step.set("plotgroup", "hide")
            step.set("plotmethod", "auto")
            
            logger.debug("Output settings configured")
            
        except Exception as e:
            logger.error(f"Failed to setup output settings: {e}")
    
    def setup_time_dependent_solver(self, solver: Any, thermal_info: Any) -> None:
        """
        设置时间相关求解器
        
        Args:
            solver: 求解器对象
            thermal_info: 热分析信息对象
        """
        try:
            # 检查是否需要时间相关求解
            if hasattr(thermal_info, 'parameters') and 'transient' in thermal_info.parameters:
                transient = thermal_info.parameters['transient']
                
                if transient.get('enabled', False):
                    # 创建时间相关求解步骤
                    time_step = solver.feature().create("TimeStep1", "Time")
                    
                    # 设置时间范围
                    if 'start_time' in transient:
                        time_step.set("tlist", str(transient['start_time']))
                    
                    if 'end_time' in transient:
                        time_step.set("tlist", f"{transient.get('start_time', 0)}, {transient['end_time']}")
                    
                    if 'time_step' in transient:
                        time_step.set("tlist", f"range({transient.get('start_time', 0)},{transient['time_step']},{transient['end_time']})")
                    
                    # 设置求解器类型
                    time_step.set("solvertype", "Direct")
                    time_step.set("solver", "pardiso")
                    
                    logger.debug("Time-dependent solver configured")
                    
        except Exception as e:
            logger.error(f"Failed to setup time-dependent solver: {e}")
    
    def setup_parametric_solver(self, solver: Any, thermal_info: Any) -> None:
        """
        设置参数化求解器
        
        Args:
            solver: 求解器对象
            thermal_info: 热分析信息对象
        """
        try:
            # 检查是否有参数化设置
            if hasattr(thermal_info, 'parameters') and 'parametric' in thermal_info.parameters:
                parametric = thermal_info.parameters['parametric']
                
                if parametric.get('enabled', False):
                    # 创建参数化求解步骤
                    param_step = solver.feature().create("ParamStep1", "Parametric")
                    
                    # 设置参数
                    if 'parameters' in parametric:
                        param_list = []
                        for param in parametric['parameters']:
                            if 'name' in param and 'values' in param:
                                param_list.append(f"{param['name']}={param['values']}")
                        
                        if param_list:
                            param_step.set("pname", param_list)
                    
                    # 设置求解器
                    param_step.set("solvertype", "Direct")
                    param_step.set("solver", "pardiso")
                    
                    logger.debug("Parametric solver configured")
                    
        except Exception as e:
            logger.error(f"Failed to setup parametric solver: {e}")
    
    def setup_multiphysics_solver(self, solver: Any, thermal_info: Any) -> None:
        """
        设置多物理场求解器
        
        Args:
            solver: 求解器对象
            thermal_info: 热分析信息对象
        """
        try:
            # 检查是否需要多物理场求解
            if hasattr(thermal_info, 'parameters') and 'multiphysics' in thermal_info.parameters:
                multiphysics = thermal_info.parameters['multiphysics']
                
                if multiphysics.get('enabled', False):
                    # 创建多物理场求解步骤
                    multi_step = solver.feature().create("MultiStep1", "Stationary")
                    
                    # 设置物理场
                    if 'physics' in multiphysics:
                        physics_list = []
                        for physics in multiphysics['physics']:
                            physics_list.append(physics)
                        
                        if physics_list:
                            multi_step.set("physics", physics_list)
                    
                    # 设置求解器
                    multi_step.set("solvertype", "Direct")
                    multi_step.set("solver", "pardiso")
                    
                    logger.debug("Multiphysics solver configured")
                    
        except Exception as e:
            logger.error(f"Failed to setup multiphysics solver: {e}")
    
    def run_solver(self, solver: Any) -> bool:
        """
        运行求解器
        
        Args:
            solver: 求解器对象
            
        Returns:
            bool: 求解是否成功
        """
        try:
            logger.info("Starting solver execution")
            
            # 运行求解器
            solver.run()
            
            logger.info("Solver execution completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Solver execution failed: {e}")
            return False
    
    def validate_solver_setup(self, solver: Any) -> bool:
        """
        验证求解器设置
        
        Args:
            solver: 求解器对象
            
        Returns:
            bool: 验证是否通过
        """
        try:
            if not solver:
                logger.error("Solver object is None")
                return False
            
            # 检查必要的特征
            required_features = ["Step1"]
            for feature_name in required_features:
                if not solver.feature(feature_name):
                    logger.error(f"Missing required solver feature: {feature_name}")
                    return False
            
            logger.info("Solver setup validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Solver setup validation failed: {e}")
            return False
    
    def get_solver_status(self, solver: Any) -> Dict:
        """
        获取求解器状态
        
        Args:
            solver: 求解器对象
            
        Returns:
            Dict: 求解器状态信息
        """
        try:
            if not solver:
                return {}
            
            # 获取求解器信息
            solver_info = solver.info()
            if not solver_info:
                return {}
            
            return {
                'status': solver_info.get("status", "unknown"),
                'progress': solver_info.get("progress", 0),
                'message': solver_info.get("message", ""),
                'error': solver_info.get("error", "")
            }
            
        except Exception as e:
            logger.error(f"Failed to get solver status: {e}")
            return {}

