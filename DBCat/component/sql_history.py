#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SQL历史记录模块
提供SQL查询历史记录的管理功能
"""

import os
import json
import time
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
from datetime import datetime

from DBCat import resource as res

# 配置日志记录
logger = logging.getLogger(__name__)


class SqlHistoryManager:
    """SQL历史记录管理器，提供历史记录的保存、加载和管理功能"""
    
    def __init__(self, max_history: int = 100):
        """
        初始化SQL历史记录管理器
        
        Args:
            max_history: 最大历史记录数量
        """
        self.max_history = max_history
        self.history_file = self._get_history_file_path()
        self.history_records = self._load_history()
    
    def _get_history_file_path(self) -> Path:
        """
        获取历史记录文件路径
        
        Returns:
            历史记录文件路径
        """
        # 使用.dbcat目录存储历史记录
        history_dir = Path.home() / ".dbcat"
        if not os.path.exists(history_dir):
            os.makedirs(history_dir)
        
        return history_dir / "sql_history.json"
    
    def _load_history(self) -> List[Dict[str, Any]]:
        """
        加载历史记录
        
        Returns:
            历史记录列表
        """
        if not os.path.exists(self.history_file):
            return []
        
        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
                
                # 验证历史记录格式
                if not isinstance(history, list):
                    logger.warning("历史记录文件格式错误，重置历史记录")
                    return []
                
                return history
        except Exception as e:
            logger.error(f"加载历史记录时出错: {str(e)}")
            return []
    
    def _save_history(self) -> bool:
        """
        保存历史记录
        
        Returns:
            是否成功保存
        """
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history_records, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            logger.error(f"保存历史记录时出错: {str(e)}")
            return False
    
    def add_record(self, sql: str, database: str = "", host_name: str = "", 
                  success: bool = True, affected_rows: int = 0) -> bool:
        """
        添加历史记录
        
        Args:
            sql: SQL语句
            database: 数据库名称
            host_name: 主机名称
            success: 是否执行成功
            affected_rows: 影响的行数
            
        Returns:
            是否成功添加
        """
        # 如果SQL为空，不添加记录
        if not sql or not sql.strip():
            return False
        
        # 创建历史记录
        record = {
            'sql': sql,
            'database': database,
            'host': host_name,
            'timestamp': time.time(),
            'datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'success': success,
            'affected_rows': affected_rows
        }
        
        # 添加到历史记录列表
        self.history_records.insert(0, record)
        
        # 限制历史记录数量
        if len(self.history_records) > self.max_history:
            self.history_records = self.history_records[:self.max_history]
        
        # 保存历史记录
        return self._save_history()
    
    def get_records(self, limit: int = 0, filter_text: str = "", 
                   database: str = "", host: str = "") -> List[Dict[str, Any]]:
        """
        获取历史记录
        
        Args:
            limit: 限制返回的记录数量，0表示不限制
            filter_text: 过滤文本，空字符串表示不过滤
            database: 数据库名称过滤，空字符串表示不过滤
            host: 主机名称过滤，空字符串表示不过滤
            
        Returns:
            历史记录列表
        """
        # 过滤记录
        filtered_records = self.history_records
        
        if filter_text:
            filtered_records = [
                record for record in filtered_records
                if filter_text.lower() in record['sql'].lower()
            ]
        
        if database:
            filtered_records = [
                record for record in filtered_records
                if record['database'] == database
            ]
        
        if host:
            filtered_records = [
                record for record in filtered_records
                if record['host'] == host
            ]
        
        # 限制记录数量
        if limit > 0:
            filtered_records = filtered_records[:limit]
        
        return filtered_records
    
    def clear_history(self) -> bool:
        """
        清空历史记录
        
        Returns:
            是否成功清空
        """
        self.history_records = []
        return self._save_history()
    
    def delete_record(self, index: int) -> bool:
        """
        删除指定索引的历史记录
        
        Args:
            index: 记录索引
            
        Returns:
            是否成功删除
        """
        if 0 <= index < len(self.history_records):
            del self.history_records[index]
            return self._save_history()
        return False


# 创建全局SQL历史记录管理器实例
sql_history_manager = SqlHistoryManager()