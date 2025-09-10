"""
形状系统
包含所有2D和3D几何形状的定义
"""

import math
from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
from loguru import logger


# ============================================================================
# 枚举类型定义
# ============================================================================

class ShapeType(Enum):
    """3D形状类型枚举"""
    CUBE = "cube"
    CYLINDER = "cylinder"
    HEXAGONAL_PRISM = "hexagonal_prism"
    OBLIQUE_CUBE = "oblique_cube"
    PRISM = "prism"
    RECT_PRISM = "rect_prism"
    SQUARE_PRISM = "square_prism"
    OBLONG_X_PRISM = "oblong_x_prism"
    OBLONG_Y_PRISM = "oblong_y_prism"
    ROUNDED_RECT_PRISM = "rounded_rect_prism"
    CHAMFERED_RECT_PRISM = "chamfered_rect_prism"
    N_SIDED_POLYGON_PRISM = "n_sided_polygon_prism"
    TRACE = "trace"


class Shape2DType(Enum):
    """2D形状类型枚举"""
    CIRCLE = "circle"
    RECTANGLE = "rectangle"
    SQUARE = "square"
    OBLONG_X = "oblong_x"
    OBLONG_Y = "oblong_y"
    ROUNDED_RECTANGLE = "rounded_rectangle"
    CHAMFERED_RECTANGLE = "chamfered_rectangle"
    N_SIDED_POLYGON = "n_sided_polygon"


# ============================================================================
# 基础数据结构
# ============================================================================

@dataclass
class Vector3D:
    """3D向量类"""
    x: float
    y: float
    z: float
    
    def __init__(self, x: float = 0.0, y: float = 0.0, z: float = 0.0):
        self.x = float(x)
        self.y = float(y)
        self.z = float(z)
    
    def __add__(self, other: 'Vector3D') -> 'Vector3D':
        return Vector3D(self.x + other.x, self.y + other.y, self.z + other.z)
    
    def __sub__(self, other: 'Vector3D') -> 'Vector3D':
        return Vector3D(self.x - other.x, self.y - other.y, self.z - other.z)
    
    def __mul__(self, scalar: float) -> 'Vector3D':
        return Vector3D(self.x * scalar, self.y * scalar, self.z * scalar)
    
    def __truediv__(self, scalar: float) -> 'Vector3D':
        return Vector3D(self.x / scalar, self.y / scalar, self.z / scalar)
    
    def magnitude(self) -> float:
        """计算向量长度"""
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
    
    def normalize(self) -> 'Vector3D':
        """归一化向量"""
        mag = self.magnitude()
        if mag == 0:
            return Vector3D(0, 0, 0)
        return self / mag


@dataclass
class Vector2D:
    """2D向量类"""
    x: float
    y: float
    
    def __init__(self, x: float = 0.0, y: float = 0.0):
        self.x = float(x)
        self.y = float(y)
    
    def __add__(self, other: 'Vector2D') -> 'Vector2D':
        return Vector2D(self.x + other.x, self.y + other.y)
    
    def __sub__(self, other: 'Vector2D') -> 'Vector2D':
        return Vector2D(self.x - other.x, self.y - other.y)
    
    def __mul__(self, scalar: float) -> 'Vector2D':
        return Vector2D(self.x * scalar, self.y * scalar)
    
    def __truediv__(self, scalar: float) -> 'Vector2D':
        return Vector2D(self.x / scalar, self.y / scalar)
    
    def magnitude(self) -> float:
        """计算向量长度"""
        return math.sqrt(self.x * self.x + self.y * self.y)
    
    def normalize(self) -> 'Vector2D':
        """归一化向量"""
        mag = self.magnitude()
        if mag == 0:
            return Vector2D(0, 0)
        return self / mag


@dataclass
class BoundingBox3D:
    """3D边界框类"""
    min_x: float
    min_y: float
    min_z: float
    max_x: float
    max_y: float
    max_z: float
    
    def __init__(self, min_x: float, min_y: float, min_z: float, 
                 max_x: float, max_y: float, max_z: float):
        self.min_x = float(min_x)
        self.min_y = float(min_y)
        self.min_z = float(min_z)
        self.max_x = float(max_x)
        self.max_y = float(max_y)
        self.max_z = float(max_z)
    
    def width(self) -> float:
        return self.max_x - self.min_x
    
    def height(self) -> float:
        return self.max_z - self.min_z
    
    def depth(self) -> float:
        return self.max_y - self.min_y
    
    def volume(self) -> float:
        return self.width() * self.height() * self.depth()
    
    def contains_point(self, point: Vector3D) -> bool:
        return (self.min_x <= point.x <= self.max_x and
                self.min_y <= point.y <= self.max_y and
                self.min_z <= point.z <= self.max_z)


@dataclass
class BoundingBox2D:
    """2D边界框类"""
    min_x: float
    min_y: float
    max_x: float
    max_y: float
    
    def __init__(self, min_x: float, min_y: float, max_x: float, max_y: float):
        self.min_x = float(min_x)
        self.min_y = float(min_y)
        self.max_x = float(max_x)
        self.max_y = float(max_y)
    
    def width(self) -> float:
        return self.max_x - self.min_x
    
    def height(self) -> float:
        return self.max_y - self.min_y
    
    def area(self) -> float:
        return self.width() * self.height()
    
    def contains_point(self, point: Vector2D) -> bool:
        return (self.min_x <= point.x <= self.max_x and
                self.min_y <= point.y <= self.max_y)


# ============================================================================
# 形状基类
# ============================================================================

class Shape(ABC):
    """3D形状基类"""
    
    def __init__(self, shape_type: ShapeType, position: Vector3D = None, rotation: float = 0.0):
        """
        初始化3D形状
        
        Args:
            shape_type: 形状类型
            position: 位置向量
            rotation: 旋转角度（度）
        """
        self.shape_type = shape_type
        self.position = position if position else Vector3D(0, 0, 0)
        self.rotation = float(rotation)
        self.is_modified = False
    
    @abstractmethod
    def get_bounding_box(self) -> BoundingBox3D:
        """获取3D边界框"""
        pass
    
    @abstractmethod
    def contains_point(self, point: Vector3D) -> bool:
        """检查点是否在形状内"""
        pass
    
    @abstractmethod
    def volume(self) -> float:
        """计算体积"""
        pass
    
    @abstractmethod
    def get_2d_type(self) -> str:
        """获取对应的2D形状类型"""
        pass
    
    @abstractmethod
    def to_string(self) -> str:
        """转换为字符串表示"""
        pass


class Shape2D(ABC):
    """2D形状基类"""
    
    def __init__(self, shape_type: Shape2DType, position: Vector2D = None, rotation: float = 0.0):
        """
        初始化2D形状
        
        Args:
            shape_type: 形状类型
            position: 位置向量
            rotation: 旋转角度（度）
        """
        self.shape_type = shape_type
        self.position = position if position else Vector2D(0, 0)
        self.rotation = float(rotation)
        self.is_modified = False
    
    @abstractmethod
    def get_bounding_box_2d(self) -> BoundingBox2D:
        """获取2D边界框"""
        pass
    
    @abstractmethod
    def contains_point(self, point: Vector2D) -> bool:
        """检查点是否在形状内"""
        pass
    
    @abstractmethod
    def get_area(self) -> float:
        """计算面积"""
        pass
    
    @abstractmethod
    def to_string(self) -> str:
        """转换为字符串表示"""
        pass


