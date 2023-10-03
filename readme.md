# Request Allocation with RL Policy Network

## Overview

This project is designed to allocate requests to a substrate graph using a simple Reinforcement Learning (RL) policy network. It operates on a set of preset chains of functions, where each function has specific CPU and bandwidth requirements. The primary goal is to efficiently allocate these requests while optimizing resource utilization in the substrate graph.

## Table of Contents

- [Request Allocation with RL Policy Network](#request-allocation-with-rl-policy-network)
  - [Overview](#overview)
  - [Table of Contents](#table-of-contents)
  - [Introduction](#introduction)
  - [Requirements](#requirements)
  - [Setup](#setup)
  - [Configuration](#configuration)
  - [Execute](#execute)

## Introduction

The project addresses the problem of allocating requests efficiently in a substrate graph. It employs a Reinforcement Learning (RL) policy network that takes into account the specific requirements of each request and aims to maximize resource utilization while meeting those requirements.


## Requirements

To run this project, you will need the following:

- Python 3.x
- TensorFlow (or any other RL framework of your choice)
- Substrate graph data
- Requests with function chains and resource requirements

## Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/Akshat-Rathore/rl-based-vne.git
   ```
2. Create environment:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

- Configure the RL policy network and training parameters as needed in the `InputConstants.py` file.

## Execute

```bash
python main.py
```
