#!/usr/bin/env python
# coding:utf-8
# env: Python3.3

import sys
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import math

### 先行研究に従ったもの ###

################################################
#  宣言
################################################
option = "C"
maxlag = 1  # 最大のラグ数（正負にこの数だけズラす）
window = 10  # 何個の要素を持った窓にするか
by     = 1      # 窓から窓へは何個ずつ増えるか（いくつ被るのを許容するか）
n_overlap = window - by

################################################
#  関数
################################################


def tw_ccf(d1, d2, maxlag, window, by):

    n = 0
    x = d1
    y = d2

    nx = len(x)
    ny = len(y)

    lag = list(np.arange(-maxlag, maxlag + 1))    # ラグ
    #print(lag)
    i_list = list(range(maxlag + 1, nx - maxlag - window + 1))
    #print(i_list)
    C = pd.DataFrame(0, index=np.arange(maxlag * 2 + 1),
                                 columns=np.arange(len(i_list)))

    for l in lag:
        #print(l)
        cor_list = []

        if l <= 0:
            for i in i_list:
                X = x[i:i + window]
                Y = y[i + l:i + window + l]
                #print(X)
                #print(Y)

                Xm = X.mean(axis=0)
                Ym = Y.mean(axis=0)
                #print(Xm)
                #print(Ym)

                Xsd = X.std(ddof=0)
                Ysd = Y.std(ddof=0)
                #print(Xsd)
                #print(Ysd)

                Z = [(Xi - Xm) * (Yi - Ym) / (Xsd * Ysd) for Xi, Yi in zip(list(X), list(Y))]
                #print(sum(Z))
                r = (1 / window) * sum(Z)
                #print(r)
                cor_list.append(r)

        if l > 0:
            for i in i_list:
                X = x[i - l:i + window - l]
                Y = y[i :i + window]
                #print(X)
                #print(Y)

                Xm = X.mean(axis=0)
                Ym = Y.mean(axis=0)
                #print(Xm)
                #print(Ym)

                Xsd = X.std(ddof=0)
                Ysd = Y.std(ddof=0)
                #print(Xsd)
                #print(Ysd)

                Z = [((Xi - Xm) * (Yi - Ym)) / (Xsd * Ysd) for Xi, Yi in zip(list(X), list(Y))]
                #print(sum(Z))
                r = (1 / window) * sum(Z)
                #print(r)
                cor_list.append(r)

        #print(C)
        #print(cor_list)
        C.iloc[n, :] = cor_list
        n += 1

    if len(cor_list) < 2:
        # print(len(cor_list))
        cor_list = cor_list[0]
        # print("hoge")

    return(C)


