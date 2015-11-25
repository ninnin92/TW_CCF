#!/usr/bin/env python
# coding:utf-8
# env: Python3.3

import sys
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
window = 6  # 何個の要素を持った窓にするか
by     = 1      # 窓から窓へは何個ずつ増えるか（いくつ被るのを許容するか）
n_overlap = window - by

################################################
#  関数
################################################


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
    df = pd.DataFrame({"A": [1, 3, 5, 6, 5, 3, 5, 2, 2, 2, 1, 12, 22, 24, 8, 1, 7, 8, 9, 13],
                       "B": list(range(21, 41))})
    print(df)

    # 対象になる２列を指定、列の長さ確認
    x = df.iloc[:, 0]  # 列数で指定したいときはiloc、ixは挙動がちんぷんかんぷん
    y = df.iloc[:, 1]

    #print(x)
    #print(y)

    nx = len(x)
    ny = len(y)



print("End Process")
