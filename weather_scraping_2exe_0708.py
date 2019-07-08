#!/usr/bin/env python
# 気象庁参考サイト：https://www.data.jma.go.jp/obd/stats/etrn/view/10min_s1.php?prec_no=61&block_no=47759&year=2018&month=12&day=1&view=
# coding: UTF-8

import requests
from bs4 import BeautifulSoup
import pandas as pd
import datetime
import re


class weather_scraping():
    def __init__(self, ID, PASS):
        self.ID = ID
        self.PASS = PASS
        self.proxies = {"http": "http://{0}:{1}@proxy.wrc.melco.co.jp:9515/".format(self.ID, self.PASS),
                        "https": "https://{0}:{1}@proxy.wrc.melco.co.jp:9515/".format(self.ID, self.PASS)}

    def setting(self):
        self.initial_url = input("取得開始日のURL:")
        pattern = r"\d{1,}"
        number = re.findall(pattern, self.initial_url)
        self.prec_no = number[2]
        self.block_no = number[3]
        year = int(number[4])
        month = int(number[5])
        day = int(number[6])
        self.startdate = datetime.datetime(year, month,day)
        self.term = int(input("データ取得日数："))

    def create_url(self):
        self.urls = []
        for i in range(self.term + 1):
            dt = self.startdate + datetime.timedelta(days=i)
            year = dt.year
            month = dt.month
            day = dt.day

            if len(self.block_no) == 4:
                # エリアコード4桁地域用
                self.urls.append(
                    'https://www.data.jma.go.jp/obd/stats/etrn/view/10min_a1.php?prec_no={0}&block_no={1}&year={2}&month={3}&day={4}&view='.format(
                        self.prec_no, self.block_no, year, month, day))

            else:
                self.urls.append(
                    'https://www.data.jma.go.jp/obd/stats/etrn/view/10min_s1.php?prec_no={0}&block_no={1}&year={2}&month={3}&day={4}&view='.format(
                        self.prec_no, self.block_no, year, month, day))


        return self.urls

    def scraping_data(self, url):
        # HTMLの取得（requestsモジュールを使用）
        if ID == "":
            r = requests.get(url, timeout=3)
        else:
            r = requests.get(url, timeout=3, proxies=self.proxies)
        r.encoding = r.apparent_encoding  # エンコード情報を取得

        # beautifulsoupへ渡す
        soup = BeautifulSoup(r.text, 'lxml')

        # tableを探す
        trs = soup.find('table', {'class': 'data2_s'})
        df = pd.DataFrame()

        # 1レコードづつ処理する
        i = 0
        for tr in trs.findAll('tr'):
            tds = tr.findAll('td')
            k = 0
            for e in tds:
                df.loc[i, k] = e.getText()
                k = k + 1
            i = i + 1
        # 列名を挿入
        if len(self.block_no) == 4:
            # エリアコード4桁地域用
            df.columns = ['時分', '降水量(mm)', '気温', '風速平均', '風向', '最大瞬間風速', '風向', '日照時間']
        else:
            df.columns = ['時分', '気圧(現地)', '気圧(海面)', '降水量(mm)', '気温', '相対温度', '風速平均', '風向', '最大瞬間風速', '風向', '日照時間']

        return df

    def save2csv(self, df, i):
        if i == 0:
            df.to_csv('気象庁データ_{0}_{1}_{2}.csv'.format(self.prec_no, self.block_no, self.startdate.date()),
                      encoding="shift_jis")
        else:
            df.to_csv('気象庁データ_{0}_{1}_{2}.csv'.format(self.prec_no, self.block_no, self.startdate.date()), mode='a',
                      header=False, encoding="shift_jis")


if __name__ == "__main__":
    # プロキシの設定
    print("ユーザー情報を入力してください")
    ID = input("情報ID：") or "FU25166"  # 情報IDを入力 プロキシ不要の場合は""でenter
    PASS = input("PW：") or "=ampmNTT3321"  # パスワードを入力

    scrap = weather_scraping(ID=ID, PASS=PASS)

    cont = "y"

    while cont == "y":
        scrap.setting()
        urls = scrap.create_url()
        # try:
        print("---------------------------")
        print("データの取得を開始します")
        for i in range(len(scrap.create_url())):
            print(urls[i])
            df=scrap.scraping_data(url=urls[i])
            scrap.save2csv(df=df, i=i)
        print("データの取得が完了しました")

        # except:
        #     print("エラーが発生しました")

        print("---------------------------")
        cont = input("続けて実行しますか？(y/n)：")