def heatmap_show(df, name, ex, trial, path, first):
    sns.set(style="white")  # テーマ
    f, ax = plt.subplots(figsize=(16, 9))  # Figサイズ
    cmap = sns.diverging_palette(220, 10, as_cmap=True)  # カラーパレット
    sns.heatmap(df, square=True, cmap=cmap, linewidths=.5, vmax=1, vmin=-1,
                          cbar_kws={"shrink": 0.6}, ax=ax)

    if first == "L":
        focus = "    A - [C] : 0    C - [A] : -1"
    else:
        focus = "    C - [A] : 0    A - [C] : 1"

    title = "Windowed Xcorr  _  " + name + "-" + ex + "-" + trial + "\n" + "first:  " + first + focus
    plt.title(title , fontsize=24, y=1.08)
    plt.xlabel("Time", fontsize=20, labelpad=20)  # Xのラベルサイズ
    plt.ylabel("Lag", fontsize=20, labelpad=20)  # Yのラベルサイズ
    plt.tick_params(labelsize=16)

    cax = plt.gcf().axes[-1]
    cax.tick_params(labelsize=16, pad=10)

    plt.savefig("fig_" + path + "/tw_ccf_" + name + "-" + ex + "-" + trial + ".png")
    #plt.show()


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

    if option == "A":
        base = pd.ExcelFile("time_analysis_Adult.xlsx")
        outpath = "adult"
    elif option == "C":
        base = pd.ExcelFile("time_analysis.xlsx")
        outpath = "child"
    else:
        sys.exit()

    # データ読み込み
    df_base = base.parse("time", index_col="s")
    ID_list    = set(df_base["ID"].tolist())  # メインファイルのIDリストを獲得して、重複削除
    df_sum = pd.DataFrame()

    for ID in ID_list:
        print("Run  " + ID)
        data = df_base[df_base["ID"] == ID]
        age = data["age"].head(1).item()
        sex = data["sex"].head(1).item()

        for exp in ["demo", "indivi", "joint", "prac"]:
            #print(exp)
            #print(data["exp"])
            data_exp = data[data["exp"] == exp]
            #print(data_exp)
            if data_exp.empty:
                continue
            else:
                print(exp)

            for tr in range(1, 5):
                data_tr = data_exp[data_exp["trial_Num"] == tr]
                tr = str(tr)
                if data_tr.empty:
                    continue
                else:
                    print(tr)

                # 前処理
                # 今はエラーを除外して分析、エラーを解析するなら複製データがいるかも
                # 余分なものを削除、エラー関係のも
                data_tr = data_tr[data_tr["step"] > 0]
                data_tr = data_tr[data_tr["error"] != 1]

                data_L = data_tr[data_tr["L_Key"] == "L"].sort_values(by="step").reset_index()
                data_R = data_tr[data_tr["R_Key"] == "R"].sort_values(by="step").reset_index()

                if data_L["step"].head(1).item() % 2 != 0:
                    first_turn = "L"
                else:
                    first_turn = "R"

                data_x = pd.DataFrame({"L": data_L["Time"], "R": data_R["Time"]})

                #print(data)


                # 対象になる２列を指定、列の長さ確認
                x = data_x.iloc[:, 0]  # 列数で指定したいときはiloc、ixは挙動がちんぷんかんぷん
                y = data_x.iloc[:, 1]

                #print(x)
                #print(y)

                nx = len(x)
                ny = len(y)

                # 出力データフレームを仮作成

                result = tw_ccf(x, y, maxlag, window, by)

                t = list(np.arange(1, nx, round((nx / len(result.columns)), 2)))  # Timeの表現（何個の窓ができるのか）
                l = list(np.arange(-maxlag, maxlag + 1))           # ラグ

                # 結果を表として出力
                result.columns = [str(n) for n in t]  # タイムを文字列としての列名に
                result.index = l                              # ラグをインデックスに
                result.fillna(0)
                print(result)

                # Seabornでヒートマップを作図
                # 一旦、縦長のデータフレームに変換する
                df_melt = result
                new_col = t  # タイムは数字にしないと意図した通りの順番にならない
                df_melt.columns = new_col
                df_melt["Lag"] = l
                df_melt = pd.melt(df_melt, id_vars=["Lag"], value_vars=new_col)  # ラグを基準に縦長にデータを変換
                df_melt = df_melt.assign(ID=ID, exp=exp, trial_num=tr, age=age, sex=sex, first_turn=first_turn)
                #print(df_melt)
                df_sum = pd.concat([df_sum, df_melt])
                df_melt.to_csv("csv_" + outpath + "/df_ccf_" + ID + "-" + exp + "-" + tr + ".csv", index=False)

                # そのあと、ピボットテーブルに再変換
                df_plot = pd.pivot_table(data=df_melt, values="value", columns="variable", index="Lag", aggfunc=np.mean)
                #print(df_plot)

                # ヒートマップ描画、保存
                heatmap_show(df_plot, ID, exp, tr, outpath, first_turn)
                plt.close()

    df_sum.to_csv("cross-corr-" + outpath + "-2.csv", index=False)
    print("End Process")