class Cube(Shape):
    """立方体形状"""
    
    def __init__(self, position: Vector3D = None, length: float = 1.0, width: float = 1.0, height: float = 1.0):
        """
        初始化立方体
        
        Args:
            position: 位置向量
            length: 长度（X方向）
            width: 宽度（Y方向）
            height: 高度（Z方向）
        """
        super().__init__(ShapeType.CUBE, position)
        if length <= 0 or width <= 0 or height <= 0:
            raise ValueError("Length, width and height must be positive")
        self.length = float(length)
        self.width = float(width)
        self.height = float(height)
    
    def get_length(self) -> float:
        """获取长度"""
        return self.length
    
    def set_length(self, length: float) -> None:
        """设置长度"""
        if length <= 0:
            raise ValueError("Length must be positive")
        self.length = float(length)
        self.is_modified = True
    
    def get_width(self) -> float:
        """获取宽度"""
        return self.width
    
    def set_width(self, width: float) -> None:
        """设置宽度"""
        if width <= 0:
            raise ValueError("Width must be positive")
        self.width = float(width)
        self.is_modified = True
    
    def get_height(self) -> float:
        """获取高度"""
        return self.height
    
    def set_height(self, height: float) -> None:
        """设置高度"""
        if height <= 0:
            raise ValueError("Height must be positive")
        self.height = float(height)
        self.is_modified = True
    
    def get_bounding_box(self) -> BoundingBox3D:
        """获取3D边界框"""
        half_length = self.length / 2
        half_width = self.width / 2
        half_height = self.height / 2
        
        return BoundingBox3D(
            self.position.x - half_length, self.position.y - half_width, self.position.z - half_height,
            self.position.x + half_length, self.position.y + half_width, self.position.z + half_height
        )
    
    def contains_point(self, point: Vector3D) -> bool:
        """检查点是否在立方体内"""
        half_length = self.length / 2
        half_width = self.width / 2
        half_height = self.height / 2
        
        return (abs(point.x - self.position.x) <= half_length and
                abs(point.y - self.position.y) <= half_width and
                abs(point.z - self.position.z) <= half_height)
    
    def volume(self) -> float:
        """计算体积"""
        return self.length * self.width * self.height
    
    def get_2d_type(self) -> str:
        """获取对应的2D形状类型"""
        return Shape2DType.RECTANGLE
    
    def to_string(self) -> str:
        """转换为字符串表示"""
        return f"cube([{self.position.x},{self.position.y},{self.position.z}], {self.length}, {self.width}, {self.height})"


class HexagonalPrism(Shape):
    """六棱柱形状"""
    
    def __init__(self, position: Vector3D = None, diameter: float = 1.0, height: float = 1.0):
        """
        初始化六棱柱
        
        Args:
            position: 位置向量
            diameter: 外接圆直径
            height: 高度
        """
        super().__init__(ShapeType.HEXAGONAL_PRISM, position)
        if diameter <= 0 or height <= 0:
            raise ValueError("Diameter and height must be positive")
        self.diameter = float(diameter)
        self.height = float(height)
        self.radius = diameter / 2
        self.side_length = diameter * math.sqrt(3) / 2
    
    def get_diameter(self) -> float:
        """获取外接圆直径"""
        return self.diameter
    
    def set_diameter(self, diameter: float) -> None:
        """设置外接圆直径"""
        if diameter <= 0:
            raise ValueError("Diameter must be positive")
        self.diameter = float(diameter)
        self.radius = diameter / 2
        self.side_length = diameter * math.sqrt(3) / 2
        self.is_modified = True
    
    def get_height(self) -> float:
        """获取高度"""
        return self.height
    
    def set_height(self, height: float) -> None:
        """设置高度"""
        if height <= 0:
            raise ValueError("Height must be positive")
        self.height = float(height)
        self.is_modified = True
    
    def get_bounding_box(self) -> BoundingBox3D:
        """获取3D边界框"""
        half_height = self.height / 2
        
        return BoundingBox3D(
            self.position.x - self.radius, self.position.y - self.radius, self.position.z - half_height,
            self.position.x + self.radius, self.position.y + self.radius, self.position.z + half_height
        )
    
    def contains_point(self, point: Vector3D) -> bool:
        """检查点是否在六棱柱内"""
        # 检查高度
        half_height = self.height / 2
        if abs(point.z - self.position.z) > half_height:
            return False
        
        # 检查2D投影是否在六边形内
        dx = point.x - self.position.x
        dy = point.y - self.position.y
        
        # 六边形边界检查
        if abs(dx) > self.radius or abs(dy) > self.radius:
            return False
        
        # 检查是否在六边形边界内
        if abs(dx) <= self.radius / 2:
            return abs(dy) <= self.radius
        else:
            # 检查斜边
            slope = math.tan(math.pi / 6)  # 30度角
            return abs(dy) <= slope * (self.radius - abs(dx))
    
    def volume(self) -> float:
        """计算体积"""
        # 六边形面积 × 高度
        hex_area = 3 * math.sqrt(3) * self.radius * self.radius / 2
        return hex_area * self.height
    
    def get_2d_type(self) -> str:
        """获取对应的2D形状类型"""
        return Shape2DType.N_SIDED_POLYGON
    
    def to_string(self) -> str:
        """转换为字符串表示"""
        return f"hexagonal_prism([{self.position.x},{self.position.y},{self.position.z}], {self.diameter}, {self.height})"


class ObliqueCube(Shape):
    """斜立方体形状"""
    
    def __init__(self, position: Vector3D = None, length: float = 1.0, width: float = 1.0, height: float = 1.0, 
                 skew_x: float = 0.0, skew_y: float = 0.0):
        """
        初始化斜立方体
        
        Args:
            position: 位置向量
            length: 长度（X方向）
            width: 宽度（Y方向）
            height: 高度（Z方向）
            skew_x: X方向倾斜角度（度）
            skew_y: Y方向倾斜角度（度）
        """
        super().__init__(ShapeType.OBLIQUE_CUBE, position)
        if length <= 0 or width <= 0 or height <= 0:
            raise ValueError("Length, width and height must be positive")
        self.length = float(length)
        self.width = float(width)
        self.height = float(height)
        self.skew_x = float(skew_x)
        self.skew_y = float(skew_y)
    
    def get_skew_x(self) -> float:
        """获取X方向倾斜角度"""
        return self.skew_x
    
    def set_skew_x(self, skew_x: float) -> None:
        """设置X方向倾斜角度"""
        self.skew_x = float(skew_x)
        self.is_modified = True
    
    def get_skew_y(self) -> float:
        """获取Y方向倾斜角度"""
        return self.skew_y
    
    def set_skew_y(self, skew_y: float) -> None:
        """设置Y方向倾斜角度"""
        self.skew_y = float(skew_y)
        self.is_modified = True
    
    def get_bounding_box(self) -> BoundingBox3D:
        """获取3D边界框（考虑倾斜）"""
        half_length = self.length / 2
        half_width = self.width / 2
        half_height = self.height / 2
        
        # 计算倾斜后的边界
        skew_rad_x = math.radians(self.skew_x)
        skew_rad_y = math.radians(self.skew_y)
        
        max_offset_x = half_width * abs(math.sin(skew_rad_y))
        max_offset_y = half_length * abs(math.sin(skew_rad_x))
        
        return BoundingBox3D(
            self.position.x - half_length - max_offset_x, 
            self.position.y - half_width - max_offset_y, 
            self.position.z - half_height,
            self.position.x + half_length + max_offset_x, 
            self.position.y + half_width + max_offset_y, 
            self.position.z + half_height
        )
    
    def contains_point(self, point: Vector3D) -> bool:
        """检查点是否在斜立方体内"""
        # 简化实现：使用边界框检查
        return self.get_bounding_box().contains_point(point)
    
    def volume(self) -> float:
        """计算体积"""
        return self.length * self.width * self.height
    
    def get_2d_type(self) -> str:
        """获取对应的2D形状类型"""
        return Shape2DType.RECTANGLE
    
    def to_string(self) -> str:
        """转换为字符串表示"""
        return f"oblique_cube([{self.position.x},{self.position.y},{self.position.z}], {self.length}, {self.width}, {self.height}, {self.skew_x}, {self.skew_y})"


class RectPrism(Shape):
    """矩形棱柱形状"""
    
    def __init__(self, position: Vector3D = None, length: float = 1.0, width: float = 1.0, height: float = 1.0):
        """
        初始化矩形棱柱
        
        Args:
            position: 位置向量
            length: 长度（X方向）
            width: 宽度（Y方向）
            height: 高度（Z方向）
        """
        super().__init__(ShapeType.RECT_PRISM, position)
        if length <= 0 or width <= 0 or height <= 0:
            raise ValueError("Length, width and height must be positive")
        self.length = float(length)
        self.width = float(width)
        self.height = float(height)
    
    def get_bounding_box(self) -> BoundingBox3D:
        """获取3D边界框"""
        half_length = self.length / 2
        half_width = self.width / 2
        half_height = self.height / 2
        
        return BoundingBox3D(
            self.position.x - half_length, self.position.y - half_width, self.position.z - half_height,
            self.position.x + half_length, self.position.y + half_width, self.position.z + half_height
        )
    
    def contains_point(self, point: Vector3D) -> bool:
        """检查点是否在矩形棱柱内"""
        half_length = self.length / 2
        half_width = self.width / 2
        half_height = self.height / 2
        
        return (abs(point.x - self.position.x) <= half_length and
                abs(point.y - self.position.y) <= half_width and
                abs(point.z - self.position.z) <= half_height)
    
    def volume(self) -> float:
        """计算体积"""
        return self.length * self.width * self.height
    
    def get_2d_type(self) -> str:
        """获取对应的2D形状类型"""
        return Shape2DType.RECTANGLE
    
    def to_string(self) -> str:
        """转换为字符串表示"""
        return f"rect_prism([{self.position.x},{self.position.y},{self.position.z}], {self.length}, {self.width}, {self.height})"


