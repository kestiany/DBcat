#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
主题切换对话框模块
提供主题切换的用户界面
"""

import logging
from typing import Optional, Callable
from PyQt5 import QtWidgets, QtCore, QtGui

from DBCat.component.theme_manager import theme_manager

# 配置日志记录
logger = logging.getLogger(__name__)


class ThemeDialog(QtWidgets.QDialog):
    """主题切换对话框，用于选择和预览主题"""
    
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None, 
                callback: Optional[Callable[[str], None]] = None):
        """
        初始化主题切换对话框
        
        Args:
            parent: 父窗口
            callback: 主题切换时的回调函数
        """
        super(ThemeDialog, self).__init__(parent)
        self.callback = callback
        self.setup_ui()
        self.load_themes()
    
    def setup_ui(self):
        """设置UI界面"""
        self.setWindowTitle("主题设置")
        self.resize(500, 400)
        
        # 主布局
        layout = QtWidgets.QVBoxLayout(self)
        
        # 主题列表
        theme_group = QtWidgets.QGroupBox("可用主题")
        theme_layout = QtWidgets.QVBoxLayout(theme_group)
        
        self.theme_list = QtWidgets.QListWidget()
        self.theme_list.setAlternatingRowColors(True)
        self.theme_list.currentItemChanged.connect(self.on_theme_selected)
        theme_layout.addWidget(self.theme_list)
        
        layout.addWidget(theme_group)
        
        # 预览区域
        preview_group = QtWidgets.QGroupBox("预览")
        preview_layout = QtWidgets.QVBoxLayout(preview_group)
        
        self.preview_widget = ThemePreviewWidget()
        preview_layout.addWidget(self.preview_widget)
        
        layout.addWidget(preview_group)
        
        # 按钮区域
        button_layout = QtWidgets.QHBoxLayout()
        
        self.apply_button = QtWidgets.QPushButton("应用")
        self.apply_button.clicked.connect(self.apply_theme)
        
        self.close_button = QtWidgets.QPushButton("关闭")
        self.close_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.apply_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
    
    def load_themes(self):
        """加载主题列表"""
        # 获取主题列表
        theme_names = theme_manager.get_theme_names()
        current_theme = theme_manager.current_theme_name
        
        # 清空列表
        self.theme_list.clear()
        
        # 填充列表
        for theme_name in theme_names:
            theme = theme_manager.get_theme(theme_name)
            item = QtWidgets.QListWidgetItem(theme["name"])
            item.setData(QtCore.Qt.UserRole, theme_name)
            item.setToolTip(theme["description"])
            self.theme_list.addItem(item)
            
            # 选中当前主题
            if theme_name == current_theme:
                self.theme_list.setCurrentItem(item)
    
    def on_theme_selected(self, current, previous):
        """
        主题选择变更时的处理
        
        Args:
            current: 当前选中项
            previous: 之前选中项
        """
        if current:
            theme_name = current.data(QtCore.Qt.UserRole)
            theme = theme_manager.get_theme(theme_name)
            self.preview_widget.update_preview(theme)
    
    def apply_theme(self):
        """应用选中的主题"""
        current_item = self.theme_list.currentItem()
        if current_item:
            theme_name = current_item.data(QtCore.Qt.UserRole)
            if theme_manager.set_current_theme(theme_name):
                if self.callback:
                    self.callback(theme_name)
                self.accept()


class ThemePreviewWidget(QtWidgets.QWidget):
    """主题预览控件，用于显示主题的预览效果"""
    
    def __init__(self, parent=None):
        """
        初始化主题预览控件
        
        Args:
            parent: 父窗口
        """
        super(ThemePreviewWidget, self).__init__(parent)
        self.theme = None
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI界面"""
        # 主布局
        layout = QtWidgets.QVBoxLayout(self)
        
        # 标签页
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.addTab(QtWidgets.QWidget(), "标签页1")
        self.tab_widget.addTab(QtWidgets.QWidget(), "标签页2")
        
        layout.addWidget(self.tab_widget)
        
        # 表格
        self.table = QtWidgets.QTableWidget(5, 3)
        self.table.setHorizontalHeaderLabels(["列1", "列2", "列3"])
        self.table.setAlternatingRowColors(True)
        
        for row in range(5):
            for col in range(3):
                self.table.setItem(row, col, QtWidgets.QTableWidgetItem(f"项目 {row+1}-{col+1}"))
        
        layout.addWidget(self.table)
        
        # 控件区域
        controls_layout = QtWidgets.QHBoxLayout()
        
        self.line_edit = QtWidgets.QLineEdit("文本输入")
        controls_layout.addWidget(self.line_edit)
        
        self.combo_box = QtWidgets.QComboBox()
        self.combo_box.addItems(["选项1", "选项2", "选项3"])
        controls_layout.addWidget(self.combo_box)
        
        self.button = QtWidgets.QPushButton("按钮")
        controls_layout.addWidget(self.button)
        
        layout.addLayout(controls_layout)
    
    def update_preview(self, theme):
        """
        更新预览效果
        
        Args:
            theme: 主题数据
        """
        self.theme = theme
        colors = theme["colors"]
        
        # 创建调色板
        palette = QtGui.QPalette()
        
        # 设置调色板颜色
        color_roles = {
            "window": QtGui.QPalette.Window,
            "windowText": QtGui.QPalette.WindowText,
            "base": QtGui.QPalette.Base,
            "alternateBase": QtGui.QPalette.AlternateBase,
            "text": QtGui.QPalette.Text,
            "button": QtGui.QPalette.Button,
            "buttonText": QtGui.QPalette.ButtonText,
            "brightText": QtGui.QPalette.BrightText,
            "highlight": QtGui.QPalette.Highlight,
            "highlightedText": QtGui.QPalette.HighlightedText
        }
        
        for color_name, role in color_roles.items():
            if color_name in colors:
                palette.setColor(role, QtGui.QColor(colors[color_name]))
        
        # 应用调色板
        self.setPalette(palette)
        
        # 创建样式表
        style_sheet = self._create_preview_style_sheet(colors)
        
        # 应用样式表
        self.setStyleSheet(style_sheet)
        
        # 更新
        self.update()
    
    def _create_preview_style_sheet(self, colors):
        """
        创建预览样式表
        
        Args:
            colors: 颜色字典
            
        Returns:
            样式表字符串
        """
        return f"""
            /* QTabWidget样式 */
            QTabWidget::pane {{
                border: 1px solid {colors.get("mid", "#b8b8b8")};
                background: {colors.get("base", "#ffffff")};
            }}
            
            QTabBar::tab {{
                background: {colors.get("tabUnselected", "#e0e0e0")};
                border: 1px solid {colors.get("mid", "#b8b8b8")};
                border-bottom-color: {colors.get("mid", "#b8b8b8")};
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 5px;
                min-width: 80px;
            }}
            
            QTabBar::tab:selected {{
                background: {colors.get("tabSelected", "#ffffff")};
                border-bottom-color: {colors.get("tabSelected", "#ffffff")};
            }}
            
            QTabBar::tab:!selected {{
                margin-top: 2px;
            }}
            
            /* QTableView样式 */
            QTableView {{
                gridline-color: {colors.get("mid", "#b8b8b8")};
                selection-background-color: {colors.get("highlight", "#308cc6")};
                selection-color: {colors.get("highlightedText", "#ffffff")};
            }}
            
            QTableView QHeaderView::section {{
                background-color: {colors.get("tableHeader", "#e0e0e0")};
                border: 1px solid {colors.get("mid", "#b8b8b8")};
                padding: 4px;
            }}
            
            QTableView::item:alternate {{
                background-color: {colors.get("tableAlternateRow", "#f5f5f5")};
            }}
            
            /* QLineEdit样式 */
            QLineEdit {{
                border: 1px solid {colors.get("mid", "#b8b8b8")};
                border-radius: 3px;
                padding: 2px;
                background: {colors.get("base", "#ffffff")};
                selection-background-color: {colors.get("highlight", "#308cc6")};
                selection-color: {colors.get("highlightedText", "#ffffff")};
            }}
            
            /* QComboBox样式 */
            QComboBox {{
                border: 1px solid {colors.get("mid", "#b8b8b8")};
                border-radius: 3px;
                padding: 1px 18px 1px 3px;
                min-width: 6em;
            }}
            
            QComboBox:editable {{
                background: {colors.get("base", "#ffffff")};
            }}
            
            QComboBox:!editable, QComboBox::drop-down:editable {{
                background: {colors.get("button", "#e0e0e0")};
            }}
            
            /* QPushButton样式 */
            QPushButton {{
                border: 1px solid {colors.get("mid", "#b8b8b8")};
                border-radius: 3px;
                background-color: {colors.get("button", "#e0e0e0")};
                padding: 5px;
                min-width: 80px;
            }}
        """