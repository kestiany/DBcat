# -*- coding: utf-8 -*-
"""
错误处理模块
提供用户友好的错误提示和处理机制
"""

import logging
from typing import Optional, Dict, Any
from PyQt5.QtWidgets import QMessageBox, QWidget
from PyQt5.QtCore import Qt

# 配置日志记录
logger = logging.getLogger(__name__)


class FileErrorHandler:
    """文件操作错误处理器"""
    
    # 错误类型到用户友好消息的映射
    ERROR_MESSAGES = {
        'file_not_found': {
            'title': '文件未找到',
            'message': '指定的文件不存在。',
            'details': '请检查文件路径是否正确，或者文件是否已被移动或删除。',
            'suggestions': [
                '确认文件路径是否正确',
                '检查文件是否存在于指定位置',
                '尝试重新创建文件'
            ]
        },
        'permission_denied': {
            'title': '权限不足',
            'message': '没有足够的权限访问该文件。',
            'details': '当前用户没有读取或写入该文件的权限。',
            'suggestions': [
                '以管理员身份运行程序',
                '检查文件权限设置',
                '确保文件未被其他程序占用'
            ]
        },
        'encoding_error': {
            'title': '文件编码错误',
            'message': '无法正确读取文件内容，可能是编码格式不支持。',
            'details': '文件可能使用了不常见的编码格式，或者文件已损坏。',
            'suggestions': [
                '尝试将文件转换为UTF-8编码',
                '使用文本编辑器检查文件内容',
                '确认文件未损坏'
            ]
        },
        'disk_full': {
            'title': '磁盘空间不足',
            'message': '磁盘空间不足，无法保存文件。',
            'details': '目标磁盘没有足够的空间来保存文件。',
            'suggestions': [
                '清理磁盘空间',
                '选择其他位置保存文件',
                '删除不需要的文件'
            ]
        },
        'file_in_use': {
            'title': '文件正在使用',
            'message': '文件正被其他程序使用，无法访问。',
            'details': '该文件可能被其他应用程序打开或锁定。',
            'suggestions': [
                '关闭可能使用该文件的其他程序',
                '等待一段时间后重试',
                '重启计算机后再试'
            ]
        },
        'unknown_error': {
            'title': '未知错误',
            'message': '发生了未知的错误。',
            'details': '系统遇到了意外的问题。',
            'suggestions': [
                '重试操作',
                '重启应用程序',
                '联系技术支持'
            ]
        }
    }
    
    @classmethod
    def classify_error(cls, exception: Exception, file_path: str = "") -> str:
        """
        根据异常类型分类错误
        
        Args:
            exception: 异常对象
            file_path: 文件路径
            
        Returns:
            错误类型字符串
        """
        error_type = type(exception).__name__
        error_message = str(exception).lower()
        
        if isinstance(exception, FileNotFoundError):
            return 'file_not_found'
        elif isinstance(exception, PermissionError):
            return 'permission_denied'
        elif isinstance(exception, UnicodeDecodeError) or 'encoding' in error_message:
            return 'encoding_error'
        elif 'no space left' in error_message or 'disk full' in error_message:
            return 'disk_full'
        elif 'being used by another process' in error_message:
            return 'file_in_use'
        else:
            return 'unknown_error'
    
    @classmethod
    def show_error_dialog(cls, error_type: str, file_path: str = "", 
                         parent: Optional[QWidget] = None, 
                         exception: Optional[Exception] = None) -> None:
        """
        显示错误对话框
        
        Args:
            error_type: 错误类型
            file_path: 文件路径
            parent: 父窗口
            exception: 异常对象
        """
        if error_type not in cls.ERROR_MESSAGES:
            error_type = 'unknown_error'
        
        error_info = cls.ERROR_MESSAGES[error_type]
        
        # 创建消息框
        msg_box = QMessageBox(parent)
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setWindowTitle(error_info['title'])
        msg_box.setText(error_info['message'])
        
        # 构建详细信息
        details = error_info['details']
        if file_path:
            details += f"\n\n文件路径: {file_path}"
        
        if exception:
            details += f"\n\n技术详情: {str(exception)}"
        
        # 添加建议
        if error_info['suggestions']:
            details += "\n\n建议解决方案:"
            for i, suggestion in enumerate(error_info['suggestions'], 1):
                details += f"\n{i}. {suggestion}"
        
        msg_box.setDetailedText(details)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
    
    @classmethod
    def handle_file_error(cls, exception: Exception, file_path: str = "", 
                         parent: Optional[QWidget] = None, 
                         show_dialog: bool = True) -> str:
        """
        处理文件操作错误
        
        Args:
            exception: 异常对象
            file_path: 文件路径
            parent: 父窗口
            show_dialog: 是否显示对话框
            
        Returns:
            错误类型字符串
        """
        error_type = cls.classify_error(exception, file_path)
        
        # 记录错误日志
        logger.error(f"文件操作错误 [{error_type}]: {file_path} - {str(exception)}")
        
        # 显示用户友好的错误对话框
        if show_dialog:
            cls.show_error_dialog(error_type, file_path, parent, exception)
        
        return error_type


def show_warning_message(title: str, message: str, details: str = "", 
                        parent: Optional[QWidget] = None) -> None:
    """
    显示警告消息对话框
    
    Args:
        title: 对话框标题
        message: 主要消息
        details: 详细信息
        parent: 父窗口
    """
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Warning)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    
    if details:
        msg_box.setDetailedText(details)
    
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.exec_()


def show_info_message(title: str, message: str, details: str = "", 
                     parent: Optional[QWidget] = None) -> None:
    """
    显示信息消息对话框
    
    Args:
        title: 对话框标题
        message: 主要消息
        details: 详细信息
        parent: 父窗口
    """
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Information)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    
    if details:
        msg_box.setDetailedText(details)
    
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.exec_()


def show_question_dialog(title: str, message: str, details: str = "", 
                        parent: Optional[QWidget] = None) -> bool:
    """
    显示询问对话框
    
    Args:
        title: 对话框标题
        message: 主要消息
        details: 详细信息
        parent: 父窗口
        
    Returns:
        用户选择Yes返回True，否则返回False
    """
    msg_box = QMessageBox(parent)
    msg_box.setIcon(QMessageBox.Question)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    
    if details:
        msg_box.setDetailedText(details)
    
    msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msg_box.setDefaultButton(QMessageBox.No)
    
    result = msg_box.exec_()
    return result == QMessageBox.Yes