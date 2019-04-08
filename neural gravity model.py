

import tensorflow as tf
import numpy as np
from func import *


# 构造添加神经层函数
def add_layer(inputs, in_size, out_size, activation_function=None):
    Weights = tf.Variable(tf.random_normal([in_size, out_size]))
    biases = tf.Variable(tf.zeros([1, out_size]) + 0.1)
    Wx_plus_b = tf.matmul(inputs, Weights) + biases
    if activation_function is None:
        outputs = Wx_plus_b
    else:
        outputs = activation_function(Wx_plus_b)
    return outputs


def read_data(path, normalization=False):
    train_X = []
    train_y = []
    test_X = []
    test_y = []
    #validation_X = []
    #validation_y = []

    tr_f = read_flows(path + 'train.txt')
    te_f = read_flows(path + 'test.txt')
    if normalization:
        features = read_features(path + 'entities.dict', path + 'features.txt')
    else:
        features = read_features(path + 'entities.dict', path + 'features_raw.txt')

    for k in tr_f:
        if k[2]:
            train_y.append(k[2])
            train_X.append([features[k[0]][3], features[k[1]][2],
                            dis(features[k[0]][0], features[k[0]][1], features[k[1]][0], features[k[1]][1])])

    for k in te_f:
        if k[2]:
            test_y.append(k[2])
            test_X.append([features[k[0]][3], features[k[1]][2],
                           dis(features[k[0]][0], features[k[0]][1], features[k[1]][0], features[k[1]][1])])

    return np.array(train_X).reshape((-1, 3)), np.array(train_y).reshape((-1, 1)), np.array(test_X), np.array(test_y)


if __name__ == '__main__':
    path = 'SI-GCN/data/taxi/'
    train_X, train_y, test_X, test_y = read_data(path, normalization=False)
    print(train_X[0])
    print(train_y[0])

    learn_rate = 0.01
    num_of_hidden_units = 20

    xs = tf.placeholder(tf.float32, [None, 3])
    ys = tf.placeholder(tf.float32, [None, 1])

    hidden_layer = add_layer(xs, 3, num_of_hidden_units, activation_function=tf.nn.sigmoid)
    prediction = add_layer(hidden_layer, num_of_hidden_units, 1, activation_function=None)

    loss = 0.5 * tf.reduce_sum(tf.square(ys - prediction))
    train_step = tf.train.GradientDescentOptimizer(learn_rate).minimize(loss)

    with tf.Session() as sess:
        init = tf.global_variables_initializer().run()
        for i in range(1000):
            sess.run(train_step, feed_dict={xs: train_X, ys: train_y})
            if i % 50 == 0:
                print(sess.run(loss, feed_dict={xs: train_X, ys: train_y}))

        pred = sess.run(prediction, feed_dict={xs:test_X})
        evaluate(pred, test_y)