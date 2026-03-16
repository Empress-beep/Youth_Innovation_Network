import re
import json
from db import MySQLDB
import subprocess
from functools import partial
from loguru import logger as log

subprocess.Popen = partial(subprocess.Popen, encoding="utf-8")

import execjs
import requests


class QCW:
    def __init__(self, index_url, data_url, db_config_file='config.ini'):
        self.db = MySQLDB(db_config_file)
        self.requests = requests.Session()
        self.index_url = index_url
        self.header = {
            "accept": "application/json, text/javascript, */*; q=0.01",
            # "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "zh-CN,zh;q=0.9",
            "app-guestid": "19673584A8B0B539634CD41F786D1244",
            "app-version": "0",
            "cache-control": "no-cache",
            # "content-length": "698",
            "content-type": "application/json",
            "data-version": "1",
            "origin": "https://xie.17qcc.com",
            "pragma": "no-cache",
            "priority": "u=1, i",
            # "qcc-pc-referer": "https://xie.17qcc.com/",
            "referer": "https://xie.17qcc.com/",
            "sec-ch-ua": "\"Not:A-Brand\";v=\"99\", \"Microsoft Edge\";v=\"145\", \"Chromium\";v=\"145\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 Edg/145.0.0.0"
        }
        self.data_url = data_url
        self.ctx = execjs.compile(open('reverse.js', 'r', encoding='utf-8').read())
        self.qccppm = None
        self.qccrkeys = None

    # 首页函数(获取key和iv)
    def get_index_url(self, max_retries=4):
        # 断点重试，最多重试3次
        for i in range(1, max_retries):
            try:
                response = self.requests.get(url=self.index_url, headers=self.header)
                log.info('第 {} 次首页提交，状态码：{}', i, response.status_code)
                response.raise_for_status()
                # 设置编码
                response.encoding = response.apparent_encoding
                # 使用正则提取数据
                key_value = re.search('var qccrkeys = (.*?]);', response.text, re.DOTALL).group(1).strip()
                iv_value = re.search('var qccppm = "(.*?)"', response.text, re.DOTALL).group(1).strip()
                # 判断两个关键变量是否都获取到值
                if key_value and iv_value:
                    self.qccppm = iv_value
                    try:
                        # 将key转为python列表
                        self.qccrkeys = json.loads(key_value)
                    except (SyntaxError, ValueError) as e:
                        log.error('解析 qccrkeys 失败: {}', e)
                    log.info('成功获取 key 值 {}, iv 值 {}', self.qccrkeys, self.qccppm)
                    # 获取到值就结束这个函数
                    return
                else:
                    print('key 或 iv 值为空，重试...')
            except Exception as e:
                print('请求或处理异常:', e)
        # 重试耗尽
        raise RuntimeError(f'在 {max_retries - 1} 次尝试后仍未成功获取key,iv数据')

    # 数据获取函数(加密数据)
    def get_data(self, page, max_retries=4):
        # 运行"get_data"函数获取加密参数
        code = self.ctx.call('get_data', page, self.qccppm, self.qccrkeys)
        data = {
            'KM': code['KM'],
            'Ver': code['Ver'],
            'Content': code['Content'],
            'Sign': code['Sign'],
            'RsaPubAes': code['RsaPubAes'],
            'IV': code['IV'],
            'TimesTamp': code['TimesTamp'],
        }
        # 转为字符串，去除空格
        data = json.dumps(data, separators=(',', ':'))
        for i in range(1, max_retries):
            try:
                response = self.requests.post(url=self.data_url, headers=self.header, data=data)
                log.info('第 {} 次数据提交，状态码：{}', i, response.status_code)
                response.raise_for_status()
                response.encoding = response.apparent_encoding
                if response.json()['Success']:
                    log.info('成功获取加密商品数据：{}', response.json())
                    return response.json()
                else:
                    log.info('签名验证失败: {}', response.json())
                    log.info('数据获取失败，重试中...')
            except Exception as e:
                print('数据获取失败:', e)
        # 重试耗尽
        raise RuntimeError(f'在 {max_retries - 1} 次尝试后仍未成功获取商品数据')

    # 解密数据函数
    def decrypt_data(self, res):
        data = self.ctx.call('decrypt_data', res['Result'], self.qccppm)
        if data['Success']:
            log.info('----数据解密成功----')
            log.info('----正在调用解析函数----')
            self.parse_data(data['Result'])
        else:
            print('数据解密失败!!!')

    # 解析数据函数
    def parse_data(self, data):
        products = []
        for info in data['Items']:
            produt = {
                'id': info['ProductId'],  # 商品ID
                'title': info['ProductName'],  # 商品名称
                'item_number': info['ProductNo'],  # 货号
                'photo_url': info['Photo'],  # 商品图片链接
                'detail_url': info['Url'],  # 详情页链接
                'release_date': info['CreationTime']  # 上市时间
            }
            products.append(produt)
        log.info('----正在调用保存函数----')
        self.save_data(products)

    # 保存函数
    def save_data(self, data):
        if not data:
            log.info('没有数据需要保存')
            return
        self.db.save_products_batch(data)

    def main(self):
        self.get_index_url()
        for page in range(1, 101):
            response = self.get_data(page)
            log.info('----正在调用数据解密函数----')
            self.decrypt_data(response)


# if __name__ == '__main__':
#     # 首页地址，用于获取key和iv
#     index_url = 'https://xie.17qcc.com/'
#     # 数据地址，用于获取数据
#     data_url = 'https://newopenapiweb.17qcc.com/api/services/app/SearchFactory/GetPageList'
#     h2 = QCW(index_url=index_url, data_url=data_url)
#     h2.main()
