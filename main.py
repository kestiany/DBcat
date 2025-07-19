# -*- coding: utf-8 -*-
import sys
import logging
import os
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore

from DBCat import dbCat
from DBCat import resource
from DBCat.component.theme_manager import theme_manager

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(resource.log_file_path(), encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    # 启用高DPI缩放
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_EnableHighDpiScaling, True)
    QtWidgets.QApplication.setAttribute(QtCore.Qt.AA_UseHighDpiPixmaps, True)
    
    app = QtWidgets.QApplication(sys.argv)
    
    # 应用主题
    theme_manager.apply_theme(app)
    
    # 记录启动信息
    logger.info("DBCat应用程序启动")
    logger.info(f"当前主题: {theme_manager.current_theme_name}")

    # 加载启动图片
    pixmap = QtGui.QPixmap(resource.resource_path('image/splash.png'))
    splash = QtWidgets.QSplashScreen(pixmap)
    splash.show()

    window = dbCat.DBCat()
    window.show()

    # 关闭启动屏
    splash.finish(window)

    sys.exit(app.exec_())