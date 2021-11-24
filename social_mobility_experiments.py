# %% codecell
import sys
import pandas as pd
from datetime import datetime
import time

import numpy as np
from scipy import spatial

import networkx as nx

import skmob
from skmob.measures.collective import visits_per_location

import social_cdr as scdr
import mobility_cdr as mcdr

import pickle

import matplotlib.pyplot as plt
from scipy.stats import pearsonr

import random

from cdlib import algorithms, evaluation
# %% codecell
def calculate_correlation(social_undirected):
	num_calls_list = []
	duration_list = []
	remove_list = []
	for user_from, user_to, data in social_undirected.edges(data=True):
		num_calls = data['num_calls']
		duration = data['duration']
		if duration < 1000:
			num_calls_list.append(num_calls)
			duration_list.append(duration)
		else:
			remove_list.append((user_from,user_to))
	#end
	
	social_undirected.remove_edges_from(remove_list)
	
	corr = pearsonr(num_calls_list, duration_list)
	print(corr)
	
	#plt.scatter(num_calls_list, duration_list)
	#plt.xlabel('num_calls')
	#plt.ylabel('duration')
	#plt.show()
#end
# %% codecell
def calculate_similarity_social_hops(social_undirected,traj_dict):
	all_1hop = []
	all_2hop = []
	all_3hop = []
	all_random = []
	for node in social_undirected.nodes():
		traj_vector_a = traj_dict[node]
		
		#print("vai calcular similarity")
		start_time = time.time()
		
		# Neighbors 1 hop
		#neighbors1 = scdr.n_neighbor(social_undirected,node, 1)
		neighbors1 = social_undirected.neighbors(node)
		cos_similarity1 = []
		#print(len(neighbors1))
		for neighbor in neighbors1:
			#print(neighbor)
			traj_vector_b = traj_dict[neighbor]
			cos_similarity = 1 - spatial.distance.cosine(traj_vector_a, traj_vector_b)
			cos_similarity1.append(cos_similarity)
		#print("terminou")
		#print(cos_similarity1)
		if len(cos_similarity1) > 0:
			all_1hop.append(np.mean(cos_similarity1))
		
		
		# Neighbors 2 hops
		neighbors2 = scdr.n_neighbor(social_undirected,node, 2)
		cos_similarity2 = []
		for neighbor in neighbors2:
			traj_vector_b = traj_dict[neighbor]
			cos_similarity = 1 - spatial.distance.cosine(traj_vector_a, traj_vector_b)
			cos_similarity2.append(cos_similarity)
		#print(cos_similarity2)
		if len(cos_similarity2) > 0:
			all_2hop.append(np.mean(cos_similarity2))
		
		
		# Neighbors 3 hops
		neighbors3 = scdr.n_neighbor(social_undirected,node, 3)
		cos_similarity3 = []
		for neighbor in neighbors3:
			traj_vector_b = traj_dict[neighbor]
			cos_similarity = 1 - spatial.distance.cosine(traj_vector_a, traj_vector_b)
			cos_similarity3.append(cos_similarity)
		#print(cos_similarity3)
		if len(cos_similarity3) > 0:
			all_3hop.append(np.mean(cos_similarity3))
			
			
		# Random nodes
		num_friends = len(cos_similarity1)
		random_nodes = scdr.get_random_nodes(social_undirected,num_friends)
		cos_similarity_random = []
		for neighbor in random_nodes:
			traj_vector_b = traj_dict[neighbor]
			cos_similarity = 1 - spatial.distance.cosine(traj_vector_a, traj_vector_b)
			cos_similarity_random.append(cos_similarity)
		if len(cos_similarity_random) > 0:
			all_random.append(np.mean(cos_similarity_random))
		
		#elapsed_time = time.time() - start_time
		#print(elapsed_time,"seconds for similarity")
		
	#end for node in social_undirected.nodes()
	
	print("Mean 1 hop:", np.mean(all_1hop))
	print("Mean 2 hop:", np.mean(all_2hop))
	print("Mean 3 hop:", np.mean(all_3hop))
	print("Mean random:", np.mean(all_random))
#end
# %% codecell
def jaccard_similarity(list1, list2):
	intersection = len(list(set(list1).intersection(list2)))
	union = (len(list1) + len(list2)) - intersection
	return float(intersection) / union
# %% codecell
def calculate_jaccard_similarity(social_undirected,traj_dict,parameters):
	
	nbins = 25
	all_jaccard = dict()
	for i in range(nbins):
		all_jaccard[i] = []
	
	
	for node in social_undirected.nodes():
		traj_vector_a = traj_dict[node]
		# Neighbors 1 hop
		#neighbors1 = scdr.n_neighbor(social_undirected,node, 1)
		neighbors1 = scdr.n_neighbor(social_undirected,node, 1)
		neighbors2 = scdr.n_neighbor(social_undirected,node, 2)
		
		neighbors_all = list(set(neighbors1+neighbors2))
		#print(neighbors_all)
		
		for neighbor in neighbors_all:
			friends_friends = scdr.n_neighbor(social_undirected,node, 1)
		
			#print(friends_friends)
			jaccard = jaccard_similarity(neighbors_all,friends_friends)
			
			
			node_bin = int(np.ceil(jaccard * (nbins - 1)))
		
			#print(jaccard)
		
			traj_vector_b = traj_dict[neighbor]
			cos_similarity = 1 - spatial.distance.cosine(traj_vector_a, traj_vector_b)
		
			all_jaccard[node_bin].append(cos_similarity)
			
		#end
	#end
	
	jaccard_list = []
	similarity_list = []
	for jaccard in all_jaccard:
		print(jaccard,len(all_jaccard[jaccard]))
		if len(all_jaccard[jaccard]) > 350:
			jaccard_list.append(jaccard/nbins)
			similarity_list.append(np.mean(all_jaccard[jaccard]))
	
		
	plt.plot(jaccard_list,similarity_list, color = parameters["color"], linewidth=1)
	#plt.plot(jaccard_list,similarity_list, parameters["style"], color = parameters["color"], label = parameters["label"], linewidth=2)
	#plt.tick_params(labelsize=30,size=20)
	plt.legend(loc="upper right")
	plt.xlabel('Jaccard',fontsize=14)
	plt.ylabel('Similarity',fontsize=14)
	
	
	#plt.plot(jaccard_list,similarity_list, parameters["style"], color = parameters["color"], label = parameters["label"], linewidth=2)
	
	#plt.show()
			
		
		
		
		
