#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库连接池模块
提供高效的数据库连接管理，减少连接创建和关闭的开销
"""

import time
import logging
import threading
import queue
from typing import Dict, Tuple, Optional, List, Any
import mysql.connector
from mysql.connector import Error

# 配置日志记录
logger = logging.getLogger(__name__)

class PooledConnection:
    """连接池中的连接包装类"""
    
    def __init__(self, connection, pool, host_id):
        """
        初始化连接包装器
        
        Args:
            connection: MySQL连接对象
            pool: 所属连接池
            host_id: 连接的主机ID
        """
        self.connection = connection
        self.pool = pool
        self.host_id = host_id
        self.last_used = time.time()
        self.in_use = False
        
    def close(self):
        """
        将连接归还到连接池，而不是真正关闭
        """
        if self.connection:
            self.pool.release_connection(self)
            
    def is_connected(self):
        """
        检查连接是否有效
        
        Returns:
            连接有效返回True，否则返回False
        """
        if not self.connection:
            return False
        
        try:
            return self.connection.is_connected()
        except:
            return False
            
    def __getattr__(self, name):
        """
        代理到实际的连接对象
        
        Args:
            name: 属性名
            
        Returns:
            连接对象的属性
        """
        return getattr(self.connection, name)


class ConnectionPool:
    """MySQL数据库连接池"""
    
    def __init__(self, max_connections=10, connection_timeout=60, max_idle_time=300):
        """
        初始化连接池
        
        Args:
            max_connections: 每个主机的最大连接数
            connection_timeout: 获取连接的超时时间(秒)
            max_idle_time: 连接最大空闲时间(秒)，超过将被关闭
        """
        self.pools: Dict[str, queue.Queue] = {}  # 每个主机ID对应一个连接队列
        self.connection_params: Dict[str, Dict] = {}  # 每个主机ID对应的连接参数
        self.max_connections = max_connections
        self.connection_timeout = connection_timeout
        self.max_idle_time = max_idle_time
        self.lock = threading.RLock()
        self.active_connections: Dict[str, List[PooledConnection]] = {}  # 每个主机ID的活跃连接
        
        # 启动空闲连接清理线程
        self.cleanup_thread = threading.Thread(target=self._cleanup_idle_connections, daemon=True)
        self.cleanup_thread.start()
        
    def register_host(self, host_id: str, host_info: Dict[str, Any]) -> None:
        """
        注册主机连接信息
        
        Args:
            host_id: 主机ID
            host_info: 主机连接信息
        """
        with self.lock:
            # 存储连接参数
            self.connection_params[host_id] = {
                'host': host_info.host,
                'port': host_info.port,
                'user': host_info.user_name,
                'password': host_info.password,
                'ssl_disabled': True
            }
            
            # 为该主机创建连接池
            if host_id not in self.pools:
                self.pools[host_id] = queue.Queue(self.max_connections)
                self.active_connections[host_id] = []
                
    def get_connection(self, host_id: str) -> Tuple[Optional[PooledConnection], Optional[str]]:
        """
        获取数据库连接
        
        Args:
            host_id: 主机ID
            
        Returns:
            (连接对象, 错误消息)，如果成功则错误消息为None
        """
        if host_id not in self.connection_params:
            return None, f"未注册的主机ID: {host_id}"
            
        # 首先尝试从池中获取连接
        try:
            # 非阻塞方式尝试获取连接
            pooled_conn = self.pools[host_id].get(block=False)
            
            # 检查连接是否有效
            if not pooled_conn.is_connected():
                logger.info(f"连接池中的连接已失效，尝试重新连接 (host_id: {host_id})")
                try:
                    pooled_conn.connection.reconnect(attempts=1)
                except:
                    # 重连失败，创建新连接
                    return self._create_new_connection(host_id)
            
            # 更新最后使用时间
            pooled_conn.last_used = time.time()
            pooled_conn.in_use = True
            return pooled_conn, None
            
        except queue.Empty:
            # 池中没有可用连接，检查是否可以创建新连接
            with self.lock:
                if len(self.active_connections[host_id]) < self.max_connections:
                    # 可以创建新连接
                    return self._create_new_connection(host_id)
                else:
                    # 已达到最大连接数，等待连接释放
                    try:
                        pooled_conn = self.pools[host_id].get(timeout=self.connection_timeout)
                        pooled_conn.last_used = time.time()
                        pooled_conn.in_use = True
                        return pooled_conn, None
                    except queue.Empty:
                        return None, "获取数据库连接超时，连接池已满"
    
    def _create_new_connection(self, host_id: str) -> Tuple[Optional[PooledConnection], Optional[str]]:
        """
        创建新的数据库连接
        
        Args:
            host_id: 主机ID
            
        Returns:
            (连接对象, 错误消息)，如果成功则错误消息为None
        """
        try:
            # 创建新连接
            connection = mysql.connector.connect(**self.connection_params[host_id])
            
            if connection.is_connected():
                pooled_conn = PooledConnection(connection, self, host_id)
                pooled_conn.last_used = time.time()
                pooled_conn.in_use = True
                
                # 添加到活跃连接列表
                with self.lock:
                    self.active_connections[host_id].append(pooled_conn)
                    
                return pooled_conn, None
            else:
                return None, f"无法连接到数据库: {self.connection_params[host_id]['host']}"
                
        except Error as e:
            error_msg = f"连接数据库时出错: {str(e)}"
            logger.error(error_msg)
            return None, error_msg
    
    def release_connection(self, pooled_conn: PooledConnection) -> None:
        """
        释放连接回连接池
        
        Args:
            pooled_conn: 要释放的连接
        """
        host_id = pooled_conn.host_id
        
        # 如果连接无效，则关闭并不放回池中
        if not pooled_conn.is_connected():
            self._close_connection(pooled_conn)
            return
            
        # 更新状态并放回池中
        pooled_conn.last_used = time.time()
        pooled_conn.in_use = False
        
        try:
            self.pools[host_id].put_nowait(pooled_conn)
        except queue.Full:
            # 如果队列已满，直接关闭连接
            self._close_connection(pooled_conn)
    
    def _close_connection(self, pooled_conn: PooledConnection) -> None:
        """
        关闭连接并从活跃连接列表中移除
        
        Args:
            pooled_conn: 要关闭的连接
        """
        host_id = pooled_conn.host_id
        
        try:
            if pooled_conn.connection and pooled_conn.is_connected():
                pooled_conn.connection.close()
        except:
            pass  # 忽略关闭连接时的错误
            
        # 从活跃连接列表中移除
        with self.lock:
            if host_id in self.active_connections and pooled_conn in self.active_connections[host_id]:
                self.active_connections[host_id].remove(pooled_conn)
    
    def close_all_connections(self) -> None:
        """关闭所有连接"""
        with self.lock:
            for host_id in list(self.active_connections.keys()):
                self.close_host_connections(host_id)
    
    def close_host_connections(self, host_id: str) -> None:
        """
        关闭指定主机的所有连接
        
        Args:
            host_id: 主机ID
        """
        if host_id not in self.active_connections:
            return
            
        # 关闭所有活跃连接
        with self.lock:
            connections = self.active_connections[host_id].copy()
            for conn in connections:
                self._close_connection(conn)
            
            # 清空连接池
            try:
                while True:
                    conn = self.pools[host_id].get_nowait()
                    if conn.connection and conn.is_connected():
                        conn.connection.close()
            except queue.Empty:
                pass
                
            # 清理数据结构
            self.active_connections[host_id] = []
    
    def _cleanup_idle_connections(self) -> None:
        """
        定期清理空闲连接的后台线程
        """
        while True:
            time.sleep(60)  # 每分钟检查一次
            
            current_time = time.time()
            with self.lock:
                for host_id in list(self.active_connections.keys()):
                    # 检查非活跃连接
                    idle_connections = [
                        conn for conn in self.active_connections[host_id]
                        if not conn.in_use and (current_time - conn.last_used) > self.max_idle_time
                    ]
                    
                    # 关闭空闲连接
                    for conn in idle_connections:
                        self._close_connection(conn)
                        
            logger.debug("已完成空闲连接清理")


# 全局连接池实例
connection_pool = ConnectionPool()