#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###############################################################
# Import packages
###############################################################
import sys

sys.path.insert(0, '../PaperFunctions')
sys.path.insert(1, '../Given')
from Given import InputConstants
from PaperFunctions import Graph, Chains
import tensorflow as tf
import matplotlib.pyplot as plt
tf.compat.v1.disable_eager_execution()
###############################################################
# Reading input files
###############################################################
input_cons = InputConstants.Inputs()
_chain = Chains()
_chain.creat_chains_functions(input_cons.chains_random_path + input_cons.chains_random_name,
                              input_cons.chains_num,
                              input_cons.fun_num,
                              input_cons.chain_ban,
                              input_cons.cpu_range)
functions = _chain.read_functions(input_cons.chains_random_path + input_cons.chains_random_name)
graph = Graph(input_cons.network_path + input_cons.network_name,
              functions)
chains = _chain.read_chains(input_cons.chains_random_path + input_cons.chains_random_name,
                            graph)

###############################################################
# Learning
###############################################################
tf.compat.v1.reset_default_graph()
node_num = len(graph.node_list)
# Define placeholder x for input
x = tf.compat.v1.placeholder(dtype=tf.float64, shape=[node_num, input_cons.node_features], name="x")
# Define placeholder y for output
y = tf.compat.v1.placeholder(dtype=tf.float64, shape=[1, node_num], name="y")
# Define variable w and fill it with random number
w_1 = tf.Variable(tf.random.normal(shape=[input_cons.node_features, 1], stddev=1e-3, mean=1e-2, dtype=tf.float64),
                  name="weights_1", dtype=tf.float64, trainable=True)
# Define variable b and fill it with zero
b_1 = tf.Variable(tf.zeros(1, dtype=tf.float64), name="bias_1", dtype=tf.float64, trainable=True)
b_2 = tf.Variable(tf.zeros(1, dtype=tf.float64), name="bias_2", dtype=tf.float64, trainable=True)
# Define variable reward and fill it with zero
reward = tf.Variable(0, name="reward", dtype=tf.float64)

# Define logistic Regression

logit = tf.matmul(x, w_1) + b_1
logit_mod = tf.reshape(logit, [1, -1])
y_predicted = tf.nn.softmax(logit_mod)
# Define maximum likelihood loss function
loss = -1 * tf.reduce_sum(tf.multiply(y, tf.math.log(y_predicted +
                                                tf.constant(1e-10, dtype=tf.float64))))
cost = tf.reduce_mean(loss)
# Define optimizer: GradientDescent
optimizer = tf.compat.v1.train.GradientDescentOptimizer(learning_rate=input_cons.learning_rate)
# Compute gradients; grad_pairs contains (gradient, variable) pairs
grad_pairs = optimizer.compute_gradients(loss, [w_1, b_1])
opt = optimizer.minimize(cost)
# Create variables to store accumulated gradients
accumulators = [
    tf.Variable(
        tf.zeros_like(tv.read_value()),
        trainable=False
    ) for tv in [w_1, b_1]
]

accumulators_stacked = [
    tf.Variable(
        tf.zeros_like(tv.read_value()),
        trainable=False
    ) for tv in [w_1, b_1]
]

accumulate_ops = [
    accumulator.assign_add(
        grad
    ) for (accumulator, (grad, var)) in zip(accumulators, grad_pairs)
]
accumulate_stacked_ops = [
    accumulator_s.assign_add(
        accumulator
    ) for accumulator_s, accumulator in zip(accumulators_stacked, accumulators)]

accumulate_mul = [
    accumulator.assign_add(
        (accumulator * reward) - accumulator
    ) for (accumulator, (grad, var)) in zip(accumulators, grad_pairs)
]

train_step = optimizer.apply_gradients(
    [(accumulator, var)
     for (accumulator, (grad, var)) in zip(accumulators_stacked, grad_pairs)]
)
zero_ops = [
    accumulator.assign(
        tf.zeros_like(tv)
    ) for (accumulator, tv) in zip(accumulators, [w_1, b_1])]

