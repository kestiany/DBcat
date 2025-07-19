#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TitleBar组件的单元测试
"""

import sys
import unittest
from unittest.mock import MagicMock, patch
from PyQt5 import QtWidgets, QtCore, QtGui, QtTest

from DBCat.component.title_bar import TitleBar


class TestTitleBar(unittest.TestCase):
    """TitleBar组件的测试类"""
    
    def setUp(self):
        """测试前的准备工作"""
        self.app = QtWidgets.QApplication.instance()
        if not self.app:
            self.app = QtWidgets.QApplication(sys.argv)
        
        # 创建主窗口
        self.window = QtWidgets.QMainWindow()
        
        # 创建标题栏
        self.title_bar = TitleBar(self.window)
    
    def tearDown(self):
        """测试后的清理工作"""
        self.title_bar = None
        self.window = None
    
    def test_title_bar_creation(self):
        """测试标题栏创建"""
        # 验证标题栏已创建
        self.assertIsNotNone(self.title_bar)
        
        # 验证标题栏高度
        self.assertEqual(self.title_bar.height(), 40)
        
        # 验证标题栏包含必要的控件
        self.assertIsNotNone(self.title_bar.title_label)
        self.assertIsNotNone(self.title_bar.min_button)
        self.assertIsNotNone(self.title_bar.max_button)
        self.assertIsNotNone(self.title_bar.close_button)
        self.assertIsNotNone(self.title_bar.theme_button)
    
    def test_window_control_buttons(self):
        """测试窗口控制按钮"""
        # 模拟窗口方法
        self.window.showMinimized = MagicMock()
        self.window.showMaximized = MagicMock()
        self.window.showNormal = MagicMock()
        self.window.close = MagicMock()
        
        # 测试最小化按钮
        QtTest.QTest.mouseClick(self.title_bar.min_button, QtCore.Qt.LeftButton)
        self.window.showMinimized.assert_called_once()
        
        # 测试最大化按钮
        QtTest.QTest.mouseClick(self.title_bar.max_button, QtCore.Qt.LeftButton)
        self.window.showMaximized.assert_called_once()
        
        # 测试关闭按钮
        QtTest.QTest.mouseClick(self.title_bar.close_button, QtCore.Qt.LeftButton)
        self.window.close.assert_called_once()
    
    def test_toggle_maximize(self):
        """测试切换最大化/还原状态"""
        # 模拟窗口方法
        self.window.isMaximized = MagicMock(return_value=False)
        self.window.showMaximized = MagicMock()
        self.window.showNormal = MagicMock()
        
        # 测试从普通状态切换到最大化状态
        self.title_bar.toggle_maximize()
        self.window.showMaximized.assert_called_once()
        
        # 模拟窗口已最大化
        self.window.isMaximized = MagicMock(return_value=True)
        
        # 测试从最大化状态切换到普通状态
        self.title_bar.toggle_maximize()
        self.window.showNormal.assert_called_once()
    
    @patch('DBCat.component.theme_manager.theme_manager.set_current_theme')
    @patch('DBCat.component.theme_manager.theme_manager.apply_theme')
    def test_toggle_theme(self, mock_apply_theme, mock_set_current_theme):
        """测试切换主题"""
        # 模拟主题管理器
        from DBCat.component.theme_manager import theme_manager
        theme_manager.current_theme_name = "light"
        
        # 测试从浅色主题切换到深色主题
        self.title_bar.toggle_theme()
        mock_set_current_theme.assert_called_once_with("dark")
        mock_apply_theme.assert_called_once()
        
        # 重置模拟对象
        mock_set_current_theme.reset_mock()
        mock_apply_theme.reset_mock()
        
        # 模拟当前主题为深色
        theme_manager.current_theme_name = "dark"
        
        # 测试从深色主题切换到浅色主题
        self.title_bar.toggle_theme()
        mock_set_current_theme.assert_called_once_with("light")
        mock_apply_theme.assert_called_once()
    
    def test_mouse_events(self):
        """测试鼠标事件"""
        # 模拟鼠标按下事件
        event = QtGui.QMouseEvent(
            QtCore.QEvent.MouseButtonPress,
            QtCore.QPointF(10, 10),
            QtCore.Qt.LeftButton,
            QtCore.Qt.LeftButton,
            QtCore.Qt.NoModifier
        )
        self.title_bar.mousePressEvent(event)
        self.assertTrue(self.title_bar.is_pressed)
        self.assertIsNotNone(self.title_bar.start_move_pos)
        
        # 模拟鼠标释放事件
        event = QtGui.QMouseEvent(
            QtCore.QEvent.MouseButtonRelease,
            QtCore.QPointF(10, 10),
            QtCore.Qt.LeftButton,
            QtCore.Qt.LeftButton,
            QtCore.Qt.NoModifier
        )
        self.title_bar.mouseReleaseEvent(event)
        self.assertFalse(self.title_bar.is_pressed)
        
        # 模拟鼠标双击事件
        self.title_bar.toggle_maximize = MagicMock()
        event = QtGui.QMouseEvent(
            QtCore.QEvent.MouseButtonDblClick,
            QtCore.QPointF(10, 10),
            QtCore.Qt.LeftButton,
            QtCore.Qt.LeftButton,
            QtCore.Qt.NoModifier
        )
        self.title_bar.mouseDoubleClickEvent(event)
        self.title_bar.toggle_maximize.assert_called_once()


if __name__ == '__main__':
    unittest.main()