class SquarePrism(Shape):
    """方形棱柱形状"""
    
    def __init__(self, position: Vector3D = None, side: float = 1.0, height: float = 1.0):
        """
        初始化方形棱柱
        
        Args:
            position: 位置向量
            side: 边长
            height: 高度
        """
        super().__init__(ShapeType.SQUARE_PRISM, position)
        if side <= 0 or height <= 0:
            raise ValueError("Side and height must be positive")
        self.side = float(side)
        self.height = float(height)
    
    def get_side(self) -> float:
        """获取边长"""
        return self.side
    
    def set_side(self, side: float) -> None:
        """设置边长"""
        if side <= 0:
            raise ValueError("Side must be positive")
        self.side = float(side)
        self.is_modified = True
    
    def get_height(self) -> float:
        """获取高度"""
        return self.height
    
    def set_height(self, height: float) -> None:
        """设置高度"""
        if height <= 0:
            raise ValueError("Height must be positive")
        self.height = float(height)
        self.is_modified = True
    
    def get_bounding_box(self) -> BoundingBox3D:
        """获取3D边界框"""
        half_side = self.side / 2
        half_height = self.height / 2
        
        return BoundingBox3D(
            self.position.x - half_side, self.position.y - half_side, self.position.z - half_height,
            self.position.x + half_side, self.position.y + half_side, self.position.z + half_height
        )
    
    def contains_point(self, point: Vector3D) -> bool:
        """检查点是否在方形棱柱内"""
        half_side = self.side / 2
        half_height = self.height / 2
        
        return (abs(point.x - self.position.x) <= half_side and
                abs(point.y - self.position.y) <= half_side and
                abs(point.z - self.position.z) <= half_height)
    
    def volume(self) -> float:
        """计算体积"""
        return self.side * self.side * self.height
    
    def get_2d_type(self) -> str:
        """获取对应的2D形状类型"""
        return Shape2DType.SQUARE
    
    def to_string(self) -> str:
        """转换为字符串表示"""
        return f"square_prism([{self.position.x},{self.position.y},{self.position.z}], {self.side}, {self.height})"


class OblongXPrism(Shape):
    """X方向椭圆棱柱"""
    
    def __init__(self, position: Vector3D = None, length: float = 1.0, width: float = 1.0, height: float = 1.0):
        """
        初始化X方向椭圆棱柱
        
        Args:
            position: 位置向量
            length: 长度（X方向）
            width: 宽度（Y方向）
            height: 高度
        """
        super().__init__(ShapeType.OBLONG_X_PRISM, position)
        if length <= 0 or width <= 0 or height <= 0:
            raise ValueError("Length, width and height must be positive")
        self.length = float(length)
        self.width = float(width)
        self.height = float(height)
        self.radius_x = length / 2
        self.radius_y = width / 2
    
    def get_bounding_box(self) -> BoundingBox3D:
        """获取3D边界框"""
        half_height = self.height / 2
        
        return BoundingBox3D(
            self.position.x - self.radius_x, self.position.y - self.radius_y, self.position.z - half_height,
            self.position.x + self.radius_x, self.position.y + self.radius_y, self.position.z + half_height
        )
    
    def contains_point(self, point: Vector3D) -> bool:
        """检查点是否在X方向椭圆棱柱内"""
        # 检查高度
        half_height = self.height / 2
        if abs(point.z - self.position.z) > half_height:
            return False
        
        # 检查2D投影是否在椭圆内
        dx = point.x - self.position.x
        dy = point.y - self.position.y
        
        # 椭圆方程：(x/a)² + (y/b)² ≤ 1
        normalized_x = dx / self.radius_x
        normalized_y = dy / self.radius_y
        
        return (normalized_x * normalized_x + normalized_y * normalized_y) <= 1.0
    
    def volume(self) -> float:
        """计算体积"""
        # 椭圆面积 × 高度
        return math.pi * self.radius_x * self.radius_y * self.height
    
    def get_2d_type(self) -> str:
        """获取对应的2D形状类型"""
        return Shape2DType.OBLONG_X
    
    def to_string(self) -> str:
        """转换为字符串表示"""
        return f"oblong_x_prism([{self.position.x},{self.position.y},{self.position.z}], {self.length}, {self.width}, {self.height})"


class OblongYPrism(Shape):
    """Y方向椭圆棱柱"""
    
    def __init__(self, length: float, width: float, height: float, position: Vector3D = None, rotation: float = 0.0):
        """
        初始化Y方向椭圆棱柱
        
        Args:
            length: 长度（Y方向）
            width: 宽度（X方向）
            height: 高度
            position: 位置向量
            rotation: 旋转角度（度）
        """
        super().__init__(ShapeType.OBLONG_Y_PRISM, position, rotation)
        if length <= 0 or width <= 0 or height <= 0:
            raise ValueError("Length, width and height must be positive")
        self.length = float(length)
        self.width = float(width)
        self.height = float(height)
        self.radius_x = width / 2
        self.radius_y = length / 2
    
    def get_length(self) -> float:
        """获取长度"""
        return self.length
    
    def set_length(self, length: float) -> None:
        """设置长度"""
        if length <= 0:
            raise ValueError("Length must be positive")
        self.length = float(length)
        self.radius_y = length / 2
        self.is_modified = True
    
    def get_width(self) -> float:
        """获取宽度"""
        return self.width
    
    def set_width(self, width: float) -> None:
        """设置宽度"""
        if width <= 0:
            raise ValueError("Width must be positive")
        self.width = float(width)
        self.radius_x = width / 2
        self.is_modified = True
    
    def get_height(self) -> float:
        """获取高度"""
        return self.height
    
    def set_height(self, height: float) -> None:
        """设置高度"""
        if height <= 0:
            raise ValueError("Height must be positive")
        self.height = float(height)
        self.is_modified = True
    
    def get_bounding_box(self) -> BoundingBox3D:
        """获取3D边界框"""
        half_height = self.height / 2
        
        return BoundingBox3D(
            self.position.x - self.radius_x, self.position.y - self.radius_y, self.position.z - half_height,
            self.position.x + self.radius_x, self.position.y + self.radius_y, self.position.z + half_height
        )
    
    def contains_point(self, point: Vector3D) -> bool:
        """检查点是否在Y方向椭圆棱柱内"""
        # 检查高度
        half_height = self.height / 2
        if abs(point.z - self.position.z) > half_height:
            return False
        
        # 检查2D投影是否在椭圆内
        dx = point.x - self.position.x
        dy = point.y - self.position.y
        
        # 椭圆方程：(x/b)² + (y/a)² ≤ 1
        normalized_x = dx / self.radius_x
        normalized_y = dy / self.radius_y
        
        return (normalized_x * normalized_x + normalized_y * normalized_y) <= 1.0
    
    def volume(self) -> float:
        """计算体积"""
        # 椭圆面积 × 高度
        return math.pi * self.radius_x * self.radius_y * self.height
    
    def get_2d_type(self) -> str:
        """获取对应的2D形状类型"""
        return Shape2DType.OBLONG_Y
    
    def to_string(self) -> str:
        """转换为字符串表示"""
        return f"OblongYPrism({self.length}, {self.width}, {self.height})"


