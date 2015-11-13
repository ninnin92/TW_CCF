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
window = 21  # 何個の要素を持った窓にするか
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

ID = "H27-28"
exp = "demo"
tr = 1


base = pd.ExcelFile("time_analysis_Adult.xlsx")

df_base = base.parse("time", index_col="s")
data = df_base[df_base["ID"] == ID]
data_exp = data[data["exp"] == exp]
data_tr = data_exp[data_exp["trial_Num"] == tr]

data_tr = data_tr[data_tr["step"] > 2]
data_tr = data_tr[data_tr["error"] != 1]

data_L = data_tr[data_tr["L_Key"] == "L"].sort_values(by="step").reset_index()
data_R = data_tr[data_tr["R_Key"] == "R"].sort_values(by="step").reset_index()

data_x = pd.DataFrame({"L": data_L["Time"], "R": data_R["Time"]})
print(data_x)

# 対象になる２列を指定、列の長さ確認
x = data_x.iloc[:, 0]  # 列数で指定したいときはiloc、ixは挙動がちんぷんかんぷん
y = data_x.iloc[:, 1]

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

#print(C)

# 相互相関解析
# -maxlag ~ 0まで：Y列を固定、X列を動かす
Yi = Y.iloc[:, 0]  # Yのフルサイズ列
print(Yi)
Yi = window_df(Yi, window, by)

print(Yi)