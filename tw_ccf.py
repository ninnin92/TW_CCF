#!/usr/bin/env python
# coding:utf-8
# env: Python3.3

import numpy as np
import scipy as sp
import matplotlib as mpl
import pandas as pd


################################################
#  宣言
################################################
maxlag = 3
window = 3
by     = 1
cnt    = 1
n_overlap = window - by
################################################
#  関数
################################################


def buffer(s, lag):
    s_list = []

    for i in range(lag + 1):
        s_shift = s.shift(i).fillna(0)
        s_shift.columns = [i]
        s_list.append(s_shift)

    df = pd.concat(s_list, axis=1)

    return df


def window_df(s, window, by):
    ns = len(s)




################################################
#  メイン処理
################################################

if __name__ == '__main__':
    data = pd.read_csv("test.csv")

    # 対象になる２列を指定、列の長さ確認
    x = data.ix[:, 0]
    y = data.ix[:, 1]

    nx = len(x)
    ny = len(y)

    print(nx, ny)

    # lag分ずらしたDfの準備
    X = buffer(x, maxlag).sort_index(axis=1, ascending=False)
    Y = buffer(y, maxlag)

    print(X)
    print(Y)

    # 出力データフレームを仮作成
    C = pd.DataFrame(0, index=np.arange(maxlag * 2 + 1),
                     columns=np.arange((nx - n_overlap) / (window - n_overlap)))
    print(C)

    # 相互相関解析
    # -maxlag ~ 0まで
    hoge = Y.ix[:, 0]
    print(hoge)
    print(type(hoge))


    # 0からmaxlagまで



    #t = ()
    l = np.arange(-maxlag, maxlag)
