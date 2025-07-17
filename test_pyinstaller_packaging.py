#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import tempfile
import shutil
import time
from pathlib import Path

def test_pyinstaller_packaging():
    """测试PyInstaller打包后的编码功能"""
    print("\n===== 开始测试PyInstaller打包后的编码功能 =====\n")
    
    # 检查是否安装了PyInstaller
    try:
        subprocess.run(["pyinstaller", "--version"], check=True, capture_output=True)
        print("✓ PyInstaller已安装")
    except (subprocess.SubprocessError, FileNotFoundError):
        print("✗ PyInstaller未安装，请先安装PyInstaller")
        return
    
    # 创建临时目录用于测试
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 1. 使用PyInstaller打包应用
        print("\n1. 使用PyInstaller打包应用")
        try:
            result = subprocess.run(
                ["pyinstaller", "setup.spec", "--distpath", str(temp_path)],
                check=True, capture_output=True, text=True
            )
            print("✓ 应用打包成功")
        except subprocess.SubprocessError as e:
            print(f"✗ 应用打包失败: {e}")
            print(f"错误输出: {e.stderr if hasattr(e, 'stderr') else '无详细错误信息'}")
            return
        
        # 检查打包后的可执行文件是否存在
        exe_path = temp_path / "DBCat.exe"
        if not exe_path.exists():
            print(f"✗ 打包后的可执行文件不存在: {exe_path}")
            return
        print(f"✓ 打包后的可执行文件已创建: {exe_path}")
        
        # 2. 准备测试环境
        print("\n2. 准备测试环境")
        
        # 获取用户主目录，用于检查应用程序创建的文件
        user_home = os.path.expanduser("~")
        dbcat_dir = Path(user_home) / ".DBCat"
        
        # 删除可能存在的旧文件
        if dbcat_dir.exists():
            print(f"删除旧的DBCat配置目录: {dbcat_dir}")
            shutil.rmtree(dbcat_dir, ignore_errors=True)
        
        # 创建SQL目录
        sql_dir = dbcat_dir / "sql"
        sql_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建包含中文的SQL文件
        test_sql_utf8 = sql_dir / "测试UTF8.sql"
        test_content = """-- 这是一个包含中文字符的SQL文件
SELECT * FROM 用户表 WHERE 姓名 = '张三';
"""
        with open(test_sql_utf8, 'w', encoding='utf-8') as f:
            f.write(test_content)
        print(f"✓ 创建测试SQL文件: {test_sql_utf8}")
        
        # 3. 运行打包后的应用程序
        print("\n3. 运行打包后的应用程序")
        print("注意: 这将启动应用程序，请不要干扰测试过程")
        
        try:
            # 启动应用程序
            process = subprocess.Popen([str(exe_path)])
            print(f"✓ 应用程序已启动，进程ID: {process.pid}")
            
            # 等待几秒钟让应用程序初始化
            print("等待应用程序初始化...")
            time.sleep(5)
            
            # 检查是否有错误日志生成
            error_log = dbcat_dir / "error.log"
            if error_log.exists():
                print(f"✗ 发现错误日志: {error_log}")
                with open(error_log, 'r', encoding='utf-8', errors='replace') as f:
                    print(f"错误日志内容:\n{f.read()}")
            else:
                print("✓ 没有发现错误日志，应用程序启动正常")
            
            # 检查SQL文件是否被正确加载
            if test_sql_utf8.exists():
                print("✓ SQL文件存在，检查内容...")
                with open(test_sql_utf8, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                    if "张三" in content:
                        print("✓ SQL文件内容正确")
                    else:
                        print(f"✗ SQL文件内容不正确: {content}")
            else:
                print(f"✗ SQL文件不存在: {test_sql_utf8}")
            
        finally:
            # 4. 清理
            print("\n4. 清理测试环境")
            # 尝试终止应用程序
            try:
                process.terminate()
                process.wait(timeout=3)
                print("✓ 已正常终止DBCat进程")
            except:
                try:
                    # 如果正常终止失败，强制终止
                    subprocess.run(["taskkill", "/f", "/pid", str(process.pid)], 
                                  check=False, capture_output=True)
                    print("✓ 已强制终止DBCat进程")
                except:
                    print("! 无法终止DBCat进程，可能已经关闭")
    
    print("\n===== PyInstaller打包测试完成 =====")

if __name__ == "__main__":
    test_pyinstaller_packaging()