class RoundedRectPrism(Shape):
    """圆角矩形棱柱"""
    
    def __init__(self, width: float, height: float, depth: float, radius: float, position: Vector3D = None, rotation: float = 0.0):
        """
        初始化圆角矩形棱柱
        
        Args:
            width: 宽度
            height: 高度
            depth: 深度
            radius: 圆角半径
            position: 位置向量
            rotation: 旋转角度（度）
        """
        super().__init__(ShapeType.ROUNDED_RECT_PRISM, position, rotation)
        if width <= 0 or height <= 0 or depth <= 0 or radius <= 0:
            raise ValueError("Width, height, depth and radius must be positive")
        if radius > min(width, depth) / 2:
            raise ValueError("Radius cannot be larger than half of the smaller dimension")
        self.width = float(width)
        self.height = float(height)
        self.depth = float(depth)
        self.radius = float(radius)
    
    def get_width(self) -> float:
        """获取宽度"""
        return self.width
    
    def set_width(self, width: float) -> None:
        """设置宽度"""
        if width <= 0:
            raise ValueError("Width must be positive")
        if self.radius > min(width, self.depth) / 2:
            raise ValueError("Radius cannot be larger than half of the smaller dimension")
        self.width = float(width)
        self.is_modified = True
    
    def get_height(self) -> float:
        """获取高度"""
        return self.height
    
    def set_height(self, height: float) -> None:
        """设置高度"""
        if height <= 0:
            raise ValueError("Height must be positive")
        self.height = float(height)
        self.is_modified = True
    
    def get_depth(self) -> float:
        """获取深度"""
        return self.depth
    
    def set_depth(self, depth: float) -> None:
        """设置深度"""
        if depth <= 0:
            raise ValueError("Depth must be positive")
        if self.radius > min(self.width, depth) / 2:
            raise ValueError("Radius cannot be larger than half of the smaller dimension")
        self.depth = float(depth)
        self.is_modified = True
    
    def get_radius(self) -> float:
        """获取圆角半径"""
        return self.radius
    
    def set_radius(self, radius: float) -> None:
        """设置圆角半径"""
        if radius <= 0:
            raise ValueError("Radius must be positive")
        if radius > min(self.width, self.depth) / 2:
            raise ValueError("Radius cannot be larger than half of the smaller dimension")
        self.radius = float(radius)
        self.is_modified = True
    
    def get_bounding_box(self) -> BoundingBox3D:
        """获取3D边界框"""
        half_width = self.width / 2
        half_height = self.height / 2
        half_depth = self.depth / 2
        
        return BoundingBox3D(
            self.position.x - half_width, self.position.y - half_depth, self.position.z - half_height,
            self.position.x + half_width, self.position.y + half_depth, self.position.z + half_height
        )
    
    def contains_point(self, point: Vector3D) -> bool:
        """检查点是否在圆角矩形棱柱内"""
        # 检查高度
        half_height = self.height / 2
        if abs(point.z - self.position.z) > half_height:
            return False
        
        # 检查2D投影是否在圆角矩形内
        dx = point.x - self.position.x
        dy = point.y - self.position.y
        
        half_width = self.width / 2
        half_depth = self.depth / 2
        
        # 检查是否在矩形边界内
        if abs(dx) > half_width or abs(dy) > half_depth:
            return False
        
        # 检查是否在圆角区域内
        if (abs(dx) > half_width - self.radius and 
            abs(dy) > half_depth - self.radius):
            # 计算到最近圆角中心的距离
            corner_x = half_width - self.radius
            corner_y = half_depth - self.radius
            
            if dx > 0:
                corner_x = -corner_x
            if dy > 0:
                corner_y = -corner_y
            
            distance_squared = ((dx - corner_x) ** 2 + (dy - corner_y) ** 2)
            return distance_squared <= self.radius * self.radius
        
        return True
    
    def volume(self) -> float:
        """计算体积"""
        # 圆角矩形面积 × 高度
        rect_area = self.width * self.depth
        corner_area = 4 * (self.radius * self.radius - math.pi * self.radius * self.radius / 4)
        base_area = rect_area - corner_area + math.pi * self.radius * self.radius
        return base_area * self.height
    
    def get_2d_type(self) -> str:
        """获取对应的2D形状类型"""
        return Shape2DType.ROUNDED_RECTANGLE
    
    def to_string(self) -> str:
        """转换为字符串表示"""
        return f"RoundedRectPrism({self.width}, {self.height}, {self.depth}, {self.radius})"


class ChamferedRectPrism(Shape):
    """倒角矩形棱柱"""
    
    def __init__(self, width: float, height: float, depth: float, chamfer: float, position: Vector3D = None, rotation: float = 0.0):
        """
        初始化倒角矩形棱柱
        
        Args:
            width: 宽度
            height: 高度
            depth: 深度
            chamfer: 倒角长度
            position: 位置向量
            rotation: 旋转角度（度）
        """
        super().__init__(ShapeType.CHAMFERED_RECT_PRISM, position, rotation)
        if width <= 0 or height <= 0 or depth <= 0 or chamfer <= 0:
            raise ValueError("Width, height, depth and chamfer must be positive")
        if chamfer > min(width, depth) / 2:
            raise ValueError("Chamfer cannot be larger than half of the smaller dimension")
        self.width = float(width)
        self.height = float(height)
        self.depth = float(depth)
        self.chamfer = float(chamfer)
    
    def get_width(self) -> float:
        """获取宽度"""
        return self.width
    
    def set_width(self, width: float) -> None:
        """设置宽度"""
        if width <= 0:
            raise ValueError("Width must be positive")
        if self.chamfer > min(width, self.depth) / 2:
            raise ValueError("Chamfer cannot be larger than half of the smaller dimension")
        self.width = float(width)
        self.is_modified = True
    
    def get_height(self) -> float:
        """获取高度"""
        return self.height
    
    def set_height(self, height: float) -> None:
        """设置高度"""
        if height <= 0:
            raise ValueError("Height must be positive")
        self.height = float(height)
        self.is_modified = True
    
    def get_depth(self) -> float:
        """获取深度"""
        return self.depth
    
    def set_depth(self, depth: float) -> None:
        """设置深度"""
        if depth <= 0:
            raise ValueError("Depth must be positive")
        if self.chamfer > min(self.width, depth) / 2:
            raise ValueError("Chamfer cannot be larger than half of the smaller dimension")
        self.depth = float(depth)
        self.is_modified = True
    
    def get_chamfer(self) -> float:
        """获取倒角长度"""
        return self.chamfer
    
    def set_chamfer(self, chamfer: float) -> None:
        """设置倒角长度"""
        if chamfer <= 0:
            raise ValueError("Chamfer must be positive")
        if chamfer > min(self.width, self.depth) / 2:
            raise ValueError("Chamfer cannot be larger than half of the smaller dimension")
        self.chamfer = float(chamfer)
        self.is_modified = True
    
    def get_bounding_box(self) -> BoundingBox3D:
        """获取3D边界框"""
        half_width = self.width / 2
        half_height = self.height / 2
        half_depth = self.depth / 2
        
        return BoundingBox3D(
            self.position.x - half_width, self.position.y - half_depth, self.position.z - half_height,
            self.position.x + half_width, self.position.y + half_depth, self.position.z + half_height
        )
    
    def contains_point(self, point: Vector3D) -> bool:
        """检查点是否在倒角矩形棱柱内"""
        # 检查高度
        half_height = self.height / 2
        if abs(point.z - self.position.z) > half_height:
            return False
        
        # 检查2D投影是否在倒角矩形内
        dx = point.x - self.position.x
        dy = point.y - self.position.y
        
        half_width = self.width / 2
        half_depth = self.depth / 2
        
        # 检查是否在矩形边界内
        if abs(dx) > half_width or abs(dy) > half_depth:
            return False
        
        # 检查是否在倒角区域内
        if (abs(dx) > half_width - self.chamfer and 
            abs(dy) > half_depth - self.chamfer):
            # 计算到最近倒角顶点的距离
            corner_x = half_width - self.chamfer
            corner_y = half_depth - self.chamfer
            
            if dx > 0:
                corner_x = -corner_x
            if dy > 0:
                corner_y = -corner_y
            
            # 检查点是否在倒角三角形内
            dx_corner = abs(dx - corner_x)
            dy_corner = abs(dy - corner_y)
            return dx_corner + dy_corner <= self.chamfer
        
        return True
    
    def volume(self) -> float:
        """计算体积"""
        # 倒角矩形面积 × 高度
        rect_area = self.width * self.depth
        chamfer_area = 4 * (self.chamfer * self.chamfer / 2)
        base_area = rect_area - chamfer_area
        return base_area * self.height
    
    def get_2d_type(self) -> str:
        """获取对应的2D形状类型"""
        return Shape2DType.CHAMFERED_RECTANGLE
    
    def to_string(self) -> str:
        """转换为字符串表示"""
        return f"ChamferedRectPrism({self.width}, {self.height}, {self.depth}, {self.chamfer})"


