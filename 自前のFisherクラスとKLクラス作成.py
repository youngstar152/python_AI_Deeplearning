# -*- coding: utf-8 -*-
"""6_feature_space.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1mwf0G8_3fWpKX0pnXK3EhBJWhTrAufDE
"""

from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import numpy as np

# データセットの準備
digits = load_digits(n_class=2)
train_X, test_X, train_y, test_y = train_test_split(digits.data, digits.target, random_state=0, test_size=0.1)

class MyKL:
    def __init__(self, n_components,tau):
        self.n_components = n_components
        self.tau = tau
        self.trans_mat = None

    def fit(self, train_X):
        # 元の次元数を取得
        d = len(train_X[0])

        # 特徴ベクトルの分散共分散行列を計算
        var_mat = np.cov(train_X, rowvar=False, bias=True)

        # outer関数を使って計算するver.
        #var_mat = np.zeros((d, d))
        #means = np.mean(train_X, axis=0)
        #for train_x in train_X:
        #    diff = train_x - means
        #    var_mat += np.outer(diff, diff)
        #var_mat /= len(train_X)

        # 分散共分散行列から固有値及び固有値ベクトルを計算し，固有値の大きい順に並び替え
        eigenvalues, eigenvectors = np.linalg.eig(var_mat)
        sorted_idx = np.argsort(-eigenvalues)
        eigenvalues = eigenvalues[sorted_idx]
        eigenvectors = eigenvectors.T[sorted_idx]
        print(sorted_idx)
        length = len(sorted_idx)
        sum=0
        sum1=0
        kiyo=0
        if self.n_components is None:
          for b in range(length):
            sum1 +=eigenvalues[b]
          for a in range(length):
            sum +=eigenvalues[a]
            kiyo = sum/sum1
            if kiyo>=self.tau:
              self.n_components=a+1
              break
        
        else:
          # 変換後の次元.
            n_components = self.n_components
        # 上位n_components個の固有値ベクトルを変換行列として抽出
        self.trans_mat = eigenvectors[: self.n_components]

    def transform(self, test_X):
        # 特徴ベクトルを変換行列により次元削減し，返す
        return test_X @ self.trans_mat.T

# 自前のKLクラスを用いて特徴量の次元を削減
kl = MyKL(n_components=None, tau=0.95)
kl.fit(train_X)
transformed_train_X = kl.transform(train_X)
transformed_test_X = kl.transform(test_X)

# 削減後の次元数を出力
print("Compressed dimension size:", len(transformed_train_X[0]))

class MyFisher:
    def __init__(self):
        self.w = None  # 1次元空間への変換ベクトル
        self.mean = None  # 変換後の期待値

        self.c = 0
        self.d = 0

    def fit(self, x_array, y_array):
        self.d = len(x_array[0])
        self.c = len(np.unique(y_array))
        # クラス0及び1の期待値ベクトルを計算
        #正解ラベルでリスト分け
        x1_array = []
        x2_array = []
        n = len(x_array)
        for i in range(n):
            x = x_array[i]
            if y_array[i]:
                x2_array.append(x)
            else:
                x1_array.append(x)

        x1_array = np.array(x1_array)
        x2_array = np.array(x2_array)

        m = np.mean(x_array, axis=0)
        m1 = np.mean(x1_array, axis=0)
        m2 = np.mean(x2_array, axis=0)

        # クラス内変動行列を計算
        S1 = np.zeros((self.d, self.d))
        for i in range(len(x1_array)):
            buf = np.reshape(x1_array[i], (self.d, 1))
            #print(buf.shape)
            S1 += np.dot(buf, buf.T)
        S2 = np.zeros((self.d, self.d))
        for i in range(len(x2_array)):
            buf = np.reshape(x2_array[i], (self.d, 1))
            S2 += np.dot(buf, buf.T)

        Sw = S1 + S2

        # 各期待値ベクトル及びクラス内変動行列から変換ベクトルを計算し，正規化
        self.w = np.dot(np.linalg.inv(Sw), m1 - m2)
        self.w /= np.linalg.norm(self.w)
        self.mean = np.dot(self.w, m)

        #self.mean = np.dot(np.reshape(self.w, (1, len(self.w))), m)

    # 評価用のメソッド.
    def predict(self, x_array):
        # 結果をいれるリスト
        answer = []
        # それぞれのパターンに対して評価を行う.
        for x in x_array:
            # 個々のパターンの評価自体は_predict_singleで行う.
            answer.append(self._predict_single(x))
        # 結果を入れたリストをNumPyの配列に変換して返す.
        return np.array(answer)

    def _predict_single(self, x):
        if(np.dot(self.w, x) < self.mean):
          a=1
        else:
          a=0
        return a

# 自前のFisherクラスを用いて分類
model = MyFisher()
model.fit(transformed_train_X, train_y)
results = model.predict(transformed_test_X)

# 結果の表示
print("Accuracy score:", accuracy_score(results, test_y))
print(results)
print(test_y)
print("Correctness of prediction:")
print(results == test_y)

# 結果の保存
np.savetxt("results.csv", results, delimiter=',', fmt="%d")

