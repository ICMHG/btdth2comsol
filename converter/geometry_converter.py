"""
几何转换器
负责将几何对象转换为COMSOL几何
"""

from typing import List, Any, Dict, Optional
from loguru import logger

from models.geometry import Section, BaseComponent
from models.shape import (
    Shape, Cube, Cylinder, HexagonalPrism, ObliqueCube, Prism, RectPrism, 
    SquarePrism, OblongXPrism, OblongYPrism, RoundedRectPrism, 
    ChamferedRectPrism, NSidedPolygonPrism, Trace,
    Circle, Rectangle, Square, OblongX, OblongY, RoundedRectangle, 
    ChamferedRectangle, NSidedPolygon
)


class GeometryConverter:
    """几何转换器"""
    
    def __init__(self):
        """初始化几何转换器"""
        logger.debug("GeometryConverter initialized")
    
    def convert_sections(self, sections: List[Section], model: Any) -> List[Any]:
        """
        转换几何区域为COMSOL几何
        
        Args:
            sections: 几何区域列表
            model: COMSOL模型对象
            
        Returns:
            List[Any]: COMSOL几何对象列表
        """
        logger.debug(f"Converting {len(sections)} sections to COMSOL geometry")
        
        geometry_objects = []
        for section in sections:
            try:
                geom_obj = self._convert_single_section(section, model)
                if geom_obj:
                    geometry_objects.append(geom_obj)
                    logger.debug(f"Converted section: {section.name}")
            except Exception as e:
                logger.error(f"Failed to convert section {section.name}: {e}")
        
        return geometry_objects
    
    def _convert_single_section(self, section: Section, model: Any) -> Optional[Any]:
        """
        转换单个几何区域
        
        Args:
            section: 几何区域对象
            model: COMSOL模型对象
            
        Returns:
            Optional[Any]: COMSOL几何对象
        """
        if not section.shape:
            logger.warning(f"Section {section.name} has no shape")
            return None
        
        try:
            # 根据形状类型创建相应的COMSOL几何
            if isinstance(section.shape, Cube):
                return self._create_cube_geometry(section, model)
            elif isinstance(section.shape, Cylinder):
                return self._create_cylinder_geometry(section, model)
            elif isinstance(section.shape, HexagonalPrism):
                return self._create_hexagonal_prism_geometry(section, model)
            elif isinstance(section.shape, ObliqueCube):
                return self._create_oblique_cube_geometry(section, model)
            elif isinstance(section.shape, Prism):
                return self._create_prism_geometry(section, model)
            elif isinstance(section.shape, RectPrism):
                return self._create_rect_prism_geometry(section, model)
            elif isinstance(section.shape, SquarePrism):
                return self._create_square_prism_geometry(section, model)
            elif isinstance(section.shape, OblongXPrism):
                return self._create_oblong_x_prism_geometry(section, model)
            elif isinstance(section.shape, OblongYPrism):
                return self._create_oblong_y_prism_geometry(section, model)
            elif isinstance(section.shape, RoundedRectPrism):
                return self._create_rounded_rect_prism_geometry(section, model)
            elif isinstance(section.shape, ChamferedRectPrism):
                return self._create_chamfered_rect_prism_geometry(section, model)
            elif isinstance(section.shape, NSidedPolygonPrism):
                return self._create_nsided_polygon_prism_geometry(section, model)
            elif isinstance(section.shape, Trace):
                return self._create_trace_geometry(section, model)
            elif isinstance(section.shape, Circle):
                return self._create_circle_geometry(section, model)
            elif isinstance(section.shape, Rectangle):
                return self._create_rectangle_geometry(section, model)
            elif isinstance(section.shape, Square):
                return self._create_square_geometry(section, model)
            elif isinstance(section.shape, OblongX):
                return self._create_oblong_x_geometry(section, model)
            elif isinstance(section.shape, OblongY):
                return self._create_oblong_y_geometry(section, model)
            elif isinstance(section.shape, RoundedRectangle):
                return self._create_rounded_rectangle_geometry(section, model)
            elif isinstance(section.shape, ChamferedRectangle):
                return self._create_chamfered_rectangle_geometry(section, model)
            elif isinstance(section.shape, NSidedPolygon):
                return self._create_nsided_polygon_geometry(section, model)
            else:
                logger.warning(f"Unsupported shape type: {type(section.shape)}")
                return self._create_generic_geometry(section, model)
        
        except Exception as e:
            logger.error(f"Failed to convert section {section.name}: {e}")
            return None
    
    def _create_cube_geometry(self, section: Section, model: Any) -> Any:
        """创建立方体几何"""
        try:
            cube = section.shape
            geom = model.geom("geom1")
            
            # 创建立方体
            cube_obj = geom.feature().create("blk", "Block")
            cube_obj.set("pos", [cube.position.x, cube.position.y, cube.position.z])
            cube_obj.set("size", [cube.length, cube.width, cube.height])
            
            # 设置名称
            cube_obj.set("name", f"{section.name}_cube")
            
            logger.debug(f"Created cube geometry for section: {section.name}")
            return cube_obj
            
        except Exception as e:
            logger.error(f"Failed to create cube geometry: {e}")
            return None
    
    def _create_cylinder_geometry(self, section: Section, model: Any) -> Any:
        """创建圆柱体几何"""
        try:
            cylinder = section.shape
            geom = model.geom("geom1")
            
            # 创建圆柱体
            cyl_obj = geom.feature().create("cyl", "Cylinder")
            cyl_obj.set("pos", [cylinder.position.x, cylinder.position.y, cylinder.position.z])
            cyl_obj.set("r", cylinder.radius)
            cyl_obj.set("h", cylinder.height)
            
            # 设置名称
            cyl_obj.set("name", f"{section.name}_cylinder")
            
            logger.debug(f"Created cylinder geometry for section: {section.name}")
            return cyl_obj
            
        except Exception as e:
            logger.error(f"Failed to create cylinder geometry: {e}")
            return None
    
    def _create_hexagonal_prism_geometry(self, section: Section, model: Any) -> Any:
        """创建六棱柱几何"""
        try:
            prism = section.shape
            geom = model.geom("geom1")
            
            # 创建六棱柱
            hex_obj = geom.feature().create("hex", "Hexagon")
            hex_obj.set("pos", [prism.position.x, prism.position.y, prism.position.z])
            hex_obj.set("r", prism.radius)
            hex_obj.set("h", prism.height)
            
            # 设置名称
            hex_obj.set("name", f"{section.name}_hexagon")
            
            logger.debug(f"Created hexagonal prism geometry for section: {section.name}")
            return hex_obj
            
        except Exception as e:
            logger.error(f"Failed to create hexagonal prism geometry: {e}")
            return None
    
    def _create_oblique_cube_geometry(self, section: Section, model: Any) -> Any:
        """创建斜立方体几何"""
        try:
            cube = section.shape
            geom = model.geom("geom1")
            
            # 创建斜立方体
            obl_obj = geom.feature().create("obl", "Block")
            obl_obj.set("pos", [cube.position.x, cube.position.y, cube.position.z])
            obl_obj.set("size", [cube.length, cube.width, cube.height])
            
            # 应用旋转
            if hasattr(cube, 'rotation') and cube.rotation:
                obl_obj.set("rot", cube.rotation)
            
            # 设置名称
            obl_obj.set("name", f"{section.name}_oblique_cube")
            
            logger.debug(f"Created oblique cube geometry for section: {section.name}")
            return obl_obj
            
        except Exception as e:
            logger.error(f"Failed to create oblique cube geometry: {e}")
            return None
    
    def _create_prism_geometry(self, section: Section, model: Any) -> Any:
        """创建棱柱几何"""
        try:
            prism = section.shape
            geom = model.geom("geom1")
            
            # 创建棱柱
            prism_obj = geom.feature().create("prism", "Block")
            prism_obj.set("pos", [prism.position.x, prism.position.y, prism.position.z])
            prism_obj.set("size", [prism.length, prism.width, prism.height])
            
            # 设置名称
            prism_obj.set("name", f"{section.name}_prism")
            
            logger.debug(f"Created prism geometry for section: {section.name}")
            return prism_obj
            
        except Exception as e:
            logger.error(f"Failed to create prism geometry: {e}")
            return None
    
    def _create_rect_prism_geometry(self, section: Section, model: Any) -> Any:
        """创建矩形棱柱几何"""
        try:
            prism = section.shape
            geom = model.geom("geom1")
            
            # 创建矩形棱柱
            rect_obj = geom.feature().create("rect", "Block")
            rect_obj.set("pos", [prism.position.x, prism.position.y, prism.position.z])
            rect_obj.set("size", [prism.length, prism.width, prism.height])
            
            # 设置名称
            rect_obj.set("name", f"{section.name}_rect_prism")
            
            logger.debug(f"Created rectangular prism geometry for section: {section.name}")
            return rect_obj
            
        except Exception as e:
            logger.error(f"Failed to create rectangular prism geometry: {e}")
            return None
    
    def _create_square_prism_geometry(self, section: Section, model: Any) -> Any:
        """创建正方形棱柱几何"""
        try:
            prism = section.shape
            geom = model.geom("geom1")
            
            # 创建正方形棱柱
            square_obj = geom.feature().create("square", "Block")
            square_obj.set("pos", [prism.position.x, prism.position.y, prism.position.z])
            square_obj.set("size", [prism.side, prism.side, prism.height])
            
            # 设置名称
            square_obj.set("name", f"{section.name}_square_prism")
            
            logger.debug(f"Created square prism geometry for section: {section.name}")
            return square_obj
            
        except Exception as e:
            logger.error(f"Failed to create square prism geometry: {e}")
            return None
    
    def _create_oblong_x_prism_geometry(self, section: Section, model: Any) -> Any:
        """创建X方向长方形棱柱几何"""
        try:
            prism = section.shape
            geom = model.geom("geom1")
            
            # 创建X方向长方形棱柱
            oblong_obj = geom.feature().create("oblong_x", "Block")
            oblong_obj.set("pos", [prism.position.x, prism.position.y, prism.position.z])
            oblong_obj.set("size", [prism.length, prism.width, prism.height])
            
            # 设置名称
            oblong_obj.set("name", f"{section.name}_oblong_x_prism")
            
            logger.debug(f"Created oblong X prism geometry for section: {section.name}")
            return oblong_obj
            
        except Exception as e:
            logger.error(f"Failed to create oblong X prism geometry: {e}")
            return None
    
    def _create_oblong_y_prism_geometry(self, section: Section, model: Any) -> Any:
        """创建Y方向长方形棱柱几何"""
        try:
            prism = section.shape
            geom = model.geom("geom1")
            
            # 创建Y方向长方形棱柱
            oblong_obj = geom.feature().create("oblong_y", "Block")
            oblong_obj.set("pos", [prism.position.x, prism.position.y, prism.position.z])
            oblong_obj.set("size", [prism.length, prism.width, prism.height])
            
            # 设置名称
            oblong_obj.set("name", f"{section.name}_oblong_y_prism")
            
            logger.debug(f"Created oblong Y prism geometry for section: {section.name}")
            return oblong_obj
            
        except Exception as e:
            logger.error(f"Failed to create oblong Y prism geometry: {e}")
            return None
    
    def _create_rounded_rect_prism_geometry(self, section: Section, model: Any) -> Any:
        """创建圆角矩形棱柱几何"""
        try:
            prism = section.shape
            geom = model.geom("geom1")
            
            # 创建圆角矩形棱柱
            rounded_obj = geom.feature().create("rounded", "Block")
            rounded_obj.set("pos", [prism.position.x, prism.position.y, prism.position.z])
            rounded_obj.set("size", [prism.length, prism.width, prism.height])
            
            # 设置圆角半径
            if hasattr(prism, 'corner_radius'):
                rounded_obj.set("cornerRadius", prism.corner_radius)
            
            # 设置名称
            rounded_obj.set("name", f"{section.name}_rounded_rect_prism")
            
            logger.debug(f"Created rounded rectangular prism geometry for section: {section.name}")
            return rounded_obj
            
        except Exception as e:
            logger.error(f"Failed to create rounded rectangular prism geometry: {e}")
            return None
    
    def _create_chamfered_rect_prism_geometry(self, section: Section, model: Any) -> Any:
        """创建倒角矩形棱柱几何"""
        try:
            prism = section.shape
            geom = model.geom("geom1")
            
            # 创建倒角矩形棱柱
            chamfered_obj = geom.feature().create("chamfered", "Block")
            chamfered_obj.set("pos", [prism.position.x, prism.position.y, prism.position.z])
            chamfered_obj.set("size", [prism.length, prism.width, prism.height])
            
            # 设置倒角距离
            if hasattr(prism, 'chamfer_distance'):
                chamfered_obj.set("chamferDistance", prism.chamfer_distance)
            
            # 设置名称
            chamfered_obj.set("name", f"{section.name}_chamfered_rect_prism")
            
            logger.debug(f"Created chamfered rectangular prism geometry for section: {section.name}")
            return chamfered_obj
            
        except Exception as e:
            logger.error(f"Failed to create chamfered rectangular prism geometry: {e}")
            return None
    
    def _create_nsided_polygon_prism_geometry(self, section: Section, model: Any) -> Any:
        """创建N边形棱柱几何"""
        try:
            prism = section.shape
            geom = model.geom("geom1")
            
            # 创建N边形棱柱
            polygon_obj = geom.feature().create("polygon", "Polygon")
            polygon_obj.set("pos", [prism.position.x, prism.position.y, prism.position.z])
            polygon_obj.set("n", prism.num_sides)
            polygon_obj.set("r", prism.radius)
            polygon_obj.set("h", prism.height)
            
            # 设置名称
            polygon_obj.set("name", f"{section.name}_nsided_polygon_prism")
            
            logger.debug(f"Created N-sided polygon prism geometry for section: {section.name}")
            return polygon_obj
            
        except Exception as e:
            logger.error(f"Failed to create N-sided polygon prism geometry: {e}")
            return None
    
    def _create_trace_geometry(self, section: Section, model: Any) -> Any:
        """创建轨迹几何"""
        try:
            trace = section.shape
            geom = model.geom("geom1")
            
            # 创建轨迹
            trace_obj = geom.feature().create("trace", "Line")
            trace_obj.set("start", [trace.start.x, trace.start.y, trace.start.z])
            trace_obj.set("end", [trace.end.x, trace.end.y, trace.end.z])
            
            # 设置名称
            trace_obj.set("name", f"{section.name}_trace")
            
            logger.debug(f"Created trace geometry for section: {section.name}")
            return trace_obj
            
        except Exception as e:
            logger.error(f"Failed to create trace geometry: {e}")
            return None
    
    def _create_circle_geometry(self, section: Section, model: Any) -> Any:
        """创建圆形几何"""
        try:
            circle = section.shape
            geom = model.geom("geom1")
            
            # 创建圆形
            circle_obj = geom.feature().create("circle", "Circle")
            circle_obj.set("pos", [circle.position.x, circle.position.y])
            circle_obj.set("r", circle.radius)
            
            # 设置名称
            circle_obj.set("name", f"{section.name}_circle")
            
            logger.debug(f"Created circle geometry for section: {section.name}")
            return circle_obj
            
        except Exception as e:
            logger.error(f"Failed to create circle geometry: {e}")
            return None
    
    def _create_rectangle_geometry(self, section: Section, model: Any) -> Any:
        """创建矩形几何"""
        try:
            rect = section.shape
            geom = model.geom("geom1")
            
            # 创建矩形
            rect_obj = geom.feature().create("rectangle", "Rectangle")
            rect_obj.set("pos", [rect.position.x, rect.position.y])
            rect_obj.set("size", [rect.length, rect.width])
            
            # 设置名称
            rect_obj.set("name", f"{section.name}_rectangle")
            
            logger.debug(f"Created rectangle geometry for section: {section.name}")
            return rect_obj
            
        except Exception as e:
            logger.error(f"Failed to create rectangle geometry: {e}")
            return None
    
    def _create_square_geometry(self, section: Section, model: Any) -> Any:
        """创建正方形几何"""
        try:
            square = section.shape
            geom = model.geom("geom1")
            
            # 创建正方形
            square_obj = geom.feature().create("square", "Square")
            square_obj.set("pos", [square.position.x, square.position.y])
            square_obj.set("size", square.side)
            
            # 设置名称
            square_obj.set("name", f"{section.name}_square")
            
            logger.debug(f"Created square geometry for section: {section.name}")
            return square_obj
            
        except Exception as e:
            logger.error(f"Failed to create square geometry: {e}")
            return None
    
    def _create_oblong_x_geometry(self, section: Section, model: Any) -> Any:
        """创建X方向长方形几何"""
        try:
            oblong = section.shape
            geom = model.geom("geom1")
            
            # 创建X方向长方形
            oblong_obj = geom.feature().create("oblong_x", "Rectangle")
            oblong_obj.set("pos", [oblong.position.x, oblong.position.y])
            oblong_obj.set("size", [oblong.length, oblong.width])
            
            # 设置名称
            oblong_obj.set("name", f"{section.name}_oblong_x")
            
            logger.debug(f"Created oblong X geometry for section: {section.name}")
            return oblong_obj
            
        except Exception as e:
            logger.error(f"Failed to create oblong X geometry: {e}")
            return None
    
    def _create_oblong_y_geometry(self, section: Section, model: Any) -> Any:
        """创建Y方向长方形几何"""
        try:
            oblong = section.shape
            geom = model.geom("geom1")
            
            # 创建Y方向长方形
            oblong_obj = geom.feature().create("oblong_y", "Rectangle")
            oblong_obj.set("pos", [oblong.position.x, oblong.position.y])
            oblong_obj.set("size", [oblong.length, oblong.width])
            
            # 设置名称
            oblong_obj.set("name", f"{section.name}_oblong_y")
            
            logger.debug(f"Created oblong Y geometry for section: {section.name}")
            return oblong_obj
            
        except Exception as e:
            logger.error(f"Failed to create oblong Y geometry: {e}")
            return None
    
    def _create_rounded_rectangle_geometry(self, section: Section, model: Any) -> Any:
        """创建圆角矩形几何"""
        try:
            rect = section.shape
            geom = model.geom("geom1")
            
            # 创建圆角矩形
            rounded_obj = geom.feature().create("rounded_rect", "Rectangle")
            rounded_obj.set("pos", [rect.position.x, rect.position.y])
            rounded_obj.set("size", [rect.length, rect.width])
            
            # 设置圆角半径
            if hasattr(rect, 'corner_radius'):
                rounded_obj.set("cornerRadius", rect.corner_radius)
            
            # 设置名称
            rounded_obj.set("name", f"{section.name}_rounded_rectangle")
            
            logger.debug(f"Created rounded rectangle geometry for section: {section.name}")
            return rounded_obj
            
        except Exception as e:
            logger.error(f"Failed to create rounded rectangle geometry: {e}")
            return None
    
    def _create_chamfered_rectangle_geometry(self, section: Section, model: Any) -> Any:
        """创建倒角矩形几何"""
        try:
            rect = section.shape
            geom = model.geom("geom1")
            
            # 创建倒角矩形
            chamfered_obj = geom.feature().create("chamfered_rect", "Rectangle")
            chamfered_obj.set("pos", [rect.position.x, rect.position.y])
            chamfered_obj.set("size", [rect.length, rect.width])
            
            # 设置倒角距离
            if hasattr(rect, 'chamfer_distance'):
                chamfered_obj.set("chamferDistance", rect.chamfer_distance)
            
            # 设置名称
            chamfered_obj.set("name", f"{section.name}_chamfered_rectangle")
            
            logger.debug(f"Created chamfered rectangle geometry for section: {section.name}")
            return chamfered_obj
            
        except Exception as e:
            logger.error(f"Failed to create chamfered rectangle geometry: {e}")
            return None
    
    def _create_nsided_polygon_geometry(self, section: Section, model: Any) -> Any:
        """创建N边形几何"""
        try:
            polygon = section.shape
            geom = model.geom("geom1")
            
            # 创建N边形
            polygon_obj = geom.feature().create("polygon", "Polygon")
            polygon_obj.set("pos", [polygon.position.x, polygon.position.y])
            polygon_obj.set("n", polygon.num_sides)
            polygon_obj.set("r", polygon.radius)
            
            # 设置名称
            polygon_obj.set("name", f"{section.name}_nsided_polygon")
            
            logger.debug(f"Created N-sided polygon geometry for section: {section.name}")
            return polygon_obj
            
        except Exception as e:
            logger.error(f"Failed to create N-sided polygon geometry: {e}")
            return None
    
    def _create_generic_geometry(self, section: Section, model: Any) -> Any:
        """创建通用几何（当形状类型不支持时）"""
        try:
            geom = model.geom("geom1")
            
            # 创建通用块
            generic_obj = geom.feature().create("generic", "Block")
            generic_obj.set("pos", [0, 0, 0])
            generic_obj.set("size", [1, 1, 1])
            
            # 设置名称
            generic_obj.set("name", f"{section.name}_generic")
            
            logger.warning(f"Created generic geometry for unsupported shape type in section: {section.name}")
            return generic_obj
            
        except Exception as e:
            logger.error(f"Failed to create generic geometry: {e}")
            return None
    
    def validate_geometry(self, geometry_objects: List[Any]) -> bool:
        """
        验证几何对象
        
        Args:
            geometry_objects: 几何对象列表
            
        Returns:
            bool: 验证是否通过
        """
        if not geometry_objects:
            logger.warning("No geometry objects to validate")
            return False
        
        try:
            for geom_obj in geometry_objects:
                if not geom_obj:
                    logger.error("Found None geometry object")
                    return False
                
                # 检查必要的属性
                if not hasattr(geom_obj, 'name'):
                    logger.error("Geometry object missing name attribute")
                    return False
            
            logger.info(f"Geometry validation passed for {len(geometry_objects)} objects")
            return True
            
        except Exception as e:
            logger.error(f"Geometry validation failed: {e}")
            return False