class NSidedPolygonPrism(Shape):
    """正多边形棱柱"""
    
    def __init__(self, diameter: float, height: float, sides: int, position: Vector3D = None, rotation: float = 0.0):
        """
        初始化正多边形棱柱
        
        Args:
            diameter: 外接圆直径
            height: 高度
            sides: 边数
            position: 位置向量
            rotation: 旋转角度（度）
        """
        super().__init__(ShapeType.N_SIDED_POLYGON_PRISM, position, rotation)
        if diameter <= 0 or height <= 0:
            raise ValueError("Diameter and height must be positive")
        if sides < 3:
            raise ValueError("Number of sides must be at least 3")
        self.diameter = float(diameter)
        self.height = float(height)
        self.sides = int(sides)
        self.radius = diameter / 2
    
    def get_diameter(self) -> float:
        """获取外接圆直径"""
        return self.diameter
    
    def set_diameter(self, diameter: float) -> None:
        """设置外接圆直径"""
        if diameter <= 0:
            raise ValueError("Diameter must be positive")
        self.diameter = float(diameter)
        self.radius = diameter / 2
        self.is_modified = True
    
    def get_height(self) -> float:
        """获取高度"""
        return self.height
    
    def set_height(self, height: float) -> None:
        """设置高度"""
        if height <= 0:
            raise ValueError("Height must be positive")
        self.height = float(height)
        self.is_modified = True
    
    def get_sides(self) -> int:
        """获取边数"""
        return self.sides
    
    def set_sides(self, sides: int) -> None:
        """设置边数"""
        if sides < 3:
            raise ValueError("Number of sides must be at least 3")
        self.sides = int(sides)
        self.is_modified = True
    
    def get_radius(self) -> float:
        """获取外接圆半径"""
        return self.radius
    
    def get_apothem(self) -> float:
        """获取内切圆半径"""
        return self.radius * math.cos(math.pi / self.sides)
    
    def get_side_length(self) -> float:
        """获取边长"""
        return 2 * self.radius * math.sin(math.pi / self.sides)
    
    def get_bounding_box(self) -> BoundingBox3D:
        """获取3D边界框"""
        half_height = self.height / 2
        
        return BoundingBox3D(
            self.position.x - self.radius, self.position.y - self.radius, self.position.z - half_height,
            self.position.x + self.radius, self.position.y + self.radius, self.position.z + half_height
        )
    
    def contains_point(self, point: Vector3D) -> bool:
        """检查点是否在正多边形棱柱内"""
        # 检查高度
        half_height = self.height / 2
        if abs(point.z - self.position.z) > half_height:
            return False
        
        # 检查2D投影是否在正多边形内
        dx = point.x - self.position.x
        dy = point.y - self.position.y
        
        # 使用内切圆半径进行快速检查
        if dx * dx + dy * dy <= self.get_apothem() * self.get_apothem():
            return True
        
        # 精确检查：计算点与各边的位置关系
        angle = math.atan2(dy, dx)
        if angle < 0:
            angle += 2 * math.pi
        
        # 找到点所在的角度区间
        angle_per_side = 2 * math.pi / self.sides
        side_index = int(angle / angle_per_side)
        
        # 计算该边的两个顶点
        angle1 = side_index * angle_per_side
        angle2 = (side_index + 1) * angle_per_side
        
        # 计算边的法向量
        edge_angle = (angle1 + angle2) / 2
        nx = math.cos(edge_angle)
        ny = math.sin(edge_angle)
        
        # 计算点到边的距离
        edge_distance = dx * nx + dy * ny
        
        return edge_distance <= self.get_apothem()
    
    def volume(self) -> float:
        """计算体积"""
        # 正多边形面积 × 高度
        perimeter = self.sides * self.get_side_length()
        apothem = self.get_apothem()
        base_area = (perimeter * apothem) / 2
        return base_area * self.height
    
    def get_2d_type(self) -> str:
        """获取对应的2D形状类型"""
        return Shape2DType.N_SIDED_POLYGON
    
    def to_string(self) -> str:
        """转换为字符串表示"""
        return f"NSidedPolygonPrism({self.diameter}, {self.height}, {self.sides})"


class Prism(Shape):
    """棱柱"""
    
    def __init__(self, base_shape: Shape2D, height: float, position: Vector3D = None, rotation: float = 0.0):
        """
        初始化棱柱
        
        Args:
            base_shape: 底面2D形状
            height: 高度
            position: 位置向量
            rotation: 旋转角度（度）
        """
        super().__init__(ShapeType.PRISM, position, rotation)
        if base_shape is None:
            raise ValueError("Base shape cannot be None")
        if height <= 0:
            raise ValueError("Height must be positive")
        self.base_shape = base_shape
        self.height = float(height)
    
    def get_base_shape(self) -> Shape2D:
        """获取底面形状"""
        return self.base_shape
    
    def set_base_shape(self, base_shape: Shape2D) -> None:
        """设置底面形状"""
        if base_shape is None:
            raise ValueError("Base shape cannot be None")
        self.base_shape = base_shape
        self.is_modified = True
    
    def get_height(self) -> float:
        """获取高度"""
        return self.height
    
    def set_height(self, height: float) -> None:
        """设置高度"""
        if height <= 0:
            raise ValueError("Height must be positive")
        self.height = float(height)
        self.is_modified = True
    
    def get_bounding_box(self) -> BoundingBox3D:
        """获取3D边界框"""
        min_x, min_y, max_x, max_y = self.base_shape.get_bounding_box_2d()
        half_height = self.height / 2
        
        return BoundingBox3D(
            self.position.x + min_x, self.position.y + min_y, self.position.z - half_height,
            self.position.x + max_x, self.position.y + max_y, self.position.z + half_height
        )
    
    def contains_point(self, point: Vector3D) -> bool:
        """检查点是否在棱柱内"""
        # 检查高度
        half_height = self.height / 2
        if abs(point.z - self.position.z) > half_height:
            return False
        
        # 检查2D投影是否在底面内
        dx = point.x - self.position.x
        dy = point.y - self.position.y
        test_point = Vector3D(dx, dy, 0)
        
        return self.base_shape.contains_point(test_point)
    
    def volume(self) -> float:
        """计算体积"""
        # 底面面积 × 高度
        return self.base_shape.get_area() * self.height
    
    def get_2d_type(self) -> str:
        """获取对应的2D形状类型"""
        return self.base_shape.type
    
    def to_string(self) -> str:
        """转换为字符串表示"""
        return f"Prism({self.base_shape.to_string()}, {self.height})"


class Cylinder(Shape):
    """圆柱体"""
    
    def __init__(self, radius: float, height: float, position: Vector3D = None, rotation: float = 0.0):
        """
        初始化圆柱体
        
        Args:
            radius: 半径
            height: 高度
            position: 位置向量
            rotation: 旋转角度（度）
        """
        super().__init__(ShapeType.CYLINDER, position, rotation)
        if radius <= 0 or height <= 0:
            raise ValueError("Radius and height must be positive")
        self.radius = float(radius)
        self.height = float(height)
    
    def get_radius(self) -> float:
        """获取半径"""
        return self.radius
    
    def set_radius(self, radius: float) -> None:
        """设置半径"""
        if radius <= 0:
            raise ValueError("Radius must be positive")
        self.radius = float(radius)
        self.is_modified = True
    
    def get_height(self) -> float:
        """获取高度"""
        return self.height
    
    def set_height(self, height: float) -> None:
        """设置高度"""
        if height <= 0:
            raise ValueError("Height must be positive")
        self.height = float(height)
        self.is_modified = True
    
    def get_bounding_box(self) -> BoundingBox3D:
        """获取3D边界框"""
        half_height = self.height / 2
        
        return BoundingBox3D(
            self.position.x - self.radius, self.position.y - self.radius, self.position.z - half_height,
            self.position.x + self.radius, self.position.y + self.radius, self.position.z + half_height
        )
    
    def contains_point(self, point: Vector3D) -> bool:
        """检查点是否在圆柱体内"""
        # 检查高度
        half_height = self.height / 2
        if abs(point.z - self.position.z) > half_height:
            return False
        
        # 检查2D投影是否在圆形内
        dx = point.x - self.position.x
        dy = point.y - self.position.y
        distance_squared = dx * dx + dy * dy
        
        return distance_squared <= self.radius * self.radius
    
    def volume(self) -> float:
        """计算体积"""
        # 圆形面积 × 高度
        return math.pi * self.radius * self.radius * self.height
    
    def get_2d_type(self) -> str:
        """获取对应的2D形状类型"""
        return Shape2DType.CIRCLE
    
    def to_string(self) -> str:
        """转换为字符串表示"""
        return f"Cylinder({self.radius}, {self.height})"


