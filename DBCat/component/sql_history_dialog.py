#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SQL历史记录对话框模块
提供SQL查询历史记录的查看和重用功能
"""

import logging
from typing import Optional, Callable
from PyQt5 import QtWidgets, QtCore, QtGui

from DBCat.component.sql_history import sql_history_manager

# 配置日志记录
logger = logging.getLogger(__name__)


class SqlHistoryDialog(QtWidgets.QDialog):
    """SQL历史记录对话框，用于查看和重用历史记录"""
    
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None, 
                callback: Optional[Callable[[str], None]] = None):
        """
        初始化SQL历史记录对话框
        
        Args:
            parent: 父窗口
            callback: 选择SQL语句时的回调函数
        """
        super(SqlHistoryDialog, self).__init__(parent)
        self.callback = callback
        self.setup_ui()
        self.load_history()
    
    def setup_ui(self):
        """设置UI界面"""
        self.setWindowTitle("SQL历史记录")
        self.resize(800, 600)
        
        # 主布局
        layout = QtWidgets.QVBoxLayout(self)
        
        # 过滤区域
        filter_layout = QtWidgets.QHBoxLayout()
        
        filter_label = QtWidgets.QLabel("过滤:")
        self.filter_edit = QtWidgets.QLineEdit()
        self.filter_edit.setPlaceholderText("输入关键字过滤历史记录")
        self.filter_edit.textChanged.connect(self.filter_history)
        
        filter_layout.addWidget(filter_label)
        filter_layout.addWidget(self.filter_edit)
        
        # 数据库过滤
        db_label = QtWidgets.QLabel("数据库:")
        self.db_combo = QtWidgets.QComboBox()
        self.db_combo.addItem("全部", "")
        self.db_combo.currentIndexChanged.connect(self.filter_history)
        
        filter_layout.addWidget(db_label)
        filter_layout.addWidget(self.db_combo)
        
        # 主机过滤
        host_label = QtWidgets.QLabel("主机:")
        self.host_combo = QtWidgets.QComboBox()
        self.host_combo.addItem("全部", "")
        self.host_combo.currentIndexChanged.connect(self.filter_history)
        
        filter_layout.addWidget(host_label)
        filter_layout.addWidget(self.host_combo)
        
        layout.addLayout(filter_layout)
        
        # 历史记录表格
        self.history_table = QtWidgets.QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(["SQL语句", "数据库", "主机", "时间", "状态"])
        self.history_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.history_table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.history_table.setAlternatingRowColors(True)
        self.history_table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        self.history_table.doubleClicked.connect(self.on_item_double_clicked)
        
        layout.addWidget(self.history_table)
        
        # 预览区域
        preview_group = QtWidgets.QGroupBox("SQL预览")
        preview_layout = QtWidgets.QVBoxLayout(preview_group)
        
        self.preview_text = QtWidgets.QPlainTextEdit()
        self.preview_text.setReadOnly(True)
        preview_layout.addWidget(self.preview_text)
        
        layout.addWidget(preview_group)
        
        # 按钮区域
        button_layout = QtWidgets.QHBoxLayout()
        
        self.use_button = QtWidgets.QPushButton("使用所选SQL")
        self.use_button.clicked.connect(self.use_selected_sql)
        
        self.delete_button = QtWidgets.QPushButton("删除所选记录")
        self.delete_button.clicked.connect(self.delete_selected_record)
        
        self.clear_button = QtWidgets.QPushButton("清空历史记录")
        self.clear_button.clicked.connect(self.clear_history)
        
        self.close_button = QtWidgets.QPushButton("关闭")
        self.close_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.use_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.clear_button)
        button_layout.addStretch()
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        # 连接信号
        self.history_table.itemSelectionChanged.connect(self.on_selection_changed)
    
    def load_history(self):
        """加载历史记录"""
        # 获取历史记录
        records = sql_history_manager.get_records()
        
        # 清空表格
        self.history_table.setRowCount(0)
        
        # 填充表格
        self.history_table.setRowCount(len(records))
        
        # 收集数据库和主机名称
        databases = set()
        hosts = set()
        
        for row, record in enumerate(records):
            # SQL语句
            sql_item = QtWidgets.QTableWidgetItem(record['sql'][:100] + ('...' if len(record['sql']) > 100 else ''))
            sql_item.setData(QtCore.Qt.UserRole, record)
            self.history_table.setItem(row, 0, sql_item)
            
            # 数据库
            db_name = record.get('database', '')
            if db_name:
                databases.add(db_name)
            self.history_table.setItem(row, 1, QtWidgets.QTableWidgetItem(db_name))
            
            # 主机
            host_name = record.get('host', '')
            if host_name:
                hosts.add(host_name)
            self.history_table.setItem(row, 2, QtWidgets.QTableWidgetItem(host_name))
            
            # 时间
            self.history_table.setItem(row, 3, QtWidgets.QTableWidgetItem(record.get('datetime', '')))
            
            # 状态
            status = "成功" if record.get('success', True) else "失败"
            status_item = QtWidgets.QTableWidgetItem(status)
            status_item.setForeground(QtGui.QColor("green" if record.get('success', True) else "red"))
            self.history_table.setItem(row, 4, status_item)
        
        # 更新过滤下拉框
        self._update_filter_combos(databases, hosts)
    
    def _update_filter_combos(self, databases, hosts):
        """
        更新过滤下拉框
        
        Args:
            databases: 数据库名称集合
            hosts: 主机名称集合
        """
        # 保存当前选择
        current_db = self.db_combo.currentData()
        current_host = self.host_combo.currentData()
        
        # 清空下拉框
        self.db_combo.clear()
        self.host_combo.clear()
        
        # 添加"全部"选项
        self.db_combo.addItem("全部", "")
        self.host_combo.addItem("全部", "")
        
        # 添加数据库选项
        for db in sorted(databases):
            if db:
                self.db_combo.addItem(db, db)
        
        # 添加主机选项
        for host in sorted(hosts):
            if host:
                self.host_combo.addItem(host, host)
        
        # 恢复选择
        db_index = self.db_combo.findData(current_db)
        if db_index >= 0:
            self.db_combo.setCurrentIndex(db_index)
        
        host_index = self.host_combo.findData(current_host)
        if host_index >= 0:
            self.host_combo.setCurrentIndex(host_index)
    
    def filter_history(self):
        """过滤历史记录"""
        filter_text = self.filter_edit.text()
        database = self.db_combo.currentData()
        host = self.host_combo.currentData()
        
        # 获取过滤后的历史记录
        records = sql_history_manager.get_records(
            filter_text=filter_text,
            database=database,
            host=host
        )
        
        # 清空表格
        self.history_table.setRowCount(0)
        
        # 填充表格
        self.history_table.setRowCount(len(records))
        
        for row, record in enumerate(records):
            # SQL语句
            sql_item = QtWidgets.QTableWidgetItem(record['sql'][:100] + ('...' if len(record['sql']) > 100 else ''))
            sql_item.setData(QtCore.Qt.UserRole, record)
            self.history_table.setItem(row, 0, sql_item)
            
            # 数据库
            self.history_table.setItem(row, 1, QtWidgets.QTableWidgetItem(record.get('database', '')))
            
            # 主机
            self.history_table.setItem(row, 2, QtWidgets.QTableWidgetItem(record.get('host', '')))
            
            # 时间
            self.history_table.setItem(row, 3, QtWidgets.QTableWidgetItem(record.get('datetime', '')))
            
            # 状态
            status = "成功" if record.get('success', True) else "失败"
            status_item = QtWidgets.QTableWidgetItem(status)
            status_item.setForeground(QtGui.QColor("green" if record.get('success', True) else "red"))
            self.history_table.setItem(row, 4, status_item)
    
    def on_selection_changed(self):
        """选择变更时的处理"""
        selected_rows = self.history_table.selectedItems()
        if not selected_rows:
            self.preview_text.clear()
            return
        
        # 获取选中行的第一列
        row = selected_rows[0].row()
        item = self.history_table.item(row, 0)
        if item:
            record = item.data(QtCore.Qt.UserRole)
            if record:
                self.preview_text.setPlainText(record['sql'])
    
    def on_item_double_clicked(self, index):
        """双击表格项的处理"""
        row = index.row()
        item = self.history_table.item(row, 0)
        if item:
            record = item.data(QtCore.Qt.UserRole)
            if record and self.callback:
                self.callback(record['sql'])
                self.accept()
    
    def use_selected_sql(self):
        """使用选中的SQL语句"""
        selected_rows = self.history_table.selectedItems()
        if not selected_rows:
            return
        
        # 获取选中行的第一列
        row = selected_rows[0].row()
        item = self.history_table.item(row, 0)
        if item:
            record = item.data(QtCore.Qt.UserRole)
            if record and self.callback:
                self.callback(record['sql'])
                self.accept()
    
    def delete_selected_record(self):
        """删除选中的记录"""
        selected_rows = self.history_table.selectedItems()
        if not selected_rows:
            return
        
        # 获取选中行
        row = selected_rows[0].row()
        
        # 确认删除
        reply = QtWidgets.QMessageBox.question(
            self,
            "确认删除",
            "确定要删除选中的历史记录吗？",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            # 删除记录
            if sql_history_manager.delete_record(row):
                # 重新加载历史记录
                self.load_history()
    
    def clear_history(self):
        """清空历史记录"""
        # 确认清空
        reply = QtWidgets.QMessageBox.question(
            self,
            "确认清空",
            "确定要清空所有历史记录吗？此操作不可恢复！",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )
        
        if reply == QtWidgets.QMessageBox.Yes:
            # 清空历史记录
            if sql_history_manager.clear_history():
                # 重新加载历史记录
                self.load_history()