#end
# %% codecell
def calculate_ranked_friends(social_undirected,traj_dict,parameters):
	
	rank_dict = dict()
	for node in social_undirected.nodes():
		traj_vector_a = traj_dict[node]
		neighbors = social_undirected.neighbors(node)
		neighbors_list = []
		num_calls_list = []
		for neighbor in neighbors:
			neighbors_list.append(neighbor)
			num_calls_list.append(social_undirected[node][neighbor]['num_calls'])#/social_undirected[node][neighbor]['num_calls'])
		#end
		
		#print(neighbors_list)
		#print("num_calls:",num_calls_list)
		
		arg_sorted_neighbors = np.argsort(np.array(num_calls_list))
		#print("arg_sort",arg_sorted_neighbors)
		
		for i in range(len(neighbors_list)-1,-1,-1):
			#for pos in arg_sorted_neighbors:
			#pos = arg_sorted_neighbors[i]
			neighbor = neighbors_list[arg_sorted_neighbors[i]]
			
			#print(pos,neighbor,neighbors_list[pos],num_calls_list[pos])
						
			traj_vector_b = traj_dict[neighbor]
			cos_similarity = 1 - spatial.distance.cosine(traj_vector_a, traj_vector_b)
			
			rank = len(neighbors_list) - i
			#rank = pos
			if rank not in rank_dict:
				rank_dict[rank] = []
			#print(rank,neighbor,neighbors_list[arg_sorted_neighbors[i]],num_calls_list[arg_sorted_neighbors[i]])
			rank_dict[rank].append(cos_similarity)
			
		#end for
		#print(rank_dict)
		#exit()
	#end for node in social_undirected.nodes()
	
	print("foi")
	rank_list = []
	similarity_list = []
	for rank in rank_dict:
		#if rank <= 30:
		rank_list.append(rank)
		similarity_list.append(np.mean(rank_dict[rank]))
	#end
	
	print(rank_list)
	print(similarity_list)
	#print(rank_dict)
	plt.plot(rank_list,similarity_list, color = parameters["color"], linewidth=1)
	plt.plot(rank_list,similarity_list, parameters["style"], color = parameters["color"], label = parameters["label"], linewidth=2)
	#plt.tick_params(labelsize=30,size=20)
	plt.legend(loc="upper right")
	plt.xlabel('Rank (# calls)',fontsize=14)
	plt.ylabel('Similarity',fontsize=14)
	
#end
# %% codecell
def calculate_ranked_reciprocity(social_directed,traj_dict,parameters):
	
	rank_dict = dict()
	for node in social_directed.nodes():
		traj_vector_a = traj_dict[node]
		neighbors = social_directed.neighbors(node)
		neighbors_list = []
		reciprocity_list = []
		for neighbor in neighbors:
			neighbors_list.append(neighbor)
			
			reciprocity = scdr.reciprocity(social_directed,node,neighbor)
			reciprocity_list.append(reciprocity)
		#end
		
		#print(neighbors_list)
		#print("num_calls:",num_calls_list)
		
		arg_sorted_neighbors = np.argsort(np.array(reciprocity_list))
		#print("arg_sort",arg_sorted_neighbors)
		
		for i in range(len(neighbors_list)-1,-1,-1):
			#for pos in arg_sorted_neighbors:
			#pos = arg_sorted_neighbors[i]
			neighbor = neighbors_list[arg_sorted_neighbors[i]]
			
			#print(pos,neighbor,neighbors_list[pos],num_calls_list[pos])
						
			traj_vector_b = traj_dict[neighbor]
			cos_similarity = 1 - spatial.distance.cosine(traj_vector_a, traj_vector_b)
			
			rank = i + 1
			#rank = pos
			if rank not in rank_dict:
				rank_dict[rank] = []
			#print(rank,neighbor,neighbors_list[arg_sorted_neighbors[i]],num_calls_list[arg_sorted_neighbors[i]])
			rank_dict[rank].append(cos_similarity)
			
		#end for
		#print(rank_dict)
		#exit()
	#end for node in social_undirected.nodes()
	
	print("foi")
	rank_list = []
	similarity_list = []
	for rank in rank_dict:
		if rank <= 30:
			rank_list.append(rank)
			similarity_list.append(np.mean(rank_dict[rank]))
	#end
	
	print(rank_list)
	print(similarity_list)
	#print(rank_dict)
	
	rank_list, similarity_list = zip(*sorted(zip(rank_list, similarity_list)))
	
	plt.plot(rank_list,similarity_list, color = parameters["color"], linewidth=1)
	plt.plot(rank_list,similarity_list, parameters["style"], color = parameters["color"], label = parameters["label"], linewidth=2)
	#plt.tick_params(labelsize=30,size=20)
	plt.legend(loc="upper right")
	plt.xlabel('Rank (reciprocity)',fontsize=14)
	plt.ylabel('Similarity',fontsize=14)
	
	
#end
# %% codecell
def calculate_reciprocity_list(social_directed,traj_dict,parameters):
	
	rank_dict = dict()
	reciprocity_list = []
	for node in social_directed.nodes():
		neighbors = social_directed.neighbors(node)
		for neighbor in neighbors:
			reciprocity = scdr.reciprocity(social_directed,node,neighbor)
			reciprocity_list.append(reciprocity)
		#end
		
		#print(neighbors_list)
		#print("num_calls:",num_calls_list)
		
	#end for node in social_undirected.nodes()
	
	
	return reciprocity_list

#end
# %% codecell
def calculate_friends_unique_places(social_undirected,traj_dict,parameters):
	num_friends_dict = dict()
	for (node, val) in social_undirected.degree():
		num_friends = val
		traj_vec = traj_dict[node]
		num_places = sum(map(lambda x : x != 0, traj_vec))
		
		if num_friends not in num_friends_dict:
			num_friends_dict[num_friends] = []
		num_friends_dict[num_friends].append(num_places)
	#end
	
	
	num_friends_list = []
	num_places_list = []
	for num_friends in num_friends_dict:
		if num_friends <= 30:
			num_friends_list.append(num_friends)
			num_places_list.append(np.mean(num_friends_dict[num_friends]))
	#end
	
	#print(num_friends_list)
	#print(num_places_list)
	
	num_friends_list, num_places_list = zip(*sorted(zip(num_friends_list, num_places_list)))
	
	plt.plot(num_friends_list,num_places_list, color = parameters["color"], linewidth=1)
	plt.plot(num_friends_list,num_places_list, parameters["style"], color = parameters["color"], label = parameters["label"], linewidth=2)
	#plt.tick_params(labelsize=30,size=20)
	plt.legend(loc="upper right")
	plt.xlabel('# of friends',fontsize=14)
	plt.ylabel('# of unique places',fontsize=14)