class Trace(Shape):
    """轨迹（细长矩形棱柱）"""
    
    def __init__(self, width: float, height: float, length: float, position: Vector3D = None, rotation: float = 0.0):
        """
        初始化轨迹
        
        Args:
            width: 宽度
            height: 高度
            length: 长度
            position: 位置向量
            rotation: 旋转角度（度）
        """
        super().__init__(ShapeType.TRACE, position, rotation)
        if width <= 0 or height <= 0 or length <= 0:
            raise ValueError("Width, height and length must be positive")
        self.width = float(width)
        self.height = float(height)
        self.length = float(length)
    
    def get_width(self) -> float:
        """获取宽度"""
        return self.width
    
    def set_width(self, width: float) -> None:
        """设置宽度"""
        if width <= 0:
            raise ValueError("Width must be positive")
        self.width = float(width)
        self.is_modified = True
    
    def get_height(self) -> float:
        """获取高度"""
        return self.height
    
    def set_height(self, height: float) -> None:
        """设置高度"""
        if height <= 0:
            raise ValueError("Height must be positive")
        self.height = float(height)
        self.is_modified = True
    
    def get_length(self) -> float:
        """获取长度"""
        return self.length
    
    def set_length(self, length: float) -> None:
        """设置长度"""
        if length <= 0:
            raise ValueError("Length must be positive")
        self.length = float(length)
        self.is_modified = True
    
    def get_bounding_box(self) -> BoundingBox3D:
        """获取3D边界框"""
        half_width = self.width / 2
        half_height = self.height / 2
        half_length = self.length / 2
        
        return BoundingBox3D(
            self.position.x - half_width, self.position.y - half_length, self.position.z - half_height,
            self.position.x + half_width, self.position.y + half_length, self.position.z + half_height
        )
    
    def contains_point(self, point: Vector3D) -> bool:
        """检查点是否在轨迹内"""
        half_width = self.width / 2
        half_height = self.height / 2
        half_length = self.length / 2
        
        return (abs(point.x - self.position.x) <= half_width and
                abs(point.y - self.position.y) <= half_length and
                abs(point.z - self.position.z) <= half_height)
    
    def volume(self) -> float:
        """计算体积"""
        return self.width * self.height * self.length
    
    def get_2d_type(self) -> str:
        """获取对应的2D形状类型"""
        return Shape2DType.RECTANGLE
    
    def to_string(self) -> str:
        """转换为字符串表示"""
        return f"Trace({self.width}, {self.height}, {self.length})"


# ============================================================================
# 2D形状类实现
# ============================================================================

class Circle(Shape2D):
    """圆形"""
    
    def __init__(self, position: Vector2D = None, radius: float = 1.0):
        """
        初始化圆形
        
        Args:
            position: 位置向量
            radius: 半径
        """
        super().__init__(Shape2DType.CIRCLE, position)
        if radius <= 0:
            raise ValueError("Radius must be positive")
        self.radius = float(radius)
    
    def get_radius(self) -> float:
        """获取半径"""
        return self.radius
    
    def set_radius(self, radius: float) -> None:
        """设置半径"""
        if radius <= 0:
            raise ValueError("Radius must be positive")
        self.radius = float(radius)
        self.is_modified = True
    
    def get_bounding_box_2d(self) -> BoundingBox2D:
        """获取2D边界框"""
        return BoundingBox2D(
            self.position.x - self.radius, self.position.y - self.radius,
            self.position.x + self.radius, self.position.y + self.radius
        )
    
    def contains_point(self, point: Vector2D) -> bool:
        """检查点是否在圆形内"""
        dx = point.x - self.position.x
        dy = point.y - self.position.y
        distance_squared = dx * dx + dy * dy
        return distance_squared <= self.radius * self.radius
    
    def get_area(self) -> float:
        """计算面积"""
        return math.pi * self.radius * self.radius
    
    def to_string(self) -> str:
        """转换为字符串表示"""
        return f"circle([{self.position.x},{self.position.y}], {self.radius})"


class Rectangle(Shape2D):
    """矩形"""
    
    def __init__(self, position: Vector2D = None, width: float = 1.0, height: float = 1.0):
        """
        初始化矩形
        
        Args:
            position: 位置向量
            width: 宽度
            height: 高度
        """
        super().__init__(Shape2DType.RECTANGLE, position)
        if width <= 0 or height <= 0:
            raise ValueError("Width and height must be positive")
        self.width = float(width)
        self.height = float(height)
    
    def get_width(self) -> float:
        """获取宽度"""
        return self.width
    
    def set_width(self, width: float) -> None:
        """设置宽度"""
        if width <= 0:
            raise ValueError("Width must be positive")
        self.width = float(width)
        self.is_modified = True
    
    def get_height(self) -> float:
        """获取高度"""
        return self.height
    
    def set_height(self, height: float) -> None:
        """设置高度"""
        if height <= 0:
            raise ValueError("Height must be positive")
        self.height = float(height)
        self.is_modified = True
    
    def get_bounding_box_2d(self) -> BoundingBox2D:
        """获取2D边界框"""
        half_width = self.width / 2
        half_height = self.height / 2
        
        return BoundingBox2D(
            self.position.x - half_width, self.position.y - half_height,
            self.position.x + half_width, self.position.y + half_height
        )
    
    def contains_point(self, point: Vector2D) -> bool:
        """检查点是否在矩形内"""
        half_width = self.width / 2
        half_height = self.height / 2
        
        return (abs(point.x - self.position.x) <= half_width and
                abs(point.y - self.position.y) <= half_height)
    
    def get_area(self) -> float:
        """计算面积"""
        return self.width * self.height
    
    def to_string(self) -> str:
        """转换为字符串表示"""
        return f"rectangle([{self.position.x},{self.position.y}], {self.width}, {self.height})"


class Square(Shape2D):
    """正方形"""
    
    def __init__(self, position: Vector2D = None, side: float = 1.0):
        """
        初始化正方形
        
        Args:
            position: 位置向量
            side: 边长
        """
        super().__init__(Shape2DType.SQUARE, position)
        if side <= 0:
            raise ValueError("Side must be positive")
        self.side = float(side)
    
    def get_side(self) -> float:
        """获取边长"""
        return self.side
    
    def set_side(self, side: float) -> None:
        """设置边长"""
        if side <= 0:
            raise ValueError("Side must be positive")
        self.side = float(side)
        self.is_modified = True
    
    def get_bounding_box_2d(self) -> BoundingBox2D:
        """获取2D边界框"""
        half_side = self.side / 2
        
        return BoundingBox2D(
            self.position.x - half_side, self.position.y - half_side,
            self.position.x + half_side, self.position.y + half_side
        )
    
    def contains_point(self, point: Vector2D) -> bool:
        """检查点是否在正方形内"""
        half_side = self.side / 2
        
        return (abs(point.x - self.position.x) <= half_side and
                abs(point.y - self.position.y) <= half_side)
    
    def get_area(self) -> float:
        """计算面积"""
        return self.side * self.side
    
    def to_string(self) -> str:
        """转换为字符串表示"""
        return f"square([{self.position.x},{self.position.y}], {self.side})"


