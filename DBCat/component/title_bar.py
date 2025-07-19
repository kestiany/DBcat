#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自定义标题栏模块
提供无边框窗口的标题栏功能，包括拖动、最小化、最大化和关闭
"""

import logging
from typing import Optional, Callable
from PyQt5 import QtWidgets, QtCore, QtGui

from DBCat import resource as res
from DBCat.component.theme_manager import theme_manager

# 配置日志记录
logger = logging.getLogger(__name__)


class TitleBar(QtWidgets.QWidget):
    """自定义标题栏，提供拖动、最小化、最大化和关闭功能"""
    
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        """
        初始化标题栏
        
        Args:
            parent: 父窗口
        """
        super(TitleBar, self).__init__(parent)
        
        # 设置固定高度
        self.setFixedHeight(40)
        
        # 初始化变量
        self.is_pressed = False
        self.start_move_pos = None
        
        # 设置鼠标跟踪
        self.setMouseTracking(True)
        
        # 创建UI
        self.setup_ui()
        
        # 应用样式
        self.apply_style()
    
    def setup_ui(self):
        """设置UI界面"""
        # 主布局
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(10, 0, 10, 0)
        layout.setSpacing(0)
        
        # 图标
        self.icon_label = QtWidgets.QLabel(self)
        self.icon_label.setFixedSize(24, 24)
        self.icon_label.setPixmap(QtGui.QPixmap(res.resource_path('image/title.svg')).scaled(
            24, 24, QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation
        ))
        layout.addWidget(self.icon_label)
        
        # 标题
        self.title_label = QtWidgets.QLabel("DBCat", self)
        self.title_label.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        layout.addWidget(self.title_label)
        
        # 设置上下文菜单
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)
        
        # 添加伸缩项
        layout.addStretch()
        
        # 主题切换按钮
        self.theme_button = QtWidgets.QPushButton(self)
        self.theme_button.setToolTip("切换主题")
        self.theme_button.setFixedSize(24, 24)
        self.theme_button.setIcon(QtGui.QIcon(res.resource_path('image/theme.svg')))
        self.theme_button.setIconSize(QtCore.QSize(14, 14))
        self.theme_button.clicked.connect(self.toggle_theme)
        layout.addWidget(self.theme_button)
        
        # 最小化按钮
        self.min_button = QtWidgets.QPushButton(self)
        self.min_button.setToolTip("最小化")
        self.min_button.setFixedSize(24, 24)
        self.min_button.setIcon(QtGui.QIcon(res.resource_path('image/minimize.svg')))
        self.min_button.setIconSize(QtCore.QSize(14, 14))
        self.min_button.clicked.connect(self.window().showMinimized)
        layout.addWidget(self.min_button)
        
        # 最大化/还原按钮
        self.max_button = QtWidgets.QPushButton(self)
        self.max_button.setToolTip("最大化")
        self.max_button.setFixedSize(24, 24)
        self.max_button.setIcon(QtGui.QIcon(res.resource_path('image/maximize.svg')))
        self.max_button.setIconSize(QtCore.QSize(14, 14))
        self.max_button.clicked.connect(self.toggle_maximize)
        layout.addWidget(self.max_button)
        
        # 关闭按钮
        self.close_button = QtWidgets.QPushButton(self)
        self.close_button.setObjectName("close_button")  # 设置对象名称以便CSS选择器可以找到它
        self.close_button.setToolTip("关闭")
        self.close_button.setFixedSize(24, 24)
        self.close_button.setIcon(QtGui.QIcon(res.resource_path('image/close.svg')))
        self.close_button.setIconSize(QtCore.QSize(14, 14))
        self.close_button.clicked.connect(self.window().close)
        layout.addWidget(self.close_button)
    
    def apply_style(self):
        """应用样式"""
        # 获取当前主题颜色
        theme = theme_manager.get_theme()
        colors = theme["colors"]
        
        # 设置标题栏样式
        self.setStyleSheet(f"""
            TitleBar {{
                background-color: {colors.get("window", "#f5f5f5")};
                border-bottom: 1px solid {colors.get("mid", "#b8b8b8")};
            }}
            
            QLabel {{
                color: {colors.get("windowText", "#000000")};
                font-size: 14px;
                font-weight: bold;
                padding-left: 5px;
            }}
            
            QPushButton {{
                border: none;
                background-color: transparent;
                border-radius: 15px;
            }}
            
            QPushButton:hover {{
                background-color: {colors.get("midLight", "#d9d9d9")};
            }}
            
            QPushButton:pressed {{
                background-color: {colors.get("mid", "#b8b8b8")};
            }}
            
            #close_button:hover {{
                background-color: #e81123;
            }}
            
            #close_button:pressed {{
                background-color: #f1707a;
            }}
        """)
    
    def toggle_theme(self):
        """切换主题"""
        # 获取当前主题
        current_theme = theme_manager.current_theme_name
        
        # 切换主题
        new_theme = "dark" if current_theme == "light" else "light"
        theme_manager.set_current_theme(new_theme)
        
        # 应用新主题
        theme_manager.apply_theme(QtWidgets.QApplication.instance())
        
        # 更新标题栏样式
        self.apply_style()
    
    def toggle_maximize(self):
        """切换最大化/还原状态"""
        if self.window().isMaximized():
            self.window().showNormal()
            self.max_button.setToolTip("最大化")
            self.max_button.setIcon(QtGui.QIcon(res.resource_path('image/maximize.svg')))
        else:
            self.window().showMaximized()
            self.max_button.setToolTip("还原")
            self.max_button.setIcon(QtGui.QIcon(res.resource_path('image/restore.svg')))
    
    def mousePressEvent(self, event):
        """鼠标按下事件"""
        if event.button() == QtCore.Qt.LeftButton:
            self.is_pressed = True
            self.start_move_pos = event.globalPos()
        return super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event):
        """鼠标移动事件"""
        if self.is_pressed:
            # 如果窗口是最大化状态，先还原
            if self.window().isMaximized():
                # 计算还原后窗口的位置，使鼠标位置保持在标题栏上
                window_width = self.window().width() / 2
                cursor_x = event.globalPos().x()
                new_x = int(cursor_x - window_width / 2)  # 转换为整数
                
                # 还原窗口
                self.window().showNormal()
                self.max_button.setToolTip("最大化")
                self.max_button.setIcon(QtGui.QIcon(res.resource_path('image/maximize.svg')))
                
                # 更新起始位置
                self.start_move_pos = QtCore.QPoint(cursor_x, event.globalPos().y())
                
                # 移动窗口到新位置
                self.window().move(new_x, 0)
            else:
                # 计算移动距离
                move_pos = event.globalPos() - self.start_move_pos
                
                # 移动窗口
                self.window().move(self.window().pos() + move_pos)
                
                # 更新起始位置
                self.start_move_pos = event.globalPos()
        return super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event):
        """鼠标释放事件"""
        self.is_pressed = False
        return super().mouseReleaseEvent(event)
    
    def mouseDoubleClickEvent(self, event):
        """鼠标双击事件"""
        if event.button() == QtCore.Qt.LeftButton:
            self.toggle_maximize()
        return super().mouseDoubleClickEvent(event)
        
    def show_context_menu(self, pos):
        """显示上下文菜单"""
        # 创建上下文菜单
        context_menu = QtWidgets.QMenu(self)
        
        # 添加关于操作
        about_action = QtWidgets.QAction("关于", self)
        about_action.triggered.connect(self.window().show_about_dialog)
        context_menu.addAction(about_action)
        
        # 添加分隔符
        context_menu.addSeparator()
        
        # 添加退出操作
        exit_action = QtWidgets.QAction("退出", self)
        exit_action.triggered.connect(self.window().close)
        context_menu.addAction(exit_action)
        
        # 显示菜单
        context_menu.exec_(self.mapToGlobal(pos))