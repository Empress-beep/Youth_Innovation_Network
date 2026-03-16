# Youth Innovation Network Data Scraper

This project is a web scraper designed to collect data from the Youth Innovation Network, developed primarily in Python with JavaScript used for handling encrypted parameters, and data stored using a MySQL database.

## Project Structure

```
youth_innovation_network/
├── config.ini          # Database configuration file
├── main.py             # Project entry point
├── spider.py           # Core scraper logic
├── db.py               # Database operations module
├── reverse.js          # JavaScript encryption/decryption tool
├── depend.js           # RSA encryption dependency library
└── node_modules/       # Node.js dependency packages
```

## Technology Stack

- **Python 3.x** - Primary programming language
- **MySQL** - Data storage
- **Node.js** - JavaScript runtime environment
- **crypto-js** - AES/SHA encryption algorithms
- **jsencrypt** - RSA public key encryption

## Features

- Breakpoint retry mechanism for more stable network requests
- RSA encrypted parameter handling
- Bulk data insertion into database
- Automatic database and table initialization

## Configuration

Edit the `config.ini` file to configure MySQL database connection details:

```ini
[mysql]
host = localhost
port = 3306
user = your_username
password = your_password
database = your_database
```

## Usage

1. Install dependencies

```bash
# Python dependencies
pip install pymysql cryptography

# Node.js dependencies (already included in project)
npm install
```

2. Configure the database

Modify the database connection parameters in `config.ini`.

3. Run the scraper

```bash
python main.py
```

## Module Descriptions

### spider.py
Core scraper module containing the `QCW` class with main methods:
- `get_index_url()` - Retrieve the homepage URL
- `get_data(page)` - Fetch data for a specified page
- `decrypt_data(res)` - Decrypt response data
- `parse_data(data)` - Parse extracted data
- `save_data(data)` - Save data to the database
- `main()` - Main entry point of the scraper

### db.py
Database operations module containing the `MySQLDB` class:
- `__init__()` - Initialize database connection
- `_read_config()` - Read configuration file
- `_init_database()` - Initialize database and tables
- `save_products_batch()` - Bulk insert product data

### reverse.js / depend.js
JavaScript encryption/decryption tools used to handle website security verification parameters.

## Notes

- Ensure the MySQL service is running
- Comply with the website's robots.txt rules
- Set appropriate scraping frequency to avoid overloading the target website
- This project is intended solely for learning and research purposes

## License

MIT License