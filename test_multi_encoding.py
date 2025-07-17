#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import tempfile
sys.path.append('.')

from DBCat.sql_editor import SqlEditor
from PyQt5.QtWidgets import QApplication, QTabWidget

def test_multi_encoding():
    """测试多编码支持功能"""
    print("开始测试多编码支持...")
    
    # 创建测试应用
    app = QApplication([])
    tab_widget = QTabWidget()
    sql_editor = SqlEditor(tab_widget)
    
    # 测试内容
    test_content = '-- 中文注释测试\nSELECT * FROM table;'
    
    # 测试UTF-8编码
    with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', suffix='.sql', delete=False) as f:
        f.write(test_content)
        utf8_file = f.name
    
    # 测试GBK编码
    with tempfile.NamedTemporaryFile(mode='w', encoding='gbk', suffix='.sql', delete=False) as f:
        f.write(test_content)
        gbk_file = f.name
    
    try:
        # 测试UTF-8文件读取
        result_utf8 = sql_editor._safe_read_file(utf8_file)
        print(f"UTF-8文件读取: {'成功' if result_utf8 else '失败'}")
        
        # 测试GBK文件读取
        result_gbk = sql_editor._safe_read_file(gbk_file)
        print(f"GBK文件读取: {'成功' if result_gbk else '失败'}")
        
        # 验证内容一致性
        if result_utf8 and result_gbk and result_utf8.strip() == result_gbk.strip():
            print("✅ 多编码读取内容一致")
        else:
            print("❌ 多编码读取内容不一致")
            
    finally:
        # 清理测试文件
        os.unlink(utf8_file)
        os.unlink(gbk_file)
    
    print("多编码测试完成")

if __name__ == "__main__":
    test_multi_encoding()