#end
# %% codecell
def calculate_reciprocity(region):
	social_directed = nx.read_gml('social_networks/%s_social_directed_filtered.gml' % region)
	print(nx.reciprocity(social_directed))
	
	social_directed_no_null_outdegree = nx.read_gml('social_networks/%s_social_directed_no_null_outdegree.gml' % region)
	print(nx.reciprocity(social_directed_no_null_outdegree))
# %% codecell
def cdf(x, plot=True, *args, **kwargs):
	x, y = sorted(x), np.arange(len(x)) / len(x)
	
	print(np.arange(len(x)))
	plt.plot(x, y, *args, **kwargs)
	plt.show()
# %% codecell
def ccdf(x, xlabel, ylabel, parameters):
	x, y = sorted(x,reverse=True), np.arange(len(x)) / len(x)
	
	plt.plot(x, y,color = parameters["color"],label = parameters["label"], linewidth=3)
	plt.legend(loc="upper right", prop={"size":18})
	plt.xlabel(xlabel,fontsize=20)
	plt.ylabel(ylabel,fontsize=20)
	
	plt.tick_params(axis='both', which='major', labelsize=16)
	
	#ax.set_xticklabels(xticklabels, fontsize=12)
	#ax.set_xticklabels(yticklabels, fontsize=12)
	
	
	
	plt.yscale('log')
	plt.xscale('log')
# %% codecell
def plot_similarity_hops():
	
	labels = ['1 hop','2 hops','3 hops','random']
	
	similarity_sjdr = [0.6877017325862492,0.5412426001930376,0.44191102936537185,0.06496870032335639]
	similarity_jf = [0.4270352122806851,0.24532627467520204,0.15570176482093037,0.04735678935674234]
	
	x = np.arange(len(labels))  # the label locations
	width = 0.35  # the width of the bars
	
	fig, ax = plt.subplots(figsize=(10,10))
	rects1 = ax.bar(x - width/2, similarity_sjdr, width, label='SJDR', color = 'tab:red')
	rects2 = ax.bar(x + width/2, similarity_jf, width, label='JF', color = 'tab:blue')
	
	# Add some text for labels, title and custom x-axis tick labels, etc.
	ax.set_xlabel('Social distance')
	ax.set_ylabel('Similarity')
	ax.set_xticks(x)
	ax.set_xticklabels(labels)
	ax.legend()

	#fig.tight_layout()

	#plt.show()
# %% codecell
def link_overlap(social_undirected,traj_dict):
	degree_list = {}
	for (node, val) in social_undirected.degree():
		degree_list[node] = val
	
	edge_duration_list = []
	edge_num_calls_list = []
	link_overlap_list = []
	for user_from, user_to, data in social_undirected.edges(data=True):
		edge_duration_list.append(data['duration'])
		edge_num_calls_list.append(data['num_calls'])
		
		neighbors_user_from = scdr.n_neighbor(social_undirected,user_from, 1)
		neighbors_user_to = scdr.n_neighbor(social_undirected,user_to, 1)
		
		number_common_neighbors = len(list(set(neighbors_user_from).intersection(neighbors_user_to)))
		degree_user_from = degree_list[user_from]
		degree_user_to = degree_list[user_to]
		
		if number_common_neighbors > 0:
			link_overlap_edge = number_common_neighbors / ((degree_user_from - 1) + (degree_user_to - 1) - number_common_neighbors)
			
		else:
			link_overlap_edge = 0
			
		
		if link_overlap_edge != 0 and link_overlap_edge != 1:
			link_overlap_list.append(link_overlap_edge)
		
		
	return [link_overlap_list,edge_duration_list]
# %% codecell
def plot_link_overlap(link_overlap_list,edge_duration_list, xlabel, ylabel, parameters):
	
	
	max_duration = max(edge_duration_list)
	print(max_duration)
	
	nbins = 25
	all_duration = dict()
	for i in range(nbins):
		all_duration[i] = []
	
	for duration,link_overlap in zip(edge_duration_list,link_overlap_list):
				
		plot_bin = int(np.ceil(duration/max_duration * (nbins - 1)))
		
		all_duration[plot_bin].append(link_overlap)
		
	#end
	
	duration_list = []
	link_list = []
	for duration in all_duration:
		#print(jaccard,len(all_jaccard[jaccard]))
		#if len(all_duration[duration]) > 350:
		duration_list.append(duration/max_duration/nbins)
		link_list.append(np.mean(all_duration[duration]))
	
	
	
	#edge_list_duration, y = sorted(edge_list_duration,reverse=True), np.arange(len(edge_list_duration)) / len(edge_list_duration)
	
	plt.plot(duration_list,link_list,color = parameters["color"],label = parameters["label"], linewidth=2)
	plt.legend(loc="upper right")
	plt.xlabel(xlabel,fontsize=14)
	plt.ylabel(ylabel,fontsize=14)
	
	#plt.yscale('log')
	#plt.xscale('log')
#end


#####################################################################
#####################################################################
#####################################################################


def run_num_calls_distribution_classes(colors_list,labels_list,num_classes,social_undirected,region):
	
	for class_index in range(num_classes):
		print("class:",class_index+1)
		parameters = {}
		parameters["color"] = colors_list[class_index] # Esquema de cores a ser usado nos gráficos
		parameters["label"] = labels_list[class_index] # Label a ser usado nos gráficos
		parameters["style"] = "x" # Estilo de marcação nos gráficos (preciso acertar um estilo pra cada classe, se precisar)
		
		
		num_calls_class = []
		for user_from, user_to, data in social_undirected.edges(data=True):
			if social_undirected.nodes[user_from]['income_class'] == class_index+1:
				num_calls_class.append(social_undirected[user_from][user_to]['num_calls'])
			if social_undirected.nodes[user_to]['income_class'] == class_index+1:
				num_calls_class.append(social_undirected[user_to][user_from]['num_calls'])
		#end
		
		ccdf(num_calls_class,'# calls','P(> # calls)',parameters)

	parameters = {}
	parameters["color"] = colors_list[7] # Esquema de cores a ser usado nos gráficos
	parameters["label"] = labels_list[7] # Label a ser usado nos gráficos
	parameters["style"] = "x" # Estilo de marcação nos gráficos (preciso acertar um estilo pra cada classe, se precisar)
	degrees_class = []
	for user_from, user_to, data in social_undirected.edges(data=True):
		num_calls_class.append(social_undirected[user_from][user_to]['num_calls'])
		num_calls_class.append(social_undirected[user_to][user_from]['num_calls'])
	#end
	ccdf(num_calls_class,'# calls','P(> # calls)',parameters)
	
	plt.legend(prop={"size":18})

	plt.tight_layout()
	plt.savefig("results/%s/num_calls_distribution.svg" % (region))
	plt.clf()
