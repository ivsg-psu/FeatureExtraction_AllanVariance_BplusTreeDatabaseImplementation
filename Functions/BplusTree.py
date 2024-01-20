#!/usr/bin/env python3
# The purpose of this script is to generate Bplus tree with 4 pointers
# Each leaf node would point to three data values.
# Author: Rinith Pakala
# Created: 2022/07/10
# Updated: Satya Prasad

# Updates:
#   1. 'key' or 'keys' are KEYS in the B+ tree
#   2. 'children' are NODES at non-leaf level, data at leaf level
#   3. 'value' is data at leaf level
#   4. Removed redundant code
#   5. Replaced break with flag
#   6. Added comments to make understable to a ME grad

# math function are used for calculations and pandas is used for data modifications
import math
import random

import pandas as pd
import matplotlib.pyplot as plt

################################
########## Node class ##########
################################
class Node:
    # Each node holds KEYS, which are used as index to create B+ tree
    # For time friction series, time is inserted as KEYS and friction is inserted as KEYS attribute.
    def __init__(self, order):
        self.order    = order   # Defines maximum number of KEYS/Children in each node
        self.keys     = []      # KEYS in the node
        self.children = []      # Children are nodes at non-leaf level and data at leaf level
        self.nextKey  = None    # Next node in same level (Only for leaf nodes)
        self.parent   = None    # Parent node
        self.check_leaf = False # Flag to indicate leaf node. True: Leaf node; False: Non-leaf node;

    # Insertion at leaf level node, which contain all data pointers
    def insert_at_leaf(self, leaf, key, value):
        if (0 < len(self.keys)):                                # If the node is non-empty, insert KEY to the appropriate location
            leaf_node_keys = self.keys
            i = 0   # Reset the counter
            flag_insert = True  # Set the flag

            while (i < len(leaf_node_keys)) and flag_insert:
                if (float(key) == float(leaf_node_keys[i])):    # Check if insertion KEY matches any of leaf node KEYS
                    self.children[i].append(value)
                    flag_insert = False

                elif (float(key) < float(leaf_node_keys[i])):   # Check if insertion KEY is less than any of leaf node KEYS
                    self.keys     = self.keys[:i] + [key] + self.keys[i:]
                    self.children = self.children[:i] + [[value]] + self.children[i:]
                    flag_insert   = False

                elif (i + 1 == len(leaf_node_keys)):            # Once reached end of leaf node, append the KEY at end of leaf node KEYS
                    self.keys.append(key)
                    self.children.append([value])
                    flag_insert = False
                i += 1
        else:                                                   # If the node is empty, append KEY to the node
            self.keys     = [key]
            self.children = [[value]]

###################################
########## B+ tree class ##########
###################################
class BplusTree:
    # B+ tree initializes with root node and check_leaf flag set to true
    def __init__(self, order):
        self.root = Node(order)
        self.root.check_leaf = True     # At the beginning Root node is a leaf node

    # Insertion of new KEY into B+ tree
    # Each insertion compares node's KEYS with inserting KEY and assigns proper position to KEY
    def insert(self, key, value):
        key      = str(key)
        old_node = self.search(key)                     # Search for the leaf node that should have the insertion
        old_node.insert_at_leaf(old_node, key, value)   # Call to insert at leaf node

        # Create a new leaf node if number of KEYS in the old_node are equal to the order of B+ tree
        # Assign a common parent node to both old and new leaf nodes
        if (len(old_node.keys) == old_node.order):
            # Create a new leaf node with parent same as the old leaf node
            new_node            = Node(old_node.order)
            new_node.check_leaf = True
            new_node.parent     = old_node.parent

            mid = math.ceil(old_node.order / 2) - 1
            # Attributes of new node
            new_node.keys     = old_node.keys[mid + 1:]
            new_node.children = old_node.children[mid + 1:]
            new_node.nextKey  = old_node.nextKey
            # Attribute of old node
            old_node.keys     = old_node.keys[:mid + 1]
            old_node.children = old_node.children[:mid + 1]
            old_node.nextKey  = new_node
            # Attach both nodes to parent and insert right mid value in parent
            self.insert_in_parent(old_node, new_node.keys[0], new_node)

    # Search operation to find leaf node that should be used for insertion
    def search(self, key):
        current_node = self.root    # Start with root node

        # Loop till leaf level is reached
        while (current_node.check_leaf == False):
            keys_current_node = current_node.keys
            i = 0   # Reset the counter
            flag_search = True  # Set the flag

            # Loop till a child node is found
            while (i < len(keys_current_node)) and flag_search:
                if (float(key) == float(keys_current_node[i])):     # Check if the KEY is matching any KEYS in the node
                    current_node = current_node.children[i + 1]
                    flag_search  = False

                elif (float(key) < float(keys_current_node[i])):    # Check if the KEY is less than any KEYS in the node
                    current_node = current_node.children[i]
                    flag_search  = False

                elif (i + 1 == len(keys_current_node)):             # If it does not match above conditions
                    current_node = current_node.children[i + 1]
                    flag_search  = False
                i += 1

        return current_node

    # Find if tree contains the value, key combination
    def find(self, value, key):
        l = self.search(value)
        for i, item in enumerate(l.values):
            if item == value:
                if key in l.keys[i]:
                    return True
                else:
                    return False
        return False

    # Insertion of KEY at parent node
    def insert_in_parent(self, n, key, ndash):
        # Create a new root node if current root node is same as the old node
        if (self.root == n):
            rootNode          = Node(n.order)
            rootNode.keys     = [key]
            rootNode.children = [n, ndash]
            self.root    = rootNode
            n.parent     = rootNode
            ndash.parent = rootNode
            return

        # Splitting keys between parent node and ndash node (new node)
        parentNode = n.parent
        children_parentNode = parentNode.children
        for i in range(len(children_parentNode)):
            if (children_parentNode[i] == n):   # When a child is the old node
                parentNode.keys     = parentNode.keys[:i] + [key] + parentNode.keys[i:]
                parentNode.children = parentNode.children[:i + 1] + [ndash] + parentNode.children[i + 1:]

                if (len(parentNode.keys) == parentNode.order):
                    # Create a new parent node
                    parentdash        = Node(parentNode.order)
                    parentdash.parent = parentNode.parent

                    mid = math.ceil(parentNode.order / 2) - 1
                    # Attributes of new parent node
                    parentdash.keys     = parentNode.keys[mid + 2:]
                    parentdash.children = parentNode.children[mid + 2:]

                    key_ = parentNode.keys[mid + 1]
                    # Attributes of old parent node
                    parentNode.keys     = parentNode.keys[:mid + 1]
                    parentNode.children = parentNode.children[:mid + 2]
                    # Update parent nodes in child nodes
                    for j in parentNode.children:
                        j.parent = parentNode
                    for j in parentdash.children:
                        j.parent = parentdash
                    self.insert_in_parent(parentNode, key_, parentdash)

