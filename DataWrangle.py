#TF etc (and friends)
import tensorflow as tf
from tensorflow.keras import datasets, layers, models
import matplotlib.pyplot as plt
import pandas as pd
import time
import numpy as np
import random
import cv2
import networkx as nx
from karateclub import Graph2Vec

#PubChem access API, chem tools et al
import pubchempy as pcp
from rdkit import Chem
from rdkit.Chem import Draw
from rdkit.Chem import RDKFingerprint
from rdkit.Chem import rdMolDescriptors

#Constants
BATCH_SIZE = 50
BATCHES = 25

#-----------Graph representation
'''
#see bond info
rdk_bonds = rdk_mol.GetBonds()
thing1 = "FC1=C(F)CC=CC1"
thing2 = "FC1C(F)=CC=CC=C1"
t1_bonds = Chem.MolFromSmiles(thing1).GetBonds()
t2_bonds = Chem.MolFromSmiles(thing2).GetBonds()
for b in t1_bonds:
    print(b.GetBondType())
print("=====")
for b in t2_bonds:
    print(b.GetBondType())
#for b in rdk_bonds:
#    print(b.GetBondType(), b.GetBondDir())
Draw.MolToFile(Chem.MolFromSmiles(thing1), 't1.png')
Draw.MolToFile(Chem.MolFromSmiles(thing2), 't2.png')
'''

def mol_to_graph(mol):
    '''
    Convert an RDK molecule to graph representation (nx graph)
    '''
    #Get empty graph, collection of atoms and bonds
    graph = nx.Graph()
    atoms = mol.GetAtoms()
    bonds = mol.GetBonds()

    #Create vectorized functions to add nodes (atoms) and edges (bonds) to created empty graph
    add_nodes = np.vectorize((lambda g, atom:g.add_node(atom.GetIdx(),
                                            atomic_num=atom.GetAtomicNum(),
                                            is_aromatic=atom.GetIsAromatic(),
                                            atom_symbol=atom.GetSymbol())), excluded=['g'])
    add_edges = np.vectorize((lambda g, bond:g.add_edge(bond.GetBeginAtomIdx(),
                                        bond.GetEndAtomIdx(),
                                        bond_type=bond.GetBondType())), excluded=['g'])

    #Populate graph with edges and nodes DOESN'T WORK
    #add_nodes(graph, atoms)
    #add_nodes(graph, bonds)

    #TODO: try removing hydrogen nodes that are connected to Carbons
    for atom in atoms : 
        graph.add_node(atom.GetIdx(),
                       atomic_num=atom.GetAtomicNum(),
                       is_aromatic=atom.GetIsAromatic(),
                       atom_symbol=atom.GetSymbol())
    for bond in bonds:
        graph.add_edge(bond.GetBeginAtomIdx(),
                      bond.GetEndAtomIdx(),
                      bond_type=bond.GetBondType(),
                      bond_stereo=bond.GetStereo(),
                      bond_dir=bond.GetBondDir())

    return graph

#Test
#print("Graph: ", mol_to_graph(rdk_mol))

#Get Embeddings