#end



def run_degree_distribution_classes(colors_list,labels_list,num_classes,social_undirected,region):
	
	for class_index in range(num_classes):
		print("class:",class_index+1)
		parameters = {}
		parameters["color"] = colors_list[class_index] # Esquema de cores a ser usado nos gráficos
		parameters["label"] = labels_list[class_index] # Label a ser usado nos gráficos
		parameters["style"] = "x" # Estilo de marcação nos gráficos (preciso acertar um estilo pra cada classe, se precisar)
		
		degrees_class = []
		for (node, val) in social_undirected.degree():
			if social_undirected.nodes[node]['income_class'] == class_index+1:
				degrees_class.append(val)
		ccdf(degrees_class,'k','P(> k)',parameters)


	parameters = {}
	parameters["color"] = colors_list[7] # Esquema de cores a ser usado nos gráficos
	parameters["label"] = labels_list[7] # Label a ser usado nos gráficos
	parameters["style"] = "x" # Estilo de marcação nos gráficos (preciso acertar um estilo pra cada classe, se precisar)
	degrees_class = []
	for (node, val) in social_undirected.degree():
		degrees_class.append(val)
	ccdf(degrees_class,'k','P(> k)',parameters)
	
	plt.legend(prop={"size":18})

	plt.tight_layout()
	plt.savefig("results/%s/degree.svg" % (region))
	plt.clf()
#end


def calculate_ranked_friends_classes(social_network,traj_dict,colors_list,labels_list,num_classes,ref_class,region,type_rank,limit_rank):
	
	
	for class_index in range(num_classes):
		print("ref_class:",ref_class+1," x class:",class_index+1)
		
		rank_dict = dict()
		for node in social_network.nodes():
			if social_network.nodes[node]['income_class'] == ref_class+1:
				traj_vector_a = traj_dict[node]
				neighbors = social_network.neighbors(node)
				neighbors_list = []
				num_calls_list = []
				for neighbor in neighbors:
					if social_network.nodes[neighbor]['income_class'] == class_index + 1:
						neighbors_list.append(neighbor)
						
						if type_rank == 'reciprocity':
							reciprocity = scdr.reciprocity(social_network,node,neighbor)
							num_calls_list.append(reciprocity)
						elif type_rank == 'num_calls':			
							num_calls_list.append(social_network[node][neighbor]['num_calls'])#/social_network[node][neighbor]['num_calls'])
						#end
					#end
				#end
				
				arg_sorted_neighbors = np.argsort(np.array(num_calls_list))
				for i in range(len(neighbors_list)-1,-1,-1):
					neighbor = neighbors_list[arg_sorted_neighbors[i]]
					traj_vector_b = traj_dict[neighbor]
					cos_similarity = 1 - spatial.distance.cosine(traj_vector_a, traj_vector_b)
					if type_rank == 'reciprocity':
						rank = i + 1
					elif type_rank == 'num_calls':
						rank = len(neighbors_list) - i
					
					if rank not in rank_dict:
						rank_dict[rank] = []
					#end
					rank_dict[rank].append(cos_similarity)
				#end
			#end
		#end
		
		rank_list = []
		similarity_list = []
		for rank in rank_dict:
			if rank <= limit_rank:
				rank_list.append(rank)
				similarity_list.append(np.mean(rank_dict[rank]))
			#end
		#end
		
		parameters = {}
		parameters["color"] = colors_list[class_index] # Esquema de cores a ser usado nos gráficos
		parameters["label"] = labels_list[class_index] # Label a ser usado nos gráficos
		parameters["style"] = "x" # Estilo de marcação nos gráficos (preciso acertar um estilo pra cada classe, se precisar)
		
		if type_rank == 'reciprocity':
			if len(similarity_list) > 0:
				rank_list, similarity_list = zip(*sorted(zip(rank_list, similarity_list)))
		#end
		
		plt.plot(rank_list,similarity_list, color = parameters["color"], label = parameters["label"],linewidth=2)
		plt.plot(rank_list,similarity_list, parameters["style"], color = parameters["color"], linewidth=2)
		
	#end
	
	
	
	
	class_index = 7
	print("ref_class:",ref_class+1," x class:",class_index+1)
	
	rank_dict = dict()
	for node in social_network.nodes():
		if social_network.nodes[node]['income_class'] == ref_class+1:
			traj_vector_a = traj_dict[node]
			neighbors = social_network.neighbors(node)
			neighbors_list = []
			num_calls_list = []
			for neighbor in neighbors:
				#if social_network.nodes[neighbor]['income_class'] == class_index + 1:
				neighbors_list.append(neighbor)
				
				if type_rank == 'reciprocity':
					reciprocity = scdr.reciprocity(social_network,node,neighbor)
					num_calls_list.append(reciprocity)
				elif type_rank == 'num_calls':
					num_calls_list.append(social_network[node][neighbor]['num_calls'])#/social_network[node][neighbor]['num_calls'])
				#end
			#end
			
			arg_sorted_neighbors = np.argsort(np.array(num_calls_list))
			for i in range(len(neighbors_list)-1,-1,-1):
				neighbor = neighbors_list[arg_sorted_neighbors[i]]
				traj_vector_b = traj_dict[neighbor]
				cos_similarity = 1 - spatial.distance.cosine(traj_vector_a, traj_vector_b)
				rank = len(neighbors_list) - i
				if rank not in rank_dict:
					rank_dict[rank] = []
				#end
				rank_dict[rank].append(cos_similarity)
			#end
		#end
	#end
	
	rank_list = []
	similarity_list = []
	for rank in rank_dict:
		if rank <= limit_rank:
			rank_list.append(rank)
			similarity_list.append(np.mean(rank_dict[rank]))
		#end
	#end
	
	parameters = {}
	parameters["color"] = colors_list[class_index] # Esquema de cores a ser usado nos gráficos
	parameters["label"] = labels_list[class_index] # Label a ser usado nos gráficos
	parameters["style"] = "x" # Estilo de marcação nos gráficos (preciso acertar um estilo pra cada classe, se precisar)
	
	if type_rank == 'reciprocity':
		if len(similarity_list) > 0:
			rank_list, similarity_list = zip(*sorted(zip(rank_list, similarity_list)))
		#end
	
	plt.plot(rank_list,similarity_list, color = parameters["color"], label = parameters["label"], linewidth=2)
	plt.plot(rank_list,similarity_list, parameters["style"], color = parameters["color"], linewidth=2)
	
	
	plt.tick_params(axis='both', which='major', labelsize=16)
	#plt.legend(loc="upper right", prop={"size":18})
	plt.legend(prop={"size":18})
	
	## reciprocity
	if type_rank == 'reciprocity':
		plt.xlabel('Rank (reciprocity)',fontsize=20)
	elif type_rank == 'num_calls':
		plt.xlabel('Rank (# calls)',fontsize=20)
	#end
	
	##
	plt.ylabel('Similarity',fontsize=20)
	
	#plt.tight_layout()
	
	
	plt.savefig("results/%s/ranked_friends_%s_%d_class%s.svg" % (region,type_rank,limit_rank,ref_class+1))
	
	
	plt.clf()