#########################################
########## Auxiliary Functions ##########
#########################################
## Print leaf level KEYS of the B+ tree
def printBTree(node):
    if (node.check_leaf == False):
        # If the node is not a leaf node, print its children (nodes)
        for i, child_node in enumerate(node.children):
            printBTree(child_node)
    else:
        # If the node is a leaf node, print its KEYS
        print(node.keys)

## Print leaf level children (data) of the B+ tree
def printBTreeChild(node):
    if (node.check_leaf == False):
        # If the node is not a leaf node, print its children (nodes)
        for i, child_node in enumerate(node.children):
            printBTreeChild(child_node)
    else:
        # If the node is a leaf node, print its children (data)
        print(node.children)

## Fetch the tree depth
def treeDepth(node):
    depth = 0
    while (node.check_leaf == False): # Loop until leaf level is reached
        node = node.children[0]
        depth += 1
    return depth + 1

## Fetch leaf level keys that are pointed by node at a given level
def leafDataAtNodeLevel(tree, level):
    node_list = []
    leaf_data_from_all_nodes_at_level = []
    
    # Fetch nodes at a tree level
    def nodesForTreeLevel(node, level):
        if level != 0:
            for i, keynode in enumerate(node.children):
                nodesForTreeLevel(keynode, level - 1)
        else:
            node_list.append(node)
        return node_list
        
    # fetch leaf level data keys pointed by node
    def datapointedbynode(node):
        if (node.check_leaf == False):
            for i, keynode in enumerate(node.children):
                datapointedbynode(keynode)
        else:
            # To fetch keys pointed by node
            for i, keynode in enumerate(node.children):
                leafDataForNode.append(keynode)
            # # To fetch values pointed by node
            # for i, item in enumerate(node.values):
            #     leafDataForNode.append(item)
        return leafDataForNode

    nodes_in_level = nodesForTreeLevel(tree, level) # calling method to fetch all nodes at a level

    while (len(nodes_in_level)):    # for each node at level, fetch all leaf data keys
        leafDataForNode = []
        level_node = nodes_in_level.pop(0)
        leaf_data_from_all_nodes_at_level.append(datapointedbynode(level_node))

    return leaf_data_from_all_nodes_at_level

