# -*- coding: utf-8 -*-
import mysql.connector
from mysql.connector import Error


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class MysqlOperator(metaclass=Singleton):
    def __init__(self):
        self.__conns = {}

    def release_connections(self):
        for connection in self.__conns.values():
            if connection.is_connected():
                connection.close()

    def release_connection(self, host_id):
        connection = self.__conns.pop(host_id)
        if connection is not None and connection.is_connected():
            connection.close()

    def do_exec_statement(self, host_id, database, sql):
        connection = self.get_database(host_id)
        if connection is None:
            return None, "error: 未找到数据库链接"
        if connection.is_connected():
            cursor = connection.cursor()
            try:
                if database:
                    cursor.execute("USE `{}`".format(database))
                cursor.execute(sql)
                if cursor.with_rows:
                    # 处理查询结果
                    records = cursor.fetchall()
                    description = cursor.description
                    connection.commit()
                    return records, [desc[0] for desc in description]
                else:
                    # 如果不是 SELECT 查询，则获取受影响的行数
                    affected_rows = cursor.rowcount
                    connection.commit()
                    return None, f"Query executed successfully. Affected rows: {affected_rows}"
            finally:
                cursor.close()
        else:
            return None, "error: 数据库链接未打开,请重新连接"

    def database(self, host_info):
        connection = self.get_database(host_info.id)
        if connection is None or connection.is_connected() == False:
            connection, msg = self.connection(host_info)
            if connection is None:
                return None, msg

        if connection is not None:
            cursor = connection.cursor()
            try:
                cursor.execute("SHOW DATABASES")
                records = cursor.fetchall()
                return [record[0] for record in records], ''
            finally:
                cursor.close()
        return None, 'failure'

    def tables(self, host_id, database):
        connection = self.get_database(host_id)
        if connection is None or not connection.is_connected():
            return None, 'error: 数据库链接未打开,请重新连接'

        if connection is not None:
            cursor = connection.cursor()
            try:
                cursor.execute("USE `{}`".format(database))
                cursor.execute('SHOW TABLES')
                records = cursor.fetchall()
                return [record[0] for record in records], ''
            finally:
                cursor.close()
        return None, 'error: 数据库链接未打开,请重新连接'

    def connection(self, host_info):
        if host_info is not None:
            try:
                # 创建连接
                connection = mysql.connector.connect(
                    host=host_info.host,
                    port=host_info.port,
                    user=host_info.user_name,
                    password=host_info.password,
                    ssl_disabled=True
                )

                if connection.is_connected():
                    self.__conns[host_info.id] = connection
                    return connection, '[Connected to MySQL Server version:{}] {}:{}'.format(
                        connection.get_server_info(), host_info.host, host_info.port)
                else:
                    return None, 'Error while connecting to MySQL:{}, open failure'.format(host_info.host)
            except Error as e:
                msg = "Error while connecting to MySQL:{}, {}".format(host_info.host, e)
                return None, msg

    def get_database(self, host_id):
        connection = self.__conns.get(host_id, None)
        if connection is not None and not connection.is_connected():
            # 尝试重新连接
            connection.reconnect(attempts=3, delay=0)
            print("数据库连接已失效，将重新连接")

        return connection