#---------Random Chemical (for ingestion)
'''
#Retrieve compound object random.randint(0, 999999))
cid = random.randint(0, 9999999)
c = pcp.Compound.from_cid(cid)

#Get SMILE representation
c_smile = (c.isomeric_smiles)

#Download Image from CID
pcp.download('PNG', 'uh.png', cid, 'cid', image_size='large', overwrite=True)

#Get RDK representation of molecule
rdk_mol = Chem.MolFromSmiles(c_smile)

#Get Fingerprint as numpy array
fingerprint_c = np.array(RDKFingerprint(rdk_mol))
print(c.iupac_name, "F_Print: ", fingerprint_c, len(fingerprint_c))
'''
#Getting a collection of the above:
def _compileData(cur_batch):
    dataDict = {}
    dataDict['Images'] = []
    dataDict['CIDs'] = []
    #dataDict['GraphEmbeddings'] = []
    dataDict['SMILES'] = []
    dataDict['Graphs'] = []
    #dataDict['BondInfo'] = []
    #dataDict['StereoInfo'] = []
    #dataDict['']
    for i in range(BATCH_SIZE):
        #Generate random molecule, get RDKit molecule object representation -> grpah representation
        cid = random.randint(1, 9999999)
        smiles = pcp.Compound.from_cid(cid).isomeric_smiles
        molecule = Chem.MolFromSmiles(smiles)

        #Obtain graph representation of molecule, and add to dataframe
        g_mol = mol_to_graph(molecule)

        #Retrieve image and save to file
        img_name = ('ImageData/uh' + str(i+(cur_batch*BATCH_SIZE)) + '.png')
        pcp.download('PNG', img_name, cid, 'cid', image_size='large', overwrite=True)

        #Save image address, CID and graph objects in dict 
        dataDict['Images'].append(img_name)
        dataDict['CIDs'].append(cid)
        dataDict['SMILES'].append(smiles)
        dataDict['Graphs'].append(g_mol)

        print(i)#, ": ", molecule)
        time.sleep(0.5)

    #dataDict['GraphEmbeddings'] = dataDict['Graphs'].apply(lambda x: mol_to_nx(x))
    embed_model = Graph2Vec()
    embed_model.fit(dataDict['Graphs'])

    #Get df representation of embeddings (to merge with main dataset dataframe)
    #dataDict['GraphEmbeddings'] = model.get_embedding()#.flatten()
    df_embedds = pd.DataFrame(embed_model.get_embedding())
    print("Done")

    #Data df reprentation of dictionary, merge embeddings to it
    DataFrame = pd.DataFrame.from_dict(dataDict)
    DataFrame = pd.concat([DataFrame, df_embedds], axis="columns")

    print(DataFrame)
    DataFrame.to_csv('CompiledDataset/data.csv', mode='a')

#Compile data in batches of 100
'''
for i in range(BATCHES):
    print(i)
    _compileData(i)
'''

#concatenated = pandas.concat([df1, df2], axis="columns")

#'''
#Loading dataframe from csv
LoadedDF = pd.read_csv('CompiledDataset/data.csv')
print(LoadedDF)

RelevantDF = LoadedDF['Images']
RelevantDF = pd.concat([RelevantDF, LoadedDF[[str(i) for i in range(128)]]], axis="columns")

count = 0
for i in range(1, BATCHES):
    drop_i = i*BATCH_SIZE + (i-1)
    print(RelevantDF['Images'][drop_i])
    RelevantDF = RelevantDF.drop(drop_i)
    count+=1

print(RelevantDF, count)
#Save to csv
RelevantDF.to_csv('CompiledDataset/relevant_data.csv')
#RelevantDF.to_excel('CompiledDataset/relevant_data.xlsx')
#-------------Image Loading
'''
loaded_img = tf.keras.preprocessing.image.load_img('uh.png', True)#colour_mode="grayscale")
print(loaded_img)

#Display image size
print(cv2.imread('uh.png').shape)
'''

#--------------Net
'''
#Test distance measurements
h3o = pcp.Compound.from_cid(123332)
h2o = pcp.Compound.from_cid(962)

rdk_h3o = Chem.MolFromSmiles(h3o.isomeric_smiles)
rdk_h2o = Chem.MolFromSmiles(h2o.isomeric_smiles)

f3 = np.array(RDKFingerprint(rdk_h3o))
f2 = np.array(RDKFingerprint(rdk_h2o))

print(h3o.isomeric_smiles, h2o.isomeric_smiles)

#Print difference lengths
print("wter v water", np.linalg.norm(np.subtract(f3, f2)))
print("wter v whatever", np.linalg.norm(np.subtract(f2, fingerprint_c)))
'''