class OblongX(Shape2D):
    """X方向椭圆形"""
    
    def __init__(self, position: Vector2D = None, length: float = 1.0, width: float = 1.0):
        """
        初始化X方向椭圆形
        
        Args:
            position: 位置向量
            length: 长度（X方向）
            width: 宽度（Y方向）
        """
        super().__init__(Shape2DType.OBLONG_X, position)
        if length <= 0 or width <= 0:
            raise ValueError("Length and width must be positive")
        self.length = float(length)
        self.width = float(width)
        self.radius_x = length / 2
        self.radius_y = width / 2
    
    def get_length(self) -> float:
        """获取长度"""
        return self.length
    
    def set_length(self, length: float) -> None:
        """设置长度"""
        if length <= 0:
            raise ValueError("Length must be positive")
        self.length = float(length)
        self.radius_x = length / 2
        self.is_modified = True
    
    def get_width(self) -> float:
        """获取宽度"""
        return self.width
    
    def set_width(self, width: float) -> None:
        """设置宽度"""
        if width <= 0:
            raise ValueError("Width must be positive")
        self.width = float(width)
        self.radius_y = width / 2
        self.is_modified = True
    
    def get_bounding_box_2d(self) -> BoundingBox2D:
        """获取2D边界框"""
        return BoundingBox2D(
            self.position.x - self.radius_x, self.position.y - self.radius_y,
            self.position.x + self.radius_x, self.position.y + self.radius_y
        )
    
    def contains_point(self, point: Vector2D) -> bool:
        """检查点是否在X方向椭圆内"""
        dx = point.x - self.position.x
        dy = point.y - self.position.y
        
        # 椭圆方程：(x/a)² + (y/b)² ≤ 1
        normalized_x = dx / self.radius_x
        normalized_y = dy / self.radius_y
        
        return (normalized_x * normalized_x + normalized_y * normalized_y) <= 1.0
    
    def get_area(self) -> float:
        """计算面积"""
        return math.pi * self.radius_x * self.radius_y
    
    def to_string(self) -> str:
        """转换为字符串表示"""
        return f"oblong_x([{self.position.x},{self.position.y}], {self.length}, {self.width})"


class OblongY(Shape2D):
    """Y方向椭圆形"""
    
    def __init__(self, position: Vector2D = None, length: float = 1.0, width: float = 1.0):
        """
        初始化Y方向椭圆形
        
        Args:
            position: 位置向量
            length: 长度（Y方向）
            width: 宽度（X方向）
        """
        super().__init__(Shape2DType.OBLONG_Y, position)
        if length <= 0 or width <= 0:
            raise ValueError("Length and width must be positive")
        self.length = float(length)
        self.width = float(width)
        self.radius_x = width / 2
        self.radius_y = length / 2
    
    def get_length(self) -> float:
        """获取长度"""
        return self.length
    
    def set_length(self, length: float) -> None:
        """设置长度"""
        if length <= 0:
            raise ValueError("Length must be positive")
        self.length = float(length)
        self.radius_y = length / 2
        self.is_modified = True
    
    def get_width(self) -> float:
        """获取宽度"""
        return self.width
    
    def set_width(self, width: float) -> None:
        """设置宽度"""
        if width <= 0:
            raise ValueError("Width must be positive")
        self.width = float(width)
        self.radius_x = width / 2
        self.is_modified = True
    
    def get_bounding_box_2d(self) -> BoundingBox2D:
        """获取2D边界框"""
        return BoundingBox2D(
            self.position.x - self.radius_x, self.position.y - self.radius_y,
            self.position.x + self.radius_x, self.position.y + self.radius_y
        )
    
    def contains_point(self, point: Vector2D) -> bool:
        """检查点是否在Y方向椭圆内"""
        dx = point.x - self.position.x
        dy = point.y - self.position.y
        
        # 椭圆方程：(x/b)² + (y/a)² ≤ 1
        normalized_x = dx / self.radius_x
        normalized_y = dy / self.radius_y
        
        return (normalized_x * normalized_x + normalized_y * normalized_y) <= 1.0
    
    def get_area(self) -> float:
        """计算面积"""
        return math.pi * self.radius_x * self.radius_y
    
    def to_string(self) -> str:
        """转换为字符串表示"""
        return f"oblong_y([{self.position.x},{self.position.y}], {self.length}, {self.width})"


class RoundedRectangle(Shape2D):
    """圆角矩形"""
    
    def __init__(self, position: Vector2D = None, width: float = 1.0, height: float = 1.0, radius: float = 0.1):
        """
        初始化圆角矩形
        
        Args:
            position: 位置向量
            width: 宽度
            height: 高度
            radius: 圆角半径
        """
        super().__init__(Shape2DType.ROUNDED_RECTANGLE, position)
        if width <= 0 or height <= 0 or radius <= 0:
            raise ValueError("Width, height and radius must be positive")
        if radius > min(width, height) / 2:
            raise ValueError("Radius cannot be larger than half of the smaller dimension")
        self.width = float(width)
        self.height = float(height)
        self.radius = float(radius)
    
    def get_width(self) -> float:
        """获取宽度"""
        return self.width
    
    def set_width(self, width: float) -> None:
        """设置宽度"""
        if width <= 0:
            raise ValueError("Width must be positive")
        if self.radius > min(width, self.height) / 2:
            raise ValueError("Radius cannot be larger than half of the smaller dimension")
        self.width = float(width)
        self.is_modified = True
    
    def get_height(self) -> float:
        """获取高度"""
        return self.height
    
    def set_height(self, height: float) -> None:
        """设置高度"""
        if height <= 0:
            raise ValueError("Height must be positive")
        if self.radius > min(self.width, height) / 2:
            raise ValueError("Radius cannot be larger than half of the smaller dimension")
        self.height = float(height)
        self.is_modified = True
    
    def get_radius(self) -> float:
        """获取圆角半径"""
        return self.radius
    
    def set_radius(self, radius: float) -> None:
        """设置圆角半径"""
        if radius <= 0:
            raise ValueError("Radius must be positive")
        if radius > min(self.width, self.height) / 2:
            raise ValueError("Radius cannot be larger than half of the smaller dimension")
        self.radius = float(radius)
        self.is_modified = True
    
    def get_bounding_box_2d(self) -> BoundingBox2D:
        """获取2D边界框"""
        half_width = self.width / 2
        half_height = self.height / 2
        
        return BoundingBox2D(
            self.position.x - half_width, self.position.y - half_height,
            self.position.x + half_width, self.position.y + half_height
        )
    
    def contains_point(self, point: Vector2D) -> bool:
        """检查点是否在圆角矩形内"""
        dx = point.x - self.position.x
        dy = point.y - self.position.y
        
        half_width = self.width / 2
        half_height = self.height / 2
        
        # 检查是否在矩形边界内
        if abs(dx) > half_width or abs(dy) > half_height:
            return False
        
        # 检查是否在圆角区域内
        if (abs(dx) > half_width - self.radius and 
            abs(dy) > half_height - self.radius):
            # 计算到最近圆角中心的距离
            corner_x = half_width - self.radius
            corner_y = half_height - self.radius
            
            if dx > 0:
                corner_x = -corner_x
            if dy > 0:
                corner_y = -corner_y
            
            distance_squared = ((dx - corner_x) ** 2 + (dy - corner_y) ** 2)
            return distance_squared <= self.radius * self.radius
        
        return True
    
    def get_area(self) -> float:
        """计算面积"""
        # 圆角矩形面积
        rect_area = self.width * self.height
        corner_area = 4 * (self.radius * self.radius - math.pi * self.radius * self.radius / 4)
        return rect_area - corner_area + math.pi * self.radius * self.radius
    
    def to_string(self) -> str:
        """转换为字符串表示"""
        return f"rounded_rectangle([{self.position.x},{self.position.y}], {self.width}, {self.height}, {self.radius})"


