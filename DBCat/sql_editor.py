# -*- coding: utf-8 -*-
import logging
from pathlib import Path
from PyQt5 import QtCore

from DBCat.texteditor import text_editor
from DBCat import resource as res
from DBCat.file_utils import safe_read_file, safe_write_file
from DBCat.error_handler import FileErrorHandler

# 配置日志记录
logger = logging.getLogger(__name__)


class SqlEditor:
    def __init__(self, sqlEditor):
        self.sqlEditor = sqlEditor
        self.sqlEditor.setTabsClosable(True)
        self.sqlEditor.tabCloseRequested.connect(self.tabClose)

        self.initSqlEdit()
        # 每隔5分钟，自动保存一次文件
        self.timer = QtCore.QTimer()
        self.timer.start(5 * 60 * 1000)
        self.timer.timeout.connect(self.saveFiles)

    def selections(self):
        return self.sqlEditor.currentWidget().selections()

    def loadFiles(self):
        directory_path = res.sql_dir()
        files_list = [file for file in directory_path.glob('**/*') if file.is_file()]
        return [file for file in files_list if file.suffix == '.sql']

    def initSqlEdit(self):
        files = self.loadFiles()
        if len(files) == 0:
            sqlCode = text_editor.TextEditor()
            self.sqlEditor.addTab(sqlCode, "新建查询")
        else:
            for file in files:
                sqlCode = text_editor.TextEditor()
                content = safe_read_file(file, parent=self.sqlEditor.parent(), show_dialog=True)
                if content is not None:
                    sqlCode.setPlainText(content)
                    self.sqlEditor.addTab(sqlCode, Path(file).stem)
                else:
                    logger.warning(f"无法读取文件 {file}，跳过该文件")

    def saveFiles(self):
        directory_path = res.sql_dir()
        # 获取所有tab页
        for i in range(self.sqlEditor.count()):
            file_path = directory_path / (self.sqlEditor.tabText(i) + '.sql')
            content = self.sqlEditor.widget(i).wholeText()
            try:
                success = safe_write_file(file_path, content, encoding='utf-8')
                if not success:
                    logger.error(f"保存文件失败: {file_path}")
                    FileErrorHandler.handle_file_error(
                        Exception("保存文件失败"), 
                        str(file_path), 
                        parent=self.sqlEditor.parent(), 
                        show_dialog=True
                    )
            except Exception as e:
                logger.error(f"保存文件时发生错误: {file_path} - {str(e)}")
                FileErrorHandler.handle_file_error(
                    e, 
                    str(file_path), 
                    parent=self.sqlEditor.parent(), 
                    show_dialog=True
                )

    def newSqlEdit(self, name):
        tab_index = self.findText(name)
        if tab_index != -1:
            self.sqlEditor.setCurrentIndex(tab_index)
        else:
            sqlCode = text_editor.TextEditor()
            self.sqlEditor.addTab(sqlCode, name)
            self.sqlEditor.setCurrentWidget(sqlCode)

    def tabClose(self, index: int):
        name = self.sqlEditor.tabText(index)
        self.sqlEditor.removeTab(index)
        file = res.sql_dir() / (name + '.sql')
        # 使用unlink()方法删除文件， unlink(missing_ok=True) 可以避免 FileNotFoundError 异常
        try:
            file.unlink(missing_ok=True)
        except Exception as e:
            logger.error(f"删除文件时发生错误: {file} - {str(e)}")
            FileErrorHandler.handle_file_error(
                e, 
                str(file), 
                parent=self.sqlEditor.parent(), 
                show_dialog=True
            )

    def findText(self, tab_name):
        """根据tab名称查找并返回其索引，如果未找到则返回-1"""
        for index in range(self.sqlEditor.count()):
            if self.sqlEditor.tabText(index) == tab_name:
                return index
        return -1


