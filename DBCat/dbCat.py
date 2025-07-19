# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets, QtCore, QtGui

from DBCat import sql_editor
from DBCat.hosts import host_tree
from DBCat.hosts import host_edit_dialog
from DBCat import sql_control_edit
from DBCat.dboperator import mysql_operator
from DBCat import resource as res
from DBCat.component import sqlTableView
from DBCat.component.theme_manager import theme_manager
from DBCat.component.title_bar import TitleBar
from DBCat.component.window_frame_handler import WindowFrameHandler

class DBCat(QtWidgets.QMainWindow):
    """主窗口"""

    def __init__(self, parent=None):
        super(DBCat, self).__init__(parent)
        # 设置无边框窗口
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        # 设置最小窗口大小，确保UI元素不会被挤压得太小
        self.setMinimumSize(800, 600)
        self.setupUi(self)

    def setupUi(self, DBcat):
        DBcat.setObjectName("DBcat")
        DBcat.resize(1187, 668)
        DBcat.setWindowTitle("DBCat")
        DBcat.setWindowIcon(QtGui.QIcon(res.resource_path('image/title.svg')))

        self.centralwidget = QtWidgets.QWidget(DBcat)
        self.centralwidget.setObjectName("centralwidget")
        
        # 创建主布局为垂直布局，以便添加标题栏
        self.verticalLayout_main = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout_main.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_main.setSpacing(0)
        self.verticalLayout_main.setObjectName("verticalLayout_main")
        
        # 添加自定义标题栏
        self.title_bar = TitleBar(self)
        self.verticalLayout_main.addWidget(self.title_bar)
        
        # 内容区域使用水平布局
        self.content_widget = QtWidgets.QWidget(self.centralwidget)
        self.content_widget.setObjectName("content_widget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.content_widget)
        self.horizontalLayout.setContentsMargins(9, 9, 9, 9)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_main.addWidget(self.content_widget, 1)  # 设置拉伸因子为1，使内容区域自适应
        self.splitter_2 = QtWidgets.QSplitter(self.content_widget)
        self.splitter_2.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_2.setObjectName("splitter_2")
        self.layoutWidget = QtWidgets.QWidget(self.splitter_2)
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.widgetSearch = QtWidgets.QWidget(self.layoutWidget)
        self.widgetSearch.setMinimumSize(QtCore.QSize(0, 36))
        self.widgetSearch.setMaximumSize(QtCore.QSize(16777215, 36))
        self.widgetSearch.setObjectName("widgetSearch")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.widgetSearch)
        self.horizontalLayout_2.setContentsMargins(2, 2, 2, 2)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.lineEdit = QtWidgets.QLineEdit(self.widgetSearch)
        self.lineEdit.setMinimumSize(QtCore.QSize(0, 24))
        self.lineEdit.setMaximumSize(QtCore.QSize(16777215, 24))
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout_2.addWidget(self.lineEdit)
        self.label = QtWidgets.QLabel(self.widgetSearch)
        self.label.setMinimumSize(QtCore.QSize(0, 32))
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.verticalLayout_2.addWidget(self.widgetSearch)
        self.widgetSearch.hide()
        self.hostWidget = QtWidgets.QTreeWidget(self.layoutWidget)
        self.hostWidget.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.hostWidget.setStyleSheet("")
        self.hostWidget.setColumnCount(1)
        self.hostWidget.setObjectName("hostWidget")
        self.hostWidget.setFocus()
        self.verticalLayout_2.addWidget(self.hostWidget)
        self.splitter = QtWidgets.QSplitter(self.splitter_2)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        self.sqlEdit = QtWidgets.QTabWidget(self.splitter)
        self.sqlEdit.setObjectName("sqlEdit")
        self.sqlEdit.setTabsClosable(True)
        self.sqlControll = QtWidgets.QTabWidget(self.splitter)
        self.sqlControll.setTabsClosable(True)
        self.sqlControll.setObjectName("sqlControll")
        self.tabMessage = QtWidgets.QWidget()
        self.tabMessage.setObjectName("tabMessage")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.tabMessage)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.textEditMessage = QtWidgets.QTextEdit(self.tabMessage)
        self.textEditMessage.setReadOnly(True)
        self.textEditMessage.setObjectName("textEditMessage")
        self.verticalLayout_4.addWidget(self.textEditMessage)
        self.sqlControll.addTab(self.tabMessage, "")
        self.tab_2 = sqlTableView.SqlTableView()
        self.tab_2.setObjectName("tab_2")
        self.sqlControll.addTab(self.tab_2, "")
        self.horizontalLayout.addWidget(self.splitter_2)
        DBcat.setCentralWidget(self.centralwidget)

        self.splitter_2.setStretchFactor(0, 1)
        self.splitter_2.setStretchFactor(1, 3)

        # action init
        newConnect = QtWidgets.QAction(QtGui.QIcon(res.resource_path('image/connect.svg')), 'New Connect',
                                       self)
        newSql = QtWidgets.QAction(QtGui.QIcon(res.resource_path('image/newsql.svg')), 'New Sql', self)
        execSql = QtWidgets.QAction(QtGui.QIcon(res.resource_path('image/run.svg')), 'Run Sql', self)
        execSql.setToolTip("运行(F9)")
        execSql.setShortcut("F9")
        
        # 添加SQL历史记录按钮
        historyAction = QtWidgets.QAction(QtGui.QIcon(res.resource_path('image/query.svg')), 'SQL History', self)
        historyAction.setToolTip("SQL历史记录")
        
        # 添加格式化SQL按钮
        formatSqlAction = QtWidgets.QAction(QtGui.QIcon(res.resource_path('image/edit.svg')), 'Format SQL', self)
        formatSqlAction.setToolTip("格式化SQL(Ctrl+L)")
        formatSqlAction.setShortcut("Ctrl+L")
        
        # 添加主题切换按钮
        themeAction = QtWidgets.QAction(QtGui.QIcon(res.resource_path('image/theme.svg')), 'Theme', self)
        themeAction.setToolTip("切换主题")
        themeAction.triggered.connect(self.show_theme_dialog)

        newSql.triggered.connect(self.newSqlEdit)
        newConnect.triggered.connect(self.new_conn_edit)
        execSql.triggered.connect(self.do_exec_sql)
        historyAction.triggered.connect(self.show_sql_history)
        formatSqlAction.triggered.connect(self.format_current_sql)

        # 创建退出操作
        exit_action = QtWidgets.QAction('退出', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        
        # 创建关于操作
        about_action = QtWidgets.QAction('关于', self)
        about_action.triggered.connect(self.show_about_dialog)
        
        # toolBar - 创建并设置为左侧工具栏
        self.toolBar = QtWidgets.QToolBar("工具栏")
        self.addToolBar(QtCore.Qt.LeftToolBarArea, self.toolBar)
        self.toolBar.setOrientation(QtCore.Qt.Vertical)  # 设置为垂直方向
        self.toolBar.setIconSize(QtCore.QSize(32, 32))   # 设置图标大小
        
        # 添加工具栏按钮
        self.toolBar.addAction(newConnect)
        self.toolBar.addAction(newSql)
        self.toolBar.addAction(execSql)
        self.toolBar.addSeparator()
        self.toolBar.addAction(historyAction)
        self.toolBar.addAction(formatSqlAction)
        self.toolBar.addSeparator()
        self.toolBar.addAction(themeAction)

        self.retranslateUi(DBcat)
        self.sqlControll.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(DBcat)

        # 初始化sql代码编辑器
        self.sqlTabEdit = sql_editor.SqlEditor(self.sqlEdit)
        self.sqlControllEdit = sql_control_edit.SqlControlEdit(self.sqlControll)
        self.sqlControllEdit.init_message(self.textEditMessage)
        self.sqlHostTreeWidget = host_tree.HostTree(self.hostWidget, self.sqlControllEdit)
        
        # 初始化窗口边框处理器，用于无边框窗口的调整大小
        self.frame_handler = WindowFrameHandler(self)

    def do_exec_sql(self):
        """执行SQL语句查询"""
        sql_statement, high_risk_operator = self.sqlTabEdit.selections()
        self.sqlHostTreeWidget.exec_sql(sql_statement, high_risk_operator)

    def retranslateUi(self, DBcat):
        _translate = QtCore.QCoreApplication.translate
        DBcat.setWindowTitle(_translate("DBcat", "DBcat"))
        self.label.setText(_translate("DBcat", "No results"))
        self.sqlControll.setTabText(self.sqlControll.indexOf(self.tabMessage), _translate("DBcat", "Message"))
        self.sqlControll.setTabText(self.sqlControll.indexOf(self.tab_2), _translate("DBcat", "Result"))

    def closeEvent(self, event):
        self.sqlTabEdit.saveFiles()
        mysql_operator.MysqlOperator().release_connections()

    def newSqlEdit(self):
        text, ok = QtWidgets.QInputDialog.getText(self, '新建查询', '请输入新查询名称:')
        # 如果用户点击OK
        if ok:
            self.sqlTabEdit.newSqlEdit(text)

    def new_conn_edit(self):
        dialog = host_edit_dialog.HostEditDialog()
        if QtWidgets.QDialog.Accepted == dialog.exec():
            self.sqlHostTreeWidget.add_host(dialog.get_host())
            
    def show_sql_history(self):
        """显示SQL历史记录对话框"""
        from DBCat.component.sql_history_dialog import SqlHistoryDialog
        
        # 创建回调函数，用于将选中的SQL插入到当前编辑器
        def insert_sql(sql):
            current_editor = self.sqlEdit.currentWidget()
            if current_editor:
                current_editor.setPlainText(sql)
        
        # 显示历史记录对话框
        dialog = SqlHistoryDialog(self, insert_sql)
        dialog.exec_()
        
    def format_current_sql(self):
        """格式化当前SQL编辑器中的内容"""
        current_editor = self.sqlEdit.currentWidget()
        if current_editor:
            current_editor.format_sql()
            
    def show_theme_dialog(self):
        """显示主题设置对话框"""
        from DBCat.component.theme_dialog import ThemeDialog
        
        # 创建回调函数，用于应用新主题
        def apply_theme(theme_name):
            # 应用主题到应用程序
            theme_manager.apply_theme(QtWidgets.QApplication.instance())
            
            # 显示提示信息
            QtWidgets.QMessageBox.information(
                self,
                "主题已应用",
                f"主题 '{theme_manager.get_theme(theme_name)['name']}' 已成功应用。\n"
                "部分界面元素可能需要重启应用程序后才能完全应用新主题。",
                QtWidgets.QMessageBox.Ok
            )
        
        # 显示主题设置对话框
        dialog = ThemeDialog(self, apply_theme)
        dialog.exec_()
        
    def show_about_dialog(self):
        """显示关于对话框"""
        about_text = """
        <h2>DBCat 数据库管理工具</h2>
        <p>版本: 1.0.0</p>
        <p>一个简单易用的MySQL数据库管理工具，提供数据库连接、查询、导出等功能。</p>
        <p>特性:</p>
        <ul>
            <li>多数据库连接管理</li>
            <li>SQL编辑器，支持语法高亮和格式化</li>
            <li>数据表查看和导出</li>
            <li>SQL历史记录</li>
            <li>主题切换</li>
        </ul>
        <p>&copy; 2025 DBCat Team</p>
        """
        
        QtWidgets.QMessageBox.about(self, "关于 DBCat", about_text)