class ChamferedRectangle(Shape2D):
    """倒角矩形"""
    
    def __init__(self, position: Vector2D = None, width: float = 1.0, height: float = 1.0, chamfer: float = 0.1):
        """
        初始化倒角矩形
        
        Args:
            position: 位置向量
            width: 宽度
            height: 高度
            chamfer: 倒角长度
        """
        super().__init__(Shape2DType.CHAMFERED_RECTANGLE, position)
        if width <= 0 or height <= 0 or chamfer <= 0:
            raise ValueError("Width, height and chamfer must be positive")
        if chamfer > min(width, height) / 2:
            raise ValueError("Chamfer cannot be larger than half of the smaller dimension")
        self.width = float(width)
        self.height = float(height)
        self.chamfer = float(chamfer)
    
    def get_width(self) -> float:
        """获取宽度"""
        return self.width
    
    def set_width(self, width: float) -> None:
        """设置宽度"""
        if width <= 0:
            raise ValueError("Width must be positive")
        if self.chamfer > min(width, self.height) / 2:
            raise ValueError("Chamfer cannot be larger than half of the smaller dimension")
        self.width = float(width)
        self.is_modified = True
    
    def get_height(self) -> float:
        """获取高度"""
        return self.height
    
    def set_height(self, height: float) -> None:
        """设置高度"""
        if height <= 0:
            raise ValueError("Height must be positive")
        if self.chamfer > min(self.width, height) / 2:
            raise ValueError("Chamfer cannot be larger than half of the smaller dimension")
        self.height = float(height)
        self.is_modified = True
    
    def get_chamfer(self) -> float:
        """获取倒角长度"""
        return self.chamfer
    
    def set_chamfer(self, chamfer: float) -> None:
        """设置倒角长度"""
        if chamfer <= 0:
            raise ValueError("Chamfer must be positive")
        if chamfer > min(self.width, self.height) / 2:
            raise ValueError("Chamfer cannot be larger than half of the smaller dimension")
        self.chamfer = float(chamfer)
        self.is_modified = True
    
    def get_bounding_box_2d(self) -> BoundingBox2D:
        """获取2D边界框"""
        half_width = self.width / 2
        half_height = self.height / 2
        
        return BoundingBox2D(
            self.position.x - half_width, self.position.y - half_height,
            self.position.x + half_width, self.position.y + half_height
        )
    
    def contains_point(self, point: Vector2D) -> bool:
        """检查点是否在倒角矩形内"""
        dx = point.x - self.position.x
        dy = point.y - self.position.y
        
        half_width = self.width / 2
        half_height = self.height / 2
        
        # 检查是否在矩形边界内
        if abs(dx) > half_width or abs(dy) > half_height:
            return False
        
        # 检查是否在倒角区域内
        if (abs(dx) > half_width - self.chamfer and 
            abs(dy) > half_height - self.chamfer):
            # 计算到最近倒角顶点的距离
            corner_x = half_width - self.chamfer
            corner_y = half_height - self.chamfer
            
            if dx > 0:
                corner_x = -corner_x
            if dy > 0:
                corner_y = -corner_y
            
            # 检查点是否在倒角三角形内
            dx_corner = abs(dx - corner_x)
            dy_corner = abs(dy - corner_y)
            return dx_corner + dy_corner <= self.chamfer
        
        return True
    
    def get_area(self) -> float:
        """计算面积"""
        # 倒角矩形面积
        rect_area = self.width * self.height
        chamfer_area = 4 * (self.chamfer * self.chamfer / 2)
        return rect_area - chamfer_area
    
    def to_string(self) -> str:
        """转换为字符串表示"""
        return f"chamfered_rectangle([{self.position.x},{self.position.y}], {self.width}, {self.height}, {self.chamfer})"


class NSidedPolygon(Shape2D):
    """正多边形"""
    
    def __init__(self, position: Vector2D = None, diameter: float = 1.0, sides: int = 6):
        """
        初始化正多边形
        
        Args:
            position: 位置向量
            diameter: 外接圆直径
            sides: 边数
        """
        super().__init__(Shape2DType.N_SIDED_POLYGON, position)
        if diameter <= 0:
            raise ValueError("Diameter must be positive")
        if sides < 3:
            raise ValueError("Number of sides must be at least 3")
        self.diameter = float(diameter)
        self.sides = int(sides)
        self.radius = diameter / 2
    
    def get_diameter(self) -> float:
        """获取外接圆直径"""
        return self.diameter
    
    def set_diameter(self, diameter: float) -> None:
        """设置外接圆直径"""
        if diameter <= 0:
            raise ValueError("Diameter must be positive")
        self.diameter = float(diameter)
        self.radius = diameter / 2
        self.is_modified = True
    
    def get_sides(self) -> int:
        """获取边数"""
        return self.sides
    
    def set_sides(self, sides: int) -> None:
        """设置边数"""
        if sides < 3:
            raise ValueError("Number of sides must be at least 3")
        self.sides = int(sides)
        self.is_modified = True
    
    def get_radius(self) -> float:
        """获取外接圆半径"""
        return self.radius
    
    def get_apothem(self) -> float:
        """获取内切圆半径"""
        return self.radius * math.cos(math.pi / self.sides)
    
    def get_side_length(self) -> float:
        """获取边长"""
        return 2 * self.radius * math.sin(math.pi / self.sides)
    
    def get_bounding_box_2d(self) -> BoundingBox2D:
        """获取2D边界框"""
        return BoundingBox2D(
            self.position.x - self.radius, self.position.y - self.radius,
            self.position.x + self.radius, self.position.y + self.radius
        )
    
    def contains_point(self, point: Vector2D) -> bool:
        """检查点是否在正多边形内"""
        dx = point.x - self.position.x
        dy = point.y - self.position.y
        
        # 使用内切圆半径进行快速检查
        if dx * dx + dy * dy <= self.get_apothem() * self.get_apothem():
            return True
        
        # 精确检查：计算点与各边的位置关系
        angle = math.atan2(dy, dx)
        if angle < 0:
            angle += 2 * math.pi
        
        # 找到点所在的角度区间
        angle_per_side = 2 * math.pi / self.sides
        side_index = int(angle / angle_per_side)
        
        # 计算该边的两个顶点
        angle1 = side_index * angle_per_side
        angle2 = (side_index + 1) * angle_per_side
        
        # 计算边的法向量
        edge_angle = (angle1 + angle2) / 2
        nx = math.cos(edge_angle)
        ny = math.sin(edge_angle)
        
        # 计算点到边的距离
        edge_distance = dx * nx + dy * ny
        
        return edge_distance <= self.get_apothem()
    
    def get_area(self) -> float:
        """计算面积"""
        # 正多边形面积
        perimeter = self.sides * self.get_side_length()
        apothem = self.get_apothem()
        return (perimeter * apothem) / 2
    
    def to_string(self) -> str:
        """转换为字符串表示"""
        return f"n_sided_polygon([{self.position.x},{self.position.y}], {self.diameter}, {self.sides})"


# ============================================================================
# 形状工厂类
# ============================================================================

class ShapeFactory:
    """形状工厂类，用于创建各种形状对象"""
    
    @staticmethod
    def create_3d_shape(shape_type: str, **kwargs) -> Shape:
        """
        创建3D形状对象
        
        Args:
            shape_type: 形状类型字符串
            **kwargs: 形状参数
            
        Returns:
            Shape: 形状对象
        """
        shape_type = shape_type.lower()
        
        if shape_type == "cube":
            return Cube(**kwargs)
        elif shape_type == "cylinder":
            return Cylinder(**kwargs)
        elif shape_type == "hexagonal_prism":
            return HexagonalPrism(**kwargs)
        elif shape_type == "oblique_cube":
            return ObliqueCube(**kwargs)
        elif shape_type == "prism":
            return Prism(**kwargs)
        elif shape_type == "rect_prism":
            return RectPrism(**kwargs)
        elif shape_type == "square_prism":
            return SquarePrism(**kwargs)
        elif shape_type == "oblong_x_prism":
            return OblongXPrism(**kwargs)
        elif shape_type == "oblong_y_prism":
            return OblongYPrism(**kwargs)
        elif shape_type == "rounded_rect_prism":
            return RoundedRectPrism(**kwargs)
        elif shape_type == "chamfered_rect_prism":
            return ChamferedRectPrism(**kwargs)
        elif shape_type == "n_sided_polygon_prism":
            return NSidedPolygonPrism(**kwargs)
        elif shape_type == "trace":
            return Trace(**kwargs)
        else:
            raise ValueError(f"Unknown 3D shape type: {shape_type}")
    
    @staticmethod
    def create_2d_shape(shape_type: str, **kwargs) -> Shape2D:
        """
        创建2D形状对象
        
        Args:
            shape_type: 形状类型字符串
            **kwargs: 形状参数
            
        Returns:
            Shape2D: 2D形状对象
        """
        shape_type = shape_type.lower()
        
        if shape_type == "circle":
            return Circle(**kwargs)
        elif shape_type == "rectangle":
            return Rectangle(**kwargs)
        elif shape_type == "square":
            return Square(**kwargs)
        elif shape_type == "oblong_x":
            return OblongX(**kwargs)
        elif shape_type == "oblong_y":
            return OblongY(**kwargs)
        elif shape_type == "rounded_rectangle":
            return RoundedRectangle(**kwargs)
        elif shape_type == "chamfered_rectangle":
            return ChamferedRectangle(**kwargs)
        elif shape_type == "n_sided_polygon":
            return NSidedPolygon(**kwargs)
        else:
            raise ValueError(f"Unknown 2D shape type: {shape_type}")