#end def


def plot_correlation_classes(social_undirected,labels_list,num_classes,region):

	corr_matrix = np.zeros((num_classes,num_classes),float)
	
	for user_from, user_to, data in social_undirected.edges(data=True):
		class_from = social_undirected.nodes[user_from]['income_class']
		class_to = social_undirected.nodes[user_to]['income_class']
		
		if(class_from != -1 and class_to != -1):
			corr_matrix[class_from-1][class_to-1] = corr_matrix[class_from-1][class_to-1] + 1
			corr_matrix[class_to-1][class_from-1] = corr_matrix[class_to-1][class_from-1] + 1
	#end
	
	print(corr_matrix)
	
	print(np.sum(corr_matrix))
	
	for line in range(num_classes):
		if(np.sum(corr_matrix[line,:]) != 0):
			corr_matrix[line,:] = corr_matrix[line,:] / np.sum(corr_matrix[line,:])
	
	fig, ax = plt.subplots()
	im = ax.imshow(corr_matrix,cmap='Blues')

	# We want to show all ticks...
	ax.set_xticks(np.arange(len(labels_list)-1))
	ax.set_yticks(np.arange(len(labels_list)-1))
	# ... and label them with the respective list entries
	ax.set_xticklabels(labels_list[0:7])
	ax.set_yticklabels(labels_list[0:7])

	# Rotate the tick labels and set their alignment.
	plt.setp(ax.get_xticklabels(), rotation=45, ha="right",rotation_mode="anchor")
	
	# Loop over data dimensions and create text annotations.
	for i in range(len(labels_list)-1):
		for j in range(len(labels_list)-1):
			text = ax.text(j, i, "%.2f" % corr_matrix[i, j],ha="center", va="center", color="gray",fontsize=12)

	fig.tight_layout()
	#plt.show()	
		
	#plt.legend(prop={"size":14})
	
	plt.tick_params(axis='both', which='major', labelsize=14)
	
	plt.savefig("results/%s/correlation_classes.svg" % (region))
	plt.clf()
#end def




