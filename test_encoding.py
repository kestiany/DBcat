#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import tempfile
sys.path.append('.')

from DBCat.sql_editor import SqlEditor
from PyQt5.QtWidgets import QApplication, QTabWidget

def test_encoding_fix():
    """测试编码修复功能"""
    print("开始测试编码修复功能...")
    
    # 创建测试应用
    app = QApplication([])
    tab_widget = QTabWidget()
    sql_editor = SqlEditor(tab_widget)
    
    # 测试内容包含中文
    test_content = '-- 测试中文注释\nSELECT * FROM users WHERE name = "张三";'
    
    # 创建UTF-8编码的测试文件
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.sql', delete=False) as f:
        f.write(test_content)
        utf8_file = f.name
    
    try:
        # 测试读取UTF-8文件 (现在使用新的工具函数)
        from DBCat.file_utils import safe_read_file
        result = safe_read_file(utf8_file)
        if result is not None:
            print("✅ UTF-8文件读取成功")
            if "张三" in result:
                print("✅ 中文字符正确读取")
            else:
                print("❌ 中文字符读取失败")
        else:
            print("❌ UTF-8文件读取失败")
            
        # 测试不存在的文件
        non_existent = safe_read_file("non_existent_file.sql")
        if non_existent is None:
            print("✅ 不存在文件的错误处理正确")
        else:
            print("❌ 不存在文件的错误处理失败")
            
    finally:
        # 清理测试文件
        os.unlink(utf8_file)
    
    print("编码修复测试完成")

if __name__ == "__main__":
    test_encoding_fix()