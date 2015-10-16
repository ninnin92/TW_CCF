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

################################################
#  関数
################################################

################################################
#  メイン処理
################################################
def hoge(x, y):
    return x + y

if __name__ == '__main__':
    foo = pd.DataFrame({"A": range(1, 11), "B": range(2, 12)})
    print(foo)

    test = test = pd.rolling_apply(foo, 3, hoge, 1, center=True)
    print(test)
