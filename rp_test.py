#!/usr/bin/env python
# coding:utf-8

import numpy as np
import pandas as pd
import scipy.stats as stats
import itertools as IT

A = pd.DataFrame([[1, 5, 2], [2, 4, 4], [3, 3, 1], [4, 2, 2], [5, 1, 4]],
                 columns=['A', 'B', 'C'], index = [1, 2, 3, 4, 5])

print("A_")
print(A)

for col1, col2 in IT.combinations(A.columns, 2):
    print("col1_")
    print(col1)
    print("col2_")
    print(col2)

    def tau(idx):
        B = A[[col1, col2]].iloc[idx]
        print("B_")
        print(B)
        return stats.kendalltau(B[col1], B[col2])[0]

    A[col1 + col2] = pd.rolling_apply(np.arange(len(A)), 3, tau)

print("A__")
print(A)