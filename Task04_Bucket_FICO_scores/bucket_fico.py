import numpy as np
import numpy.typing as npt

from typing import List

def error(a: int, b: int, x: npt.ArrayLike) -> float:
    """0<=a,b<n"""
    return np.var(x[a:b+1])

def find_bucket(x: npt.ArrayLike, n: int) -> List[int]:

    x = np.sort(x)
    N = len(x)

    dp = np.zeros((N, n))
    mini = np.zeros((N, n))


    for j in range(1, n):
        for i in range(N):
            fico_mini = np.inf
            x_mini = 0
            for k in range(j-1, i):
                res = dp[k][j-1] + error(k+1, i)
                if res < fico_mini:
                    fico_mini = res
                    x_mini = x[k]
            mini[i][j] = x_mini
            dp[i][j] = fico_mini

    # Reconstruction de la liste des indices L
    L = []
    nb_points = N # au début n points à traiter
    for t in range(1, n+1):
        L.append(mini[nb_points, n-t])
        nb_points = mini[nb_points, n-t]

    return L
                

