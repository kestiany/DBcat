#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
窗口边框处理模块
提供无边框窗口的调整大小功能
"""

import logging
from enum import Enum
from PyQt5 import QtCore, QtWidgets

# 配置日志记录
logger = logging.getLogger(__name__)


class Direction(Enum):
    """窗口调整方向枚举"""
    LEFT = 1
    TOP = 2
    RIGHT = 3
    BOTTOM = 4
    TOP_LEFT = 5
    TOP_RIGHT = 6
    BOTTOM_LEFT = 7
    BOTTOM_RIGHT = 8
    NONE = 9


class WindowFrameHandler:
    """窗口边框处理器，提供无边框窗口的调整大小功能"""
    
    # 边框宽度
    BORDER_WIDTH = 5
    
    def __init__(self, window):
        """
        初始化窗口边框处理器
        
        Args:
            window: 主窗口
        """
        self.window = window
        self.direction = Direction.NONE
        self.mouse_pressed = False
        
        # 设置鼠标跟踪
        self.window.setMouseTracking(True)
        self.window.centralWidget().setMouseTracking(True)
        
        # 保存原始事件处理器
        self.original_mouse_press_event = window.mousePressEvent
        self.original_mouse_move_event = window.mouseMoveEvent
        self.original_mouse_release_event = window.mouseReleaseEvent
        
        # 替换事件处理器
        window.mousePressEvent = self.mouse_press_event
        window.mouseMoveEvent = self.mouse_move_event
        window.mouseReleaseEvent = self.mouse_release_event
    
    def get_direction(self, pos):
        """
        获取鼠标位置对应的调整方向
        
        Args:
            pos: 鼠标位置
            
        Returns:
            调整方向
        """
        # 获取窗口大小
        width = self.window.width()
        height = self.window.height()
        
        # 判断鼠标位置
        if pos.x() <= self.BORDER_WIDTH and pos.y() <= self.BORDER_WIDTH:
            return Direction.TOP_LEFT
        elif width - self.BORDER_WIDTH <= pos.x() <= width and pos.y() <= self.BORDER_WIDTH:
            return Direction.TOP_RIGHT
        elif pos.x() <= self.BORDER_WIDTH and height - self.BORDER_WIDTH <= pos.y() <= height:
            return Direction.BOTTOM_LEFT
        elif width - self.BORDER_WIDTH <= pos.x() <= width and height - self.BORDER_WIDTH <= pos.y() <= height:
            return Direction.BOTTOM_RIGHT
        elif pos.x() <= self.BORDER_WIDTH:
            return Direction.LEFT
        elif pos.y() <= self.BORDER_WIDTH:
            return Direction.TOP
        elif width - self.BORDER_WIDTH <= pos.x() <= width:
            return Direction.RIGHT
        elif height - self.BORDER_WIDTH <= pos.y() <= height:
            return Direction.BOTTOM
        else:
            return Direction.NONE
    
    def set_cursor_shape(self, direction):
        """
        设置鼠标形状
        
        Args:
            direction: 调整方向
        """
        if direction == Direction.LEFT or direction == Direction.RIGHT:
            self.window.setCursor(QtCore.Qt.SizeHorCursor)
        elif direction == Direction.TOP or direction == Direction.BOTTOM:
            self.window.setCursor(QtCore.Qt.SizeVerCursor)
        elif direction == Direction.TOP_LEFT or direction == Direction.BOTTOM_RIGHT:
            self.window.setCursor(QtCore.Qt.SizeFDiagCursor)
        elif direction == Direction.TOP_RIGHT or direction == Direction.BOTTOM_LEFT:
            self.window.setCursor(QtCore.Qt.SizeBDiagCursor)
        else:
            self.window.setCursor(QtCore.Qt.ArrowCursor)
    
    def mouse_press_event(self, event):
        """
        鼠标按下事件
        
        Args:
            event: 事件对象
        """
        # 如果窗口最大化，不处理调整大小
        if self.window.isMaximized():
            self.original_mouse_press_event(event)
            return
        
        # 获取鼠标位置
        pos = event.pos()
        
        # 获取调整方向
        self.direction = self.get_direction(pos)
        
        # 如果在边框上，开始调整大小
        if self.direction != Direction.NONE:
            self.mouse_pressed = True
            event.accept()
        else:
            # 否则，调用原始事件处理器
            self.original_mouse_press_event(event)
    
    def mouse_move_event(self, event):
        """
        鼠标移动事件
        
        Args:
            event: 事件对象
        """
        # 如果窗口最大化，不处理调整大小
        if self.window.isMaximized():
            self.original_mouse_move_event(event)
            return
        
        # 获取鼠标位置
        pos = event.pos()
        
        # 如果鼠标按下，调整窗口大小
        if self.mouse_pressed:
            # 获取窗口位置和大小
            window_pos = self.window.pos()
            window_rect = self.window.geometry()
            
            # 根据调整方向调整窗口大小
            if self.direction == Direction.LEFT:
                # 计算新的左边界
                left = event.globalPos().x()
                # 确保窗口不会太小
                if window_rect.right() - left >= self.window.minimumWidth():
                    window_rect.setLeft(left)
            elif self.direction == Direction.RIGHT:
                window_rect.setRight(event.globalPos().x())
            elif self.direction == Direction.TOP:
                # 计算新的上边界
                top = event.globalPos().y()
                # 确保窗口不会太小
                if window_rect.bottom() - top >= self.window.minimumHeight():
                    window_rect.setTop(top)
            elif self.direction == Direction.BOTTOM:
                window_rect.setBottom(event.globalPos().y())
            elif self.direction == Direction.TOP_LEFT:
                # 计算新的左边界和上边界
                left = event.globalPos().x()
                top = event.globalPos().y()
                # 确保窗口不会太小
                if window_rect.right() - left >= self.window.minimumWidth():
                    window_rect.setLeft(left)
                if window_rect.bottom() - top >= self.window.minimumHeight():
                    window_rect.setTop(top)
            elif self.direction == Direction.TOP_RIGHT:
                # 计算新的右边界和上边界
                right = event.globalPos().x()
                top = event.globalPos().y()
                # 确保窗口不会太小
                if right - window_rect.left() >= self.window.minimumWidth():
                    window_rect.setRight(right)
                if window_rect.bottom() - top >= self.window.minimumHeight():
                    window_rect.setTop(top)
            elif self.direction == Direction.BOTTOM_LEFT:
                # 计算新的左边界和下边界
                left = event.globalPos().x()
                bottom = event.globalPos().y()
                # 确保窗口不会太小
                if window_rect.right() - left >= self.window.minimumWidth():
                    window_rect.setLeft(left)
                if bottom - window_rect.top() >= self.window.minimumHeight():
                    window_rect.setBottom(bottom)
            elif self.direction == Direction.BOTTOM_RIGHT:
                # 计算新的右边界和下边界
                right = event.globalPos().x()
                bottom = event.globalPos().y()
                # 确保窗口不会太小
                if right - window_rect.left() >= self.window.minimumWidth():
                    window_rect.setRight(right)
                if bottom - window_rect.top() >= self.window.minimumHeight():
                    window_rect.setBottom(bottom)
            
            # 设置窗口几何形状
            self.window.setGeometry(window_rect)
            
            event.accept()
        else:
            # 否则，更新鼠标形状
            direction = self.get_direction(pos)
            self.set_cursor_shape(direction)
            
            # 调用原始事件处理器
            self.original_mouse_move_event(event)
    
    def mouse_release_event(self, event):
        """
        鼠标释放事件
        
        Args:
            event: 事件对象
        """
        # 重置鼠标按下状态
        self.mouse_pressed = False
        self.direction = Direction.NONE
        
        # 调用原始事件处理器
        self.original_mouse_release_event(event)