#TF etc (and friends)
import tensorflow as tf
from tensorflow.keras import datasets, layers, models
import matplotlib.pyplot as plt
import pandas as pd
import time
import numpy as np
import random
import networkx as nx
from karateclub import Graph2Vec

#Enable eager execution TODO
'''
import tensorflow as tf
tf.enable_eager_execution()
tfe = tf.contrib.eager
'''
DATA_PATH = 'CompiledDataset/relevant_data.csv'

#Retrieve dataframe from stored csv file
def GetData(file):
    """
    Retrieve data from file, return pandas dataframe
    """
    d = pd.read_csv(file)
    Data = d['Images']
    Data = pd.concat([Data, d[[str(i) for i in range(128)]]], axis="columns")
    return Data

#TEST:

Data = GetData(DATA_PATH)
print(Data)
