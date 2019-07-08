# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import math as math


def ceil(src, range):
    """
    Number rounding function
    :param src: target number
    :param range: round up digit　 ex) 100,1000,10000
    :return: number after rounding up
    """
    return (int(src / range) + 1) * range


class corr_simulation():
    def __init__(self, tilt, intercept, max, min, thickness, interval, calc_time):
        self.tilt = tilt
        self.intercept = intercept
        self.max = max
        self.min = min
        self.thickness = thickness
        self.interval = interval
        self.calc_time = calc_time

    def calc_concent(self, progress):
        concentration = self.max - ((self.max - self.min) / self.thickness) * progress
        if concentration >= 0:
            return concentration
        else:
            return 0

    def calc_progress(self):
        Zn_con = self.max
        corr_rate = self.tilt * Zn_con + self.intercept
        t = 0
        corr_progress = 0
        result = np.array([[0, 0]])

        while t < self.calc_time:
            t = t + self.interval
            corr_progress = corr_progress + corr_rate * self.interval
            Zn_con = self.calc_concent(progress=corr_progress)
            corr_rate = self.tilt * Zn_con + self.intercept
            result = np.append(result, np.array([[t, corr_progress]]), axis=0)

        return result

    def calc_progress_diagonal(self, angle):
        thickness_fix = self.thickness / np.sin(angle)

        Zn_con = self.max
        corr_rate = self.tilt * Zn_con + self.intercept
        t = 0
        corr_progress = 0
        result = np.array([[[0, 0, 0]]])

        while t < self.calc_time:
            t = t + self.interval
            corr_progress = corr_progress + corr_rate * self.interval
            corr_progress_X = corr_progress * np.cos(angle)
            corr_progress_Y = corr_progress * np.sin(angle)

            Zn_con = self.calc_concent(progress=corr_progress_Y)
            corr_rate = self.tilt * Zn_con + self.intercept
            result = np.append(result, np.array([[[t, corr_progress_X, corr_progress_Y]]]), axis=1)

        return result

    def plot_graph(self, data, year, resolution, name):
        X = 0
        Y = 0
        size = 30  # グラフエリアのサイズ
        plot_num = int(year / self.interval)
        plt.figure(figsize=(size, size / 4))
        plt.scatter(X, Y, s=10)

        for i in range(1, plot_num, int(plot_num / resolution)):
            X = data[:, i, 1]
            Y = data[:, i, 2]
            plt.plot(X, Y, color=cm.jet(i / plot_num))

        limit = ceil(np.max(data[:, plot_num, 1]), 100)
        plt.xlim(-1 * limit, limit)
        plt.ylim(-1 * limit / 2, 0)
        plt.xticks(np.arange(-1 * limit, limit + 1, 20))
        plt.yticks(np.arange(-1 * limit / 2, 1, 20))
        plt.grid(True)
        plt.savefig(name)
        plt.show()


if __name__ == '__main__':
    # ----arrayの表示書式設定----#
    np.set_printoptions(precision=2)
    np.set_printoptions(suppress=True)

    # ----シミュレーションインスタンスの生成----#
    corr = corr_simulation(tilt=4.3972, intercept=7, max=5, min=0.2, thickness=75, interval=0.05, calc_time=10)

    # ----データのスタック元になるarrayの生成----#
    result_all = corr.calc_progress_diagonal(angle=np.deg2rad(90))
    print(result_all.shape)
    print(result_all)
    print("--------------")

    # ----各角度で腐食進度を計算----#
    for i in range(1, 180):
        result_all = np.append(result_all, corr.calc_progress_diagonal(angle=np.deg2rad(i)), axis=0)

    result_all = np.delete(result_all, obj=0, axis=0)  # スタック元となったデータを削除
    print("-------------")
    print(result_all.shape)
    print(result_all)

    result_all = result_all * -1  # 負の数に変換

    corr.plot_graph(data=result_all, year=5, resolution=20, name="result_1.png")
