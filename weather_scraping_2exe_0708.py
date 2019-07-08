#!/usr/bin/env python
# 気象庁参考サイト：https://www.data.jma.go.jp/obd/stats/etrn/view/10min_s1.php?prec_no=63&block_no=47769&year=2018&month=12&day=1&view=
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
        self.initial_url = input("取得を開始する日のurlを入力してください:")
        pattern = r"\d{1,}"
        number = re.findall(pattern, self.initial_url)
        self.prec_no=number[2]
        self.block_no=number[3]
        self.year=number[4]
        self.month = number[5]
        self.day = number[6]
        self.startdate= datetime.datetime(self.year, self.month, self.day)
        self.term= int(input("データ取得期間："))

    def weater_scraping(self,url):
        # HTMLの取得（requestsモジュールを使用）
        if ID == "":
            r = requests.get(url, timeout=3)
        else:
            r = requests.get(url, timeout=3, proxies=proxies)
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
        if areaflag == 0:
            df.columns = ['時分', '気圧(現地)', '気圧(海面)', '降水量(mm)', '気温', '相対温度', '風速平均', '風向', '最大瞬間風速', '風向', '日照時間']
        else:
            # エリアコード4桁地域用
            df.columns = ['時分', '降水量(mm)', '気温', '風速平均', '風向', '最大瞬間風速', '風向', '日照時間']

        return df


if __name__ == "__main__":

    # プロキシの設定
    print("ユーザー情報を入力してください")
    ID = input("情報ID：")  # 情報IDを入力 プロキシ不要の場合は""でenter
    PASS = input("PW：")  # パスワードを入力

    scraping =weather_scraping(ID=ID,PASS=PASS)
    scraping.setting()

    cont = "y"
    while cont == "y":

        try:
            # --------------データ取得条件入力---------------- #
            print("データの取得条件を入力してください")
            startyear = int(input(" 年："))
            startmonth = int(input(" 月："))
            startday = int(input(" 日："))
            start = datetime.datetime(startyear, startmonth, startday)  # 開始日

            testterm = int(input("試験期間："))  # 期間
            areacode1 = input("prec_no：")  # ex)63   気象庁ページのエリアコード1
            areacode2 = input("block_no：")  # ex)47769 気象庁ページのエリアコード2
            # ------------------------------------------------ #

            # areaflagを設定　areacode2が4桁の場合は1,それ以外は0
            if len(areacode2) == 4:
                areaflag = 1
            else:
                areaflag = 0
            print("---------------------------")
            print("データの取得を開始します")
            for i in range(testterm + 1):
                dt = start + datetime.timedelta(days=i)
                year = dt.year
                month = dt.month
                day = dt.day
                print(dt)

                if areaflag == 0:
                    # 対象のサイト
                    url = 'https://www.data.jma.go.jp/obd/stats/etrn/view/10min_s1.php?prec_no={0}&block_no={1}&year={2}&month={3}&day={4}&view='.format(
                        areacode1, areacode2, year, month, day)
                else:
                    # エリアコード4桁地域用
                    url = 'https://www.data.jma.go.jp/obd/stats/etrn/view/10min_a1.php?prec_no={0}&block_no={1}&year={2}&month={3}&day={4}&view='.format(
                        areacode1, areacode2, year, month, day)

                print(url)

                if i == 0:
                    weater_scraping(url, areaflag).to_csv(
                        '気象庁データ_{0}_{1}_{2}{3}{4}.csv'.format(areacode1, areacode2, start.year, start.month,
                                                              start.day), encoding="shift_jis")
                else:
                    weater_scraping(url, areaflag).to_csv(
                        '気象庁データ_{0}_{1}_{2}{3}{4}.csv'.format(areacode1, areacode2, start.year, start.month, start.day),
                        mode='a', header=False, encoding="shift_jis")
            print("データの取得が完了しました")

        except:
            print("エラーが発生しました")

        print("---------------------------")
        cont = input("続けて実行しますか？(y/n)：")
