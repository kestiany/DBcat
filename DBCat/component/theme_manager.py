#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
主题管理模块
提供应用程序主题的管理和切换功能
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from pathlib import Path
from PyQt5 import QtWidgets, QtGui, QtCore

# 配置日志记录
logger = logging.getLogger(__name__)


class ThemeManager:
    """主题管理器，提供主题的加载、保存和应用功能"""
    
    # 默认主题
    DEFAULT_THEMES = {
        "light": {
            "name": "浅色主题",
            "description": "默认浅色主题",
            "colors": {
                "window": "#f5f5f5",
                "windowText": "#000000",
                "base": "#ffffff",
                "alternateBase": "#f0f0f0",
                "text": "#000000",
                "button": "#e0e0e0",
                "buttonText": "#000000",
                "brightText": "#ffffff",
                "highlight": "#308cc6",
                "highlightedText": "#ffffff",
                "link": "#0000ff",
                "midLight": "#d9d9d9",
                "dark": "#a0a0a0",
                "mid": "#b8b8b8",
                "shadow": "#505050",
                "toolTipBase": "#ffffdc",
                "toolTipText": "#000000",
                "tableHeader": "#e0e0e0",
                "tableAlternateRow": "#f5f5f5",
                "sqlKeyword": "#0000ff",
                "sqlComment": "#008000",
                "sqlString": "#a31515",
                "sqlNumber": "#098658",
                "sqlOperator": "#800000",
                "sqlFunction": "#795e26",
                "sqlHighlightLine": "#f0f0ff",
                "sqlCurrentLine": "#e8f2fe",
                "lineNumber": "#767676",
                "lineNumberArea": "#f0f0f0",
                "tabSelected": "#ffffff",
                "tabUnselected": "#e0e0e0",
                "splitter": "#c0c0c0"
            }
        },
        "dark": {
            "name": "深色主题",
            "description": "默认深色主题",
            "colors": {
                "window": "#2d2d2d",
                "windowText": "#ffffff",
                "base": "#353535",
                "alternateBase": "#3a3a3a",
                "text": "#ffffff",
                "button": "#454545",
                "buttonText": "#ffffff",
                "brightText": "#ffffff",
                "highlight": "#2a82da",
                "highlightedText": "#ffffff",
                "link": "#3ca4ff",
                "midLight": "#5a5a5a",
                "dark": "#202020",
                "mid": "#404040",
                "shadow": "#181818",
                "toolTipBase": "#4a4a4a",
                "toolTipText": "#ffffff",
                "tableHeader": "#404040",
                "tableAlternateRow": "#383838",
                "sqlKeyword": "#569cd6",
                "sqlComment": "#57a64a",
                "sqlString": "#d69d85",
                "sqlNumber": "#b5cea8",
                "sqlOperator": "#d4d4d4",
                "sqlFunction": "#dcdcaa",
                "sqlHighlightLine": "#303030",
                "sqlCurrentLine": "#282828",
                "lineNumber": "#858585",
                "lineNumberArea": "#2d2d2d",
                "tabSelected": "#353535",
                "tabUnselected": "#2d2d2d",
                "splitter": "#505050"
            }
        }
    }
    
    def __init__(self):
        """初始化主题管理器"""
        self.themes = {}
        self.current_theme_name = "light"
        self.themes_dir = self._get_themes_dir()
        self._load_themes()
    
    def _get_themes_dir(self) -> Path:
        """
        获取主题目录路径
        
        Returns:
            主题目录路径
        """
        # 使用.dbcat/themes目录存储主题
        themes_dir = Path.home() / ".dbcat" / "themes"
        if not os.path.exists(themes_dir):
            os.makedirs(themes_dir)
        
        return themes_dir
    
    def _load_themes(self) -> None:
        """加载所有主题"""
        # 首先加载默认主题
        self.themes = self.DEFAULT_THEMES.copy()
        
        # 然后加载自定义主题
        try:
            for theme_file in self.themes_dir.glob("*.json"):
                try:
                    with open(theme_file, 'r', encoding='utf-8') as f:
                        theme_data = json.load(f)
                        
                        # 验证主题数据
                        if self._validate_theme(theme_data):
                            theme_name = theme_file.stem
                            self.themes[theme_name] = theme_data
                            logger.info(f"已加载主题: {theme_name}")
                        else:
                            logger.warning(f"主题文件格式错误: {theme_file}")
                except Exception as e:
                    logger.error(f"加载主题文件时出错: {theme_file}, {str(e)}")
        except Exception as e:
            logger.error(f"加载主题目录时出错: {str(e)}")
        
        # 加载当前主题设置
        self._load_current_theme()
    
    def _validate_theme(self, theme_data: Dict[str, Any]) -> bool:
        """
        验证主题数据格式
        
        Args:
            theme_data: 主题数据
            
        Returns:
            是否有效
        """
        # 检查必要的字段
        if not all(key in theme_data for key in ["name", "description", "colors"]):
            return False
        
        # 检查颜色字段
        colors = theme_data.get("colors", {})
        required_colors = [
            "window", "windowText", "base", "text", "highlight", "highlightedText"
        ]
        
        return all(color in colors for color in required_colors)
    
    def _load_current_theme(self) -> None:
        """加载当前主题设置"""
        settings_file = Path.home() / ".dbcat" / "settings.json"
        
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                    theme_name = settings.get("theme", "light")
                    
                    # 检查主题是否存在
                    if theme_name in self.themes:
                        self.current_theme_name = theme_name
                    else:
                        logger.warning(f"主题不存在: {theme_name}，使用默认主题")
                        self.current_theme_name = "light"
            except Exception as e:
                logger.error(f"加载设置文件时出错: {str(e)}")
                self.current_theme_name = "light"
        else:
            self.current_theme_name = "light"
    
    def _save_current_theme(self) -> bool:
        """
        保存当前主题设置
        
        Returns:
            是否成功保存
        """
        settings_file = Path.home() / ".dbcat" / "settings.json"
        
        # 确保目录存在
        settings_dir = settings_file.parent
        if not os.path.exists(settings_dir):
            os.makedirs(settings_dir)
        
        # 读取现有设置
        settings = {}
        if os.path.exists(settings_file):
            try:
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            except:
                settings = {}
        
        # 更新主题设置
        settings["theme"] = self.current_theme_name
        
        # 保存设置
        try:
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"保存设置文件时出错: {str(e)}")
            return False
    
    def get_theme_names(self) -> list:
        """
        获取所有主题名称
        
        Returns:
            主题名称列表
        """
        return list(self.themes.keys())
    
    def get_theme(self, theme_name: Optional[str] = None) -> Dict[str, Any]:
        """
        获取指定主题
        
        Args:
            theme_name: 主题名称，如果为None则返回当前主题
            
        Returns:
            主题数据
        """
        if theme_name is None:
            theme_name = self.current_theme_name
        
        return self.themes.get(theme_name, self.themes["light"])
    
    def set_current_theme(self, theme_name: str) -> bool:
        """
        设置当前主题
        
        Args:
            theme_name: 主题名称
            
        Returns:
            是否成功设置
        """
        if theme_name in self.themes:
            self.current_theme_name = theme_name
            self._save_current_theme()
            return True
        return False
    
    def apply_theme(self, app: QtWidgets.QApplication) -> None:
        """
        应用当前主题到应用程序
        
        Args:
            app: QApplication实例
        """
        theme = self.get_theme()
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
            "highlightedText": QtGui.QPalette.HighlightedText,
            "link": QtGui.QPalette.Link,
            "midLight": QtGui.QPalette.Midlight,
            "dark": QtGui.QPalette.Dark,
            "mid": QtGui.QPalette.Mid,
            "shadow": QtGui.QPalette.Shadow,
            "toolTipBase": QtGui.QPalette.ToolTipBase,
            "toolTipText": QtGui.QPalette.ToolTipText
        }
        
        for color_name, role in color_roles.items():
            if color_name in colors:
                palette.setColor(role, QtGui.QColor(colors[color_name]))
        
        # 应用调色板
        app.setPalette(palette)
        
        # 创建样式表
        style_sheet = self._create_style_sheet(colors)
        
        # 应用样式表
        app.setStyleSheet(style_sheet)
    
    def _create_style_sheet(self, colors: Dict[str, str]) -> str:
        """
        创建样式表
        
        Args:
            colors: 颜色字典
            
        Returns:
            样式表字符串
        """
        return f"""
            /* 自定义标题栏样式 */
            TitleBar {{
                background-color: {colors.get("window", "#f5f5f5")};
                border-bottom: 1px solid {colors.get("mid", "#b8b8b8")};
            }}
            
            TitleBar QLabel {{
                color: {colors.get("windowText", "#000000")};
                font-size: 14px;
                font-weight: bold;
                padding-left: 5px;
            }}
            
            TitleBar QPushButton {{
                border: none;
                background-color: transparent;
                border-radius: 15px;
            }}
            
            TitleBar QPushButton:hover {{
                background-color: {colors.get("midLight", "#d9d9d9")};
            }}
            
            TitleBar QPushButton:pressed {{
                background-color: {colors.get("mid", "#b8b8b8")};
            }}
            
            TitleBar #close_button:hover {{
                background-color: #e81123;
            }}
            
            TitleBar #close_button:pressed {{
                background-color: #f1707a;
            }}
            /* QMenuBar和QMenu样式 - 确保菜单在深色模式下可见 */
            QMenuBar {{
                background-color: {colors.get("window", "#f5f5f5")};
                color: {colors.get("windowText", "#000000")};
                border-bottom: 1px solid {colors.get("mid", "#b8b8b8")};
            }}
            
            QMenuBar::item {{
                background-color: transparent;
                padding: 4px 8px;
                border-radius: 4px;
            }}
            
            QMenuBar::item:selected {{
                background-color: {colors.get("highlight", "#308cc6")};
                color: {colors.get("highlightedText", "#ffffff")};
            }}
            
            QMenu {{
                background-color: {colors.get("window", "#f5f5f5")};
                color: {colors.get("windowText", "#000000")};
                border: 1px solid {colors.get("mid", "#b8b8b8")};
                padding: 2px;
            }}
            
            QMenu::item {{
                padding: 5px 30px 5px 20px;
                border: 1px solid transparent;
            }}
            
            QMenu::item:selected {{
                background-color: {colors.get("highlight", "#308cc6")};
                color: {colors.get("highlightedText", "#ffffff")};
            }}
            
            QMenu::separator {{
                height: 1px;
                background: {colors.get("mid", "#b8b8b8")};
                margin: 4px 0px;
            }}
            
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
            
            /* QSplitter样式 */
            QSplitter::handle {{
                background: {colors.get("splitter", "#c0c0c0")};
            }}
            
            QSplitter::handle:horizontal {{
                width: 1px;
            }}
            
            QSplitter::handle:vertical {{
                height: 1px;
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
            
            /* QTreeWidget样式 */
            QTreeWidget {{
                border: 1px solid {colors.get("mid", "#b8b8b8")};
            }}
            
            QTreeWidget::item:selected {{
                background-color: {colors.get("highlight", "#308cc6")};
                color: {colors.get("highlightedText", "#ffffff")};
            }}
            
            /* QToolBar样式 */
            QToolBar {{
                border: none;
                background: {colors.get("window", "#f5f5f5")};
                spacing: 3px;
                padding: 3px;
            }}
            
            QToolButton {{
                border: 1px solid transparent;
                border-radius: 3px;
                background-color: transparent;
                padding: 5px;
            }}
            
            QToolButton:hover {{
                background-color: {colors.get("midLight", "#d9d9d9")};
            }}
            
            QToolButton:pressed {{
                background-color: {colors.get("mid", "#b8b8b8")};
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
            
            /* QPlainTextEdit样式 */
            QPlainTextEdit {{
                border: 1px solid {colors.get("mid", "#b8b8b8")};
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
            
            QComboBox:!editable:on, QComboBox::drop-down:editable:on {{
                background: {colors.get("midLight", "#d9d9d9")};
            }}
            
            /* QPushButton样式 */
            QPushButton {{
                border: 1px solid {colors.get("mid", "#b8b8b8")};
                border-radius: 3px;
                background-color: {colors.get("button", "#e0e0e0")};
                padding: 5px;
                min-width: 80px;
            }}
            
            QPushButton:hover {{
                background-color: {colors.get("midLight", "#d9d9d9")};
            }}
            
            QPushButton:pressed {{
                background-color: {colors.get("mid", "#b8b8b8")};
            }}
            
            QPushButton:disabled {{
                background-color: {colors.get("window", "#f5f5f5")};
                color: {colors.get("mid", "#b8b8b8")};
            }}
        """


# 创建全局主题管理器实例
theme_manager = ThemeManager()