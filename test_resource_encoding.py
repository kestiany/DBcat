#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import json
import tempfile
from pathlib import Path
sys.path.append('.')

from DBCat import resource

def test_resource_encoding():
    """测试resource.py中的编码修复"""
    print("开始测试resource.py编码修复...")
    
    # 创建临时目录模拟用户目录
    with tempfile.TemporaryDirectory() as temp_dir:
        # 临时修改Path.home()的返回值
        original_home = Path.home
        Path.home = lambda: Path(temp_dir)
        
        try:
            # 测试setting_file函数
            setting_file_path = resource.setting_file()
            print(f"设置文件路径: {setting_file_path}")
            
            # 验证文件是否创建
            if os.path.exists(setting_file_path):
                print("✅ 设置文件创建成功")
                
                # 验证文件内容和编码
                with open(setting_file_path, 'r', encoding='utf-8') as f:
                    content = json.load(f)
                    if content == []:
                        print("✅ JSON内容正确")
                    else:
                        print("❌ JSON内容不正确")
                
                # 测试包含中文的JSON写入
                test_data = [{"name": "测试数据库", "host": "localhost"}]
                with open(setting_file_path, 'w', encoding='utf-8') as f:
                    json.dump(test_data, f, ensure_ascii=False, indent=2)
                
                # 验证中文内容读取
                with open(setting_file_path, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    if loaded_data[0]["name"] == "测试数据库":
                        print("✅ 中文JSON数据读写正确")
                    else:
                        print("❌ 中文JSON数据读写失败")
                        
            else:
                print("❌ 设置文件创建失败")
                
            # 测试sql_dir函数
            sql_directory = resource.sql_dir()
            if os.path.exists(sql_directory):
                print("✅ SQL目录创建成功")
            else:
                print("❌ SQL目录创建失败")
                
        finally:
            # 恢复原始的Path.home函数
            Path.home = original_home
    
    print("resource.py编码测试完成")

if __name__ == "__main__":
    test_resource_encoding()