def calculate_similarity_classes(social_undirected,traj_dict,colors_list,labels_list,num_classes,region):
	
	nodes_class = []
	print("entrou")
	nodes_class1 = [x for x,y in social_undirected.nodes(data=True) if y['income_class']==1]
	nodes_class.append(nodes_class1)
	print('nodes class 1 = ',len(nodes_class1))
	nodes_class2 = [x for x,y in social_undirected.nodes(data=True) if y['income_class']==2]
	nodes_class.append(nodes_class2)
	print('nodes class 2 = ',len(nodes_class2))
	nodes_class3 = [x for x,y in social_undirected.nodes(data=True) if y['income_class']==3]
	nodes_class.append(nodes_class3)
	print('nodes class 3 = ',len(nodes_class3))
	nodes_class4 = [x for x,y in social_undirected.nodes(data=True) if y['income_class']==4]
	nodes_class.append(nodes_class4)
	print('nodes class 4 = ',len(nodes_class4))
	nodes_class5 = [x for x,y in social_undirected.nodes(data=True) if y['income_class']==5]
	nodes_class.append(nodes_class5)
	print('nodes class 5 = ',len(nodes_class5))
	nodes_class6 = [x for x,y in social_undirected.nodes(data=True) if y['income_class']==6]
	nodes_class.append(nodes_class6)
	print('nodes class 6 = ',len(nodes_class6))
	nodes_class7 = [x for x,y in social_undirected.nodes(data=True) if y['income_class']==7]
	nodes_class.append(nodes_class7)
	print('nodes class 7 = ',len(nodes_class7))
	
	total_nodes = len(nodes_class1) + len(nodes_class2) + len(nodes_class3) + len(nodes_class4) + len(nodes_class5) + len(nodes_class6) + len(nodes_class7)
	print('total nodes = ',total_nodes)
	
	
	nodes_other = [x for x,y in social_undirected.nodes(data=True) if y['income_class'] not in [1,2,3,4,5,6,7]] 
	print('nodes other = ',len(nodes_other))
	
	
	
	similarity_matrix = np.zeros((num_classes,num_classes),float)
	# Para cada classe de referência
	for ref_class in range(num_classes):
		if len(nodes_class[ref_class]) > 0:
			# Escolher 100 representantes aleatórios _nodes_ref_class
			random_nodes_ref_class = []
			for i in range(1000):
				random_nodes_ref_class.append( random.choice(nodes_class[ref_class]) )
			#end
			
			# Para cada uma das outras classes
			for class_index in range(num_classes):
				similarity_list = []
				if len(nodes_class[class_index]) > 0:
					# Escolher 100 representantes aleatórios random_nodes_class_index
					random_nodes_class_index = []
					for i in range(1000):
						random_nodes_class_index.append( random.choice(nodes_class[class_index]) )
					
					
					for ref_class_node in random_nodes_ref_class:
						for class_index_node in random_nodes_class_index:
							traj_vector_a = traj_dict[ref_class_node]
							traj_vector_b = traj_dict[class_index_node]
							cos_similarity = 1 - spatial.distance.cosine(traj_vector_a, traj_vector_b)
							
							similarity_list.append( cos_similarity )
						#emd
					#end
					similarity_matrix[ref_class][class_index] = np.mean(similarity_list)
				#end
			#end
		#end
	#end
	print(similarity_matrix)
	
	#similarity_matrix = [[1,2,3,4,5,0,0],[2,4,5,6,7,0,0],[5,6,7,8,1,0,0],[2,3,4,5,6,0,0],[6,5,4,3,2,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0]]
	#similarity_matrix = np.array(similarity_matrix)
		
	# https://shantoroy.com/python/python-bar-chart-using-matplotlib/
	
	#figure(num=None, figsize=(14, 7))
	
	fig, ax = plt.subplots(figsize=(12,10))
	#t_1 = [854, 1185, 1860, 377, 352]
	#t_2 = [258005, 385351, 800054, 194111, 99980]
	#t_3 = [26794, 39706, 78924, 18066, 8666]
	#t_4 = [1491, 2032, 4358, 765, 469]

	labels = []
	for i in range(num_classes):
		labels.append(labels_list[i])
	
	
	#Labels=['test-1', 'test-2', 'test-3',  'test-4', 'test-5']
	y_pos=np.arange(num_classes)
	#y_pos = []
	#for i in range(num_classes):
	#	y_pos.append(i)
		#y_pos[i] = y_pos[i]# + (3 * 0.12)
	
	for i in range(num_classes):
		bar = similarity_matrix[:,i]
		#print(i,bar)
		plt.bar(y_pos + (i * 0.12) , bar, width=0.12, color=colors_list[i] , label=labels_list[i])
	#end
	
	#plt.bar(y_pos + 0, t_1,width=0.2, color = 'navy' , label='test label-1')
	#plt.bar(y_pos + 0.2,t_2, width=0.2,color = 'skyblue',label = 'test label-2')
	#plt.bar(y_pos + 0.4, t_3,width=0.2, color = 'darkcyan' , label='test label-3')
	#plt.bar(y_pos + 0.6, t_4,width=0.2, color = 'black' , label='test label-4')
	
	t_pos = []
	for i in range(num_classes):
		t_pos.append(i + (3 * 0.12) )
		#print("")
	
	plt.xticks(t_pos, labels)
	plt.legend()
	plt.ylabel('Similarity',fontsize=20)
	plt.xlabel('Income class',fontsize=20)
	
	plt.legend(prop={"size":18})
	
	plt.tick_params(axis='both', which='major', labelsize=16)
	
	plt.savefig("results/%s/similarity_classes.svg" % (region))
	plt.clf()
	
	
	
	
	"""
	
	# set width of bars
	barWidth = 0.2
	 
	# Set position of bar on X axis
	r = []
	r.append(np.arange(num_classes))
	for i in range(1,num_classes,1):
		r.append([x * barWidth for x in r[i-1]])
	 
	
	labels = []
	for i in range(num_classes):
		labels.append(labels_list[i])
		plt.bar(r[i], similarity_matrix[:][i], color=colors_list[i], width=barWidth, edgecolor='white', label=labels_list[i])
	
	# Make the plot
	###plt.bar(r1, bars1, color='#7f6d5f', width=barWidth, edgecolor='white', label='var1')
	###plt.bar(r2, bars2, color='#557f2d', width=barWidth, edgecolor='white', label='var2')
	###plt.bar(r3, bars3, color='#2d7f5e', width=barWidth, edgecolor='white', label='var3')
	 
	# Add xticks on the middle of the group bars
	plt.xlabel('Income class')
	plt.xlabel('Similarity')
	plt.xticks([rr + barWidth*2 + barWidth for rr in range(num_classes) ],labels)
	 
	# Create legend & Show graphic
	plt.legend()
	"""
	
	
	
	
	"""
	
	
	
	x = np.arange(num_classes)  # the label locations
	fig, ax = plt.subplots(figsize=(20,20))
	labels = []
	for i in range(num_classes):
		labels.append(labels_list[i])
		width = 0.15  # the width of the bars
		rects = ax.bar(x - int(num_classes/2) +  (int(num_classes/2) * i) , similarity_matrix[i,:], width, label=labels_list[i], color = colors_list[i])
	#end
	
	
	#rects1 = ax.bar(x - width/2, similarity_sjdr, width, label='SJDR', color = 'tab:red')
	#rects2 = ax.bar(x + width/2, similarity_jf, width, label='JF', color = 'tab:blue')
	
	# Add some text for labels, title and custom x-axis tick labels, etc.
	ax.set_xlabel('Income class')
	ax.set_ylabel('Similarity')
	ax.set_xticks(x)
	ax.set_xticklabels(labels)
	ax.legend()
	fig.tight_layout()
	"""

	
#end def






		
	
	
"""
	rank_dict = dict()
	for node in social_undirected.nodes():
		traj_vector_a = traj_dict[node]
		neighbors = social_undirected.neighbors(node)
		neighbors_list = []
		num_calls_list = []
		for neighbor in neighbors:
			neighbors_list.append(neighbor)
			num_calls_list.append(social_undirected[node][neighbor]['num_calls'])#/social_undirected[node][neighbor]['num_calls'])
		#end
		
		#print(neighbors_list)
		#print("num_calls:",num_calls_list)
		
		arg_sorted_neighbors = np.argsort(np.array(num_calls_list))
		#print("arg_sort",arg_sorted_neighbors)
		
		for i in range(len(neighbors_list)-1,-1,-1):
			#for pos in arg_sorted_neighbors:
			#pos = arg_sorted_neighbors[i]
			neighbor = neighbors_list[arg_sorted_neighbors[i]]
			
			#print(pos,neighbor,neighbors_list[pos],num_calls_list[pos])
						
			traj_vector_b = traj_dict[neighbor]
			cos_similarity = 1 - spatial.distance.cosine(traj_vector_a, traj_vector_b)
			
			rank = len(neighbors_list) - i
			#rank = pos
			if rank not in rank_dict:
				rank_dict[rank] = []
			#print(rank,neighbor,neighbors_list[arg_sorted_neighbors[i]],num_calls_list[arg_sorted_neighbors[i]])
			rank_dict[rank].append(cos_similarity)
			
		#end for
		#print(rank_dict)
		#exit()
	#end for node in social_undirected.nodes()
	
	print("foi")
	rank_list = []
	similarity_list = []
	for rank in rank_dict:
		#if rank <= 30:
		rank_list.append(rank)
		similarity_list.append(np.mean(rank_dict[rank]))
	#end
	
	print(rank_list)
	print(similarity_list)
	#print(rank_dict)
	plt.plot(rank_list,similarity_list, color = parameters["color"], linewidth=1)
	plt.plot(rank_list,similarity_list, parameters["style"], color = parameters["color"], label = parameters["label"], linewidth=2)
	#plt.tick_params(labelsize=30,size=20)
	plt.legend(loc="upper right")
	plt.xlabel('Rank (# calls)',fontsize=14)
	plt.ylabel('Similarity',fontsize=14)
	
#end
"""
	
	



