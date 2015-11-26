#!/usr/bin/env python
# coding:utf-8
# env: Python3.3

import sys
import numpy as np
import pandas as pd
import math


################################################
#  宣言
################################################
option = "C"
maxlag = 1  # 最大のラグ数（正負にこの数だけズラす）
window = 3  # 何個の要素を持った窓にするか
by     = 1      # 窓から窓へは何個ずつ増えるか（いくつ被るのを許容するか）
n_overlap = window - by

################################################
#  関数
################################################


def window_df(s, window, by):
    win_list = []
    times = math.floor(((len(s) - window) / by) + 1)  # 窓の個数：floorで切り捨て
    for p in range(0, times):
        win_s = s[(0 + by * p) : (window + by * p)]  # データを窓に分割
        win_s = win_s.reset_index(drop=True)
        win_list.append(win_s)

    df = pd.concat(win_list, axis=1)

    return df


def tw_ccf(d1, d2, maxlag, window, by):

    ix = 0
    x = d1
    y = d2

    nx = len(x)
    ny = len(y)

    lag = list(np.arange(-maxlag, maxlag + 1))    # ラグ
    # print(lag)
    cor = pd.DataFrame(0, index=np.arange(maxlag * 2 + 1), columns=np.arange(1))

    Xm = x.mean(axis=0)
    Ym = y.mean(axis=0)

    Xsd = x.std(ddof=0)
    Ysd = y.std(ddof=0)

    for l in lag:
        # print(l)
        c = 0

        if l < 0:
            for n in range((- l), nx):
                c = c + (x.iloc[n] - Xm) * (y.iloc[n + l] - Ym)

        if l >= 0:
            for n in range(0, nx - l):
                c = c + (x.iloc[n] - Xm) * (y.iloc[n + l] - Ym)

        c = c / nx
        r = c / (Xsd * Ysd)

        cor.iloc[ix, :] = r
        ix += 1

    # if len(cor_list) < 2:
        # print(len(cor_list))
        # cor_list = cor_list[0]
        # print("hoge")

    cor = pd.Series(cor.values.flatten())
    return(cor)


################################################
#  メイン処理
################################################

if __name__ == '__main__':

    print("Run Process")
    print("------------------")
    print("Option:  " + option)
    print("Maxlag:  " + str(maxlag))
    print("Window:  "  + str(window))
    print("By:  " + str(by))
    print("------------------")

    # 前処理
    # 今はエラーを除外して分析、エラーを解析するなら複製データがいるかも
    # 余分なものを削除、エラー関係のも

    data_x = pd.DataFrame({"L": [1, 3, 1, 3, 1, 3], "R": [2.5, 1, 3, 1, 3, 1]})

    print(data_x)

    # 対象になる２列を指定、列の長さ確認
    x = data_x.iloc[:, 0]  # 列数で指定したいときはiloc、ixは挙動がちんぷんかんぷん
    y = data_x.iloc[:, 1]

    #print(x)
    #print(y)

    nx = len(x)
    ny = len(y)

    # 出力データフレームを仮作成
    dfC = pd.DataFrame(0, index=np.arange(maxlag * 2 + 1),
                       columns=np.arange((nx - n_overlap) / (window - n_overlap)))
    print(dfC)

    Xi = window_df(x, window, by)
    print(Xi)
    Yi = window_df(y, window, by)
    print(Yi)

    for tm in range(0, len(dfC.columns)):
        print(tm)
        Xwi = Xi.iloc[:, tm]
        Ywi = Yi.iloc[:, tm]
        print(Xwi)
        print(Ywi)
        ccf = tw_ccf(Xwi, Ywi, maxlag, window, by)
        print(ccf)
        dfC.iloc[:, tm] = ccf

    print(dfC)
    result = dfC

    t = list(np.arange(1, nx, round((nx / len(result.columns)), 2)))  # Timeの表現（何個の窓ができるのか）
    l = list(np.arange(-maxlag, maxlag + 1))           # ラグ

    # 結果を表として出力
    result.columns = [str(m) for m in t]  # タイムを文字列としての列名に
    result.index = l                              # ラグをインデックスに
    result.fillna(0)
    print(result)

    print("End Process")
