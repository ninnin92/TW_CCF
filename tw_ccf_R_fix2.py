#!/usr/bin/env python
# coding:utf-8
# env: Python3.3

import sys
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import math

### Rでのccfに従ったもの（どっかの大学のページで解説されているものと同一） ###
### エラーターンのペアを全削除するよ

################################################
#  宣言
################################################
option = "C"
maxlag = 1  # 最大のラグ数（正負にこの数だけズラす）

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


def tw_ccf(data1, data2, maxlag):
    print(data1)
    print(data2)
    lag = list(np.arange(-maxlag, maxlag + 1))    # ラグ
    cnt_list = []
    # print(lag)
    cor = pd.DataFrame(0, index=np.arange(maxlag * 2 + 1), columns=np.arange(1))

    ix = 0
    for l in lag:
        print("Lag :::: " + str(l))
        if l == -1:
            # -1の時の処理

            data1_prm = data1.head(1).reset_index(drop=True)
            data2_prm = data2.tail(1).reset_index(drop=True)
            dt_prm = pd.concat([data1_prm, data2_prm], axis=1)
            #print(dt_prm)

            data1m = data1.tail(-1).reset_index(drop=True)
            data2m = data2.head(-1).reset_index(drop=True)

            dt = pd.concat([data1m, data2m], axis=1)
            dt = dt.loc[dt["turnEL"]  != 1, :]
            dt = dt.loc[dt["turnER"]  != 1, :]
            print(dt)
            dt_prm = pd.concat([dt, dt_prm])

        elif l == 0:
            dt = pd.concat([data1, data2], axis=1)
            dt = dt.loc[dt["turnEL"]  != 1, :]
            dt = dt.loc[dt["turnER"]  != 1, :]
            print(dt)
            dt_prm = dt.copy()

        elif l == 1:
            data1_prm = data1.tail(1).reset_index(drop=True)
            data2_prm = data2.head(1).reset_index(drop=True)
            dt_prm = pd.concat([data1_prm, data2_prm], axis=1)

            data1p = data1.head(-1).reset_index(drop=True)
            data2p = data2.tail(-1).reset_index(drop=True)

            dt = pd.concat([data1p, data2p], axis=1)
            dt = dt.loc[dt["turnEL"]  != 1, :]
            dt = dt.loc[dt["turnER"]  != 1, :]
            print(dt)
            dt_prm = pd.concat([dt, dt_prm])

        print(dt_prm)

        data_x = pd.DataFrame({"L": dt["TimeL"], "R": dt["TimeR"]})
        data_prm = pd.DataFrame({"L": dt_prm["TimeL"], "R": dt_prm["TimeR"]})
        print(data_x)
        #print(data_prm)

        # 対象になる２列を指定、列の長さ確認
        x = data_x.iloc[:, 0]  # 列数で指定したいときはiloc、ixは挙動がちんぷんかんぷん
        y = data_x.iloc[:, 1]
        # パラメータ用
        prm_x = data_prm.iloc[:, 0]  # 列数で指定したいときはiloc、ixは挙動がちんぷんかんぷん
        prm_y = data_prm.iloc[:, 1]

        nx = len(x)
        cnt_list.append(nx)
        ny = len(y)

        Xm = prm_x.mean(axis=0)
        Ym = prm_y.mean(axis=0)

        Xsd = prm_x.std(ddof=0)
        Ysd = prm_y.std(ddof=0)

        # print(l)
        c = 0

        for n in range(0, nx):
            c = c + (x.iloc[n] - Xm) * (y.iloc[n] - Ym)

        c = c / nx
        r = c / (Xsd * Ysd)

        cor.iloc[ix, :] = r
        ix += 1

    cor = pd.Series(cor.values.flatten())
    return(cor, cnt_list)


################################################
#  メイン処理
################################################

if __name__ == '__main__':

    print("Run Process")
    print("------------------")
    print("Option:  " + option)
    print("Maxlag:  " + str(maxlag))
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
            # print(exp)
            # print(data["exp"])
            data_exp = data[data["exp"] == exp]
            # print(data_exp)
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
                # data_tr = data_tr[data_tr["error"] != 1]

                turnE_list = list(set(list(data_tr.ix[data_tr["error"] == 1, :]["step"])))
                print(turnE_list)

                data_tr = data_tr.assign(turnE=0)
                data_tr_te = pd.DataFrame()
                for sp in range(1, 43):
                    if sp in turnE_list:
                        dt = data_tr.loc[data_tr["step"] == sp, :]
                        dt["turnE"] = 1
                        data_tr_te = pd.concat([dt, data_tr_te])
                    else:
                        dt = data_tr.loc[data_tr["step"] == sp, :]
                        data_tr_te = pd.concat([dt, data_tr_te])

                data_tr = data_tr_te.copy()

                data_L = data_tr[data_tr["L_Key"] == "L"].sort_values(by="step").reset_index()
                data_R = data_tr[data_tr["R_Key"] == "R"].sort_values(by="step").reset_index()

                if data_L["step"].head(1).item() % 2 != 0:
                    first_turn = "L"
                else:
                    first_turn = "R"

                data_L = data_L.loc[:, ["Time", "error", "step", "turnE"]]
                data_R = data_R.loc[:, ["Time", "error", "step", "turnE"]]
                data_L = data_L.rename(columns={"Time": "TimeL", "error": "errorL", "step": "stepL", "turnE": "turnEL"})
                data_R = data_R.rename(columns={"Time": "TimeR", "error": "errorR", "step": "stepR", "turnE": "turnER"})

                data_L = data_L[data_L["errorL"] != 1].reset_index(drop=True)
                data_R = data_R[data_R["errorR"] != 1].reset_index(drop=True)


                # 出力データフレームを仮作成
                dfC = pd.DataFrame(0, index=np.arange(maxlag * 2 + 1),
                                   columns=np.arange(1))

                ccf, cnt_list = tw_ccf(data_L, data_R, maxlag)
                # print(ccf)
                dfC.iloc[:, 0] = ccf

                # print(dfC)
                result = dfC

                t = 1  # Timeの表現（何個の窓ができるのか）
                l = list(np.arange(-maxlag, maxlag + 1))           # ラグ

                # 結果を表として出力
                result.columns = ["1"]  # タイムを文字列としての列名に
                result.index = l                              # ラグをインデックスに
                result.fillna(0)
                print(result)

                # Seabornでヒートマップを作図
                # 一旦、縦長のデータフレームに変換する
                df_melt = dfC.copy()
                new_col = [1]  # タイムは数字にしないと意図した通りの順番にならない
                df_melt.columns = new_col
                df_melt["Lag"] = l
                df_melt = pd.melt(df_melt, id_vars=["Lag"], value_vars=new_col)  # ラグを基準に縦長にデータを変換
                df_melt = df_melt.assign(ID=ID, exp=exp, trial_num=tr, age=age, sex=sex, first_turn=first_turn, cnt=cnt_list)
                # print(df_melt)
                df_sum = pd.concat([df_sum, df_melt])

    df_sum = df_sum.fillna(0)
    df_sum.to_csv("cross-corr-" + outpath + "-R_fix2.csv", index=False)
    print("End Process")
