"""
几何管理器
负责管理几何区域和层次结构
"""

from typing import List, Dict, Optional, Tuple
from loguru import logger

from models.geometry import Section
from utils.geometry_utils import GeometryUtils


class GeometryManager:
    """
    几何管理器
    
    负责管理几何区域和层次结构，提供几何处理功能
    """
    
    def __init__(self):
        """初始化几何管理器"""
        self.sections: List[Section] = []
        self.hierarchy_map: Dict[str, List[str]] = {}
        logger.debug("GeometryManager initialized")
    
    def add_section(self, section: Section) -> None:
        """
        添加几何区域
        
        Args:
            section: 几何区域对象
        """
        self.sections.append(section)
        logger.debug(f"Added section: {section.name}")
    
    def get_sections(self) -> List[Section]:
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
    
    def remove_section(self, name: str) -> bool:
        """
        删除几何区域
        
        Args:
            name: 区域名称
            
        Returns:
            bool: 删除是否成功
        """
        for i, section in enumerate(self.sections):
            if section.name == name:
                del self.sections[i]
                logger.debug(f"Removed section: {name}")
                return True
        return False
    
    def clear_sections(self) -> None:
        """清空所有几何区域"""
        self.sections.clear()
        self.hierarchy_map.clear()
        logger.debug("Cleared all sections")
    
    def sort_sections_by_z(self) -> List[Section]:
        """
        按Z坐标排序几何区域
        
        Returns:
            List[Section]: 排序后的几何区域列表
        """
        sorted_sections = sorted(self.sections, key=lambda s: s.get_offset_z())
        logger.debug(f"Sorted {len(sorted_sections)} sections by Z coordinate")
        return sorted_sections
    
    def build_hierarchy_map(self) -> Dict[str, List[str]]:
        """
        构建层次结构映射
        
        Returns:
            Dict[str, List[str]]: 层次结构映射
        """
        self.hierarchy_map.clear()
        
        for section in self.sections:
            if section.children:
                self.hierarchy_map[section.name] = [child.name for child in section.children]
        
        logger.debug(f"Built hierarchy map with {len(self.hierarchy_map)} parent sections")
        return self.hierarchy_map
    
    def get_parent_sections(self) -> List[Section]:
        """
        获取有子组件的父区域
        
        Returns:
            List[Section]: 父区域列表
        """
        return [section for section in self.sections if section.children]
    
    def get_child_sections(self) -> List[Section]:
        """
        获取所有子组件
        
        Returns:
            List[Section]: 子组件列表
        """
        children = []
        for section in self.sections:
            if section.children:
                children.extend(section.children)
        return children
    
    def get_standalone_sections(self) -> List[Section]:
        """
        获取独立的几何区域（无父子关系）
        
        Returns:
            List[Section]: 独立区域列表
        """
        return [section for section in self.sections if not section.children]
    
    def merge_thin_layers(self, threshold: float = 0.1) -> List[Section]:
        """
        合并薄层
        
        Args:
            threshold: 薄层阈值
            
        Returns:
            List[Section]: 合并后的几何区域列表
        """
        sorted_sections = self.sort_sections_by_z()
        merged_sections = GeometryUtils.merge_thin_layers(sorted_sections, threshold)
        
        logger.info(f"Merged thin layers: {len(sorted_sections)} -> {len(merged_sections)}")
        return merged_sections
    
    def unify_geometry_dimensions(self) -> None:
        """统一几何尺寸"""
        GeometryUtils.unify_geometry_dimensions(self.sections)
        logger.info("Unified geometry dimensions")
    
    def establish_parent_child_relationships(self) -> None:
        """建立父子关系"""
        for section in self.sections:
            if section.children:
                for child in section.children:
                    # 设置布尔运算关系（默认为差集）
                    section.add_child_with_operation(child, "difference")
        
        logger.info("Established parent-child relationships")
    
    def validate_geometry_integrity(self) -> bool:
        """
        验证几何完整性
        
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
            
            # 验证子组件
            if section.children:
                for child in section.children:
                    if not child.material:
                        logger.warning(f"Child component {child.name} has no material")
        
        logger.info("Geometry integrity validation passed")
        return True
    
    def get_geometry_bounds(self) -> Tuple[float, float, float, float, float, float]:
        """
        获取几何边界框
        
        Returns:
            Tuple[float, float, float, float, float, float]: (min_x, min_y, min_z, max_x, max_y, max_z)
        """
        if not self.sections:
            return (0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        
        min_x = min_y = min_z = float('inf')
        max_x = max_y = max_z = float('-inf')
        
        for section in self.sections:
            bounds = section.get_bounding_box()
            min_x = min(min_x, bounds[0])
            min_y = min(min_y, bounds[1])
            min_z = min(min_z, bounds[2])
            max_x = max(max_x, bounds[3])
            max_y = max(max_y, bounds[4])
            max_z = max(max_z, bounds[5])
        
        return (min_x, min_y, min_z, max_x, max_y, max_z)
    
    def get_sections_by_type(self, section_type: str) -> List[Section]:
        """
        根据类型获取几何区域
        
        Args:
            section_type: 区域类型
            
        Returns:
            List[Section]: 匹配的区域列表
        """
        return [section for section in self.sections if section.type_str == section_type]
    
    def get_sections_by_layer(self, layer: str) -> List[Section]:
        """
        根据层获取几何区域
        
        Args:
            layer: 层名称
            
        Returns:
            List[Section]: 匹配的区域列表
        """
        return [section for section in self.sections if section.layer == layer]
    
    def get_geometry_summary(self) -> Dict[str, int]:
        """
        获取几何统计摘要
        
        Returns:
            Dict[str, int]: 几何统计信息
        """
        total = len(self.sections)
        parent_sections = len(self.get_parent_sections())
        child_sections = len(self.get_child_sections())
        standalone = len(self.get_standalone_sections())
        
        return {
            "total": total,
            "parent_sections": parent_sections,
            "child_sections": child_sections,
            "standalone": standalone
        }
    
    def print_summary(self) -> None:
        """打印几何摘要信息"""
        summary = self.get_geometry_summary()
        bounds = self.get_geometry_bounds()
        
        logger.info("=" * 40)
        logger.info("Geometry Summary")
        logger.info("=" * 40)
        logger.info(f"Total sections: {summary['total']}")
        logger.info(f"Parent sections: {summary['parent_sections']}")
        logger.info(f"Child sections: {summary['child_sections']}")
        logger.info(f"Standalone sections: {summary['standalone']}")
        logger.info(f"Bounds: ({bounds[0]:.3f}, {bounds[1]:.3f}, {bounds[2]:.3f}) to ({bounds[3]:.3f}, {bounds[4]:.3f}, {bounds[5]:.3f})")
        
        for section in self.sections:
            logger.info(f"  - {section.name}: {section.type_str} (layer: {section.layer})")
        
        logger.info("=" * 40)

