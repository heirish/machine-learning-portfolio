import random
import itertools
import math
import numpy as np
import pandas as pd
from keras.models import Sequential
from keras import optimizers
from keras.layers import *

blue_ball_list = range(1, 33)
red_ball_list = range(1, 16)


# 无重复，用于测试
def random_generate():
    numbers = sorted(random.sample(blue_ball_list, 6))
    red_number = random.sample(red_ball_list, 1)
    while red_number in numbers:
        red_number = random.sample(red_ball_list, 1)
    numbers.extend(red_number)
    return numbers


# 有重复，用于训练
def get_all_possible():
    blue_combinations = itertools.combinations(blue_ball_list, 6)
    df = pd.DataFrame(columns=["number", "blue_ball"])
    index = 0
    for combination in blue_combinations:
        for i in red_ball_list:
            numbers = list(combination)
            numbers.append(i)
            df.loc[index] = [numbers, i]
            index += 1

        if index % 100 == 0:
            print(index)
            break
    return df


def nCr(n, r):
    f = math.factorial
    return f(n) / f(r) / f(n - r)


def prepare_train_data(lucky_number_file):
    df_lucky = pd.read_csv(lucky_number_file)
    df_lucky["luck_number"] = df_lucky[
        ["bonus_no0", "bonus_no1", "bonus_no2", "bonus_no3", "bonus_no4", "bonus_no5", "bonus_no6"]].values.tolist()
    df_lucky["number"] = df_lucky["luck_number"]
    df_lucky["lucky"] = 1
    df_lucky.rename(columns={"bonus_no6": "blue_ball"})
    print("lucky df rows:", df_lucky.shape[0])
    df_lucky["number_str"] = df_lucky["number"].astype(str)
    print("duplicated rows:", df_lucky[df_lucky.duplicated(["number_str"], keep=False)])


    # combine two df
    df_all = pd.DataFrame(columns=["number", "lucky"])
    df_got = get_all_possible()
    df_all["number"] = df_got["number"]
    df_all["blue_ball"] = df_got["blue_ball"]
    df_all["lucky"] = 0
    print("df all rows:", df_all.shape[0])
    df_all = df_all.append(df_lucky, ignore_index=True)
    print("df all rows after append: ", df_all.shape[0])

    # delete duplicates
    df_all["number_str"] = df_all["number"].astype(str)
    df_all.drop_duplicates("number_str", keep="last", inplace=True)
    df_all.drop(["number_str"], axis=1)
    print("df all rows after drop duplicated: ", df_all.shape[0])
    print("df all rows that are lucky: ", df_all[df_all["lucky"] == 1].shape[0])

    return df_all["number"].values.tolist(), df_all["lucky"].values.tolist()


def split_data(X, y, test_rate=0.2, random_seed=1234):
    random.seed(random_seed)
    random.shuffle(X)
    random.shuffle(y)
    test_size = math.floor(len(X) * test_rate)
    return X[test_size:], y[test_size:], X[0:test_size], y[0:test_size]


def create_model():
    model = Sequential()
    model.add(Dense(4, input_dim=7, activation="relu"))
    model.add(Dense(2, activation="relu"))
    model.add(Dense(1, activation="sigmoid"))
    return model

if __name__ == "__main__":
    print(nCr(33, 7))
    print(nCr(33, 6) * 16)

    X_list, y_list = prepare_train_data("./data_out/lottery.csv")
    X, y = np.array(X_list), np.array(y_list)
    X_train, y_train, X_validate, y_validate = split_data(X, y)
    print(X_train[:10], y_train[:10])
    print(X_validate[:10], y_validate[:10])

    model = create_model()
    rmsp = optimizers.RMSprop(lr=0.00001)
    model.compile(optimizer=rmsp, loss="binary_crossentropy", metrics=["accuracy"])
    model.fit(X_train, y_train, epochs=150, batch_size=10)
    scores = model.evaluate(X_validate, y_validate)
    print("\n%s: %.2f%%" % (model.metrics_names[1], scores[1] * 100))