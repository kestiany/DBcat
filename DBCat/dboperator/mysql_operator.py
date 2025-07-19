# -*- coding: utf-8 -*-
"""
MySQL数据库操作模块
提供MySQL数据库连接和查询功能，使用连接池提高性能
"""

import logging
import time
from typing import Tuple, List, Optional, Dict, Any, Union
import mysql.connector
from mysql.connector import Error

from DBCat.dboperator.connection_pool import connection_pool

# 配置日志记录
logger = logging.getLogger(__name__)


class Singleton(type):
    """单例模式元类"""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class MysqlOperator(metaclass=Singleton):
    """MySQL数据库操作类"""
    
    def __init__(self):
        """初始化MySQL操作器"""
        self.__active_queries = {}  # 跟踪活跃查询
        self.__query_id = 0  # 查询ID计数器
    
    def release_connections(self) -> None:
        """释放所有数据库连接"""
        connection_pool.close_all_connections()
        logger.info("已释放所有数据库连接")
    
    def release_connection(self, host_id: str) -> None:
        """
        释放指定主机的所有连接
        
        Args:
            host_id: 主机ID
        """
        connection_pool.close_host_connections(host_id)
        logger.info(f"已释放主机 {host_id} 的所有连接")
    
    def do_exec_statement(self, host_id: str, database: str, sql: str) -> Tuple[Optional[List[tuple]], str]:
        """
        执行SQL语句
        
        Args:
            host_id: 主机ID
            database: 数据库名称
            sql: SQL语句
            
        Returns:
            (查询结果, 消息)，如果是非查询语句则结果为None
        """
        # 获取连接
        connection, error = connection_pool.get_connection(host_id)
        if connection is None:
            return None, f"error: {error}"
        
        # 生成查询ID
        query_id = self.__next_query_id()
        start_time = time.time()
        
        try:
            # 记录查询开始
            self.__active_queries[query_id] = {
                'sql': sql,
                'database': database,
                'host_id': host_id,
                'start_time': start_time
            }
            
            # 创建游标
            cursor = connection.cursor()
            
            try:
                # 选择数据库
                if database:
                    cursor.execute(f"USE `{database}`")
                
                # 执行SQL语句
                cursor.execute(sql)
                
                # 处理结果
                if cursor.with_rows:
                    # 查询语句，获取结果
                    records = cursor.fetchall()
                    description = cursor.description
                    connection.commit()
                    
                    # 记录查询性能
                    duration = time.time() - start_time
                    logger.debug(f"查询执行时间: {duration:.3f}秒, SQL: {sql[:100]}...")
                    
                    return records, [desc[0] for desc in description]
                else:
                    # 非查询语句，获取影响行数
                    affected_rows = cursor.rowcount
                    connection.commit()
                    
                    # 记录查询性能
                    duration = time.time() - start_time
                    logger.debug(f"非查询语句执行时间: {duration:.3f}秒, 影响行数: {affected_rows}, SQL: {sql[:100]}...")
                    
                    return None, f"Query executed successfully. Affected rows: {affected_rows}"
            finally:
                cursor.close()
                # 从活跃查询中移除
                if query_id in self.__active_queries:
                    del self.__active_queries[query_id]
        except Exception as e:
            logger.error(f"执行SQL语句时出错: {str(e)}, SQL: {sql[:100]}...")
            return None, f"error: {str(e)}"
        finally:
            # 释放连接回连接池
            connection.close()
    
    def database(self, host_info: Any) -> Tuple[Optional[List[str]], str]:
        """
        获取数据库列表
        
        Args:
            host_info: 主机信息对象
            
        Returns:
            (数据库列表, 消息)，如果失败则列表为None
        """
        # 注册主机
        connection_pool.register_host(host_info.id, host_info)
        
        # 获取连接
        connection, error = connection_pool.get_connection(host_info.id)
        if connection is None:
            return None, f"error: {error}"
        
        try:
            cursor = connection.cursor()
            try:
                cursor.execute("SHOW DATABASES")
                records = cursor.fetchall()
                return [record[0] for record in records], ''
            finally:
                cursor.close()
        except Exception as e:
            logger.error(f"获取数据库列表时出错: {str(e)}")
            return None, f"error: {str(e)}"
        finally:
            connection.close()
    
    def tables(self, host_id: str, database: str) -> Tuple[Optional[List[str]], str]:
        """
        获取表列表
        
        Args:
            host_id: 主机ID
            database: 数据库名称
            
        Returns:
            (表列表, 消息)，如果失败则列表为None
        """
        # 获取连接
        connection, error = connection_pool.get_connection(host_id)
        if connection is None:
            return None, f"error: {error}"
        
        try:
            cursor = connection.cursor()
            try:
                cursor.execute(f"USE `{database}`")
                cursor.execute('SHOW TABLES')
                records = cursor.fetchall()
                return [record[0] for record in records], ''
            finally:
                cursor.close()
        except Exception as e:
            logger.error(f"获取表列表时出错: {str(e)}")
            return None, f"error: {str(e)}"
        finally:
            connection.close()
    
    def connection(self, host_info: Any) -> Tuple[Optional[Any], str]:
        """
        创建数据库连接
        
        Args:
            host_info: 主机信息对象
            
        Returns:
            (连接对象, 消息)，如果失败则连接为None
        """
        # 注册主机
        connection_pool.register_host(host_info.id, host_info)
        
        # 获取连接
        connection, error = connection_pool.get_connection(host_info.id)
        if connection is None:
            return None, f"error: {error}"
        
        try:
            server_info = connection.get_server_info()
            return connection, f'[Connected to MySQL Server version:{server_info}] {host_info.host}:{host_info.port}'
        except Exception as e:
            logger.error(f"获取服务器信息时出错: {str(e)}")
            connection.close()
            return None, f"error: {str(e)}"
    
    def get_database(self, host_id: str) -> Optional[Any]:
        """
        获取数据库连接
        
        Args:
            host_id: 主机ID
            
        Returns:
            连接对象，如果失败则返回None
        """
        connection, error = connection_pool.get_connection(host_id)
        if connection is None:
            logger.error(f"获取数据库连接失败: {error}")
        return connection
    
    def __next_query_id(self) -> int:
        """
        生成下一个查询ID
        
        Returns:
            查询ID
        """
        self.__query_id += 1
        return self.__query_id
    
    def get_active_queries(self) -> Dict[int, Dict[str, Any]]:
        """
        获取活跃查询列表
        
        Returns:
            活跃查询字典，键为查询ID
        """
        return self.__active_queries.copy()
    
    def cancel_query(self, query_id: int) -> bool:
        """
        取消查询（目前仅从活跃查询列表中移除，实际取消需要MySQL的KILL QUERY支持）
        
        Args:
            query_id: 查询ID
            
        Returns:
            是否成功取消
        """
        if query_id in self.__active_queries:
            del self.__active_queries[query_id]
            return True
        return False
