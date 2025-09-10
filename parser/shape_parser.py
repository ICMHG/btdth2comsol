"""
形状解析器
负责解析形状字符串，创建相应的形状对象
"""

import re
from typing import Optional, Union
from loguru import logger

from models.shape import (
    Shape, Shape2D, ShapeFactory, Vector3D,
    Cube, Cylinder, HexagonalPrism, ObliqueCube, Prism,
    RectPrism, SquarePrism, OblongXPrism, OblongYPrism,
    RoundedRectPrism, ChamferedRectPrism, NSidedPolygonPrism, Trace,
    Circle, Rectangle, Square, OblongX, OblongY,
    RoundedRectangle, ChamferedRectangle, NSidedPolygon
)


class ShapeParsingError(Exception):
    """形状解析错误"""
    pass


class ShapeParser:
    """形状字符串解析器"""
    
    def __init__(self):
        """初始化解析器"""
        logger.debug("ShapeParser initialized")
    
    def parse_shape_string(self, shape_string: str) -> Union[Shape, Shape2D]:
        """
        解析形状字符串，返回形状对象
        
        Args:
            shape_string: 形状字符串，如 "cube([x,y,z], length, width, height)"
            
        Returns:
            Union[Shape, Shape2D]: 形状对象
            
        Raises:
            ShapeParsingError: 解析失败时抛出
        """
        if not shape_string or not shape_string.strip():
            raise ShapeParsingError("Shape string cannot be empty")
        
        shape_string = shape_string.strip()
        logger.debug(f"Parsing shape string: {shape_string}")
        
        try:
            # 尝试解析3D形状
            shape = self._parse_3d_shape(shape_string)
            if shape:
                return shape
            
            # 尝试解析2D形状
            shape = self._parse_2d_shape(shape_string)
            if shape:
                return shape
            
            # 如果都失败，抛出错误
            raise ShapeParsingError(f"Unable to parse shape string: {shape_string}")
            
        except Exception as e:
            if isinstance(e, ShapeParsingError):
                raise
            raise ShapeParsingError(f"Error parsing shape string '{shape_string}': {e}")
    
    def _parse_3d_shape(self, shape_string: str) -> Optional[Shape]:
        """解析3D形状字符串"""
        # 立方体: cube([x,y,z], length, width, height)
        cube_pattern = r"cube\(\[([^,]+),([^,]+),([^,]+)\],([^,]+),([^,]+),([^,]+)\)"
        match = re.match(cube_pattern, shape_string)
        if match:
            x, y, z = float(match.group(1)), float(match.group(2)), float(match.group(3))
            length, width, height = float(match.group(4)), float(match.group(5)), float(match.group(6))
            
            # 处理0值的情况，将其替换为小的正数
            if length <= 0:
                length = 0.001  # 1微米
                logger.warning(f"Invalid cube length {match.group(4)}, using {length}")
            if width <= 0:
                width = 0.001   # 1微米
                logger.warning(f"Invalid cube width {match.group(5)}, using {width}")
            if height <= 0:
                height = 0.001  # 1微米
                logger.warning(f"Invalid cube height {match.group(6)}, using {height}")
            
            position = Vector3D(x, y, z)
            return Cube(position, length, width, height)
        
        # 圆柱体: cylinder([x,y,z], radius, height)
        cylinder_pattern = r"cylinder\(\[([^,]+),([^,]+),([^,]+)\],([^,]+),([^,]+)\)"
        match = re.match(cylinder_pattern, shape_string)
        if match:
            x, y, z = float(match.group(1)), float(match.group(2)), float(match.group(3))
            radius, height = float(match.group(4)), float(match.group(5))
            position = Vector3D(x, y, z)
            return Cylinder(position, radius, height)
        
        # 六棱柱: hexagonal_prism([x,y,z], radius, height)
        hex_pattern = r"hexagonal_prism\(\[([^,]+),([^,]+),([^,]+)\],([^,]+),([^,]+)\)"
        match = re.match(hex_pattern, shape_string)
        if match:
            x, y, z = float(match.group(1)), float(match.group(2)), float(match.group(3))
            radius, height = float(match.group(4)), float(match.group(5))
            position = Vector3D(x, y, z)
            return HexagonalPrism(position, radius, height)
        
        # 斜立方体: oblique_cube([x1,y1,z1], [x2,y2,z2], width, thickness)
        oblique_pattern = r"oblique_cube\(\[([^,]+),([^,]+),([^,]+)\],\[([^,]+),([^,]+),([^,]+)\],([^,]+),([^,]+)\)"
        match = re.match(oblique_pattern, shape_string)
        if match:
            x1, y1, z1 = float(match.group(1)), float(match.group(2)), float(match.group(3))
            x2, y2, z2 = float(match.group(4)), float(match.group(5)), float(match.group(6))
            width, thickness = float(match.group(7)), float(match.group(8))
            start = Vector3D(x1, y1, z1)
            end = Vector3D(x2, y2, z2)
            return ObliqueCube(start, end, width, thickness)
        
        # 矩形棱柱: rect_prism([x,y,z], width, height, depth)
        rect_pattern = r"rect_prism\(\[([^,]+),([^,]+),([^,]+)\],([^,]+),([^,]+),([^,]+)\)"
        match = re.match(rect_pattern, shape_string)
        if match:
            x, y, z = float(match.group(1)), float(match.group(2)), float(match.group(3))
            width, height, depth = float(match.group(4)), float(match.group(5)), float(match.group(6))
            position = Vector3D(x, y, z)
            return RectPrism(width, height, depth, position)
        
        # 正方形棱柱: square_prism([x,y,z], side, height)
        square_pattern = r"square_prism\(\[([^,]+),([^,]+),([^,]+)\],([^,]+),([^,]+)\)"
        match = re.match(square_pattern, shape_string)
        if match:
            x, y, z = float(match.group(1)), float(match.group(2)), float(match.group(3))
            side, height = float(match.group(4)), float(match.group(5))
            position = Vector3D(x, y, z)
            return SquarePrism(side, height, position)
        
        # X方向椭圆棱柱: oblong_x_prism([x,y,z], length, width, height)
        oblong_x_pattern = r"oblong_x_prism\(\[([^,]+),([^,]+),([^,]+)\],([^,]+),([^,]+),([^,]+)\)"
        match = re.match(oblong_x_pattern, shape_string)
        if match:
            x, y, z = float(match.group(1)), float(match.group(2)), float(match.group(3))
            length, width, height = float(match.group(4)), float(match.group(5)), float(match.group(6))
            position = Vector3D(x, y, z)
            return OblongXPrism(length, width, height, position)
        
        # Y方向椭圆棱柱: oblong_y_prism([x,y,z], length, width, height)
        oblong_y_pattern = r"oblong_y_prism\(\[([^,]+),([^,]+),([^,]+)\],([^,]+),([^,]+),([^,]+)\)"
        match = re.match(oblong_y_pattern, shape_string)
        if match:
            x, y, z = float(match.group(1)), float(match.group(2)), float(match.group(3))
            length, width, height = float(match.group(4)), float(match.group(5)), float(match.group(6))
            position = Vector3D(x, y, z)
            return OblongYPrism(length, width, height, position)
        
        # 圆角矩形棱柱: rounded_rect_prism([x,y,z], width, height, depth, radius)
        rounded_pattern = r"rounded_rect_prism\(\[([^,]+),([^,]+),([^,]+)\],([^,]+),([^,]+),([^,]+),([^,]+)\)"
        match = re.match(rounded_pattern, shape_string)
        if match:
            x, y, z = float(match.group(1)), float(match.group(2)), float(match.group(3))
            width, height, depth = float(match.group(4)), float(match.group(5)), float(match.group(6))
            radius = float(match.group(7))
            position = Vector3D(x, y, z)
            return RoundedRectPrism(width, height, depth, radius, position)
        
        # 倒角矩形棱柱: chamfered_rect_prism([x,y,z], width, height, depth, chamfer)
        chamfered_pattern = r"chamfered_rect_prism\(\[([^,]+),([^,]+),([^,]+)\],([^,]+),([^,]+),([^,]+),([^,]+)\)"
        match = re.match(chamfered_pattern, shape_string)
        if match:
            x, y, z = float(match.group(1)), float(match.group(2)), float(match.group(3))
            width, height, depth = float(match.group(4)), float(match.group(5)), float(match.group(6))
            chamfer = float(match.group(7))
            position = Vector3D(x, y, z)
            return ChamferedRectPrism(width, height, depth, chamfer, position)
        
        # N边形棱柱: n_sided_polygon_prism([x,y,z], diameter, height, sides)
        n_sided_pattern = r"n_sided_polygon_prism\(\[([^,]+),([^,]+),([^,]+)\],([^,]+),([^,]+),([^,]+)\)"
        match = re.match(n_sided_pattern, shape_string)
        if match:
            x, y, z = float(match.group(1)), float(match.group(2)), float(match.group(3))
            diameter, height, sides = float(match.group(4)), float(match.group(5)), int(match.group(6))
            position = Vector3D(x, y, z)
            return NSidedPolygonPrism(diameter, height, sides, position)
        
        # 轨迹: trace([x,y,z], width, height, length)
        trace_pattern = r"trace\(\[([^,]+),([^,]+),([^,]+)\],([^,]+),([^,]+),([^,]+)\)"
        match = re.match(trace_pattern, shape_string)
        if match:
            x, y, z = float(match.group(1)), float(match.group(2)), float(match.group(3))
            width, height, length = float(match.group(4)), float(match.group(5)), float(match.group(6))
            position = Vector3D(x, y, z)
            return Trace(width, height, length, position)
        
        # 棱柱: prism(base_shape, height) - 需要特殊处理
        prism_pattern = r"prism\(([^,]+),([^,]+)\)"
        match = re.match(prism_pattern, shape_string)
        if match:
            base_shape_str = match.group(1)
            height = float(match.group(2))
            # 递归解析底面形状
            base_shape = self.parse_shape_string(base_shape_str)
            if isinstance(base_shape, Shape2D):
                return Prism(base_shape, height)
            else:
                raise ShapeParsingError("Prism base shape must be a 2D shape")
        
        return None
    
    def _parse_2d_shape(self, shape_string: str) -> Optional[Shape2D]:
        """解析2D形状字符串"""
        # 圆形: circle([x,y], radius)
        circle_pattern = r"circle\(\[([^,]+),([^,]+)\],([^,]+)\)"
        match = re.match(circle_pattern, shape_string)
        if match:
            x, y = float(match.group(1)), float(match.group(2))
            radius = float(match.group(3))
            position = Vector3D(x, y, 0)
            return Circle(position, radius)
        
        # 矩形: rectangle([x,y], width, height)
        rect_pattern = r"rectangle\(\[([^,]+),([^,]+)\],([^,]+),([^,]+)\)"
        match = re.match(rect_pattern, shape_string)
        if match:
            x, y = float(match.group(1)), float(match.group(2))
            width, height = float(match.group(3)), float(match.group(4))
            position = Vector3D(x, y, 0)
            return Rectangle(position, width, height)
        
        # 正方形: square([x,y], side)
        square_pattern = r"square\(\[([^,]+),([^,]+)\],([^,]+)\)"
        match = re.match(square_pattern, shape_string)
        if match:
            x, y = float(match.group(1)), float(match.group(2))
            side = float(match.group(3))
            position = Vector3D(x, y, 0)
            return Square(position, side)
        
        # X方向椭圆: oblong_x([x,y], length, width)
        oblong_x_pattern = r"oblong_x\(\[([^,]+),([^,]+)\],([^,]+),([^,]+)\)"
        match = re.match(oblong_x_pattern, shape_string)
        if match:
            x, y = float(match.group(1)), float(match.group(2))
            length, width = float(match.group(3)), float(match.group(4))
            position = Vector3D(x, y, 0)
            return OblongX(position, length, width)
        
        # Y方向椭圆: oblong_y([x,y], length, width)
        oblong_y_pattern = r"oblong_y\(\[([^,]+),([^,]+)\],([^,]+),([^,]+)\)"
        match = re.match(oblong_y_pattern, shape_string)
        if match:
            x, y = float(match.group(1)), float(match.group(2))
            length, width = float(match.group(3)), float(match.group(4))
            position = Vector3D(x, y, 0)
            return OblongY(position, length, width)
        
        # 圆角矩形: rounded_rectangle([x,y], width, height, radius)
        rounded_pattern = r"rounded_rectangle\(\[([^,]+),([^,]+)\],([^,]+),([^,]+),([^,]+)\)"
        match = re.match(rounded_pattern, shape_string)
        if match:
            x, y = float(match.group(1)), float(match.group(2))
            width, height, radius = float(match.group(3)), float(match.group(4)), float(match.group(5))
            position = Vector3D(x, y, 0)
            return RoundedRectangle(position, width, height, radius)
        
        # 倒角矩形: chamfered_rectangle([x,y], width, height, chamfer)
        chamfered_pattern = r"chamfered_rectangle\(\[([^,]+),([^,]+)\],([^,]+),([^,]+),([^,]+)\)"
        match = re.match(chamfered_pattern, shape_string)
        if match:
            x, y = float(match.group(1)), float(match.group(2))
            width, height, chamfer = float(match.group(3)), float(match.group(4)), float(match.group(5))
            position = Vector3D(x, y, 0)
            return ChamferedRectangle(position, width, height, chamfer)
        
        # N边形: n_sided_polygon([x,y], diameter, sides)
        n_sided_pattern = r"n_sided_polygon\(\[([^,]+),([^,]+)\],([^,]+),([^,]+)\)"
        match = re.match(n_sided_pattern, shape_string)
        if match:
            x, y = float(match.group(1)), float(match.group(2))
            diameter, sides = float(match.group(3)), int(match.group(4))
            position = Vector3D(x, y, 0)
            return NSidedPolygon(position, diameter, sides)
        
        return None
    
    def validate_shape_string(self, shape_string: str) -> bool:
        """
        验证形状字符串格式是否正确
        
        Args:
            shape_string: 形状字符串
            
        Returns:
            bool: 格式是否正确
        """
        try:
            self.parse_shape_string(shape_string)
            return True
        except ShapeParsingError:
            return False
    
    def get_shape_type(self, shape_string: str) -> str:
        """
        获取形状类型
        
        Args:
            shape_string: 形状字符串
            
        Returns:
            str: 形状类型
        """
        try:
            shape = self.parse_shape_string(shape_string)
            return shape.type.value
        except ShapeParsingError:
            return "unknown"
    
    def create_shape_from_dict(self, shape_data: dict) -> Union[Shape, Shape2D]:
        """
        从字典数据创建形状对象
        
        Args:
            shape_data: 形状数据字典
            
        Returns:
            Union[Shape, Shape2D]: 形状对象
        """
        shape_type = shape_data.get("type", "").lower()
        
        if not shape_type:
            raise ShapeParsingError("Shape type is required")
        
        # 提取位置信息
        position_data = shape_data.get("position", {})
        position = Vector3D(
            position_data.get("x", 0.0),
            position_data.get("y", 0.0),
            position_data.get("z", 0.0)
        )
        
        # 提取旋转角度
        rotation = shape_data.get("rotation", 0.0)
        
        # 根据类型创建形状
        if shape_type == "cube":
            return Cube(
                position=position,
                length=shape_data["length"],
                width=shape_data["width"],
                height=shape_data["height"],
                rotation=rotation
            )
        elif shape_type == "cylinder":
            return Cylinder(
                position=position,
                radius=shape_data["radius"],
                height=shape_data["height"],
                rotation=rotation
            )
        elif shape_type == "hexagonal_prism":
            return HexagonalPrism(
                position=position,
                radius=shape_data["radius"],
                height=shape_data["height"],
                rotation=rotation
            )
        elif shape_type == "circle":
            return Circle(
                position=position,
                radius=shape_data["radius"]
            )
        elif shape_type == "rectangle":
            return Rectangle(
                position=position,
                width=shape_data["width"],
                height=shape_data["height"]
            )
        elif shape_type == "square":
            return Square(
                position=position,
                side=shape_data["side"]
            )
        else:
            raise ShapeParsingError(f"Unsupported shape type: {shape_type}")
    
    def create_shape_string(self, shape: Union[Shape, Shape2D]) -> str:
        """
        从形状对象创建形状字符串
        
        Args:
            shape: 形状对象
            
        Returns:
            str: 形状字符串
        """
        return shape.to_string()

