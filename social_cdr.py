import sys
import pandas as pd
from datetime import datetime

import matplotlib.pyplot as plt
from scipy import *

import numpy as np
import networkx as nx


def get_social_directed(cdr_filename_region):

	G = nx.DiGraph()
	for df_cdr in pd.read_csv(cdr_filename_region, sep=';', iterator=True, chunksize=1000000):
		for user in df_cdr.itertuples():
			user_from = user.user_from
			user_to = user.user_to
			duration = user.duration
			
			#print(user)
			#print(user_from,user_to,duration)
			
			if user_from not in G:
				G.add_node(user_from)
			if user_to not in G:
				G.add_node(user_to)
			if G.has_edge(user_from,user_to) == False:
				G.add_edge(user_from,user_to,num_calls=0,duration=0.0)#,{'num_calls': 0, 'duration':0})
			G[user_from][user_to]['num_calls'] = G[user_from][user_to]['num_calls'] + 1
			G[user_from][user_to]['duration'] = G[user_from][user_to]['duration'] + duration
							
		#end
	#end

	return G
	
def plot_ccdf(series,xlabel,ylabel,title,parameters):
	#print("\n\nEntrou no plot")
	# +++++++++++++++++++++ CCDF ++++++++++++++++++++++++++++++++
	sorted_series = sorted(series)
	len_series = len(series)
	set_series = set(sorted_series)
	remaining = len_series
	ccdf_list = []
	for value in sorted(list(set_series)):
		#print(value)
		#exit()
		freq_value = list(sorted_series).count(value)
		ccdf_list.append(remaining/len_series)
		remaining = remaining - freq_value
	#end
	#print(ccdf_list)
	plt.plot(sorted(list(set_series)),ccdf_list,color = parameters["color"],label = parameters["label"], linewidth=2)
	plt.legend(loc="upper right")
	plt.xlabel(xlabel,fontsize=14)
	plt.ylabel(ylabel,fontsize=14)
	plt.yscale('log')
	plt.xscale('log')
	#plt.title(title)
	#plt.axis([40, 160, 0, 0.03])
	#plt.grid(True)
	#plt.show()

#end def

def filter_social_network(social_directed):
	
	#filter nodes with large out_degree
	remove_list = []
	for (node, val) in social_directed.out_degree():
		if val > 150:
			remove_list.append(node)
	social_directed.remove_nodes_from(remove_list)
	#print("After filtering large outdegree (nodes):")
	#print(nx.info(social_directed))
	
	#filter nodes with large in_degree
	remove_list = []
	for (node, val) in social_directed.in_degree():
		if val > 150:
			remove_list.append(node)
	social_directed.remove_nodes_from(remove_list)
	#print("After filtering large indegree (nodes):")
	#print(nx.info(social_directed))
	
	
	
	#filter edges with few calls
	remove_list = []
	for user_from, user_to, data in social_directed.edges(data=True):
		if data['num_calls'] < 3:# or data['duration'] < 0.5:
			remove_list.append((user_from,user_to))
		
	social_directed.remove_edges_from(remove_list)
	#print("After filtering few num_calls (edges):")
	#print(nx.info(social_directed))
	
	
	
	#filter edges with few calls
	remove_list = []
	for user_from, user_to, data in social_directed.edges(data=True):
		if data['duration'] < 0.5:
			remove_list.append((user_from,user_to))
		
	social_directed.remove_edges_from(remove_list)
	#print("After filtering small duration (edges):")
	#print(nx.info(social_directed))
	
	
	return social_directed
	
def filter_null_outdegree(social_directed,social_undirected):
	remove_list = []
	for (node, val) in social_directed.out_degree():
		if val == 0:
			remove_list.append(node)
	social_directed.remove_nodes_from(remove_list)
	social_undirected.remove_nodes_from(remove_list)
	
	return social_directed,social_undirected
	
def n_neighbor(G, id, n_hop):
	node = [id]
	node_visited = set()
	neighbors= []
	
	while n_hop !=0:
		neighbors= []
		for node_id in node:
			node_visited.add(node_id)
			neighbors +=  [id for id in G.neighbors(node_id) if id not in node_visited]
		node = neighbors
		n_hop -=1
		
		if len(node) == 0 :
			return neighbors 
		
	return neighbors

def get_random_nodes(social_undirected,num_friends):
	random_nodes = []
	social_undirected_nodes = social_undirected.nodes()
	for i in range(num_friends):
		random_nodes.append(random.choice(social_undirected_nodes))
	return random_nodes


def correct_network_data(social_directed,social_undirected):
	for user_from, user_to, data in social_undirected.edges(data=True):
		num_calls = 0
		duration = 0
		if social_directed.has_edge(user_from,user_to):
			num_calls = num_calls + social_directed[user_from][user_to]['num_calls']
			duration = duration + social_directed[user_from][user_to]['duration']
		if social_directed.has_edge(user_to,user_from):
			num_calls = num_calls + social_directed[user_to][user_from]['num_calls']
			duration = duration + social_directed[user_to][user_from]['duration']
			
		social_undirected[user_from][user_to]['num_calls'] = num_calls
		social_undirected[user_from][user_to]['duration'] = duration
	return social_undirected
#end


def calc_p(graph, node_i, node_j):
	wij = graph[node_i][node_j]['num_calls']
	w_plus = graph.out_degree(node_i, weight='num_calls')
	return wij/w_plus
	

def reciprocity(graph, node_i, node_j):
	try:
		pij = calc_p(graph, node_i, node_j)
		pji = calc_p(graph, node_j, node_i)
	except (KeyError, ZeroDivisionError):
		return math.inf	   
	
	ln = math.log
	
	# Ri j=|ln(pi j)−ln(pji)|\
	try:
		reciprocity = abs(ln(pij) - ln(pji))
	except ValueError:
		return math.inf
	return reciprocity
	
def calculate_all_reciprocities(digraph):
	reciprocity_of_nodes = {}
	all_reciprocities = []

	for node in digraph.nodes():
		reciprocity_of_neighbors = {}
		for neighbor in digraph.neighbors(node):
			rec_i_j = reciprocity(digraph, node, neighbor)
			
			reciprocity_of_neighbors[neighbor] = rec_i_j
			if rec_i_j !=0 and rec_i_j != math.inf:
				all_reciprocities.append(rec_i_j)
		reciprocity_of_nodes[node] = reciprocity_of_neighbors
