#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SQL格式化模块
提供SQL语句的格式化功能，使SQL代码更易读
"""

import re
import logging
from typing import List, Dict, Any, Optional

# 配置日志记录
logger = logging.getLogger(__name__)


class SqlFormatter:
    """SQL格式化类，提供SQL语句的美化功能"""
    
    # SQL关键字列表
    KEYWORDS = [
        "SELECT", "FROM", "WHERE", "JOIN", "LEFT", "RIGHT", "INNER", "OUTER", "FULL", "CROSS",
        "GROUP BY", "ORDER BY", "HAVING", "LIMIT", "OFFSET", "UNION", "ALL", "INSERT", "INTO",
        "VALUES", "UPDATE", "SET", "DELETE", "CREATE", "ALTER", "DROP", "TABLE", "INDEX",
        "VIEW", "PROCEDURE", "FUNCTION", "TRIGGER", "DATABASE", "SCHEMA", "GRANT", "REVOKE",
        "BEGIN", "COMMIT", "ROLLBACK", "TRANSACTION", "WITH", "AS", "ON", "AND", "OR", "NOT",
        "IN", "EXISTS", "CASE", "WHEN", "THEN", "ELSE", "END", "DISTINCT", "BETWEEN", "IS",
        "NULL", "LIKE", "TOP", "PERCENT", "CONSTRAINT", "PRIMARY", "FOREIGN", "KEY", "REFERENCES"
    ]
    
    # 需要缩进的关键字
    INDENT_AFTER_KEYWORDS = [
        "SELECT", "FROM", "WHERE", "JOIN", "LEFT JOIN", "RIGHT JOIN", "INNER JOIN", 
        "OUTER JOIN", "FULL JOIN", "CROSS JOIN", "GROUP BY", "ORDER BY", "HAVING", 
        "INSERT INTO", "VALUES", "UPDATE", "SET", "CREATE TABLE", "ALTER TABLE"
    ]
    
    # 需要换行的关键字
    NEWLINE_KEYWORDS = [
        "FROM", "WHERE", "JOIN", "LEFT JOIN", "RIGHT JOIN", "INNER JOIN", "OUTER JOIN", 
        "FULL JOIN", "CROSS JOIN", "GROUP BY", "ORDER BY", "HAVING", "LIMIT", "UNION", 
        "VALUES", "SET"
    ]
    
    def __init__(self, indent_size: int = 4):
        """
        初始化SQL格式化器
        
        Args:
            indent_size: 缩进大小，默认为4个空格
        """
        self.indent_size = indent_size
    
    def format(self, sql: str) -> str:
        """
        格式化SQL语句
        
        Args:
            sql: 原始SQL语句
            
        Returns:
            格式化后的SQL语句
        """
        if not sql or not sql.strip():
            return ""
            
        # 去除多余的空白字符
        sql = self._normalize_whitespace(sql)
        
        # 分割SQL为标记列表
        tokens = self._tokenize(sql)
        
        # 格式化标记
        formatted = self._format_tokens(tokens)
        
        return formatted
    
    def _normalize_whitespace(self, sql: str) -> str:
        """
        规范化空白字符
        
        Args:
            sql: 原始SQL语句
            
        Returns:
            规范化后的SQL语句
        """
        # 去除开头和结尾的空白
        sql = sql.strip()
        
        # 将多个空白字符替换为单个空格
        sql = re.sub(r'\s+', ' ', sql)
        
        # 在逗号后添加空格
        sql = re.sub(r',(?!\s)', ', ', sql)
        
        # 在括号周围添加空格
        sql = re.sub(r'\((?!\s)', '( ', sql)
        sql = re.sub(r'(?<!\s)\)', ' )', sql)
        
        return sql
    
    def _tokenize(self, sql: str) -> List[str]:
        """
        将SQL语句分割为标记列表
        
        Args:
            sql: 规范化后的SQL语句
            
        Returns:
            标记列表
        """
        # 处理字符串字面量
        string_literals = {}
        string_count = 0
        
        # 提取单引号字符串
        def replace_string(match):
            nonlocal string_count
            placeholder = f"__STRING_{string_count}__"
            string_literals[placeholder] = match.group(0)
            string_count += 1
            return placeholder
            
        sql = re.sub(r"'[^']*'", replace_string, sql)
        
        # 处理注释
        comments = {}
        comment_count = 0
        
        # 提取单行注释
        def replace_comment(match):
            nonlocal comment_count
            placeholder = f"__COMMENT_{comment_count}__"
            comments[placeholder] = match.group(0)
            comment_count += 1
            return placeholder
            
        sql = re.sub(r'--.*?$', replace_comment, sql, flags=re.MULTILINE)
        
        # 分割SQL
        tokens = []
        current_token = ""
        
        for char in sql:
            if char in ",()+*/-=<>":
                if current_token:
                    tokens.append(current_token)
                    current_token = ""
                tokens.append(char)
            elif char.isspace():
                if current_token:
                    tokens.append(current_token)
                    current_token = ""
            else:
                current_token += char
                
        if current_token:
            tokens.append(current_token)
        
        # 恢复字符串字面量和注释
        for i, token in enumerate(tokens):
            if token in string_literals:
                tokens[i] = string_literals[token]
            elif token in comments:
                tokens[i] = comments[token]
        
        return tokens
    
    def _format_tokens(self, tokens: List[str]) -> str:
        """
        格式化标记列表
        
        Args:
            tokens: 标记列表
            
        Returns:
            格式化后的SQL语句
        """
        result = []
        indent_level = 0
        new_line = True
        
        i = 0
        while i < len(tokens):
            token = tokens[i].upper()
            original_token = tokens[i]
            
            # 检查是否是关键字
            is_keyword = token in self.KEYWORDS
            
            # 检查是否需要换行
            if token in self.NEWLINE_KEYWORDS:
                if not new_line:
                    result.append("\n")
                result.append(" " * (indent_level * self.indent_size))
                result.append(original_token)
                result.append("\n")
                new_line = True
            
            # 检查是否需要缩进
            elif token in self.INDENT_AFTER_KEYWORDS:
                if not new_line:
                    result.append("\n")
                result.append(" " * (indent_level * self.indent_size))
                result.append(original_token)
                indent_level += 1
                result.append("\n")
                new_line = True
            
            # 处理括号
            elif token == "(":
                result.append(original_token)
                indent_level += 1
                if i + 1 < len(tokens) and tokens[i + 1].upper() not in self.KEYWORDS:
                    result.append("\n")
                    result.append(" " * (indent_level * self.indent_size))
                    new_line = True
                else:
                    new_line = False
            
            elif token == ")":
                indent_level = max(0, indent_level - 1)
                if new_line:
                    result.append(" " * (indent_level * self.indent_size))
                result.append(original_token)
                new_line = False
            
            # 处理逗号
            elif token == ",":
                result.append(original_token)
                result.append("\n")
                result.append(" " * (indent_level * self.indent_size))
                new_line = True
            
            # 处理其他标记
            else:
                if new_line:
                    result.append(" " * (indent_level * self.indent_size))
                result.append(original_token)
                new_line = False
            
            # 添加空格
            if i + 1 < len(tokens) and not new_line and tokens[i + 1] not in ",()+*/-=<>":
                result.append(" ")
            
            i += 1
        
        return "".join(result)


# 创建一个全局格式化器实例
sql_formatter = SqlFormatter()


def format_sql(sql: str) -> str:
    """
    格式化SQL语句的便捷函数
    
    Args:
        sql: 原始SQL语句
        
    Returns:
        格式化后的SQL语句
    """
    return sql_formatter.format(sql)