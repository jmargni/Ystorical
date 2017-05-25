import re
import sys
import time
from datetime import datetime as dt

import dryscrape
import pandas as pd
from fake_useragent import UserAgent
from lxml.html import fromstring
from xvfbwrapper import Xvfb

try:
    import requesocks as requests
except:
    import requests

ua = UserAgent()


class YahooHistorical(object):
    url = 'https://finance.yahoo.com/quote/{0}/history?p={0}'

    def __init__(self, proxy_port=None):
        try:
            vdisplay = Xvfb()
            vdisplay.start()
        except:
            pass
        self.session = dryscrape.Session()
        self.session.set_attribute('auto_load_images', False)
        self.session.set_header('User-agent', ua.random)
        if proxy_port:
            self.session.proxies = {'http': 'socks5://127.0.0.1:' + str(proxy_port),
                                    'https': 'socks5://127.0.0.1:' + str(proxy_port)}
    def __del__(self):
        try:
            self.vdisplay.stop()
        except:
            pass

    def call(self, symbols, from_date=None, to_date=None):
        download_link = self.get_download_link(symbols[0])
        if from_date is not None and to_date is not None:
            download_link = self.fix_dates(download_link, from_date, to_date)
        data = []
        for symbol in symbols:
            download_link = self.fix_symbol(symbol, download_link)
            dataframe = self.get_dataframe(download_link)
            dataframe.insert(0, 'Symbol', symbol)
            data.append(dataframe)
        return pd.concat(data).reset_index().drop('index', 1)

    def get_download_link(self, symbol):
        self.session.visit(self.url.format(symbol))
        response = fromstring(self.session.body())
        download_link = response.xpath("//a[@class='Fl(end) Mt(3px) Cur(p)']")
        return download_link[0].xpath("./@href")[0]

    def get_dataframe(self, download_link):
        self.session.visit(download_link)
        csv_data = self.session.body()
        # and finally if you want to get a dataframe from it
        if sys.version_info[0] < 3:
            from StringIO import StringIO
        else:
            from io import StringIO
        df = pd.read_csv(StringIO(csv_data), index_col=[0], parse_dates=True)
        df = df.reset_index()
        df.rename(columns={'Adj Close': 'Adj_Close'}, inplace=True)
        df.sort_values(['Date'], inplace=True)
        return df

    @staticmethod
    def fix_dates(download_link, from_date, to_date):
        # now replace the default end date end start date that yahoo provides
        s = from_date
        period1 = '%.0f' % time.mktime(dt.strptime(s, "%Y-%m-%d").timetuple())
        e = to_date
        period2 = '%.0f' % time.mktime(dt.strptime(e, "%Y-%m-%d").timetuple())
        # now we replace the period download by our dates, please feel free to improve, I suck at regex
        m = re.search('period1=(.+?)&', download_link)
        if m:
            to_replace = m.group(m.lastindex)
            download_link = download_link.replace(to_replace, period1)
        m = re.search('period2=(.+?)&', download_link)
        if m:
            to_replace = m.group(m.lastindex)
            download_link = download_link.replace(to_replace, period2)
        return download_link

    @staticmethod
    def fix_symbol(symbol, download_link):
        m = re.search('download/(.+?)\?', download_link)
        if m:
            to_replace = m.group(m.lastindex)
            download_link = download_link.replace(to_replace, symbol)
        return download_link



if __name__ == "__main__":
    page = YahooHistorical()
    print page.call(['AAPL', 'GOOGL', 'IBM'], "2017-05-10", "2017-05-15")

    pass
