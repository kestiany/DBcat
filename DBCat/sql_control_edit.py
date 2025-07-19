# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QTabWidget, QTabBar, QTableView, QApplication, QAbstractItemView
from PyQt5.QtCore import Qt, QModelIndex, QAbstractTableModel, QVariant, QSortFilterProxyModel

from DBCat.dboperator import mysql_operator
from DBCat import resource as res
from DBCat.component import sqlTableView
from DBCat.component.sql_history import sql_history_manager

# 配置日志记录
logger = logging.getLogger(__name__)


class SqlControlEdit:
    def __init__(self, tabWidget):
        super().__init__()
        self.sqlMessage = None
        self.tabWidget = tabWidget

        self.tabWidget.setTabsClosable(True)
        self.tabWidget.tabBar().setTabButton(0, QTabBar.RightSide, None)
        self.tabWidget.tabBar().setTabButton(1, QTabBar.RightSide, None)
        self.tabWidget.setCurrentIndex(0)
        self.tabWidget.setTabIcon(0, QIcon(res.resource_path("image/msg.svg")))
        self.tabWidget.setTabIcon(1, QIcon(res.resource_path("image/result.svg")))
        self.tabWidget.tabCloseRequested.connect(self.tab_close)

        self.icon_table = QIcon(res.resource_path("image/table.svg"))
        self.icon_index = QIcon(res.resource_path("image/index.svg"))

    def init_message(self, sqlMessage):
        self.sqlMessage = sqlMessage
        font = QFont()
        font.setFamily("Courier New")
        font.setStyleHint(QFont.Monospace)
        font.setPointSize(12)
        self.sqlMessage.setFont(font)

    def tab_close(self, index):
        self.tabWidget.removeTab(index)

    def set_msg(self, msg):
        current_time = datetime.now()
        self.sqlMessage.setPlainText(
            '{}{} {}'.format(current_time.strftime("%H:%M:%S"), ".{:03d}"
                             .format(current_time.microsecond // 1000), msg))
        self.tabWidget.setCurrentIndex(0)

    def show_index(self, id, db_name, table_name):
        records, headers = mysql_operator.MysqlOperator().do_exec_statement(id, db_name, 'SHOW INDEX FROM {}'.format(table_name))
        if records is not None:
            self.add_tab(table_name, records, headers, 'INDEX')
        else:
            self.set_msg(headers)

    def open_table(self, id, db_name, table_name):
        records, headers = mysql_operator.MysqlOperator().do_exec_statement(id, db_name, 'SELECT * FROM {}'.format(table_name))
        if records is not None:
            self.add_tab(table_name, records, headers, 'TABLE')
        else:
            self.set_msg(headers)

    def add_tab(self, name, records, headers, type):
        table_view = sqlTableView.SqlTableView()
        self.__fill_table_widget(table_view, records, headers)
        index = self.tabWidget.addTab(table_view, self.icon_index if type == 'INDEX' else self.icon_table, name)
        self.tabWidget.setCurrentIndex(index)

    def exec_sql(self, id, db_name, sql, host_name=""):
        try:
            # 执行SQL语句
            records, headers = mysql_operator.MysqlOperator().do_exec_statement(id, db_name, sql)
            
            # 记录到历史记录
            success = True
            affected_rows = 0
            
            if records is not None:
                # 查询语句执行成功
                affected_rows = len(records)
                self.set_msg('[exec success]: {}, [result rows]: {}'.format(sql, affected_rows))
                self.fill_result(records, headers)
            else:
                # 非查询语句执行成功或失败
                if isinstance(headers, str) and headers.startswith("error:"):
                    success = False
                    self.set_msg(headers)
                else:
                    # 提取受影响的行数
                    try:
                        if isinstance(headers, str) and "Affected rows:" in headers:
                            affected_rows = int(headers.split("Affected rows:")[1].strip())
                    except:
                        pass
                    self.set_msg(headers)
            
            # 保存到历史记录
            sql_history_manager.add_record(
                sql=sql,
                database=db_name,
                host_name=host_name,
                success=success,
                affected_rows=affected_rows
            )
            
        except Exception as e:
            # 执行出错
            self.set_msg(f'[ERROR]: {e}')
            
            # 记录错误到历史记录
            sql_history_manager.add_record(
                sql=sql,
                database=db_name,
                host_name=host_name,
                success=False,
                affected_rows=0
            )

    def fill_result(self, records, headers):
        table_view = self.tabWidget.widget(1)
        table_view.reset()
        self.__fill_table_widget(table_view, records, headers)
        self.tabWidget.setCurrentIndex(1)

    def __fill_table_widget(self, view, records, headers):
        # 创建模型
        model = MyTableModel(records, headers)
        proxy_model = QSortFilterProxyModel()
        proxy_model.setSourceModel(model)
        view.setModel(proxy_model)
        view.setSortingEnabled(True)
        view.setSelectionMode(QAbstractItemView.ContiguousSelection)


class MyTableModel(QAbstractTableModel):
    def __init__(self, data, header):
        super().__init__()
        self._data = data
        self._header = header

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self._header)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            row = index.row()
            col = index.column()
            return '' if not self._data[row][col] else str(self._data[row][col])

        return QVariant()

    def item_data(self, row, col):
        return '' if not self._data[row][col] else str(self._data[row][col])

    def item_head(self, col):
        return self._header[col]

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._header[section]
            elif orientation == Qt.Vertical:
                return f"{section}"
        return QVariant()
