# -*- coding: utf-8 -*-
"""
文件操作工具模块
提供安全的文件读写功能，支持多种编码格式和详细的错误处理
"""

import os
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from PyQt5.QtWidgets import QWidget

from DBCat.error_handler import FileErrorHandler, show_warning_message

# 配置日志记录
logger = logging.getLogger(__name__)


class FileEncodingError(Exception):
    """文件编码错误异常"""
    pass


class SafeFileReader:
    """安全的文件读取器，支持多编码检测和错误处理"""
    
    # 默认编码尝试策略，按优先级排序
    DEFAULT_ENCODINGS = [
        'utf-8',           # 首选编码
        'utf-8-sig',       # 带BOM的UTF-8
        'gbk',             # Windows中文编码
        'gb2312',          # 简体中文编码
        'cp1252',          # Windows西文编码
        'iso-8859-1',      # Latin-1编码
        'latin1'           # 最后备选
    ]
    
    def __init__(self, encodings: Optional[List[str]] = None):
        """
        初始化文件读取器
        
        Args:
            encodings: 自定义编码尝试列表，如果为None则使用默认列表
        """
        self.encodings = encodings or self.DEFAULT_ENCODINGS
        
    def read_file(self, file_path: Path, encodings: Optional[List[str]] = None, 
                  parent: Optional[QWidget] = None, show_dialog: bool = False) -> Optional[str]:
        """
        安全读取文件内容，支持多种编码格式
        
        Args:
            file_path: 文件路径
            encodings: 可选的编码列表，覆盖实例默认编码
            parent: 父窗口，用于显示错误对话框
            show_dialog: 是否显示用户友好的错误对话框
            
        Returns:
            文件内容字符串，如果读取失败则返回None
        """
        if not isinstance(file_path, Path):
            file_path = Path(file_path)
            
        # 使用传入的编码列表或实例默认编码列表
        encoding_list = encodings or self.encodings
        attempted_encodings = []
        
        try:
            # 首先检查文件是否存在
            if not file_path.exists():
                raise FileNotFoundError(f"文件不存在: {file_path}")
                
            # 检查文件权限
            if not os.access(file_path, os.R_OK):
                raise PermissionError(f"没有权限读取文件: {file_path}")
            
            # 尝试不同编码读取文件
            for encoding in encoding_list:
                try:
                    with open(file_path, 'r', encoding=encoding) as file_handler:
                        content = file_handler.read()
                        
                        # 如果成功读取且不是首选编码，记录信息
                        if encoding != encoding_list[0]:
                            logger.info(f"文件 {file_path} 使用 {encoding} 编码读取成功")
                        
                        return content
                        
                except UnicodeDecodeError as e:
                    attempted_encodings.append(encoding)
                    logger.debug(f"编码 {encoding} 读取文件 {file_path} 失败: {e}")
                    continue
            
            # 所有编码都失败了，创建编码错误
            error_msg = f"无法读取文件，尝试的编码: {attempted_encodings}"
            encoding_error = UnicodeDecodeError('multiple-encodings', b'', 0, 1, error_msg)
            raise encoding_error
            
        except Exception as e:
            # 使用错误处理器处理异常
            if show_dialog:
                FileErrorHandler.handle_file_error(e, str(file_path), parent, show_dialog=True)
            else:
                logger.error(f"读取文件 {file_path} 失败: {e}")
            return None
    
    def detect_encoding(self, file_path: Path) -> Optional[str]:
        """
        检测文件编码
        
        Args:
            file_path: 文件路径
            
        Returns:
            检测到的编码名称，如果检测失败则返回None
        """
        if not isinstance(file_path, Path):
            file_path = Path(file_path)
            
        for encoding in self.encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as file_handler:
                    # 尝试读取一小部分内容来验证编码
                    file_handler.read(1024)
                    return encoding
            except UnicodeDecodeError:
                continue
            except Exception as e:
                logger.error(f"检测文件 {file_path} 编码时发生错误: {e}")
                return None
        
        return None


class SafeFileWriter:
    """安全的文件写入器"""
    
    @staticmethod
    def write_file(file_path: Path, content: str, encoding: str = 'utf-8', 
                   create_dirs: bool = True) -> bool:
        """
        安全写入文件内容
        
        Args:
            file_path: 文件路径
            content: 要写入的内容
            encoding: 编码格式，默认UTF-8
            create_dirs: 是否自动创建目录
            
        Returns:
            写入成功返回True，失败返回False
        """
        if not isinstance(file_path, Path):
            file_path = Path(file_path)
        
        try:
            # 如果需要，创建父目录
            if create_dirs and not file_path.parent.exists():
                file_path.parent.mkdir(parents=True, exist_ok=True)
                logger.info(f"创建目录: {file_path.parent}")
            
            # 写入文件
            with open(file_path, 'w', encoding=encoding) as file_handler:
                file_handler.write(content)
                
            logger.info(f"文件写入成功: {file_path}")
            return True
            
        except PermissionError as e:
            logger.error(f"权限错误，无法写入文件 {file_path}: {e}")
            return False
            
        except OSError as e:
            logger.error(f"系统错误，写入文件 {file_path} 失败: {e}")
            return False
            
        except Exception as e:
            logger.error(f"写入文件 {file_path} 时发生未知错误: {e}")
            return False


# 便捷函数
def safe_read_file(file_path, encodings: Optional[List[str]] = None, 
                parent: Optional[QWidget] = None, show_dialog: bool = False) -> Optional[str]:
    """
    便捷的安全文件读取函数
    
    Args:
        file_path: 文件路径
        encodings: 可选的编码列表
        parent: 父窗口，用于显示错误对话框
        show_dialog: 是否显示用户友好的错误对话框
        
    Returns:
        文件内容字符串，如果读取失败则返回None
    """
    reader = SafeFileReader(encodings)
    try:
        return reader.read_file(Path(file_path), encodings, parent, show_dialog)
    except FileEncodingError as e:
        if show_dialog:
            FileErrorHandler.handle_file_error(e, str(file_path), parent, show_dialog=True)
        return None


def safe_write_file(file_path, content: str, encoding: str = 'utf-8') -> bool:
    """
    便捷的安全文件写入函数
    
    Args:
        file_path: 文件路径
        content: 要写入的内容
        encoding: 编码格式，默认UTF-8
        
    Returns:
        写入成功返回True，失败返回False
    """
    return SafeFileWriter.write_file(Path(file_path), content, encoding)


def detect_file_encoding(file_path) -> Optional[str]:
    """
    便捷的文件编码检测函数
    
    Args:
        file_path: 文件路径
        
    Returns:
        检测到的编码名称，如果检测失败则返回None
    """
    reader = SafeFileReader()
    return reader.detect_encoding(Path(file_path))