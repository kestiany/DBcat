#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import tempfile
import logging
from pathlib import Path
sys.path.append('.')

from PyQt5.QtWidgets import QApplication, QTabWidget
from DBCat.sql_editor import SqlEditor
from DBCat.file_utils import safe_read_file, safe_write_file, detect_file_encoding
from DBCat import resource as res

# 配置日志以便查看详细信息
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def test_encoding_fix_comprehensive():
    """全面测试编码修复的有效性"""
    print("\n===== 开始全面测试编码修复的有效性 =====\n")
    
    # 创建测试应用
    app = QApplication([])
    tab_widget = QTabWidget()
    sql_editor = SqlEditor(tab_widget)
    
    # 测试内容 - 包含各种中文字符和SQL语法
    test_content_utf8 = """-- 这是一个包含中文字符的SQL文件
/* 
 * 多行注释测试
 * 包含特殊字符: ！@#￥%……&*（）
 */
SELECT 
    u.用户名,
    u.密码,
    p.产品名称,
    p.价格
FROM 
    用户表 u
JOIN 
    产品表 p ON u.用户ID = p.用户ID
WHERE 
    u.用户名 LIKE '%张三%'
    AND p.价格 > 100.00
ORDER BY 
    p.价格 DESC;

-- 测试中文字符串
INSERT INTO 用户表 (用户名, 密码, 电子邮件) 
VALUES ('李四', 'password123', 'lisi@example.com');

-- 测试Unicode字符
-- 中文、日文、韩文: 你好 こんにちは 안녕하세요
"""
    
    # GBK/GB2312兼容的测试内容 (只包含中文字符)
    test_content_gbk = """-- 这是一个包含中文字符的SQL文件
/* 
 * 多行注释测试
 * 包含特殊字符: ！@#￥%……&*（）
 */
SELECT 
    u.用户名,
    u.密码,
    p.产品名称,
    p.价格
FROM 
    用户表 u
JOIN 
    产品表 p ON u.用户ID = p.用户ID
WHERE 
    u.用户名 LIKE '%张三%'
    AND p.价格 > 100.00
ORDER BY 
    p.价格 DESC;

-- 测试中文字符串
INSERT INTO 用户表 (用户名, 密码, 电子邮件) 
VALUES ('李四', 'password123', 'lisi@example.com');
"""
    
    # 创建临时目录用于测试
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        print("1. 测试不同编码的文件读取")
        # 创建不同编码的测试文件
        encodings = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312']
        test_files = {}
        
        for encoding in encodings:
            file_path = temp_path / f"test_{encoding}.sql"
            try:
                # 使用适合的内容 - UTF-8编码可以处理所有字符，GBK/GB2312只使用中文内容
                content = test_content_utf8 if encoding.startswith('utf') else test_content_gbk
                with open(file_path, 'w', encoding=encoding) as f:
                    f.write(content)
                test_files[encoding] = file_path
                print(f"  ✓ 成功创建 {encoding} 编码的测试文件")
            except Exception as e:
                print(f"  ✗ 创建 {encoding} 编码的测试文件失败: {e}")
        
        print("\n2. 测试文件编码检测")
        for encoding, file_path in test_files.items():
            detected = detect_file_encoding(file_path)
            if detected:
                print(f"  ✓ {file_path.name} 检测到编码: {detected}")
            else:
                print(f"  ✗ {file_path.name} 编码检测失败")
        
        print("\n3. 测试安全文件读取")
        for encoding, file_path in test_files.items():
            content = safe_read_file(file_path, parent=tab_widget, show_dialog=False)
            if content and "用户表" in content and "李四" in content:
                print(f"  ✓ 成功读取 {encoding} 编码的文件")
            else:
                print(f"  ✗ 读取 {encoding} 编码的文件失败")
        
        print("\n4. 测试SQL编辑器加载文件")
        # 创建一个专用的测试目录，确保只有我们的测试文件
        sql_test_dir = temp_path / "sql_test_dir"
        sql_test_dir.mkdir(exist_ok=True)
        
        # 复制测试文件到专用目录
        test_sql_files = {}
        for encoding, file_path in test_files.items():
            new_path = sql_test_dir / file_path.name
            content = safe_read_file(file_path)
            if content:
                safe_write_file(new_path, content)
                test_sql_files[encoding] = new_path
        
        # 临时修改SQL目录
        original_sql_dir = res.sql_dir
        res.sql_dir = lambda: sql_test_dir
        
        try:
            # 清空当前标签页
            while tab_widget.count() > 0:
                tab_widget.removeTab(0)
                
            # 重新初始化SQL编辑器
            sql_editor = SqlEditor(tab_widget)
            
            # 检查是否所有文件都被加载
            tab_count = tab_widget.count()
            if tab_count == len(test_sql_files):
                print(f"  ✓ SQL编辑器成功加载了所有 {tab_count} 个测试文件")
            else:
                print(f"  ✗ SQL编辑器只加载了 {tab_count}/{len(test_sql_files)} 个测试文件")
            
            # 检查每个标签页的内容
            for i in range(tab_count):
                tab_text = tab_widget.tabText(i)
                widget = tab_widget.widget(i)
                content = widget.wholeText() if hasattr(widget, 'wholeText') else ""
                
                if "用户表" in content and "李四" in content:
                    print(f"  ✓ 标签页 '{tab_text}' 内容正确")
                else:
                    print(f"  ✗ 标签页 '{tab_text}' 内容不正确")
        finally:
            # 恢复原始SQL目录函数
            res.sql_dir = original_sql_dir
        
        print("\n5. 测试文件保存编码一致性")
        # 创建新的测试文件
        test_file = temp_path / "save_test.sql"
        success = safe_write_file(test_file, test_content_utf8)
        
        if success:
            print("  ✓ 文件保存成功")
            
            # 读取保存的文件并验证内容
            saved_content = safe_read_file(test_file)
            if saved_content == test_content_utf8:
                print("  ✓ 保存和读取的内容一致")
            else:
                print("  ✗ 保存和读取的内容不一致")
                
            # 检测保存文件的编码
            encoding = detect_file_encoding(test_file)
            if encoding == 'utf-8':
                print(f"  ✓ 文件以 {encoding} 编码保存")
            else:
                print(f"  ✗ 文件编码不是UTF-8，而是 {encoding}")
        else:
            print("  ✗ 文件保存失败")
        
        print("\n6. 测试Windows环境特定问题")
        if sys.platform == 'win32':
            print("  在Windows环境下运行测试...")
            
            # 测试包含非ASCII字符的文件名
            chinese_filename = temp_path / "中文文件名.sql"
            success = safe_write_file(chinese_filename, test_content_utf8)
            
            if success and chinese_filename.exists():
                print("  ✓ 成功创建包含中文的文件名")
                
                # 尝试读取该文件
                content = safe_read_file(chinese_filename)
                if content and "用户表" in content:
                    print("  ✓ 成功读取包含中文的文件名")
                else:
                    print("  ✗ 读取包含中文的文件名失败")
            else:
                print("  ✗ 创建包含中文的文件名失败")
        else:
            print("  不在Windows环境下，跳过Windows特定测试")
    
    print("\n===== 编码修复全面测试完成 =====")

if __name__ == "__main__":
    test_encoding_fix_comprehensive()