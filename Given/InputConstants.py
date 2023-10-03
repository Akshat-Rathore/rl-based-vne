#!/usr/bin/env python3
# -*- coding: utf-8 -*-
class Inputs:
    #  Path and name of input files
    network_path = "Data/"
    network_name = "nsf_14_network.json"
    chains_path = "Data/"
    chains_name = "nsf_14_network.json"
    chains_random_name = "chain_random.json"
    chains_random_path = "Data/"

    # Network topology parameters
    network_topology_node_name = 0
    network_topology_node_cap = 1
    network_topology_link_name = 0
    network_topology_link_dis = 1
    network_topology_link_cap = 2
    function_name = 0
    function_usage = 1
    # Learning parameters
    epoch_num = 500
    batch_Size = 4
    node_features = 4
    learning_rate = 1e-2  # one e power -7 = 9.11*10^-4
    # Creat chains parameters
    chains_num = 100
    fun_num = 3
    chain_ban = 90
    cpu_range = 3
    max_node_cap = 60
    min_node_cap = 30
    td_mean = 100
    td_std = 10
