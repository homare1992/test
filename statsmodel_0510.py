# coding: utf-8
import pandas as pd
import numpy as np
from sklearn import linear_model
import itertools
from tqdm import tqdm
import time
import collections
import statsmodels.api as sm


def Normalize(dataframe, STD_FLAG=0):
    '''
    データの正規化用の関数
    :param dataframe: 対象のデータフレームオブジェクト
    :param STD_FLAG: 正規化の方法、STD_FLAG: ==1ならデータの標準化を実行, ==2ならデータの最大値で割って(0~1)データ化
    :return: 処理後のデータフレーム
    '''
    if STD_FLAG == 1:
        data = dataframe.apply(lambda x: (x - np.mean(x)) / (np.max(x) - np.min(x)))
    elif STD_FLAG == 2:
        data = dataframe.apply(lambda x: x / np.max(x))
    else:
        data = dataframe

    return data


def regression_sm(data, name_Y, list_X):
    x = data[list_X]  # 説明変数に list_Xの変数を利用
    Y = data[name_Y]  # 目的変数に "Y" を利用

    # 全要素が1の列を説明変数の先頭に追加（切片算出時に必要！！）
    X = sm.add_constant(x)

    # モデルの設定
    model = sm.OLS(Y, X)
    # 回帰分析の実行
    result = model.fit()
    # 結果の詳細を表示
    # print(result.summary())

    # 各種統計量を算出
    name = np.insert(list_X, 0, "const")
    Rsuquared = result.rsquared
    Rsuquared_adj = result.rsquared_adj
    coef = result.params
    impact = pd.Series([])
    for i in range(len(X.columns)):
        impact_one = (X.iloc[:, i].max() - X.iloc[:, i].min()) * np.abs(coef[i])
        impact[name[i]] = impact_one
    pvalue = result.pvalues

    # 出力用のデータフレーム
    output = pd.DataFrame(
        {"Coefficients": coef, "impact": impact, "pvalue": pvalue,
         "R2": Rsuquared, "R2f": Rsuquared_adj})
    # 並び替え
    output = output.loc[:, ["R2", "R2f", "Coefficients", "impact", "pvalue"]]

    return output, Rsuquared, Rsuquared_adj, coef, impact, pvalue


def eval_winner(eval_f,evalflag=0):
    eval_f_ex = eval_f.drop("const")
    if evalflag==0:
        win = eval_f_ex.idxmax()
    else:
        win= eval_f_ex.idxmin()

    return win


def counter2csv(filename, dict):
    winner, num_win = zip(*dict.most_common())
    df = pd.DataFrame({"factor": winner, "wins": num_win})
    df.to_csv(filename)


if __name__ == '__main__':

    # ----パラメータ設定------#
    INPUT = "data_kit_rate.xlsx"
    obj_var = 2  # 目的変数　[1]=腐食体積、[2]=腐食速度
    STD_FLAG = 3  # データの正規化方法,==1：標準化, ==2：最大値で割って(0~1)データ化
    num_extract_fac = 2  # 重回帰分析時の因子数
    eval_f = 1  # 因子同士の勝敗を評価する関数 [0]=impact、[1]=pvalue

    # --------実行-------#
    start = time.time()
    timestr = time.strftime("%Y%m%d-%H%M%S")

    obj_name = "腐食体積" if obj_var == 1 else "腐食速度"
    eval_name = "影響度" if eval_f == 0 else "P値"
    filename1 = 'output_{0}_{1}因子_{2}.csv'.format(obj_name, num_extract_fac, timestr)
    filename2 = 'output_{0}_{1}因子_{2}_victory_{3}.csv'.format(obj_name, num_extract_fac, timestr,eval_name)

    # データの読み込み
    data = pd.read_excel(INPUT)
    columns_name = data.columns.values
    # 正規化
    data_ex = data.drop(columns_name[0], axis=1)
    data_std = Normalize(data_ex, STD_FLAG=STD_FLAG)

    fac = columns_name[3:]  # 不要な因子をカット
    name_Y = columns_name[obj_var]
    print("-------------------------------\n目的変数：" + name_Y)
    print("対象因子")
    print(fac)

    # 組み合わせの作成
    comb = list(itertools.combinations(fac, num_extract_fac))
    print("-------------------------------\n組み合わせ数：" + str(len(comb)) + "通り")

    winner = []
    # 重回帰分析を全パターンで実施
    for i in tqdm(range(len(comb))):
        list_X = list(comb[i])
        output1, _, _, _, impact1, pvalue1 = regression_sm(data=data_std, name_Y=name_Y, list_X=list_X)
        output1.to_csv(filename1, mode="a")
        if eval_f == 0:
            winner.append(eval_winner(eval_f=impact1,evalflag=0))
        elif eval_f == 1:
            winner.append(eval_winner(eval_f=pvalue1,evalflag=1))
        else:
            print("error: Unacceptable value is assigned to eval_f.")

    # 勝利数をカウント
    victory = collections.Counter(winner)
    # 勝理数をcsvで出力
    counter2csv(filename2, victory)

    # --------------計測終了----------------#
    process_time = time.time() - start
    print("処理時間：" + str(round(process_time, 0)) + "秒")
