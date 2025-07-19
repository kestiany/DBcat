#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
主题集成的单元测试
"""

import sys
import os
import json
import unittest
import tempfile
from unittest.mock import MagicMock, patch
from pathlib import Path
from PyQt5 import QtWidgets, QtCore, QtGui

from DBCat.component.theme_manager import ThemeManager
from DBCat.component.title_bar import TitleBar


class TestThemeIntegration(unittest.TestCase):
    """主题集成的测试类"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.app = QtWidgets.QApplication.instance()
        if not self.app:
            self.app = QtWidgets.QApplication(sys.argv)
        
        # 创建临时目录用于测试
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        
        # 创建测试主题管理器
        self.theme_manager = ThemeManager()
        
        # 创建主窗口
        self.window = QtWidgets.QMainWindow()
        
        # 创建标题栏
        self.title_bar = TitleBar(self.window)
    
    def tearDown(self):
        """测试后的清理工作"""
        self.title_bar = None
        self.window = None
        self.theme_manager = None
        self.temp_dir.cleanup()
    
    @patch('DBCat.component.theme_manager.Path.home')
    def test_theme_persistence(self, mock_home):
        """测试主题持久化"""
        # 模拟home目录为临时目录
        mock_home.return_value = self.temp_path
        
        # 创建测试主题管理器
        test_manager = ThemeManager()
        
        # 设置当前主题
        test_manager.set_current_theme("dark")
        
        # 验证设置已保存
        settings_file = self.temp_path / ".dbcat" / "settings.json"
        self.assertTrue(os.path.exists(settings_file))
        
        # 读取设置文件
        with open(settings_file, 'r', encoding='utf-8') as f:
            settings = json.load(f)
        
        # 验证主题设置
        self.assertEqual(settings.get("theme"), "dark")
        
        # 创建新的主题管理器，验证设置是否被加载
        new_manager = ThemeManager()
        self.assertEqual(new_manager.current_theme_name, "dark")
    
    def test_theme_application_to_components(self):
        """测试主题应用到组件"""
        # 应用浅色主题
        self.theme_manager.set_current_theme("light")
        self.theme_manager.apply_theme(self.app)
        
        # 验证标题栏样式
        light_bg_color = self.title_bar.palette().color(QtGui.QPalette.Window)
        
        # 应用深色主题
        self.theme_manager.set_current_theme("dark")
        self.theme_manager.apply_theme(self.app)
        
        # 验证标题栏样式已更改
        dark_bg_color = self.title_bar.palette().color(QtGui.QPalette.Window)
        
        # 验证颜色确实发生了变化
        self.assertNotEqual(light_bg_color, dark_bg_color)
    
    def test_theme_dialog_integration(self):
        """测试主题对话框集成"""
        from DBCat.component.theme_dialog import ThemeDialog
        
        # 创建回调函数
        callback = MagicMock()
        
        # 创建主题对话框
        dialog = ThemeDialog(self.window, callback)
        
        # 验证对话框已加载主题列表
        self.assertGreater(dialog.theme_list.count(), 0)
        
        # 模拟选择主题
        dialog.theme_list.setCurrentRow(1)  # 选择第二个主题
        
        # 模拟点击应用按钮
        with patch.object(dialog, 'accept') as mock_accept:
            dialog.apply_theme()
            
            # 验证回调函数被调用
            callback.assert_called_once()
            
            # 验证对话框被接受
            mock_accept.assert_called_once()


if __name__ == '__main__':
    unittest.main()