# %% codecell
# Os comentários do código são voltados às análise realizadas para o artigo
# do Brasnam ("Caracterização da relação entre redes sociais e mobilidade de
# indivíduos em contextos urbanos")

# Cada gráfico e análise do paper é resultado de uma função deste código.
# Então a cada vez que preciso de um gráfico, eu descomento a linha correspondente 
# à análise e comento as outras.


# Nessa linha eu abro uma figura única, que vai guardar os gráficos com 
# as análises de todas as cidades
# (no caso paper do Branam, foram apenas SJDR e JF)
fig= plt.figure(figsize=(10,10))


# Essa função plota o gráfico da Fig. 5(a).
# Eu não passo nada pra ela (os valores são todos previamente calculados).
# (por isso essa função ficou um pouco mais distante das outras)
# O cálculo desses valores é feito na função calculate_similarity_social_hops e levam bastante tempo
# (especialmente pra JF).
#plot_similarity_hops()
#plt.savefig("results/similarity_hops.svg")

# Aqui eu defino algumas propriedades da execução, para tornar mais clara a visualização
# Se quiser rodar outra cidade, tem que definir os seus parâmetros em outro trecho,
region = 'sjdr' # Nome da região, para referência no código
prefix = '/media/vinicius/vinicius-HDD3TB/TODAS_UFS_CDR/%s/' % (region)
#prefix = '/media/vinicius/c481e5d8-7446-40fe-9f30-32cfd502a796/social_mobility_data/%s/' % (region)

# Temos duas versõs das redes sociais, uma direcionada e uma não direcionada,
# cada tipo de análise vai demandar um tipo de rede.
# As redes já foram previamente computadas pelo código do arquivo build_social_network.py,
# que demora bastante para ser executado.
# É bom dar preferência para o uso das redes com "_no_null_outdegree" porque todos
# os nós delas realizaram chamadas e, por isso, têm marcação de geolocalização.
# [Mais recente] É melhor usar a versão "_no_null_outdegree_income_class", que já tem as classes como atributos
social_undirected = nx.read_gml('%s/social_networks/%s_social_undirected_no_null_outdegree_income_class.gml' %(prefix,region))
print("social_undirected ok")
print(nx.info(social_undirected))
social_directed = nx.read_gml('%s/social_networks/%s_social_directed_no_null_outdegree_income_class.gml' % (prefix,region))
print("social_directed ok")

# Esse trecho lê a estrutura de dados que guarda as trajetórias dos indivíduos,
# que é um dicionário. Isso já foi computado previamente no arquivo mobility_cdr.py,
# que demora bastante para ser executado.
traj_filename = '%s/traj_vectors_%s.picke' % (prefix,region)
traj_file = open(traj_filename,'rb')
traj_dict = pickle.load(traj_file)
traj_file.close()
print("traj vectors ok")

# Esse trecho lê a estrutura de dados que guarda as informações de renda.
# (Mas, na real, acho que nem precisa, já que as rendas já estão nas redes sociais)
filename_users_residence_antenna = open('%s/dict_users_residence_antenna_%s.pickle' % (prefix,region),'rb')
dict_users_residence_antenna = pickle.load(filename_users_residence_antenna)
filename_users_residence_antenna.close()
filename_income_antenna = open('%s/dict_income_antenna_%s.pickle' % (prefix,region),'rb')
dict_income_antenna = pickle.load(filename_income_antenna)
filename_income_antenna.close()




# Agora a gente começa a conversar sobre experimentos de fato.
colors_list = ['tab:blue','tab:orange','tab:green','tab:red','tab:purple','tab:brown','tab:pink','tab:gray','tab:olive','tab:cyan']
labels_list = ['Class 1', 'Class 2', 'Class 3', 'Class 4', 'Class 5', 'Class 6', 'Class 7', 'All']
num_classes = 7

#run_degree_distribution_classes(colors_list,labels_list,num_classes,social_directed,region)

run_num_calls_distribution_classes(colors_list,labels_list,num_classes,social_undirected,region)

"""
parameters = {}
parameters["color"] = "blue" # Esquema de cores a ser usado nos gráficos
parameters["label"] = "all x all" # Label a ser usado nos gráficos
parameters["style"] = "x" # Estilo de marcação nos gráficos (preciso acertar um estilo pra cada classe, se precisar)
calculate_ranked_reciprocity(social_directed,traj_dict,parameters)
plt.savefig("results/%s/teste/reciprocity_similarity.svg" % (region))
"""



"""
limit_rank = 5
for ref_class in range(num_classes):
	calculate_ranked_friends_classes(social_directed,traj_dict,colors_list,labels_list,num_classes,ref_class,region,'reciprocity',limit_rank)
	print("foi", ref_class+1)
#end

limit_rank = 10
for ref_class in range(num_classes):
	calculate_ranked_friends_classes(social_directed,traj_dict,colors_list,labels_list,num_classes,ref_class,region,'reciprocity',limit_rank)
	print("foi", ref_class+1)
#end
"""

"""
limit_rank = 15
for ref_class in range(num_classes):
	calculate_ranked_friends_classes(social_directed,traj_dict,colors_list,labels_list,num_classes,ref_class,region,'reciprocity',limit_rank)
	print("foi", ref_class+1)
#end
"""

#"""
limit_rank = 5
for ref_class in range(num_classes):
	calculate_ranked_friends_classes(social_undirected,traj_dict,colors_list,labels_list,num_classes,ref_class,region,'num_calls',limit_rank)
	print("foi", ref_class+1)
#end

"""
limit_rank = 10
for ref_class in range(num_classes):
	calculate_ranked_friends_classes(social_undirected,traj_dict,colors_list,labels_list,num_classes,ref_class,region,'num_calls',limit_rank)
	print("foi", ref_class+1)
#end
"""
"""
limit_rank = 15
for ref_class in range(num_classes):
	calculate_ranked_friends_classes(social_undirected,traj_dict,colors_list,labels_list,num_classes,ref_class,region,'num_calls',limit_rank)
	print("foi", ref_class+1)
#end
"""

plot_correlation_classes(social_undirected,labels_list,num_classes,region)

calculate_similarity_classes(social_undirected,traj_dict,colors_list,labels_list,num_classes,region)




	
	
exit()



# Daqui pra baixo eu não vi nada ainda...












# Com a rede social e o dicionário de trajetórias calculados, as análises podem ser realizadas.

