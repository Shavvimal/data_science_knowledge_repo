from tensorflow.keras import Input, Model, Sequential
from tensorflow.keras.layers import (
    Conv2D,
    MaxPooling2D,
    Concatenate,
    Activation,
    Dropout,
    Flatten,
    Dense,
    BatchNormalization,
    ReLU,
)
import tensorflow as tf
from pulp import LpContinuous, LpVariable, LpProblem, LpMinimize, lpSum, value

padding_type = "valid"


def linear_cnn():

    model = Sequential()

    model.add(Conv2D(16, 3, 3, activation="relu"))
    model.add(BatchNormalization())
    model.add(ReLU())
    model.add(MaxPooling2D(pool_size=(2, 2)))
    model.add(Dropout(0.2))

    model.add(Flatten())
    model.add(Dense(128, activation="relu"))
    model.add(Dense(1, activation="sigmoid"))

    model.compile(
        loss="binary_crossentropy",
        optimizer="adam",
        metrics=["accuracy", tf.keras.metrics.Precision(), tf.keras.metrics.Recall()],
    )

    return model


def parallel_cnn(nb_filters, kernel_size, input_shape, pool_size):
    # parallel cnn
    no_parallel_filters = len(kernel_size)
    # create seperate model graph for parallel processing with different filter sizes
    inp = Input(shape=input_shape)
    convs = []
    for k_no in range(no_parallel_filters):
        conv = Conv2D(
            nb_filters[k_no],
            kernel_size[k_no][0],
            kernel_size[k_no][1],
            activation="relu",
            padding=padding_type,
            # input_shape=input_shape,
        )(inp)
        batchnorm = BatchNormalization()(conv)
        act = Activation(activation="relu")(batchnorm)
        pool = MaxPooling2D(pool_size=pool_size, padding=padding_type)(act)

        conv = Conv2D(
            nb_filters[k_no],
            kernel_size[k_no][0],
            kernel_size[k_no][1],
            activation="relu",
            padding=padding_type,
        )(pool)
        batchnorm = BatchNormalization()(conv)
        act = Activation(activation="relu")(batchnorm)
        pool = MaxPooling2D(pool_size=pool_size, padding=padding_type)(act)

        conv = Conv2D(
            nb_filters[k_no],
            kernel_size[k_no][0],
            kernel_size[k_no][1],
            activation="relu",
            padding=padding_type,
        )(pool)
        batchnorm = BatchNormalization()(conv)
        act = Activation(activation="relu")(batchnorm)
        pool = MaxPooling2D(pool_size=pool_size, padding=padding_type)(act)

        conv = Conv2D(
            nb_filters[k_no],
            kernel_size[k_no][0],
            kernel_size[k_no][1],
            activation="relu",
            padding=padding_type,
        )(pool)
        batchnorm = BatchNormalization()(conv)
        act = Activation(activation="relu")(batchnorm)

        convs.append(act)

    if len(kernel_size) > 1:
        out = Concatenate()(convs)
    else:
        out = convs[0]

    conv_model = Model(inputs=inp, outputs=out)

    # # add created model grapg in sequential model

    model = Sequential()
    model.add(conv_model)
    model.add(MaxPooling2D(pool_size=pool_size, padding=padding_type))
    model.add(Flatten())
    model.add(Dropout(0.5))
    model.add(Dense(128, activation="relu"))
    model.add(Dense(1, activation="sigmoid"))
    model.compile(
        loss="binary_crossentropy",
        optimizer="adam",
        metrics=["accuracy", tf.keras.metrics.Precision(), tf.keras.metrics.Recall()],
    )
    return model


def fit_monotone_increasing(y):
    pulp_model = LpProblem(name="problem", sense=LpMinimize)
    yhat = LpVariable.dicts(name="yhat", indexs=(range(len(y))), cat=LpContinuous)
    diff = LpVariable.dicts(name="diff", indexs=(range(len(y))), cat=LpContinuous)
    for i in range(len(y) - 1):
        pulp_model += yhat[i] <= yhat[i + 1]
    for i in range(len(y)):
        pulp_model += diff[i] >= (yhat[i] - y[i]) / (len(y) - i)
        pulp_model += diff[i] >= (y[i] - yhat[i]) / (len(y) - i)
    pulp_model += lpSum(diff[i] for i in range(len(y)))
    pulp_model.solve()
    y_fitted = [value(yhat[x]) for x in yhat]

    return y_fitted
