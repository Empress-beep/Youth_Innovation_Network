from spider import QCW

if __name__ == '__main__':
    # 首页地址，用于获取key和iv
    index_url = 'https://xie.17qcc.com/'
    # 数据地址，用于获取数据
    data_url = 'https://newopenapiweb.17qcc.com/api/services/app/SearchFactory/GetPageList'
    h2 = QCW(index_url=index_url, data_url=data_url, db_config_file='config.ini')
    h2.main()