## AVAR calculation for nodes in a level
def AVAR_calculation_at_level(tree, level):
    #leaf_data format : [[leafdata_by_levelnode1],[leafdata_by_levelnode2]]
    # leaf_data format : [ [[leafnode1key1],[leafnode1key2],[leafnode2key1],[leafnode2key2]] , [[leafnode3key1],[leafnode3key2],[leafnode4key1],[leafnode4key2]] ]
    leaf_data = leafDataAtNodeLevel(tree, level)
    level_node_mean_list, level_node_weight_list = [], []
    weight_mean_diff = 0
    min_level_node_weight = 0

    for level_node_data in leaf_data:
        level_node_sum = sum(sum(leaf_key_data) for leaf_key_data in level_node_data)
        level_node_mean_list.append(level_node_sum / len(level_node_data))  # fetching mean of each level node
        level_node_weight_list.append(len(level_node_data))                 # fetching weights of each level node

    #for plotting purpose
    # min_level_node_weight = min(level_node_weight_list)
    min_level_node_weight = round(sum(level_node_weight_list)/len(level_node_weight_list))
    cons_weight_prod = 0
    for i in range(len(level_node_mean_list) - 1):
        # sum of squares of adjacent mean differences
        weight_mean_diff += level_node_weight_list[i] * level_node_weight_list[i + 1] * ((level_node_mean_list[i] - level_node_mean_list[i + 1]) ** 2)
        cons_weight_prod += level_node_weight_list[i] * level_node_weight_list[i + 1]

    #sum of squares of adjacent mean differences over twice the sum of level node leaf key weights
    return weight_mean_diff / (2 * cons_weight_prod), min_level_node_weight

## AVAR calculation for all levels of tree
# Level 1 for leaf or lowest correlation interval and AVAR is calculated upwards
def AVAR_calculation_All_Levels(tree):
    depth = treeDepth(tree)
    AVAR_list, correlation_interval_list = [], []
    for i in range(1, depth):
        AVAR, correlation_interval = AVAR_calculation_at_level(tree, i)  # Fetch individual AVAR for a level

        AVAR_list.append(AVAR)
        correlation_interval_list.append(correlation_interval)
        
    return AVAR_list, correlation_interval_list

####################################################
########## Estimating AVAR using B+ trees ##########
####################################################
# Assigning order of B+ tree to be m:
#   At non-leaf level, there are a maximum of m-1 KEYS and m Children
#   At leaf level, there are a maximum of m-1 data pointers and 1 pointer to next node
order_BplusTree = 4
bplustree = BplusTree(order_BplusTree)  # Initializing B+ tree

########## Examples ##########
# # Inserting N sequential elements
# N = 17
# for i in range(1,N+1):
#     bplustree.insert(i, random.randint(1, N+1))
# printBTree(bplustree.root)

# # Inserting N sequential elements
# N = 17
# for i in range(1,N+1):
#     bplustree.insert(i, i)
# printBTreeChild(bplustree.root)

# read csv for white_random
df = pd.read_csv('test_data.csv')
for index, row in df.iterrows():
    bplustree.insert(row['Time'], row['White_Random'])
# AVAR value for all levels in tree
AVAR_list, min_weight_list = AVAR_calculation_All_Levels(bplustree.root)
# dictionary of lists  
dict = {'AVAR': AVAR_list, 'correlation_interval': min_weight_list}
df   = pd.DataFrame(dict)
# saving the dataframe
df.to_csv('bpTree_WNpRWAVAR.csv')

# # read csv for White Noise
# df = pd.read_csv('test_data.csv')
# for index, row in df.iterrows():
#     bplustree.insert(row['Time'], row['WhiteNoise'])
# # AVAR value for all levels in tree
# AVAR_list, min_weight_list = AVAR_calculation_All_Levels(bplustree.root)
# # dictionary of lists  
# dict = {'AVAR': AVAR_list, 'correlation_interval': min_weight_list}
# df   = pd.DataFrame(dict)
# # saving the dataframe
# df.to_csv('bpTree_WNAVAR.csv')

# # read csv for Random Walk
# df = pd.read_csv('test_data.csv')
# for index, row in df.iterrows():
#     bplustree.insert(row['Time'], row['RandomWalk'])
# # AVAR value for all levels in tree
# AVAR_list, min_weight_list = AVAR_calculation_All_Levels(bplustree.root)
# # dictionary of lists  
# dict = {'AVAR': AVAR_list, 'correlation_interval': min_weight_list}
# df   = pd.DataFrame(dict)
# # saving the dataframe
# df.to_csv('bpTree_RWAVAR.csv')

# print(AVAR_list)
plt.plot(min_weight_list, AVAR_list, marker = 'o')
plt.xlabel('Leaf data points',size=16)
plt.ylabel('AVAR',size=16)
plt.title('White noise with Random Walk AVAR for Tree levels',size=16)
plt.xscale('log')
plt.yscale('log')
plt.savefig('AVAR_whiterandom.png')
plt.show()

# # Printing B plus tree index (time) values
# print(f'printing bplus tree index values')
# printBTree(bplustree.root)
#
# # Printing B plus tree keys (friction)
# print(f'printing associated keys')
# printBTreeChild(bplustree.root)

# # Fetching Tree depth
# print(treeDepth(bplustree.root))

# # Fetching Leaf Data pointed by nodes in a tree level
# leafData=leafDataAtNodeLevel(bplustree.root,2)
# print(leafData)
