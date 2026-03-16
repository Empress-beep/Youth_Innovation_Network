


# 电商数据爬虫

本项目是一个用于采集电商平台数据的爬虫程序，采用 Python 作为主要开发语言，结合 JavaScript 进行加密参数、响应体解密处理，数据存储使用 MySQL 数据库。

## 项目结构

```
youth_innovation_network/
├── config.ini          # 数据库配置文件
├── main.py             # 项目入口文件
├── spider.py           # 爬虫核心逻辑
├── db.py               # 数据库操作模块
├── reverse.js          # JavaScript 加密解密工具
├── depend.js           # RSA 加密依赖库
└── node_modules/       # Node.js 依赖包
```

## 技术栈

- **Python 3.x** - 主要编程语言
- **MySQL** - 数据存储
- **Node.js** - JavaScript 运行时
- **crypto-js** - AES/SHA 等加密算法
- **jsencrypt** - RSA 公钥加密

## 功能特性

- 断点重试机制，网络请求更稳定
- RSA 加密参数处理
- 数据批量入库
- 自动初始化数据库和数据表

## 配置说明

编辑 `config.ini` 文件，配置 MySQL 数据库连接信息：

```ini
[mysql]
host = localhost
port = 3306
user = your_username
password = your_password
database = your_database
```

## 使用方法

1. 安装依赖

```bash
# Python 依赖
pip install pymysql cryptography

# Node.js 依赖（项目已包含）
npm install
```

2. 配置数据库

修改 `config.ini` 中的数据库连接参数。

3. 运行爬虫

```bash
python main.py
```

## 模块说明

### spider.py
爬虫核心模块，包含 `QCW` 类，主要方法：
- `get_index_url()` - 获取首页key和iv
- `get_data(page)` - 参数加密并获取指定页码数据
- `decrypt_data(res)` - 解密响应数据
- `parse_data(data)` - 解析数据
- `save_data(data)` - 保存数据到数据库
- `main()` - 爬虫主入口

### db.py
数据库操作模块，包含 `MySQLDB` 类：
- `__init__()` - 初始化数据库连接
- `_read_config()` - 读取配置文件
- `_init_database()` - 初始化数据库和数据表
- `save_products_batch()` - 批量保存产品数据

### reverse.js / depend.js
JavaScript 加密解密工具，用于处理网站的安全验证参数。

## 注意事项

- 请确保 MySQL 服务已启动
- 遵守网站的 robots.txt 规则
- 合理设置爬取频率，避免对目标网站造成压力
- 本项目仅供学习研究使用

## 许可证

MIT License