#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据导出模块
提供将数据库表导出为SQL、CSV等格式的功能
"""

import os
import csv
import logging
import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import pandas as pd
from PyQt5 import QtWidgets, QtCore, QtGui

from DBCat.dboperator.mysql_operator import MysqlOperator
from DBCat.error_handler import show_info_message, show_warning_message, FileErrorHandler

# 配置日志记录
logger = logging.getLogger(__name__)


class DataExporter:
    """数据导出类，提供多种格式的数据导出功能"""
    
    # 支持的导出格式
    EXPORT_FORMATS = {
        'sql': '数据库SQL脚本 (*.sql)',
        'csv': '逗号分隔值 (*.csv)',
        'excel': 'Excel工作表 (*.xlsx)',
        'json': 'JSON文件 (*.json)',
        'xml': 'XML文件 (*.xml)',
    }
    
    def __init__(self, parent: Optional[QtWidgets.QWidget] = None):
        """
        初始化数据导出器
        
        Args:
            parent: 父窗口，用于显示对话框
        """
        self.parent = parent
        self.mysql_operator = MysqlOperator()
    
    def export_table_data(self, host_id: str, database: str, table: str) -> bool:
        """
        导出表数据
        
        Args:
            host_id: 主机ID
            database: 数据库名称
            table: 表名
            
        Returns:
            是否成功导出
        """
        # 创建导出选项对话框
        dialog = ExportOptionsDialog(self.parent, table)
        if dialog.exec_() != QtWidgets.QDialog.Accepted:
            return False
        
        # 获取用户选择的选项
        options = dialog.get_options()
        
        # 获取保存文件路径
        file_path = self._get_save_file_path(table, options['format'])
        if not file_path:
            return False
        
        # 根据选项构建SQL查询
        query = self._build_export_query(table, options)
        
        # 执行查询获取数据
        records, columns = self.mysql_operator.do_exec_statement(host_id, database, query)
        if records is None:
            show_warning_message(
                "导出失败", 
                "无法获取表数据", 
                "查询执行失败，请检查表是否存在或权限是否足够。", 
                self.parent
            )
            return False
        
        # 导出数据到文件
        try:
            if options['format'] == 'sql':
                success = self._export_to_sql(file_path, database, table, records, columns, options)
            elif options['format'] == 'csv':
                success = self._export_to_csv(file_path, records, columns)
            elif options['format'] == 'excel':
                success = self._export_to_excel(file_path, records, columns, table)
            elif options['format'] == 'json':
                success = self._export_to_json(file_path, records, columns)
            elif options['format'] == 'xml':
                success = self._export_to_xml(file_path, records, columns, table)
            else:
                show_warning_message(
                    "导出失败", 
                    f"不支持的导出格式: {options['format']}", 
                    "请选择支持的导出格式。", 
                    self.parent
                )
                return False
                
            if success:
                show_info_message(
                    "导出成功", 
                    f"表 {table} 已成功导出到 {file_path}", 
                    f"共导出 {len(records)} 条记录。", 
                    self.parent
                )
                return True
            else:
                return False
                
        except Exception as e:
            logger.error(f"导出数据时出错: {str(e)}")
            FileErrorHandler.handle_file_error(
                e, 
                str(file_path), 
                parent=self.parent, 
                show_dialog=True
            )
            return False
    
    def _get_save_file_path(self, table: str, format_type: str) -> Optional[str]:
        """
        获取保存文件的路径
        
        Args:
            table: 表名
            format_type: 导出格式
            
        Returns:
            文件路径，如果用户取消则返回None
        """
        # 获取当前日期时间字符串
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"{table}_{now}"
        
        # 获取文件过滤器
        file_filter = self.EXPORT_FORMATS.get(format_type, '')
        
        # 显示保存文件对话框
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
            self.parent,
            "保存导出文件",
            default_name,
            file_filter
        )
        
        return file_path if file_path else None
    
    def _build_export_query(self, table: str, options: Dict[str, Any]) -> str:
        """
        根据选项构建导出查询
        
        Args:
            table: 表名
            options: 导出选项
            
        Returns:
            SQL查询语句
        """
        # 构建SELECT部分
        if options['selected_columns']:
            columns = ", ".join([f"`{col}`" for col in options['selected_columns']])
        else:
            columns = "*"
        
        # 构建WHERE部分
        where_clause = ""
        if options['where_condition']:
            where_clause = f" WHERE {options['where_condition']}"
        
        # 构建ORDER BY部分
        order_by = ""
        if options['order_by']:
            order_by = f" ORDER BY {options['order_by']}"
        
        # 构建LIMIT部分
        limit = ""
        if options['limit'] > 0:
            limit = f" LIMIT {options['limit']}"
        
        # 组合完整查询
        query = f"SELECT {columns} FROM `{table}`{where_clause}{order_by}{limit}"
        
        return query
    
    def _export_to_sql(self, file_path: str, database: str, table: str, 
                      records: List[tuple], columns: List[str], 
                      options: Dict[str, Any]) -> bool:
        """
        导出为SQL脚本
        
        Args:
            file_path: 文件路径
            database: 数据库名称
            table: 表名
            records: 记录列表
            columns: 列名列表
            options: 导出选项
            
        Returns:
            是否成功导出
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                # 写入文件头
                f.write(f"-- 导出表 {database}.{table} 的数据\n")
                f.write(f"-- 导出时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # 如果需要包含表结构
                if options['include_structure']:
                    # 获取表结构
                    create_table_query = f"SHOW CREATE TABLE `{table}`"
                    result, _ = self.mysql_operator.do_exec_statement(
                        options['host_id'], database, create_table_query
                    )
                    if result and len(result) > 0:
                        create_statement = result[0][1]
                        f.write(f"{create_statement};\n\n")
                
                # 写入数据插入语句
                if records:
                    # 如果需要包含DELETE语句
                    if options['include_delete']:
                        f.write(f"DELETE FROM `{table}`;\n\n")
                    
                    # 写入INSERT语句
                    column_names = ", ".join([f"`{col}`" for col in columns])
                    
                    # 分批写入，每批1000条记录
                    batch_size = 1000
                    for i in range(0, len(records), batch_size):
                        batch = records[i:i+batch_size]
                        
                        # 构建INSERT语句
                        f.write(f"INSERT INTO `{table}` ({column_names}) VALUES\n")
                        
                        # 构建VALUES部分
                        values_list = []
                        for record in batch:
                            values = []
                            for value in record:
                                if value is None:
                                    values.append("NULL")
                                elif isinstance(value, (int, float)):
                                    values.append(str(value))
                                elif isinstance(value, (datetime.date, datetime.datetime)):
                                    values.append(f"'{value}'")
                                else:
                                    # 转义字符串中的单引号
                                    escaped_value = str(value).replace("'", "''")
                                    values.append(f"'{escaped_value}'")
                            values_list.append(f"({', '.join(values)})")
                        
                        # 写入VALUES
                        f.write(",\n".join(values_list))
                        f.write(";\n\n")
            
            return True
            
        except Exception as e:
            logger.error(f"导出SQL文件时出错: {str(e)}")
            raise
    
    def _export_to_csv(self, file_path: str, records: List[tuple], columns: List[str]) -> bool:
        """
        导出为CSV文件
        
        Args:
            file_path: 文件路径
            records: 记录列表
            columns: 列名列表
            
        Returns:
            是否成功导出
        """
        try:
            with open(file_path, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                
                # 写入表头
                writer.writerow(columns)
                
                # 写入数据行
                for record in records:
                    writer.writerow(record)
            
            return True
            
        except Exception as e:
            logger.error(f"导出CSV文件时出错: {str(e)}")
            raise
    
    def _export_to_excel(self, file_path: str, records: List[tuple], 
                        columns: List[str], sheet_name: str) -> bool:
        """
        导出为Excel文件
        
        Args:
            file_path: 文件路径
            records: 记录列表
            columns: 列名列表
            sheet_name: 工作表名称
            
        Returns:
            是否成功导出
        """
        try:
            # 创建DataFrame
            df = pd.DataFrame(records, columns=columns)
            
            # 导出到Excel
            with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            return True
            
        except Exception as e:
            logger.error(f"导出Excel文件时出错: {str(e)}")
            raise
    
    def _export_to_json(self, file_path: str, records: List[tuple], columns: List[str]) -> bool:
        """
        导出为JSON文件
        
        Args:
            file_path: 文件路径
            records: 记录列表
            columns: 列名列表
            
        Returns:
            是否成功导出
        """
        try:
            # 创建DataFrame
            df = pd.DataFrame(records, columns=columns)
            
            # 导出到JSON
            df.to_json(file_path, orient='records', force_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            logger.error(f"导出JSON文件时出错: {str(e)}")
            raise
    
    def _export_to_xml(self, file_path: str, records: List[tuple], 
                      columns: List[str], root_name: str) -> bool:
        """
        导出为XML文件
        
        Args:
            file_path: 文件路径
            records: 记录列表
            columns: 列名列表
            root_name: XML根元素名称
            
        Returns:
            是否成功导出
        """
        try:
            # 创建DataFrame
            df = pd.DataFrame(records, columns=columns)
            
            # 导出到XML
            xml_content = f'<?xml version="1.0" encoding="UTF-8"?>\n<{root_name}>\n'
            
            # 遍历记录
            for _, row in df.iterrows():
                xml_content += '  <record>\n'
                for col in columns:
                    value = row[col]
                    if pd.isna(value):
                        xml_content += f'    <{col} xsi:nil="true" />\n'
                    else:
                        # 转义XML特殊字符
                        if isinstance(value, str):
                            value = value.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
                        xml_content += f'    <{col}>{value}</{col}>\n'
                xml_content += '  </record>\n'
            
            xml_content += f'</{root_name}>'
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(xml_content)
            
            return True
            
        except Exception as e:
            logger.error(f"导出XML文件时出错: {str(e)}")
            raise


class ExportOptionsDialog(QtWidgets.QDialog):
    """导出选项对话框"""
    
    def __init__(self, parent: Optional[QtWidgets.QWidget], table_name: str):
        """
        初始化导出选项对话框
        
        Args:
            parent: 父窗口
            table_name: 表名
        """
        super(ExportOptionsDialog, self).__init__(parent)
        self.table_name = table_name
        self.selected_columns = []
        self.setup_ui()
    
    def setup_ui(self):
        """设置UI界面"""
        self.setWindowTitle(f"导出表 {self.table_name}")
        self.setMinimumWidth(500)
        
        # 主布局
        layout = QtWidgets.QVBoxLayout(self)
        
        # 导出格式
        format_group = QtWidgets.QGroupBox("导出格式")
        format_layout = QtWidgets.QVBoxLayout(format_group)
        
        self.format_combo = QtWidgets.QComboBox()
        self.format_combo.addItem("SQL脚本 (*.sql)", "sql")
        self.format_combo.addItem("CSV文件 (*.csv)", "csv")
        self.format_combo.addItem("Excel文件 (*.xlsx)", "excel")
        self.format_combo.addItem("JSON文件 (*.json)", "json")
        self.format_combo.addItem("XML文件 (*.xml)", "xml")
        self.format_combo.currentIndexChanged.connect(self.on_format_changed)
        format_layout.addWidget(self.format_combo)
        
        layout.addWidget(format_group)
        
        # SQL选项组
        self.sql_options_group = QtWidgets.QGroupBox("SQL选项")
        sql_options_layout = QtWidgets.QVBoxLayout(self.sql_options_group)
        
        self.include_structure = QtWidgets.QCheckBox("包含表结构 (CREATE TABLE)")
        self.include_structure.setChecked(True)
        sql_options_layout.addWidget(self.include_structure)
        
        self.include_delete = QtWidgets.QCheckBox("包含DELETE语句")
        self.include_delete.setChecked(False)
        sql_options_layout.addWidget(self.include_delete)
        
        layout.addWidget(self.sql_options_group)
        
        # 数据选项组
        data_options_group = QtWidgets.QGroupBox("数据选项")
        data_options_layout = QtWidgets.QVBoxLayout(data_options_group)
        
        # 列选择
        columns_layout = QtWidgets.QHBoxLayout()
        columns_label = QtWidgets.QLabel("选择列:")
        self.columns_button = QtWidgets.QPushButton("选择列...")
        self.columns_button.clicked.connect(self.select_columns)
        columns_layout.addWidget(columns_label)
        columns_layout.addWidget(self.columns_button)
        data_options_layout.addLayout(columns_layout)
        
        # WHERE条件
        where_layout = QtWidgets.QHBoxLayout()
        where_label = QtWidgets.QLabel("WHERE条件:")
        self.where_edit = QtWidgets.QLineEdit()
        where_layout.addWidget(where_label)
        where_layout.addWidget(self.where_edit)
        data_options_layout.addLayout(where_layout)
        
        # ORDER BY
        order_layout = QtWidgets.QHBoxLayout()
        order_label = QtWidgets.QLabel("ORDER BY:")
        self.order_edit = QtWidgets.QLineEdit()
        order_layout.addWidget(order_label)
        order_layout.addWidget(self.order_edit)
        data_options_layout.addLayout(order_layout)
        
        # LIMIT
        limit_layout = QtWidgets.QHBoxLayout()
        limit_label = QtWidgets.QLabel("LIMIT:")
        self.limit_spin = QtWidgets.QSpinBox()
        self.limit_spin.setMinimum(0)
        self.limit_spin.setMaximum(1000000)
        self.limit_spin.setValue(0)
        self.limit_spin.setSpecialValueText("无限制")
        limit_layout.addWidget(limit_label)
        limit_layout.addWidget(self.limit_spin)
        data_options_layout.addLayout(limit_layout)
        
        layout.addWidget(data_options_group)
        
        # 按钮
        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        # 初始化UI状态
        self.on_format_changed()
    
    def on_format_changed(self):
        """格式选择变更时的处理"""
        current_format = self.format_combo.currentData()
        self.sql_options_group.setVisible(current_format == "sql")
    
    def select_columns(self):
        """选择列对话框"""
        # 这里应该从数据库获取列信息，但为简化示例，我们使用一个简单的对话框
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle(f"选择 {self.table_name} 表的列")
        dialog.setMinimumWidth(300)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        
        # 这里应该添加列选择控件，但为简化示例，我们使用一个文本输入
        label = QtWidgets.QLabel("输入列名，用逗号分隔:")
        layout.addWidget(label)
        
        columns_edit = QtWidgets.QLineEdit()
        if self.selected_columns:
            columns_edit.setText(", ".join(self.selected_columns))
        layout.addWidget(columns_edit)
        
        button_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            columns_text = columns_edit.text().strip()
            if columns_text:
                self.selected_columns = [col.strip() for col in columns_text.split(",")]
            else:
                self.selected_columns = []
    
    def get_options(self) -> Dict[str, Any]:
        """
        获取用户选择的导出选项
        
        Returns:
            导出选项字典
        """
        return {
            'format': self.format_combo.currentData(),
            'include_structure': self.include_structure.isChecked(),
            'include_delete': self.include_delete.isChecked(),
            'selected_columns': self.selected_columns,
            'where_condition': self.where_edit.text().strip(),
            'order_by': self.order_edit.text().strip(),
            'limit': self.limit_spin.value(),
            'host_id': '',  # 这个值会在实际导出时设置
        }