#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import traceback
import logging
from pathlib import Path
import subprocess
import tempfile
import time
import shutil

# 配置日志
log_dir = Path.home() / ".dbcat"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "debug_pyinstaller.log"

logging.basicConfig(
    filename=str(log_file),
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def debug_pyinstaller_packaging():
    """调试PyInstaller打包后的程序闪退问题"""
    logging.info("===== 开始调试PyInstaller打包后的程序闪退问题 =====")
    
    try:
        # 1. 备份原始main.py
        logging.info("1. 备份原始main.py")
        original_main_path = Path("main.py")
        backup_main_path = Path("main.py.bak")
        
        if not original_main_path.exists():
            logging.error("找不到main.py文件")
            return
        
        shutil.copy2(original_main_path, backup_main_path)
        logging.info(f"原始main.py已备份到: {backup_main_path}")
        
        # 2. 创建调试版本的main.py
        logging.info("2. 创建调试版本的main.py")
        
        # 读取原始main.py
        with open(original_main_path, "r", encoding="utf-8") as f:
            main_content = f.read()
        
        # 创建调试版本的main.py
        debug_main = """# -*- coding: utf-8 -*-
import sys
import os
import traceback
import logging
from pathlib import Path
from PyQt5 import QtWidgets
from PyQt5 import QtGui

# 配置日志
log_dir = Path.home() / ".dbcat"
log_dir.mkdir(exist_ok=True)
log_file = log_dir / "dbcat_error.log"

logging.basicConfig(
    filename=str(log_file),
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

try:
    logging.info("程序启动")
    
    from DBCat import dbCat
    from DBCat import resource
    
    logging.info("模块导入成功")

    if __name__ == "__main__":
        try:
            app = QtWidgets.QApplication(sys.argv)
            logging.info("QApplication创建成功")

            # 加载启动图片
            try:
                splash_path = resource.resource_path('image/splash.png')
                logging.info(f"启动图片路径: {splash_path}")
                pixmap = QtGui.QPixmap(splash_path)
                splash = QtWidgets.QSplashScreen(pixmap)
                splash.show()
                logging.info("启动画面显示成功")
            except Exception as e:
                logging.error(f"启动画面显示失败: {e}")
                logging.error(traceback.format_exc())
                # 继续执行，不因启动画面失败而退出

            try:
                window = dbCat.DBCat()
                logging.info("主窗口创建成功")
                window.show()
                logging.info("主窗口显示成功")

                # 如果启动画面创建成功，关闭它
                if 'splash' in locals():
                    splash.finish(window)
                    logging.info("启动画面关闭")
            except Exception as e:
                logging.error(f"主窗口创建或显示失败: {e}")
                logging.error(traceback.format_exc())
                raise

            sys.exit(app.exec_())
        except Exception as e:
            logging.error(f"主程序执行失败: {e}")
            logging.error(traceback.format_exc())
            
            # 显示错误对话框
            error_app = QtWidgets.QApplication(sys.argv) if 'app' not in locals() else app
            error_msg = QtWidgets.QMessageBox()
            error_msg.setIcon(QtWidgets.QMessageBox.Critical)
            error_msg.setWindowTitle("DBCat启动错误")
            error_msg.setText("程序启动时发生错误")
            error_msg.setDetailedText(f"错误详情: {str(e)}\\n\\n{traceback.format_exc()}")
            error_msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            error_msg.exec_()
            sys.exit(1)
except Exception as e:
    # 写入错误到文件
    with open(str(Path.home() / ".dbcat" / "critical_error.log"), "w", encoding="utf-8") as f:
        f.write(f"严重错误: {str(e)}\\n\\n{traceback.format_exc()}")
    
    # 尝试显示错误对话框
    try:
        from PyQt5 import QtWidgets
        app = QtWidgets.QApplication(sys.argv)
        error_msg = QtWidgets.QMessageBox()
        error_msg.setIcon(QtWidgets.QMessageBox.Critical)
        error_msg.setWindowTitle("DBCat严重错误")
        error_msg.setText("程序初始化时发生严重错误")
        error_msg.setDetailedText(f"错误详情: {str(e)}\\n\\n{traceback.format_exc()}")
        error_msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
        error_msg.exec_()
    except:
        pass
    
    sys.exit(1)
"""
        
        # 保存调试版本的main.py
        with open(original_main_path, "w", encoding="utf-8") as f:
            f.write(debug_main)
        
        logging.info("调试版本的main.py已创建")
        
        # 3. 使用PyInstaller打包应用
        logging.info("3. 使用PyInstaller打包应用")
        
        # 创建临时目录用于输出
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # 执行PyInstaller打包
            logging.info("执行PyInstaller打包")
            try:
                result = subprocess.run(
                    ["pyinstaller", "setup.spec", "--distpath", str(temp_path)],
                    check=True, capture_output=True, text=True
                )
                logging.info("PyInstaller打包成功")
            except subprocess.SubprocessError as e:
                logging.error(f"PyInstaller打包失败: {e}")
                if hasattr(e, 'stderr'):
                    logging.error(f"错误输出: {e.stderr}")
                # 恢复原始main.py
                shutil.copy2(backup_main_path, original_main_path)
                logging.info("已恢复原始main.py")
                return
            
            # 检查打包后的可执行文件是否存在
            exe_path = temp_path / "DBCat.exe"
            if not exe_path.exists():
                logging.error(f"打包后的可执行文件不存在: {exe_path}")
                # 恢复原始main.py
                shutil.copy2(backup_main_path, original_main_path)
                logging.info("已恢复原始main.py")
                return
            logging.info(f"打包后的可执行文件已创建: {exe_path}")
            
            # 4. 运行打包后的程序
            logging.info("4. 运行打包后的程序")
            
            try:
                # 启动应用程序
                process = subprocess.Popen([str(exe_path)])
                logging.info(f"应用程序已启动，进程ID: {process.pid}")
                
                # 等待程序运行一段时间
                logging.info("等待程序运行...")
                time.sleep(10)
                
                # 检查程序是否仍在运行
                if process.poll() is None:
                    logging.info("程序仍在运行，看起来没有立即闪退")
                    # 终止程序
                    process.terminate()
                    process.wait(timeout=5)
                    logging.info("程序已终止")
                else:
                    logging.warning(f"程序已退出，退出码: {process.returncode}")
                
                # 检查是否生成了错误日志
                error_log = Path.home() / ".dbcat" / "dbcat_error.log"
                critical_log = Path.home() / ".dbcat" / "critical_error.log"
                
                if error_log.exists():
                    logging.info(f"发现错误日志: {error_log}")
                    with open(error_log, 'r', encoding='utf-8', errors='replace') as f:
                        log_content = f.read()
                        logging.info(f"错误日志内容:\n{log_content}")
                else:
                    logging.info("没有发现普通错误日志")
                
                if critical_log.exists():
                    logging.info(f"发现严重错误日志: {critical_log}")
                    with open(critical_log, 'r', encoding='utf-8', errors='replace') as f:
                        log_content = f.read()
                        logging.info(f"严重错误日志内容:\n{log_content}")
                else:
                    logging.info("没有发现严重错误日志")
                
            except Exception as e:
                logging.error(f"运行程序时发生错误: {e}")
                logging.error(traceback.format_exc())
            
            # 5. 恢复原始main.py
            shutil.copy2(backup_main_path, original_main_path)
            logging.info("已恢复原始main.py")
    
    except Exception as e:
        logging.error(f"调试过程中发生错误: {e}")
        logging.error(traceback.format_exc())
        
        # 确保恢复原始main.py
        if 'backup_main_path' in locals() and backup_main_path.exists():
            shutil.copy2(backup_main_path, original_main_path)
            logging.info("已恢复原始main.py")
    
    logging.info("===== PyInstaller打包调试完成 =====")
    print(f"调试日志已保存到: {log_file}")

if __name__ == "__main__":
    debug_pyinstaller_packaging()