"""
PkgDie模型类
对应C++的PkgDie类，管理封装芯片组件
"""

from typing import List, Optional, Dict, Any
from loguru import logger

from .stacked_die import StackedDieSection
from .package_para import PackagePara


class PkgComponent:
    """封装芯片组件类，对应C++的PkgComponent"""
    
    def __init__(self, json_data: Optional[Dict[str, Any]] = None):
        """
        初始化PkgComponent
        
        Args:
            json_data: JSON数据字典
        """
        # 引用标识
        self.ref_des: str = ""
        
        # 模型名称
        self.mdl_name: str = ""
        
        # 附着层
        self.attach_layer: str = ""
        
        # 芯片标识
        self.die: str = ""
        
        # 是否有堆叠芯片
        self.has_stacked_dies: bool = False
        
        # 堆叠芯片列表
        self.stacked_dies: List[StackedDieSection] = []
        
        # 封装参数
        self.package_para: PackagePara = PackagePara()
        
        # 从JSON加载数据
        if json_data:
            self.from_json(json_data)
    
    def get_ref_des(self) -> str:
        """获取引用标识"""
        return self.ref_des
    
    def set_ref_des(self, ref_des: str) -> None:
        """设置引用标识"""
        self.ref_des = ref_des
    
    def get_mdl_name(self) -> str:
        """获取模型名称"""
        return self.mdl_name
    
    def set_mdl_name(self, mdl_name: str) -> None:
        """设置模型名称"""
        self.mdl_name = mdl_name
    
    def get_attach_layer(self) -> str:
        """获取附着层"""
        return self.attach_layer
    
    def set_attach_layer(self, attach_layer: str) -> None:
        """设置附着层"""
        self.attach_layer = attach_layer
    
    def get_die(self) -> str:
        """获取芯片标识"""
        return self.die
    
    def set_die(self, die: str) -> None:
        """设置芯片标识"""
        self.die = die
    
    def get_stacked_dies(self) -> List[StackedDieSection]:
        """获取堆叠芯片列表"""
        return self.stacked_dies
    
    def set_stacked_dies(self, stacked_dies: List[StackedDieSection]) -> None:
        """设置堆叠芯片列表"""
        self.stacked_dies = stacked_dies
    
    def set_has_stacked_dies(self, has: bool) -> None:
        """设置是否有堆叠芯片"""
        self.has_stacked_dies = has
    
    def get_has_stacked_dies(self) -> bool:
        """获取是否有堆叠芯片"""
        return self.has_stacked_dies
    
    def get_package_para(self) -> PackagePara:
        """获取封装参数"""
        return self.package_para
    
    def set_package_para(self, para: PackagePara) -> None:
        """设置封装参数"""
        self.package_para = para
    
    def from_json(self, json_data: Dict[str, Any]) -> None:
        """从JSON数据加载"""
        try:
            self.ref_des = json_data.get("refDes", "")
            self.mdl_name = json_data.get("mdlName", "")
            self.attach_layer = json_data.get("attachLayer", "")
            self.die = json_data.get("die", "")
            self.has_stacked_dies = json_data.get("hasStackedDies", False)
            
            # 加载堆叠芯片
            if "stackedDies" in json_data:
                stacked_dies_data = json_data["stackedDies"]
                for die_data in stacked_dies_data:
                    stacked_die = StackedDieSection(die_data)
                    self.stacked_dies.append(stacked_die)
            
            # 加载封装参数
            if "packagePara" in json_data:
                self.package_para.from_json(json_data["packagePara"])
            
            logger.debug(f"Loaded PkgComponent: {self.mdl_name}")
            
        except Exception as e:
            logger.error(f"Failed to load PkgComponent from JSON: {e}")
            raise
    
    def to_json(self) -> Dict[str, Any]:
        """转换为JSON数据"""
        try:
            data = {
                "refDes": self.ref_des,
                "mdlName": self.mdl_name,
                "attachLayer": self.attach_layer,
                "die": self.die,
                "hasStackedDies": self.has_stacked_dies,
                "stackedDies": [die.to_json() for die in self.stacked_dies],
                "packagePara": self.package_para.to_json()
            }
            return data
            
        except Exception as e:
            logger.error(f"Failed to convert PkgComponent to JSON: {e}")
            raise


class PkgDie:
    """封装芯片类，对应C++的PkgDie"""
    
    def __init__(self):
        """初始化PkgDie"""
        self.components: List[PkgComponent] = []
        logger.debug("PkgDie initialized")
    
    def add_component(self, component: PkgComponent) -> None:
        """添加组件"""
        self.components.append(component)
        logger.debug(f"Added component: {component.get_mdl_name()}")
    
    def set_components(self, components: List[PkgComponent]) -> None:
        """设置组件列表"""
        self.components = components
        logger.debug(f"Set {len(components)} components")
    
    def get_component(self, component_name: str) -> Optional[PkgComponent]:
        """根据名称获取组件"""
        for component in self.components:
            if component.get_mdl_name() == component_name:
                return component
        return None
    
    def get_components(self) -> List[PkgComponent]:
        """获取所有组件"""
        return self.components
    
    def from_json(self, json_data: Dict[str, Any]) -> None:
        """从JSON数据加载"""
        try:
            if "components" in json_data:
                components_data = json_data["components"]
                for comp_data in components_data:
                    component = PkgComponent(comp_data)
                    self.add_component(component)
            
            logger.debug(f"Loaded PkgDie with {len(self.components)} components")
            
        except Exception as e:
            logger.error(f"Failed to load PkgDie from JSON: {e}")
            raise
    
    def to_json(self) -> Dict[str, Any]:
        """转换为JSON数据"""
        try:
            data = {
                "components": [comp.to_json() for comp in self.components]
            }
            return data
            
        except Exception as e:
            logger.error(f"Failed to convert PkgDie to JSON: {e}")
            raise
