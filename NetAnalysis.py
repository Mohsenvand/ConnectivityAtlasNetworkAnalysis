import csv
csvF = list(csv.reader(open("modeled.csv")))
keyList = csvF[0][1:]

csvHash = {}
for i in range(1,len(csvF)):
    csvHash[csvF[i][0]]=dict(zip(keyList, csvF[i][1:]))

import json
with open('modeledMatrix.json' , 'wb') as jsf:
    jsf.write(json.dumps(csvHash, indent = 4))

import sys
import networkx as nx
# create a new graph
G = nx.Graph()
# use tags to add and label all the nodes
G.add_nodes_from(keyList)

#initialize the edge list
edgeList=[]

# add the edges and their weights to the edge list
for vertex in keyList:
    for otherVertex in csvHash[vertex].keys():
        if float(csvHash[vertex][otherVertex])>0:
        # the edge list should be a list of tuples with 3 entries, (node1, node2, weight)
            edgeList.append((vertex,otherVertex,float(csvHash[vertex][otherVertex])))
        
#use the method of add_weighted_edges_from that takes a list of tuples as shown before
G.add_weighted_edges_from (edgeList)

sys.stdout.write(" done\n")

#save a copy of the labeled and weighted graph in GML format for further visualizations
sys.stdout.write("Saving the Graph as GML . . .")
nx.write_gml(G,"ModeledGraph.gml")
sys.stdout.write(" done\n")

print "="*100

###################################################################################################
####################################### Centrality Analysis #######################################
###################################################################################################

print "Analysis :"

#using NetworkX for centrality analysis of the graph

sys.stdout.write("calculating Degrees . . .")
DegreeDict = nx.degree_centrality(G)
sys.stdout.write(" done\n")

sys.stdout.write("calculating PageRank Centrality . . .")
PageRankDict = nx.pagerank(G)
sys.stdout.write(" done\n")

sys.stdout.write("calculating Closeness Centrality . . .")
ClosenessDict = nx.closeness_centrality(G)
sys.stdout.write(" done\n")

sys.stdout.write("calculating Betweenness Centrality . . .")
BetweennessDict = nx.betweenness_centrality(G)
sys.stdout.write(" done\n")

sys.stdout.write("calculating Communicability Centrality . . .")
CommunicabilityDict= nx.communicability_centrality(G)
sys.stdout.write(" done\n")

print "="*100

import re
csvRegion = list(csv.reader(open("Regions.csv")))
regions = {}
for i in range(1,len(csvRegion)) :
    regions[csvRegion[i][2].strip()] = [re.sub(r'(,)', '/',csvRegion[i][3]), re.sub(r'(,)', '/',csvRegion[i][4])]

import matplotlib.pyplot as plt
nx.draw(G)  # networkx draw()
plt.show()

sys.stdout.write("Clustering by depth 3 . . .")

# using community library to perform community detection.
# check this address for documentation and installation of the package:
# http://perso.crans.org/aynaud/communities/
# note that it won't install using pip and the user should use setup.py to add it to the virtualenv.

import community

#tagPath is going to store the cluster path. A cluster path that is assigned to each node(tag) is an address like /0/1/2
# the address shows the hierarchical classification of the node or it's address in the ontology tree
# / : root /0 : the first layer /0/1 : the second layer ...
tagPath = {}
for tag in keyList :
    #starting with the root of the tree
    tagPath[tag] = "/"

# first community detection:
partition0 = community.best_partition(G)
# number of communities in the first layer
maxval0 = max(partition0.values())

# adding the first layer address to the tagPath
for tag in partition0:
    tagPath[tag] += str(partition0[tag])
#starting the hierarchical clustering:
# 1-take each cluster
for i in range(maxval0+1):
    # create a sub-graph for the cluster
    G1 = nx.Graph()
    # choose the right nodes (clusters are numbered from 0 to the number of clusters -1)
    # here "i" notes the number of cluster
    tagListG1 = [tag for tag in partition0.keys() if partition0[tag]==i]
    # add nodes
    G1.add_nodes_from(tagListG1)
    # add edges as before
    edgeListG1=[]
    for vertex in tagListG1:
        for otherVertex in csvHash[vertex].keys():
            if otherVertex in tagListG1:
                edgeListG1.append((vertex,otherVertex,float(csvHash[vertex][otherVertex])))
    G1.add_weighted_edges_from (edgeListG1)
    # sub-clustering
    partitionG1 = community.best_partition(G1)
    # updating the paths by adding the second layer address
    for tag in partitionG1:
        tagPath[tag] += "/" + str(partitionG1[tag])
    # number of subclusters
    maxval1 = max(partitionG1.values())
    # repeat the same process again !
    for j in range(maxval1+1):
        G2 = nx.Graph()
        tagListG2 = [tag for tag in partitionG1.keys() if partitionG1[tag]==j]
        G2.add_nodes_from(tagListG2)
        edgeListG2=[]
        for vertex in tagListG2:
            for otherVertex in csvHash[vertex].keys():
                if otherVertex in tagListG2:
                    edgeListG2.append((vertex,otherVertex,float(csvHash[vertex][otherVertex])))
        G2.add_weighted_edges_from (edgeListG2)
        partitionG2 = community.best_partition(G2)
        for tag in partitionG2:
            tagPath[tag] += "/"+str(partitionG2[tag])
sys.stdout.write(" done\n")
print "="*100

###################################################################################################
####################################### Saving the results ########################################
###################################################################################################

print "Saving the Analysis results as CSV."
with open('AnalysisResults.csv','wb') as csvo:
    csvo.write('Region,Parrent,cluster,Degree,PageRank,Closeness,Betweenness,Communicability'+'\n')
    for tag in keyList:
        csvo.write(regions[tag][0]+','+regions[tag][1]+','+tagPath[tag]+','+str(DegreeDict[tag])+','+str(PageRankDict[tag])+','
                   +str(ClosenessDict[tag])+','+str(BetweennessDict[tag])+','+str(CommunicabilityDict[tag])+'\n')


print "Saving the Analysis results as CSV - Separate Path."
with open('AnalysisResults_Sep.csv','wb') as csvo:
    csvo.write('Region,Parrent,l1,l2,l3,Degree,PageRank,Closeness,Betweenness,Communicability'+'\n')
    for tag in keyList:
        address = tagPath[tag][1:].split('/')
        csvo.write(regions[tag][0]+','+regions[tag][1]+','+str(address[0])+','+str(address[1])+','+str(address[2])+','+str(DegreeDict[tag])+','+str(PageRankDict[tag])+','
                   +str(ClosenessDict[tag])+','+str(BetweennessDict[tag])+','+str(CommunicabilityDict[tag])+'\n')


print "Saving the Analysis results as JSON."

resultsDict ={}
for tag in keyList:
    address = tagPath[tag][1:].split('/')
    resultsDict[tag] = {'l1':address[0],
                        'l2':address[1],
                        'l3':address[2],
                        'Degree':DegreeDict[tag],
                        'PageRank':PageRankDict[tag],
                        'Closeness':ClosenessDict[tag],
                        'Betweenness':BetweennessDict[tag],
                        "Communicability":CommunicabilityDict[tag]
                        }
with open('AnalysisResults.json','wb') as jsfA:
    jsfA.write(json.dumps(resultsDict, indent = 4))




















