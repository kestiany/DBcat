#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import tempfile
import logging
from pathlib import Path
sys.path.append('.')

from DBCat.file_utils import (
    SafeFileReader, SafeFileWriter, 
    safe_read_file, safe_write_file, 
    detect_file_encoding, FileEncodingError
)

# 配置日志以便查看详细信息
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def test_file_utils():
    """测试文件工具模块的功能"""
    print("开始测试文件工具模块...")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # 测试内容
        test_content_utf8 = '-- UTF-8测试文件\nSELECT * FROM users WHERE name = "张三";'
        test_content_gbk = '-- GBK测试文件\nSELECT * FROM products WHERE name = "产品";'
        
        # 创建不同编码的测试文件
        utf8_file = temp_path / "test_utf8.sql"
        gbk_file = temp_path / "test_gbk.sql"
        
        # 使用safe_write_file创建UTF-8文件
        print("\n=== 测试安全文件写入 ===")
        success = safe_write_file(utf8_file, test_content_utf8)
        print(f"UTF-8文件写入: {'成功' if success else '失败'}")
        
        # 手动创建GBK文件用于测试
        with open(gbk_file, 'w', encoding='gbk') as f:
            f.write(test_content_gbk)
        print("GBK文件创建: 成功")
        
        # 测试SafeFileReader类
        print("\n=== 测试SafeFileReader类 ===")
        reader = SafeFileReader()
        
        # 测试UTF-8文件读取
        content_utf8 = reader.read_file(utf8_file)
        if content_utf8 and "张三" in content_utf8:
            print("✅ UTF-8文件读取成功")
        else:
            print("❌ UTF-8文件读取失败")
        
        # 测试GBK文件读取
        content_gbk = reader.read_file(gbk_file)
        if content_gbk and "产品" in content_gbk:
            print("✅ GBK文件读取成功")
        else:
            print("❌ GBK文件读取失败")
        
        # 测试编码检测
        print("\n=== 测试编码检测 ===")
        detected_utf8 = reader.detect_encoding(utf8_file)
        detected_gbk = reader.detect_encoding(gbk_file)
        print(f"UTF-8文件检测编码: {detected_utf8}")
        print(f"GBK文件检测编码: {detected_gbk}")
        
        # 测试便捷函数
        print("\n=== 测试便捷函数 ===")
        content_via_func = safe_read_file(utf8_file)
        if content_via_func and content_via_func == content_utf8:
            print("✅ safe_read_file函数工作正常")
        else:
            print("❌ safe_read_file函数工作异常")
        
        # 测试错误处理
        print("\n=== 测试错误处理 ===")
        
        # 测试不存在的文件
        non_existent = temp_path / "non_existent.sql"
        content_none = safe_read_file(non_existent)
        if content_none is None:
            print("✅ 不存在文件处理正确")
        else:
            print("❌ 不存在文件处理错误")
        
        # 测试SafeFileWriter类
        print("\n=== 测试SafeFileWriter类 ===")
        writer = SafeFileWriter()
        
        # 测试创建目录并写入文件
        nested_file = temp_path / "nested" / "dir" / "test.sql"
        success = writer.write_file(nested_file, test_content_utf8, create_dirs=True)
        if success and nested_file.exists():
            print("✅ 嵌套目录文件写入成功")
        else:
            print("❌ 嵌套目录文件写入失败")
        
        # 验证写入的内容
        read_back = safe_read_file(nested_file)
        if read_back == test_content_utf8:
            print("✅ 写入内容验证正确")
        else:
            print("❌ 写入内容验证失败")
        
        # 测试编码检测便捷函数
        print("\n=== 测试编码检测便捷函数 ===")
        encoding = detect_file_encoding(utf8_file)
        if encoding:
            print(f"✅ 编码检测成功: {encoding}")
        else:
            print("❌ 编码检测失败")
    
    print("\n文件工具模块测试完成")

if __name__ == "__main__":
    test_file_utils()