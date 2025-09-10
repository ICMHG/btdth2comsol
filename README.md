# BTD Thermal JSON到COMSOL MPH转换器

一个强大的工具，用于将BTD Thermal JSON格式的热分析数据转换为COMSOL MPH文件，支持完整的几何建模、材料属性、热物理场设置和求解器配置。

## 功能特性

### 🏗️ 完整的几何系统
- **3D形状支持**: 13种3D几何形状，包括立方体、圆柱体、六棱柱、斜立方体、棱柱、矩形棱柱、方形棱柱、椭圆形棱柱、圆角矩形棱柱、倒角矩形棱柱、N边形棱柱、轨迹等
- **2D形状支持**: 8种2D形状，包括圆形、矩形、正方形、椭圆形、圆角矩形、倒角矩形、N边形等
- **几何层次结构**: 支持复杂的组件层次关系和布尔运算
- **位置和变换**: 支持3D位置、旋转、缩放等变换操作

### 🔬 先进的材料系统
- **温度相关属性**: 支持材料属性随温度变化的线性插值
- **复合材料**: 支持基于体积分数的复合材料定义
- **对象材料**: 支持为特定几何对象分配材料
- **材料验证**: 完整的材料属性验证和一致性检查

### 🌡️ 热物理场设置
- **热传导**: 自动设置热传导物理场接口
- **热源**: 支持表面热流、功率图和总功率等热源
- **边界条件**: 环境温度、对流边界条件等
- **材料属性**: 导热系数、密度、比热容等温度相关属性

### 🎯 智能解析系统
- **JSON解析**: 完整的BTD Thermal JSON格式解析
- **数据验证**: 多层次的数据验证和一致性检查
- **错误处理**: 详细的错误报告和诊断信息
- **模块化设计**: 分离的解析器模块，便于维护和扩展

### ⚙️ COMSOL集成
- **MPH文件生成**: 直接生成可运行的COMSOL MPH文件
- **几何构建**: 自动构建COMSOL几何模型
- **材料分配**: 自动创建和分配COMSOL材料
- **网格生成**: 自动生成适合的网格
- **求解器配置**: 配置稳态热传导求解器

## 系统要求

- **Python**: 3.8+
- **COMSOL**: 5.0+ (需要MPh Python库)
- **操作系统**: Windows, macOS, Linux

## 安装

### 1. 克隆仓库
```bash
git clone <repository-url>
cd btd_comsol_converter
```

### 2. 创建虚拟环境（推荐）
```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows
```

### 3. 安装依赖
```bash
pip install -r requirements.txt
```

### 4. 安装MPh库（COMSOL Python接口）
```bash
pip install mph
```

**注意**: MPh库需要COMSOL许可证和正确的环境配置。

## 使用方法

### 基本用法

```bash
# 基本转换
python main.py input.json output.mph

# 详细日志输出
python main.py -v input.json output.mph

# 仅验证输入文件
python main.py --validate-only input.json output.mph

# 导出解析后的数据
python main.py input.json output.mph --export-parsed parsed_data.json
```

### 命令行参数

- `input_file`: 输入的BTD Thermal JSON文件路径
- `output_file`: 输出的COMSOL MPH文件路径
- `-v, --verbose`: 启用详细日志输出
- `--validate-only`: 仅验证输入文件，不进行转换
- `--export-parsed`: 导出解析后的数据到指定JSON文件

### 输入文件格式

BTD Thermal JSON文件应包含以下主要部分：

```json
{
  "model_name": "示例热分析模型",
  "materials": {
    "base_materials": [...],
    "composite_materials": [...],
    "object_materials": [...]
  },
  "geometry": {
    "sections": [...],
    "stacked_die_sections": [...],
    "package_components": [...]
  },
  "parameters": {...},
  "thermal_parameters": {...},
  "netlist": {...},
  "power_maps": {...}
}
```

## 项目结构

```
btd_comsol_converter/
├── src/
│   ├── core/           # 核心数据结构和管理器
│   ├── models/         # 数据模型类
│   ├── parser/         # 解析器模块
│   ├── converter/      # COMSOL转换器
│   └── utils/          # 工具函数
├── tests/              # 测试文件
├── examples/           # 示例文件
├── main.py            # 主程序入口
├── requirements.txt    # 依赖列表
└── README.md          # 项目文档
```

## 核心模块

### 解析器模块

- **`BTDJsonParser`**: 主要的JSON解析器，协调其他解析器
- **`MaterialParser`**: 材料定义解析器
- **`GeometryParser`**: 几何结构解析器
- **`ShapeParser`**: 形状定义解析器

### 转换器模块

- **`MPHConverter`**: 主要的COMSOL MPH转换器
- **`GeometryConverter`**: 几何转换器
- **`MaterialConverter`**: 材料转换器
- **`PhysicsConverter`**: 物理场转换器

### 核心数据结构

- **`ThermalInfo`**: 热分析信息的中央管理器
- **`MaterialInfo`**: 材料信息类
- **`Shape`/`Shape2D`**: 几何形状基类
- **`BaseComponent`**: 组件基类

## 开发指南

### 添加新的几何形状

1. 在 `src/models/shape.py` 中定义新的形状类
2. 继承自 `Shape` 或 `Shape2D`
3. 实现必要的方法：`get_bounding_box`, `contains_point`, `to_string`
4. 在 `ShapeParser` 中添加解析支持

### 添加新的材料类型

1. 在 `src/models/material.py` 中定义新的材料类
2. 在 `MaterialParser` 中添加解析逻辑
3. 在 `MaterialConverter` 中添加COMSOL转换逻辑

### 扩展物理场支持

1. 在 `src/converter/physics_converter.py` 中添加新的物理场接口
2. 在 `MPHConverter` 中集成新的物理场设置

## 测试

运行测试套件：

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试文件
python -m pytest tests/test_models.py

# 运行测试并显示覆盖率
python -m pytest --cov=src tests/
```

## 错误处理

系统提供详细的错误处理和诊断信息：

- **解析错误**: 详细的JSON解析错误信息
- **验证错误**: 数据一致性和完整性检查
- **转换错误**: COMSOL模型创建过程中的错误
- **日志记录**: 完整的操作日志，便于调试

## 性能优化

- **内存管理**: 高效的数据结构设计
- **批量处理**: 支持大型模型的批量转换
- **并行处理**: 可选的并行几何处理
- **缓存机制**: 智能缓存重复计算

## 故障排除

### 常见问题

1. **MPh库导入错误**
   - 确保COMSOL已正确安装
   - 检查Python环境变量设置
   - 验证COMSOL许可证

2. **几何转换失败**
   - 检查输入JSON的几何定义
   - 验证形状参数的有效性
   - 查看详细错误日志

3. **材料属性错误**
   - 验证材料属性的数值范围
   - 检查温度相关属性的插值点
   - 确保材料引用的一致性

### 调试模式

启用详细日志输出：

```bash
python main.py -v input.json output.mph
```

查看日志文件 `btd_converter.log` 获取详细信息。

## 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 支持

如果您遇到问题或有建议，请：

1. 查看 [Issues](../../issues) 页面
2. 创建新的 Issue 描述问题
3. 联系开发团队

## 更新日志

### v1.0.0
- 完整的几何系统实现
- 材料系统和温度相关属性支持
- JSON解析器模块
- COMSOL MPH转换器
- 命令行界面
- 完整的测试套件

---

**注意**: 本工具需要有效的COMSOL许可证才能生成MPH文件。请确保您的COMSOL安装和许可证配置正确。

