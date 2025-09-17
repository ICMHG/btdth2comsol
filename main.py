#!/usr/bin/env python3
"""
BTD Thermal文件到COMSOL MPH转换器主程序
支持.btd_th和.json文件格式
"""

import sys
import argparse
from pathlib import Path
from typing import Optional
from loguru import logger

from core.thermal_info import ThermalInfo, BTDJsonParsingError
from converter.mph_converter import MPHConverter, ComsolCreationError


def setup_logging(verbose: bool = False) -> None:
    """设置日志配置"""
    # 移除默认的日志处理器
    logger.remove()
    
    # 添加控制台日志处理器
    if verbose:
        logger.add(sys.stderr, level="DEBUG", format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")
    else:
        logger.add(sys.stderr, level="INFO", format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>")
    
    # 添加文件日志处理器
    log_file = Path("btd_converter.log")
    logger.add(log_file, level="DEBUG", format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}")


def validate_input_file(input_file: Path) -> bool:
    """验证输入文件"""
    if not input_file.exists():
        logger.error(f"输入文件不存在: {input_file}")
        return False
    
    if not input_file.is_file():
        logger.error(f"输入路径不是文件: {input_file}")
        return False
    
    # 支持.btd_th和.json文件格式
    if input_file.suffix.lower() not in ['.json', '.btd_th']:
        logger.error(f"输入文件必须是JSON或BTD_TH格式: {input_file}")
        return False
    
    return True


def validate_output_file(output_file: Path) -> bool:
    """验证输出文件"""
    output_dir = output_file.parent
    
    if not output_dir.exists():
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"创建输出目录: {output_dir}")
        except Exception as e:
            logger.error(f"无法创建输出目录: {e}")
            return False
    
    if not output_dir.is_dir():
        logger.error(f"输出路径不是目录: {output_dir}")
        return False
    
    if output_file.suffix.lower() != '.mph':
        logger.error(f"输出文件必须是MPH格式: {output_file}")
        return False
    
    return True


def parse_btd_file(input_file: Path) -> Optional[object]:
    """解析BTD文件（支持.btd_th和.json格式）"""
    try:
        logger.info(f"开始解析BTD文件: {input_file}")
        
        # 创建ThermalInfo对象并加载JSON文件
        thermal_info = ThermalInfo()
        thermal_info.load_from_json(input_file)
        
        logger.info("BTD文件解析完成")
        return thermal_info
        
    except BTDJsonParsingError as e:
        logger.error(f"BTD文件解析错误: {e}")
        return None
    except Exception as e:
        logger.error(f"BTD文件解析过程中发生未知错误: {e}")
        return None


def convert_to_mph(thermal_info: object, output_file: Path) -> bool:
    """转换为MPH文件"""
    try:
        logger.info(f"开始转换为MPH文件: {output_file}")
        
        # 创建MPH转换器
        converter = MPHConverter()
        
        # 执行转换
        success = converter.convert(thermal_info, output_file)
        
        if success:
            logger.info("MPH文件转换完成")
            return True
        else:
            logger.error("MPH文件转换失败")
            return False
        
    except ComsolCreationError as e:
        logger.error(f"COMSOL转换错误: {e}")
        return False
    except Exception as e:
        logger.error(f"MPH转换过程中发生未知错误: {e}")
        return False


def main():
    """主函数"""
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(
        description="BTD Thermal文件到COMSOL MPH转换器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例用法:
  python main.py input.btd_th output.mph
  python main.py input.json output.mph
  python main.py -v input.btd_th output.mph
        """
    )
    
    # 添加命令行参数
    parser.add_argument(
        "input_file",
        type=Path,
        help="输入的BTD Thermal文件路径（支持.btd_th和.json格式）"
    )
    
    parser.add_argument(
        "output_file",
        type=Path,
        help="输出的COMSOL MPH文件路径"
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="启用详细日志输出"
    )
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 设置日志
    setup_logging(args.verbose)
    
    logger.info("=" * 60)
    logger.info("BTD Thermal文件到COMSOL MPH转换器")
    logger.info("=" * 60)
    
    # 验证输入文件
    if not validate_input_file(args.input_file):
        logger.error("输入文件验证失败")
        sys.exit(1)
    
    # 验证输出文件
    if not validate_output_file(args.output_file):
        logger.error("输出文件验证失败")
        sys.exit(1)
    
    # 解析BTD文件
    thermal_info = parse_btd_file(args.input_file)
    if not thermal_info:
        logger.error("BTD文件解析失败")
        sys.exit(1)
    
    # 转换为MPH文件
    if not convert_to_mph(thermal_info, args.output_file):
        logger.error("MPH文件转换失败")
        sys.exit(1)
    
    logger.info("=" * 60)
    logger.info("转换完成！")
    logger.info(f"输出文件: {args.output_file}")
    logger.info("=" * 60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("用户中断操作")
        sys.exit(1)
    except Exception as e:
        logger.error(f"程序执行过程中发生错误: {e}")
        sys.exit(1)