# Aqui, é importante dizer que na rede social os nós são as pessoas
# e uma aresta (i,j) existe se um indivíduo i liga para um indivíduo j.
# Uma aresta (i,j) guarda as informações agregadas de todas chamadas de i para j.
# Ou seja, não importa quantas ligações existam entre i e j, vai haver no máximo
# uma aresta (i,j). A aresta (i,j) tem duas propriedades:
# - "num_calls", que guarda o total de ligações de i para j.
# - "duration", que guarda o tempo total de ligação de i para j.
# Na versão não-direcionada, as propriedades "num_calls" e "duration" guardam o
# total de ligações e duração de i para j e de j para i.

# Essa função faz uma análise do link overlap como descrito por 
# Onnela, Jukka-Pekka & Saramäki, Jari & Hyvönen, J & Szabó, G & Lazer, David & Kaski, Kimmo & Kertész, János & Barabási, A.-L. (2007). Structure and Tie Strengths in Mobile Communication Networks. Proceedings of the National Academy of Sciences of the United States of America. 104. 7332-6. 10.1073/pnas.0610245104. 
link_overlap_list,edge_duration_list = link_overlap(social_undirected,traj_dict)
#plot_link_overlap(link_overlap_list,edge_duration_list,'link overlap','P',parameters)
ccdf(link_overlap_list,'link weight','P(> link weight)',parameters)




exit()



# Essa função faz uma análise da correlação entre as propriedades "num_calls" e "duration".
# Isso não entrou no paper, mas serviu para ver que meio que tanto faz usar uma ou outra.
#calculate_correlation(social_undirected)

# Essa função faz os cálculos da variação similaridade x hops (Fig 5(a)),
# que retorna os resultados que foram anotados e usados na função plot_similarity_hops
# lá em cima.
#calculate_similarity_social_hops(social_undirected,traj_dict)

# Essa função faz o cálculo que foi usado para as Fig. 4(a)
#calculate_ranked_friends(social_undirected,traj_dict,parameters)

# Essa função faz um cálculo de número de amigos X número de locais visitados,
# mas não entrou no paper.
# Eu fiquei com medo de que o número de amigos significasse apenas que um indivíduo
# fez mais chamadas e por isso ele visita mais lugares.
# Isso representaria um viés que eu preferi não expor no paper, por isso
# não coloquei esse gráfico.
#calculate_friends_unique_places(social_undirected,traj_dict,parameters)


# Nesse trecho eu identifico comunidades usando a biblioteca cdlib, usando o método
# de Louvain. Eu cheguei a considerar outros métodos, mas alguns testes que eu fiz
# mostraram que não ia ser muito diferente, então acabei usando só o Louvain mesmo.
# (no paper, usei o resultado desse trecho combinado com a Fig. 3(a) para discutir)
#partition = algorithms.louvain(social_undirected, resolution=1., randomize=False)
#mod = evaluation.newman_girvan_modularity(social_undirected,partition)
#print(mod)
#print(len(partition.communities))


# Nessa função eu calculo a reciprocidade das relações direcionadas, seguindo a
# metodologia de Chawla. O retorno é uma lista com as reciprocidades de todas
# as arestas da rede.
#reciprocity_list = calculate_reciprocity_list(social_directed,traj_dict,parameters)

# Essa função é um plor CCDF da reciprocidade (Fig. 3(b))
#ccdf(reciprocity_list,'reciprocity','P(> reciprocity)',parameters)

# Essa função é semelhante à calculate_ranked_friends, mas considerando a 
# reciprocidade (Fig. 4(b)).
#calculate_ranked_reciprocity(social_directed,traj_dict,parameters)

# O trecho abaixo pega os graus para a rede não-direcionada e para a rede direcionada
# e depois plota o CCDF (Fig. 1 (a)(b)(c))
#num_calls_list = []
#for user_from, user_to, data in social_undirected.edges(data=True):
#	num_calls_list.append(data['num_calls'])
#ccdf(num_calls_list,'# calls','P(> # calls)',parameters)
#degree_list = []
#for (node, val) in social_directed.out_degree():
#	degree_list.append(val)
#ccdf(degree_list,'k_out','P(> k_out)',parameters)


# Essa função calcula o coeficiente de Jaccard e faz a análise da Fig. 5(b).
#calculate_jaccard_similarity(social_undirected,traj_dict,parameters)


# A partir daqui, todo o código é repetido, para fazer a mesma análise para outra cidade.



#"""
region = 'sjdr'
parameters = {}
parameters["color"] = "tab:blue"
parameters["label"] = "JF"
parameters["style"] = "s"
social_undirected = nx.read_gml('social_networks/%s_social_undirected_no_null_outdegree.gml' % region)
#social_directed = nx.read_gml('social_networks/%s_social_directed_no_null_outdegree.gml' % region)

traj_filename = 'traj_vectors/%s_traj_vectors.picke' % region
traj_file = open(traj_filename,'rb')
traj_dict = pickle.load(traj_file)
traj_file.close()

#calculate_correlation(social_undirected)
#calculate_similarity_social_hops(social_undirected,traj_dict)
#calculate_ranked_friends(social_undirected,traj_dict,parameters)
#calculate_friends_unique_places(social_undirected,traj_dict,parameters)

#partition = algorithms.louvain(social_undirected, resolution=1., randomize=False)
#mod = evaluation.newman_girvan_modularity(social_undirected,partition)
#print(mod)
#print(len(partition.communities))
#calculate_reciprocity(region)

#calculate_ranked_reciprocity(social_directed,traj_dict,parameters)

#num_calls_list = []
#for user_from, user_to, data in social_undirected.edges(data=True):
#	num_calls_list.append(data['num_calls'])
#ccdf(num_calls_list,'# calls','P(> # calls)',parameters)

#degree_list = []
#for (node, val) in social_directed.out_degree():
#	degree_list.append(val)
#ccdf(degree_list,'k_out','P(> k_out)',parameters)

#calculate_jaccard_similarity(social_undirected,traj_dict,parameters)

#reciprocity_list = calculate_reciprocity_list(social_directed,traj_dict,parameters)
#print("foi 3")
#ccdf(reciprocity_list,'Reciprocity','P(> Reciprocity)',parameters)
#print("foi 4")

link_overlap_list,edge_duration_list = link_overlap(social_undirected,traj_dict)
#plot_link_overlap(link_overlap_list,edge_duration_list,'link overlap','P',parameters)
ccdf(link_overlap_list,'link weight','P(> link weight)',parameters)


# Aqui termina o código da outra cidade e eu já posso salvar a figura.

plt.savefig("results/ccdf_link_weight.svg")
# %% codecell

# %% codecell

