#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import subprocess
import tempfile
import time
from pathlib import Path

def test_pyinstaller_packaging():
    """测试PyInstaller打包后的功能"""
    print("\n===== 开始测试PyInstaller打包后的功能 =====\n")
    
    # 1. 使用PyInstaller打包应用
    print("1. 使用PyInstaller打包应用")
    try:
        # 创建临时目录用于输出
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # 执行PyInstaller打包
            print("执行PyInstaller打包...")
            result = subprocess.run(
                ["pyinstaller", "setup.spec", "--distpath", str(temp_path)],
                check=True, capture_output=True, text=True
            )
            print("✓ 应用打包成功")
            
            # 检查打包后的可执行文件是否存在
            exe_path = temp_path / "DBCat.exe"
            if not exe_path.exists():
                print(f"✗ 打包后的可执行文件不存在: {exe_path}")
                return
            print(f"✓ 打包后的可执行文件已创建: {exe_path}")
            
            # 2. 运行打包后的程序
            print("\n2. 运行打包后的程序")
            print("注意: 这将启动应用程序，请等待几秒钟...")
            
            # 启动应用程序
            process = subprocess.Popen([str(exe_path)])
            print(f"✓ 应用程序已启动，进程ID: {process.pid}")
            
            # 等待几秒钟
            time.sleep(5)
            
            # 检查程序是否仍在运行
            if process.poll() is None:
                print("✓ 程序仍在运行，没有闪退")
                # 终止程序
                process.terminate()
                try:
                    process.wait(timeout=5)
                    print("✓ 程序已正常终止")
                except subprocess.TimeoutExpired:
                    # 如果无法正常终止，强制终止
                    process.kill()
                    print("! 程序已强制终止")
            else:
                print(f"✗ 程序已退出，退出码: {process.returncode}")
                print("程序可能闪退，请检查日志文件")
    
    except subprocess.SubprocessError as e:
        print(f"✗ 打包或运行失败: {e}")
        if hasattr(e, 'stderr'):
            print(f"错误输出: {e.stderr}")
    except Exception as e:
        print(f"✗ 测试过程中发生错误: {e}")
    
    print("\n===== PyInstaller打包测试完成 =====")

if __name__ == "__main__":
    test_pyinstaller_packaging()