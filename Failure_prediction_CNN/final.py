from my_other_functions import *
from my_models import *
import matplotlib.pyplot as plt
from sklearn.metrics import (
    balanced_accuracy_score,
    confusion_matrix,
)

pixel_size = 64
batch_size = 64
epochs = 10

data, X, y = read_and_transform_data()

# Print number of bladders per press:
# print(data[["Press_cat", "Bladder_index"]].groupby("Press_cat").nunique().sort_values("Bladder_index"))

# Create test and train conditions
test_bladders = data[
    [
        x in ["C_10RIGHT", "D_11RIGHT", "C_13RIGHT", "A_10RIGHT"]
        for x in data["Press_cat"]
    ]
]["Bladder_index"].unique()
condition_train = [x not in test_bladders for x in data["Bladder_index"]]
condition_test = [x in test_bladders for x in data["Bladder_index"]]
# Separate data
X_train = X[condition_train]
y_train = y[condition_train]
X_test = X[condition_test]
y_test = y[condition_test]

mat_train, mat_test = create_images(X_train, X_test, pixel_size)

# Set learning model
model = linear_cnn()
# Train
model.fit(
    mat_train,
    y_train,
    epochs=10,
    verbose=1,
    validation_split=0.2,
    workers=-1,
    class_weight={1: sum(y_train == 0), 0: sum(y_train == 1)},
)

# Save model
model.save("model")

# Create prediction
y_pred = model.predict(mat_test)[:, 0]
for i in np.where(np.isnan(y_pred))[0]:
    y_pred[i] = (y_pred[i - 1] + y_pred[i + 1]) / 2

plt.figure(figsize=(18, 6))
plt.plot(y_pred, label="prediction")
plt.show()

# Result table
results = pd.DataFrame({"prediction": y_pred})
results["Bladder_index"] = data[condition_test]["Bladder_index"].values
results["Press_cat"] = data[condition_test]["Press_cat"].values
results["label"] = y_test

# Moving average on predictions
window_size = 3
ma_vector = []
for id, df in results.groupby("Bladder_index"):
    for w in range(window_size):
        ma_vector.append(df["prediction"].iloc[w])
    for i in range(window_size, len(df)):
        ma_vector.append(
            sum(df["prediction"].iloc[(i - window_size) : (i)]) / window_size
        )
results["moving_avg"] = ma_vector

# Monotone filter
monotone_vector = []
for id, df in results.groupby("Bladder_index"):
    monotone_vector.append(fit_monotone_increasing(df["prediction"].values))
monotone_vector = [x for y in monotone_vector for x in y]
results["monotone"] = monotone_vector

plt.figure(figsize=(18, 6))
plt.plot(y_pred, label="prediction")
plt.plot(ma_vector, label="moving_avg")
plt.plot(monotone_vector, label="monotone")
plt.show()


# Thresholds
def my_own_scoring(y_true, y_prob, th):
    y_pred = [int(p >= th) for p in y_prob]
    ACC = balanced_accuracy_score(y_true, y_pred)
    return ACC


thresholds = {}
for press, df_press in results.groupby("Press_cat"):
    th_list = df_press["monotone"].unique()
    y_true = df_press["label"].values
    y_prob = df_press["monotone"].values
    scores = np.array([my_own_scoring(y_true, y_prob, th) for th in th_list])
    best_th = th_list[np.argmax(scores)]
    thresholds[press] = best_th

results["class"] = [
    1 if val >= thresholds[press] else 0
    for val, press in zip(results["monotone"], results["Press_cat"])
]

print(thresholds)
for press, df_press in results.groupby("Press_cat"):
    print(f"{press}:")
    print(confusion_matrix(df_press["label"], df_press["class"]))