zero_stacked_ops = [
    accumulator.assign(
        tf.zeros_like(tv)
    ) for (accumulator, tv) in zip(accumulators_stacked, [w_1, b_1])
]
# %%
with tf.compat.v1.Session() as sess:  # A Session object encapsulates the environment in which Operation objects are executed, and Tensor objects are evaluated
    graph.make_empty_nodes(chains)
    reward_list_1 = []
    cost_list_1 = []
    rev_list_1 = []
    loss_list_1 = []
    train_cnt = 0
    reward_list = []
    reward_list_final = []
    cost_list_final = []
    cost_list = []
    rev_list = []
    rev_list_final = []
    loss_list = []
    loss_list_final = []
    tf.compat.v1.local_variables_initializer().run()
    tf.compat.v1.global_variables_initializer().run()
    for epoch in range(input_cons.epoch_num):
        placed_chains = []
        graph.make_empty_nodes(chains)
        node_fun_list = []
        grads_stack = 0
        cnt = 0
        node_fun = []
        mf_matrix = graph.update_feature_matrix(node_fun)
        ser_name_list = []
        for ser_num, s in enumerate(chains):
            print(ser_num,s.fun)
            node_fun = []
            ser_name_list.append(s.name)
            for fun in s.fun:
                y_RL = sess.run(y_predicted, feed_dict={x: mf_matrix})
                # print("y_rl",y_RL)
                y_one_hot, candidate = graph.select_one(y_RL,
                                                        approach='sample')
                loss_list.append(sess.run(cost, feed_dict={y: y_RL, x: mf_matrix}))
                gradient_val = sess.run(accumulate_ops, feed_dict={x: mf_matrix, y: y_one_hot})
                node_fun.append((candidate, fun))
                mf_matrix = graph.update_feature_matrix(node_fun)
            node_fun_list.append(node_fun)
            reward_val = graph.rev_to_cost(node_fun, ser_num, chains)
            sess.run(accumulate_mul, feed_dict={reward: reward_val})
            sess.run(accumulate_stacked_ops)
            sess.run(zero_ops)
            cost_list.append(graph.cost_measure(node_fun,
                                                ser_num, chains))
            rev_list.append(graph.revenue_measure(node_fun, ser_num,
                                                  chains))
            reward_list.append(reward_val)
            cnt += 1
            node_fun = []
            if cnt == input_cons.batch_Size:
                if (graph.node_is_mapped(node_fun_list, chains) &
                        graph.link_is_mapped(node_fun_list, chains)):
                    reward_list_1.append(sum(reward_list) / cnt)
                    reward_list = []
                    loss_list_1.append(sum(loss_list) / cnt)
                    loss_list = []
                    cost_list_1.append(sum(cost_list) / cnt)
                    cost_list = []
                    rev_list_1.append(sum(rev_list) / cnt)
                    rev_list = []
                    train_cnt += 1
                    print("epoch = ", epoch)
                    print("Train cnt = ", train_cnt)
                    sess.run(train_step)
                    w_1_val, b_val = sess.run([w_1, b_1])
                    # print("b_val = ", b_val)
                    # print("w[0]_val = ", w_1_val[0])
                    # print("w[1]_val = ", w_1_val[1])
                    # print("w[2]_val = ", w_1_val[2])
                    # print("w[3]_val = ", w_1_val[3]
                    print("**********************")
                    graph.batch_function_placement(ser_name_list, node_fun_list)
                    ser_name_list = []
                    cnt = 0
                    sess.run(zero_ops)
                    sess.run(zero_stacked_ops)
                    node_fun = []
                    node_fun_list = []
                else:
                    loss_list = []
                    reward_list = []
                    rev_list = []
                    cost_list = []
                    sess.run(zero_ops)
                    sess.run(zero_stacked_ops)
                    cnt = 0
                    node_fun = []
                    node_fun_list = []
        if len(reward_list_1) != 0:
            reward_list_final.append(sum(reward_list_1) / len(reward_list_1))
        reward_list_1 = []
        if len(cost_list_1) != 0:
            cost_list_final.append(sum(cost_list_1) / len(cost_list_1))
        cost_list_1 = []
        if len(rev_list_1) != 0:
            rev_list_final.append(sum(rev_list_1) / len(rev_list_1))
        rev_list_1 = []
        if len(loss_list_1) != 0:
            loss_list_final.append(sum(loss_list_1) / len(loss_list_1))
        loss_list_1 = []
###############################################################
# Plots
###############################################################
fig, ax = plt.subplots(2, 2, figsize=(10, 10))
for a in ax.reshape(-1, 1):
    a[0].set_xlabel("epochs")
rToC=[]
l = len(reward_list_final)
i=0
while(i<l):
    rToC.append(reward_list_final[i]/cost_list_final[i])
    i=i+1
ax[0][0].plot(rToC, color='red', label='rtoc')
ax[0][0].legend()
ax[1][0].plot(loss_list_final, color='red', label='loss')
ax[1][0].legend()
ax[0][1].plot(cost_list_final, color='red', label='cost')
ax[0][1].legend()
ax[1][1].plot(rev_list_final, color='red', label='revenue')
ax[1][1].legend()
plt.savefig("Plots/results" + ".pdf")
