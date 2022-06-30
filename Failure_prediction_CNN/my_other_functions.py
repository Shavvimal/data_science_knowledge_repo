import pandas as pd
import numpy as np
from pyDeepInsight import ImageTransformer, LogScaler
import pickle

def read_and_transform_data():
    data = pd.read_csv("data_ready_for_learning_steps_new_0723.csv", parse_dates=True)
    line_dict = {chr(i): i - 65 for i in range(65, 71)}
    side_dict = {"LEFT": 1, "RIGHT": -1}
    data["Line_num"] = [line_dict[i] for i in data.line]
    data["Side_num"] = [side_dict[i] for i in data.Side]
    data["Y_coord"] = (
        data["press"]
        + (data["Line_num"].apply(lambda x: x % 2) * 2 - 1) * data["Side_num"] * 0.2
    )
    data["ActualEndTimestamp"] = pd.to_datetime(data["ActualEndTimestamp"])
    data["ActualStartTimestamp"] = pd.to_datetime(data["ActualStartTimestamp"])
    data["Load_num"] = [1 if load == "X" else 0 for load in data["Load"]]
    speed_dict = {
        "L": 75,
        "M": 81,
        "N": 87,
        "Q": 100,
        "R": 112,
        "S": 106,
        "T": 118,
        "U": 124,
        "H": 130,
        "V": 149,
        "Z": 150,
        "W": 168,
        "Y": 186,
        "(Y)": 187,
    }  # source: https://wheelzine.com/tire-speed-rating-codes
    data["Speed_num"] = [speed_dict[i] for i in data["Speed"]]
    data["Press_cat"] = data["PressNo"] + data["Side"]
    # indexing the bladders
    index_of_last_cycles = np.where(
        (data[1:]["Lifetime"].values > data[:-1]["Lifetime"].values)
        | (data[1:]["Press_cat"].values != data[:-1]["Press_cat"].values)
    )[0]
    data["Bladder_index"] = 0
    for i in index_of_last_cycles:
        data[(i + 1) :]["Bladder_index"] = data[(i + 1) :]["Bladder_index"] + 1
    code_plan_dict = {
        "18/2 H84E.": 350,
        "15/5 H74G.": 600,
        "..........": 380,
        "15/2 H54L.": 600,
        "15/2 H74G.": 600,
        "15/2 74G..": 600,
        "15/2 H64L.": 600,
        "15/0 H64L.": 350,
        "15/2H54L..": 600,
        "15/2H64L..": 600,
        "15/1 H74L.": 350,
        "15/0H64L..": 350,
        "18/1 H84G.": 350,
        "18/2 H86E.": 350,
        "15/2 H74E.": 600,
        "15/5 H76E.": 600,
    }
    data["PlannedLife"] = [code_plan_dict[x] for x in data["BladderCode"]]
    feature_names = [
        [
            "Duration",
            "BladderCount",
            "Width",
            "AspectRatio",
            "RimDiameter",
            "Load_num",
            "Speed_num",
            "Number of steps",
            "Cycletime_target",
            "PlannedLife",
        ]
    ]
    X = np.array(data[feature_names[0]])
    X = np.concatenate(
        (X, np.array(pd.get_dummies(data[["Pattern", "Press_cat"]]))), axis=1
    )
    feature_names.append(pd.get_dummies(data[["Pattern", "Press_cat"]]).columns)
    X = np.concatenate((X, np.array(data.iloc[:, 32:-7])), axis=1)
    feature_names.append(data.columns[32:-7])
    feature_names = [x for y in feature_names for x in y]
    y = np.array(data["Lifetime"])
    y = np.array([int(i <= 4) for i in y])
    col_mean = np.nanmean(X, axis=0)
    inds = np.where(np.isnan(X.astype(float)))
    X[inds] = np.take(col_mean, inds[1])

    return data, X, y


def create_images(X_train, X_test, pixel_size):
    ln = LogScaler()
    X_train_norm = ln.fit_transform(X_train)
    X_test_norm = ln.transform(X_test)
    it = ImageTransformer(
        feature_extractor="tsne", pixels=pixel_size, random_state=1701, n_jobs=-1
    )
    mat_train = it.fit_transform(X_train_norm)
    mat_test = it.transform(X_test_norm)

    outfile = open("ImageTransformer", "wb")
    pickle.dump(it, outfile)
    outfile.close()

    outfile = open("LogScaler", "wb")
    pickle.dump(ln, outfile)
    outfile.close()

    return mat_train, mat_test
