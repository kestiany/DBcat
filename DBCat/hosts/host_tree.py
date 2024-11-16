# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QTreeWidgetItem, QMenu, QDialog, QMessageBox, QInputDialog
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QCursor, QFont

from DBCat.hosts import host_oper
from DBCat.hosts import host_edit_dialog
from DBCat.dboperator import mysql_operator
from DBCat import resource as res


class HostTree:
    """节点类型定义(常量)"""
    HOST = 'HOST'
    DATABASE = 'DATABASE'
    TABLE = 'TABLE'
    INDEX = 'INDEX'

    def __init__(self, tree_widget, sql_control_widget):
        self.contextMenu = QMenu()
        self.sql_tree_widget = tree_widget
        self.sql_control_widget = sql_control_widget
        font = QFont()
        font.setFamily("Courier New")
        font.setStyleHint(QFont.Monospace)
        font.setPointSize(12)
        self.sql_tree_widget.setFont(font)
        self.sql_tree_widget.setIndentation(int(self.sql_tree_widget.indentation() / 2))
        self.sql_tree_widget.header().setVisible(False)
        self.sql_tree_widget.setExpandsOnDoubleClick(True)
        self.sql_tree_widget.setColumnCount(1)

        self.sql_tree_widget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.sql_tree_widget.customContextMenuRequested.connect(self.showContextMenu)
        self.sql_tree_widget.itemDoubleClicked.connect(self.itemDoubleClicked)

        self.host_oper = host_oper.HostOper(res.setting_file())
        self.init_host()
        self.init_menu()

    def exec_sql(self, sql_statement, high_risk_operator):
        if not sql_statement:
            return

        item = self.sql_tree_widget.currentItem()
        if item is not None:
            node_type = self.getItemType(item)
            database = ''
            if node_type == HostTree.DATABASE:
                database = item.text(0)
            elif node_type == HostTree.TABLE:
                database = item.parent().text(0)

        if high_risk_operator:
            is_production, name = HostTree.is_production_env(item)
            if is_production:
                text, ok = QInputDialog.getText(self.sql_tree_widget,
                                                '数据更改警告',
                                                '高危操作-数据变更\n\n生产数据库[{}]\n\n'
                                                '若要继续，请输入连接名称：'.format(name))
                # 如果用户点击OK
                if ok:
                    if text == name:
                        self.sql_control_widget.exec_sql(self.getItemHostId(item), database, sql_statement)
                    else:
                        QMessageBox.warning(self.sql_tree_widget, "警告",
                                            "您输入的连接名称：{} 与实际名称不匹配，\n操作将终止!".format(text),
                                            QMessageBox.Yes,
                                            QMessageBox.Yes)
            else:
                self.sql_control_widget.exec_sql(self.getItemHostId(item), database, sql_statement)
        else:
            self.sql_control_widget.exec_sql(self.getItemHostId(item), database, sql_statement)

    @staticmethod
    def is_production_env(item):
        """判断当前数据库是否为生产环境"""
        if item is not None:
            while item.parent() is not None:
                item = item.parent()

            label_name = item.text(0)
            last_open_bracket = label_name.rfind('[')
            last_close_bracket = label_name.rfind(']')

            # 确保找到的括号是有效的
            if last_open_bracket == -1 or last_close_bracket == -1 or last_open_bracket >= last_close_bracket:
                return False, ''

            # 分割字符串
            part_in_brackets = label_name[last_open_bracket + 1 :last_close_bracket]
            if part_in_brackets == "生产":
                return True, label_name[:last_open_bracket]
            else:
                return False, label_name[:last_open_bracket]

        return False, ''

    def add_host(self, host):
        # 先存储到文件
        self.host_oper.add_host(host)
        # 新增节点到左树
        self.sql_tree_widget.addTopLevelItem(self.create_host_item(host))

    def init_host(self):
        hosts = self.host_oper.get_hosts()
        for host in hosts:
            self.sql_tree_widget.addTopLevelItem(self.create_host_item(host))

    def create_host_item(self, host):
        item = QTreeWidgetItem()
        item.setText(0, '{}[{}]'.format(host.name, host.environment))
        self.setItemHost(item, host)
        self.setItemTypeAndIcon(item, HostTree.HOST, host.type)
        return item

    @staticmethod
    def getItemHostId(item):
        return item.data(0, Qt.UserRole + 998)

    @staticmethod
    def setItemHostId(item, id):
        if item is not None:
            item.setData(0, Qt.UserRole + 998, id)

    @staticmethod
    def getItemHost(item):
        return item.data(0, Qt.UserRole + 997)

    @staticmethod
    def setItemHost(item, host):
        if item is not None:
            item.setData(0, Qt.UserRole + 998, host.id)
            item.setData(0, Qt.UserRole + 997, host)

    @staticmethod
    def setItemTypeAndIcon(item, node, type):
        if item is not None:
            item.setData(0, Qt.UserRole + 999, node)

            if node == HostTree.HOST:
                item.setIcon(0, QIcon(res.resource_path('image/{}.svg'.format(type))))
            elif node == HostTree.DATABASE:
                item.setIcon(0, QIcon(res.resource_path('image/database.svg')))
            elif node == HostTree.TABLE:
                item.setIcon(0, QIcon(res.resource_path('image/table.svg')))

    @staticmethod
    def getItemType(item):
        if item is not None:
            return item.data(0, Qt.UserRole + 999)
        else:
            return 'NONE'

    def init_menu(self):
        # connect action
        self.actEditConn = self.contextMenu.addAction(QIcon(res.resource_path("image/edit.svg")), "edit Connection")
        self.actEditConn.triggered.connect(self.edit_conn)
        self.actDelConn = self.contextMenu.addAction(QIcon(res.resource_path("image/delete.svg")), "del Connection")
        self.actDelConn.triggered.connect(self.del_conn)
        self.actCloseConn = self.contextMenu.addAction(QIcon(res.resource_path("image/database_close.svg")),
                                                       "close Connection")
        self.actCloseConn.triggered.connect(self.close_conn)
        # database action
        self.actCloseDB = self.contextMenu.addAction(QIcon(res.resource_path("image/edit.svg")), "close database")
        self.actCloseDB.triggered.connect(self.close_database)
        self.actCreateDB = self.contextMenu.addAction(QIcon(res.resource_path("image/newsql.svg")), "create database")
        self.actCreateDB.triggered.connect(self.create_database)
        self.actDropDB = self.contextMenu.addAction(QIcon(res.resource_path("image/delete.svg")), "drop database")
        self.actDropDB.triggered.connect(self.drop_database)
        # table action
        self.actIndexTable = self.contextMenu.addAction(QIcon(res.resource_path("image/index.svg")), "view index")
        self.actIndexTable.triggered.connect(self.show_index)
        self.actDeleteData = self.contextMenu.addAction(QIcon(res.resource_path("image/delete.svg")), "delete data")
        self.actDeleteData.triggered.connect(self.delete_data)
        self.actDropTable = self.contextMenu.addAction(QIcon(res.resource_path("image/delete.svg")), "drop table")
        self.actDropTable.triggered.connect(self.drop_data)

    def edit_conn(self):
        item = self.sql_tree_widget.currentItem()
        if self.getItemType(item) == HostTree.HOST:
            dialog = host_edit_dialog.HostEditDialog()
            dialog.init_with_host(self.getItemHost(item))
            if QDialog.Accepted == dialog.exec():
                host = dialog.get_host()
                self.host_oper.update_host(host)
                self.setItemHost(item, host)
                item.setText(0, '{}[{}]'.format(host.name, host.environment))

    def del_conn(self):
        item = self.sql_tree_widget.currentItem()
        if self.getItemType(item) == HostTree.HOST:
            item.takeChildren()
            self.host_oper.del_host(self.getItemHostId(item))
            self.sql_tree_widget.takeTopLevelItem(self.sql_tree_widget.indexOfTopLevelItem(item))

    def close_conn(self):
        item = self.sql_tree_widget.currentItem()
        if self.getItemType(item) == HostTree.HOST:
            item.takeChildren()
            mysql_operator.MysqlOperator().release_connection(self.getItemHostId(item))

    def close_database(self):
        item = self.sql_tree_widget.currentItem()
        if item is not None and self.getItemType(item) == HostTree.DATABASE:
            item.takeChildren()

    def create_database(self):
        self.sql_control_widget.set_msg(
            "create database sql statement\r\nCREATE DATABASE [name] DEFAULT CHARACTER SET = 'utf8'")

    def drop_database(self):
        item = self.sql_tree_widget.currentItem()
        if item is not None and self.getItemType(item) == HostTree.DATABASE:
            if self.warn_message_box('确认删除DB[{}]!!!    \r\n这将清空数据并删除数据表.    '.format(item.text(0))):
                sql = "DROP DATABASE {}".format(item.text(0))
                databases, msg = mysql_operator.MysqlOperator().do_exec_statement(self.getItemHostId(item), sql)
                self.sql_control_widget.set_msg('{}: {}'.format(sql, msg))
                item.takeChildren()
                item.parent().removeChild(item)

    def show_index(self):
        item = self.sql_tree_widget.currentItem()
        if item is not None and self.getItemType(item) == HostTree.TABLE:
            self.sql_control_widget.show_index(self.getItemHostId(item), item.parent().text(0), item.text(0))

    def delete_data(self):
        item = self.sql_tree_widget.currentItem()
        if item is not None and self.getItemType(item) == HostTree.TABLE:
            if self.warn_message_box('确认清空表[{}]内的所有数据？    '.format(item.text(0))):
                sql = "DELETE FROM {}".format(item.text(0))
                _, msg = mysql_operator.MysqlOperator().do_exec_statement(self.getItemHostId(item), "", sql)
                self.sql_control_widget.set_msg('[DELETE TABLE]{}: {}'.format(sql, msg))

    def drop_data(self):
        item = self.sql_tree_widget.currentItem()
        if item is not None and self.getItemType(item) == HostTree.TABLE:
            if self.warn_message_box('确认清空表[{}]内的所有数据, 并删除此表？    '.format(item.text(0))):
                sql = "DROP TABLE {}".format(item.text(0))
                _, msg = mysql_operator.MysqlOperator().do_exec_statement(self.getItemHostId(item), "", sql)
                self.sql_control_widget.set_msg('[DROP TABLE]{}: {}'.format(sql, msg))
                item.parent().removeChild(item)

    def warn_message_box(self, content):
        reply = QMessageBox.warning(
            self.sql_tree_widget, 'Warning', content,
            QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)
        if reply == QMessageBox.Ok:
            return True
        else:
            return False

    def showContextMenu(self, pos):
        item = self.sql_tree_widget.itemAt(pos)
        if item is None:
            return

        count = item.childCount()
        node_type = self.getItemType(item)
        for act in self.contextMenu.actions():
            act.setVisible(False)  # 先隐藏所有菜单
            act.setDisabled(False)

        if node_type == HostTree.HOST:
            self.actEditConn.setVisible(True)
            self.actDelConn.setVisible(True)
            if count > 0:
                self.actCloseConn.setVisible(True)
        elif node_type == HostTree.DATABASE:
            self.actCreateDB.setVisible(True)
            # self.actDropDB.setVisible(True)
            if count > 0:
                self.actCloseDB.setVisible(True)
        elif node_type == HostTree.TABLE:
            self.actIndexTable.setVisible(True)
            self.actDeleteData.setVisible(True)
            self.actDropTable.setVisible(True)
            production, _ = HostTree.is_production_env(item)
            if production:
                self.actDeleteData.setDisabled(True)
                self.actDropTable.setDisabled(True)
        elif node_type == HostTree.INDEX:
            pass

        self.contextMenu.exec(QCursor.pos())

    def itemDoubleClicked(self, item):
        if item is not None:
            node_type = self.getItemType(item)
            host_id = self.getItemHostId(item)
            child_count = item.childCount()
            if node_type == HostTree.HOST and child_count == 0:
                # 打开连接
                databases, msg = mysql_operator.MysqlOperator().database(self.getItemHost(item))
                self.sql_control_widget.set_msg('connect to:{} {}'.format(item.text(0), msg))
                if databases is not None:
                    for db in databases:
                        item.addChild(self.create_child_item(db, host_id, HostTree.DATABASE))
            elif node_type == HostTree.DATABASE and child_count == 0:
                # 查询数据库表
                tables, msg = mysql_operator.MysqlOperator().tables(host_id, item.text(0))
                for table in tables:
                    item.addChild(self.create_child_item(table, host_id, HostTree.TABLE))
            elif node_type == HostTree.TABLE:
                self.sql_control_widget.open_table(host_id, item.parent().text(0), item.text(0))

    def create_child_item(self, name, id, type):
        item = QTreeWidgetItem()
        item.setText(0, name)
        self.setItemTypeAndIcon(item, type, "")
        self.setItemHostId(item, id)
        return item
