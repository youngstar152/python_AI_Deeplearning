# -*- coding: utf-8 -*-
"""5_neural_network.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1coiJMtSo7zV9OWhjGf877JKX808diZ9J
"""

from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.neural_network import MLPClassifier
import numpy as np

digits = load_digits()
train_X, test_X, train_y, test_y = train_test_split(digits.data, digits.target, random_state=0, test_size=0.1)

# 特徴ベクトルを正規化
max_train_val = train_X.max()
train_X /= max_train_val
test_X /= max_train_val

import numpy as np

# シグモイド関数.
def sigmoid(h):
    return 1.0 / (1.0 + np.exp(-h))

# ベクトルの配列を拡張ベクトルの配列に変換する関数.
def extend(x_array):
    return np.hstack((np.ones((len(x_array), 1)), x_array))

# ラベルの配列を教師信号の配列に変換する関数.
def to_one_hot(y_array, class_num):
    return np.identity(class_num)[y_array]

class MyMLP:
    def __init__(self, hidden_unit_size, rho, loss_threshold):
        # 中間層のユニット数
        self.hidden_unit_size = hidden_unit_size
        # 学習係数
        self.rho = rho
        # 収束判定のしきい値
        self.loss_threshold = loss_threshold

        # シード値
        self.random_seed = 123

        # クラスの数（未学習時は0）
        self.c = 0
        # パターンの次元（未学習時は0）
        self.d = 0
        # 重みベクトルの配列（未学習時は空の配列）
        self.w_hid = np.zeros((0, 1))
        self.w_out = np.zeros((0, 1))

    # 学習用のメソッド
    def fit(self, x_array, y_array):
        # パターンの次元を記憶.
        self.d = len(x_array[0])
        # y_arrayの重複する要素を一つだけ残してできる配列の数を取得することでクラスの数を得る.
        self.c = len(np.unique(y_array))
        # パターンを拡張.
        train_X_ext = extend(x_array)
        # ラベルを教師信号に.
        one_hot_Y = to_one_hot(y_array, self.c)

     # 1. 入力層と中間層の重みを標準正規分布に従う乱数で初期化
        # 乱数生成器を用意.
        rand_gen = np.random.default_rng(self.random_seed)

        # 中間層の重みと出力層の重みの配列.
        # 便宜上, 転置させる（引数を入れ替えてもよいが, 乱数生成器によって生成される順番が異なってしまう）.
        self.w_hid = rand_gen.standard_normal((self.d + 1, self.hidden_unit_size)).T
        self.w_out = rand_gen.standard_normal((self.hidden_unit_size, self.c)).T

        # 収束するまで学習を行う.
        while True:
           for i, train_x_ext in enumerate(train_X_ext):
                one_hot_y = one_hot_Y[i]
      
                # 2-1. 順伝搬
                # 入力パターンから中間層の出力を計算
                g_inp = train_x_ext                
                # 入力層の出力と中間層の重みで線形和を計算を行って, 中間層の入力を得る.
                h_hid = np.dot(self.w_hid, g_inp)
                # 中間層の入力とシグモイド関数で中間層の出力を得る.
                g_hid = sigmoid(h_hid)
                # 中間層の出力から出力層の出力を計算
                h_out = np.dot(self.w_out, g_hid)                
                # 出力層の入力とシグモイド関数で出力層の出力を得る.
                g_out = sigmoid(h_out)                

                # 2-2. 逆伝搬              
                # 出力層のイプシロンの配列を得る.
                e_out = (g_out - one_hot_y) * g_out * (1.0 - g_out)
                # 出力層の重みを更新する.
                self.w_out -= np.multiply((self.rho * e_out).reshape((self.c, 1)), g_hid)
                # 中間層のイプシロンの配列を得る.
                e_hid = np.zeros(self.hidden_unit_size)
                w_out2 = self.w_out.T
                for j in range(self.hidden_unit_size):
                    e_hid[j] = np.dot(e_out, w_out2[j]) * g_hid[j] * (1.0 - g_hid[j])

                # 中間層の重みの配列を更新する.
                self.w_hid -= np.multiply((self.rho * e_hid).reshape((self.hidden_unit_size, 1)), g_inp)

        # 3. 収束判定
            # 二乗誤差の平均を取得する.
           error = self._get_error(train_X_ext, one_hot_Y)
           print(error)
            # 収束判定を行う.
           if error < self.loss_threshold:
                break

    # 評価用のメソッド.
    def predict(self, x_array):
        # 結果のリスト
        answer = []
        # パターンを拡張.
        x_array_ext = extend(x_array)
        # それぞれのパターンに対して評価を行う.
        for x in x_array_ext:
            # 個々のパターンの評価自体は_predict_singleで行う.
            answer.append(self._predict_single(x))
        # 結果を入れたリストをNumPyの配列に変換して返す.
        return np.array(answer)

    # 1つのパターンの評価を行うメソッド.
    def _predict_single(self, x):
       # 2-1の順伝搬と同様の計算で予測する
        g_inp = x
        h_hid = np.dot(self.w_hid, g_inp)
        g_hid = sigmoid(h_hid)
        h_out = np.dot(self.w_out, g_hid)
        g_out = sigmoid(h_out)

        box=[]
        # 予測の最大値を返す.
        box.append(g_out)
        return np.argmax(box)

    # 二乗誤差の平均を得るためのメソッド.
    def _get_error(self, x_ar, y_ar):
        # 全てのパターンに対して以下の配列を一度の取得する.
        # ・入力層の出力の配列
        g_inp_ar = x_ar
        # ・中間層の入力の配列
        h_hid_ar = np.dot(self.w_hid, g_inp_ar.T).T
        # ・中間層の出力の配列
        g_hid_ar = sigmoid(h_hid_ar)
        # ・出力層の入力の配列
        h_out_ar = np.dot(self.w_out, g_hid_ar.T).T
        # ・出力層の出力の配列
        g_out_ar = sigmoid(h_out_ar)
        # それぞれの出力層の出力の配列から教師信号を引いたものを要素とする配列を得る.
        buf = g_out_ar - y_ar

        # 二乗誤差の平均を返す.
        return np.sum(buf * buf) / (2 * len(x_ar))

models = []
models.append(MyMLP(hidden_unit_size=20, rho=1, loss_threshold=0.01)) # 自前MLPクラス
models.append(MLPClassifier(hidden_layer_sizes=20, batch_size=1))     # sklearnのMLPクラス

# 学習
for model in models:
    model.fit(train_X, train_y)

# 評価
all_results = []
for model in models:
    all_results.append(model.predict(test_X))

# 結果の表示
for results in all_results:
    print(accuracy_score(test_y, results))

# 同じ結果か確認
print(all_results[0] == all_results[1])

# 結果の保存
np.savetxt("results.csv", all_results, delimiter=',', fmt="%d")

