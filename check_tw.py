#!/usr/bin/env python
# coding:utf-8
# env: Python3.3

import sys
import array
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import math


################################################
#  宣言
################################################
option = "A"
maxlag = 3  # 最大のラグ数（正負にこの数だけズラす）
window = 10  # 何個の要素を持った窓にするか
by     = 1      # 窓から窓へは何個ずつ増えるか（いくつ被るのを許容するか）
n_overlap = window - by

################################################
#  関数
################################################


def buffer(s, lag):
    s_list = []

    for i in range(lag + 1):
        s_shift = s.shift(i).fillna(0)  # ずらしたデータの作成
        s_shift.name = i
        s_list.append(s_shift)

    df = pd.concat(s_list, axis=1)

    return df


def window_df(s, window, by):
    win_list = []
    times = math.floor(((len(s) - window) / by) + 1)  # 窓の個数：floorで切り捨て
    for n in range(0, times):
        win_s = s[(0 + by * n) : (window + by * n)]  # データを窓に分割
        win_s = win_s.reset_index(drop=True)
        win_list.append(win_s)

    df = pd.concat(win_list, axis=1)

    return df


# 標準化、偏差和を（母集団）標準偏差で割る
# とりあえずは使わず
def normalize(df):
    df_set = pd.DataFrame()
    df_list = []

    for i in range(0, len(df.columns)):
        col = df.iloc[:, i]

        m = col.mean()
        sd = col.std()
        nz = col.sub(m).div(sd)

        df_list.append(nz)

    df_set = pd.concat(df_list, axis=1)
    return df_set


def win_ccf(d1, d2):

    cor_list = []

    # ある時点（列）での窓同士を選択して、相関解析 → それを各列
    for x in range(0, len(d1.columns)):
        a1 = np.array(d1.iloc[:, x])
        a2 = np.array(d2.iloc[:, x])

        nx = len(a1)
        ny = len(a2)

        sum = sum + float(a1) * float(a2)
        cor_list.append(sum)

    if len(cor_list) < 2:
        # print(len(cor_list))
        cor_list = cor_list[0]
        # print("hoge")

    return cor_list


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


    # データ読み込み
    df = pd.DataFrame({"A": list(range(1, 11)), "B": list(range(11, 21))})
    print(df)
    df_sum = pd.DataFrame()

    # 対象になる２列を指定、列の長さ確認
    x = df.iloc[:, 0]  # 列数で指定したいときはiloc、ixは挙動がちんぷんかんぷん
    y = df.iloc[:, 1]

    print(x)
    print(y)

    nx = len(x)
    ny = len(y)

    # lag分ずらしたDfの準備
    X = buffer(x, maxlag).sort_index(axis=1, ascending=False)  # +1カウントに合わせてできるように列を逆順にする
    Y = buffer(y, maxlag)

    print(X)
    print(Y)

    # 出力データフレームを仮作成
    C = pd.DataFrame(0, index=np.arange(maxlag * 2 + 1),
                     columns=np.arange((nx - n_overlap) / (window - n_overlap)))

    print(C)

    # 相互相関解析
    # -maxlag ~ 0まで：Y列を固定、X列を動かす
    Yi = Y.iloc[:, 0]  # Yのフルサイズ列
    Yi = window_df(Yi, window, by)  # 窓ごとに分割
    print(Yi)

    for i in range(0, maxlag):
        Xi = X.iloc[:, i]  # ラグに合わせた列を選択
        Xi = window_df(Xi, window, by)  # 窓ごとに分割
        print(Xi)
        xcor = win_ccf(Xi, Yi)  # すべての窓について相互相関
        C.iloc[i, :] = xcor  # 出力データフレームの書き換え
        print(C)

    # 0からmaxlagまで：X列を固定、Y列を動かす
    Xi = X.iloc[:, maxlag]  # Yのフルサイズ列
    Xi = window_df(Xi, window, by)
    print(Xi)

    for i in range(0, maxlag + 1):
        Yi = Y.iloc[:, i]
        Yi = window_df(Yi, window, by)
        print(Yi)
        xcor = win_ccf(Xi, Yi)
        print(xcor)
        C.iloc[i + maxlag, :] = xcor

    t = list(np.arange(1, nx, round((nx / len(Xi.columns)), 2)))  # Timeの表現（何個の窓ができるのか）
    l = list(np.arange(-maxlag, maxlag + 1))           # ラグ

    # 結果を表として出力
    result = C
    result.columns = [str(n) for n in t]  # タイムを文字列としての列名に
    result.index = l                              # ラグをインデックスに
    print(result)

    # Seabornでヒートマップを作図
    # 一旦、縦長のデータフレームに変換する
    df_melt = C
    new_col = t  # タイムは数字にしないと意図した通りの順番にならない
    df_melt.columns = new_col
    df_melt["Lag"] = l
    df_melt = pd.melt(df_melt, id_vars=["Lag"], value_vars=new_col)  # ラグを基準に縦長にデータを変換
    print(df_melt)

print("End Process")
