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
# %% codecell

region = 'sjdr'
prefix = '/media/vinicius/vinicius-HDD3TB/TODAS_UFS_CDR/%s/' % region
#prefix = '/media/vinicius/c481e5d8-7446-40fe-9f30-32cfd502a796/social_mobility_data/%s/' % (region)

cdr_filename_region = '%s/cdr_regiao_imediata_%s_all_unique_filtered.txt' % (prefix,region)
antennas_filename_region = '%s/antennas_%s.txt' % (prefix,region)


df_antennas = pd.read_csv(antennas_filename_region, sep=';')
# %% codecell
social_directed = scdr.get_social_directed(cdr_filename_region)
print("Directed network (original):")
print(nx.info(social_directed))
print("===")
# %% codecell
social_directed = scdr.filter_social_network(social_directed)
print("Directed network (after filters):")
print(nx.info(social_directed))
print("===")
nx.write_gml(social_directed,'%s/social_networks/%s_social_directed_filtered.gml' % (prefix,region) )
# %% codecell
social_undirected = social_directed.to_undirected()
print("Undirected network:")
print(nx.info(social_undirected))
print("===")
nx.write_gml(social_directed,'%s/social_networks/%s_social_undirected_filtered.gml' % (prefix,region) )
# %% codecell
social_directed,social_undirected = scdr.filter_null_outdegree(social_directed,social_undirected)
print("Directed network (after removing null out-degree):")
print(nx.info(social_directed))
print("===")
nx.write_gml(social_directed,'%s/social_networks/%s_social_directed_no_null_outdegree.gml' % (prefix,region) )
# %% codecell
print("Undirected network (after removing null out-degree):")
print(nx.info(social_undirected))
print("===")
nx.write_gml(social_undirected,'%s/social_networks/%s_social_undirected_no_null_outdegree.gml' % (prefix,region) )
# %% codecell
social_undirected = scdr.correct_network_data(social_directed,social_undirected)
print("Undirected network (after removing null out-degree and correcting data):")
print(nx.info(social_undirected))
print("===")
nx.write_gml(social_undirected,'%s/social_networks/%s_social_undirected_no_null_outdegree.gml' % (prefix,region) ) 
# %% codecell
