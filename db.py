# 数据库存储文件
import pymysql
import configparser
from loguru import logger as log


class MySQLDB:
    def __init__(self, config_file='config.ini'):
        self.config = self._read_config(config_file)
        self._init_database()

    def _read_config(self, config_file):
        # 读取配置文件，返回数据库连接参数字典
        config = configparser.ConfigParser()
        config.read(config_file, encoding='utf-8')
        mysql_config = {
            'host': config.get('mysql', 'host'),
            'port': config.getint('mysql', 'port'),
            'user': config.get('mysql', 'user'),
            'password': config.get('mysql', 'password'),
            'database': config.get('mysql', 'database'),
            'charset': config.get('mysql', 'charset')
        }
        return mysql_config

    def _init_database(self):
        # 初始化数据库和数据表(不存在就创建)
        # 先连接MySQL服务器(不指定数据库)创建数据库
        conn = pymysql.connect(
            host=self.config['host'],
            port=self.config['port'],
            user=self.config['user'],
            password=self.config['password'],
            charset=self.config['charset']
        )
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    f'CREATE DATABASE IF NOT EXISTS {self.config['database']} DEFAULT CHARACTER SET {self.config['charset']}')
                conn.commit()
        finally:
            conn.close()
        conn = pymysql.connect(**self.config)
        try:
            with conn.cursor() as cursor:
                create_table_sql = """
        CREATE TABLE IF NOT EXISTS products(
          id VARCHAR(50) PRIMARY KEY COMMENT '商品ID',
          title VARCHAR(255) NOT NULL COMMENT '商品名称',
          item_number VARCHAR(100) COMMENT '货号',
          photo_url VARCHAR(500) COMMENT '商品图片链接',
          detail_url VARCHAR(500) COMMENT '详情页链接',
          release_date DATETIME COMMENT '上市时间',
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录创建时间'
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='商品信息表';
        """
                cursor.execute(create_table_sql)
            conn.commit()
        finally:
            conn.close()
        log.info('数据库，数据表初始化完成')

    def save_products_batch(self, products_list):
        """批量保存商品数据（提高效率）"""
        if not products_list:
            return
        conn = None
        try:
            conn = pymysql.connect(**self.config)
            with conn.cursor() as cursor:
                sql = """
                INSERT INTO products (id, title, item_number, photo_url, detail_url, release_date)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    title = VALUES(title),
                    item_number = VALUES(item_number),
                    photo_url = VALUES(photo_url),
                    detail_url = VALUES(detail_url),
                    release_date = VALUES(release_date)
                """
                data = [(
                    p['id'],
                    p['title'],
                    p['item_number'],
                    p['photo_url'],
                    p['detail_url'],
                    p['release_date']
                ) for p in products_list]
                cursor.executemany(sql, data)
            conn.commit()
            log.info("批量保存 {} 条商品成功", len(products_list))
        except Exception as e:
            log.error("批量保存失败: {}", e)
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()
