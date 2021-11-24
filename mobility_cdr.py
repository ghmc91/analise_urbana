import sys
import pandas as pd
from datetime import datetime

import numpy as np
from scipy import spatial

import skmob
from skmob.measures.collective import visits_per_location

import social_cdr as scdr


def get_trajectory_vector(cdr_filename_region,df_antennas,user):
	
	df_calls_user = []
	for df_cdr in pd.read_csv(cdr_filename_region, sep=';', iterator=True, chunksize=1000000):
		df_calls_user_chunk = df_cdr.loc[df_cdr['user_from'] == user]
		df_calls_user.append(df_calls_user_chunk)
	df_calls_user = pd.concat(df_calls_user)
		

	#print(df_calls_user)
	#print(df_antennas)
	
	num_locations = len(df_antennas.index)
	
	trajectory_vector = np.zeros(num_locations,int)
	
	for row in df_calls_user.itertuples():
		antenna_call = df_antennas.loc[df_antennas['CELLID'] == row.antenna]
		#print(antenna_call.index)
		trajectory_vector[antenna_call.index] = trajectory_vector[antenna_call.index] + 1
		
		
	return trajectory_vector
	
#end


def get_trajectory_dict(cdr_filename_region,df_antennas,social_undirected):

	traj_dict = dict()
	
	count = 0
	for node in social_undirected.nodes():
		traj_vector = get_trajectory_vector(cdr_filename_region,df_antennas,node)
		traj_dict[node] = traj_vector
		print(count)
		count = count + 1
	#end
	
	return traj_dict
#end

def get_trajectory_dict_large_cdr(cdr_filename_region,df_antennas,social_undirected):

	
	num_locations = len(df_antennas.index)
	traj_dict = dict()
	
	for node in social_undirected.nodes():
		traj_dict[node] = np.zeros(num_locations,int)
	#end
	
	print("zerou")
	for df_cdr in pd.read_csv(cdr_filename_region, sep=';', iterator=True, chunksize=1000000):
		for row in df_cdr.itertuples():
			user_from = row.user_from
			antenna = row.antenna
			antenna_call = df_antennas.loc[df_antennas['CELLID'] == antenna]
			if user_from in social_undirected:
				traj_dict[user_from][antenna_call.index] = traj_dict[user_from][antenna_call.index] + 1
		#end
	#end
	
	return traj_dict
	
#end
