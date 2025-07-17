# -*- coding: utf-8 -*-
import sys
from PyQt5 import QtWidgets
from PyQt5 import QtGui

from DBCat import dbCat
from DBCat import resource


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    # 加载启动图片
    pixmap = QtGui.QPixmap(resource.resource_path('image/splash.png'))
    splash = QtWidgets.QSplashScreen(pixmap)
    splash.show()

    window = dbCat.DBCat()
    window.show()

    # 关闭启动屏
    splash.finish(window)

    sys.exit(app.exec_())