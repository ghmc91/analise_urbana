# %% codecell
import sys
import pandas as pd
import datetime
import csv
import pickle

import networkx as nx
import skmob
from skmob.measures.individual import radius_of_gyration
from skmob.measures.individual import k_radius_of_gyration
from skmob.measures.individual import uncorrelated_entropy
from skmob.measures.individual import maximum_distance
from skmob.measures.individual import number_of_locations
from skmob.measures.individual import max_distance_from_home


import seaborn as sns
import matplotlib.pyplot as plt

import numpy as np

# %% codecell
def read_df_from_file(filename):
	df = pd.read_csv(filename, sep=";")
	return df
# %% codecell


def cdr_df_to_dict(social_network,prefix,region):	

	# Nessa função eu pego o CSV e transformo em dicionários, já separados por classe.
	# Os dicionários são indexados pelo usuário, pelo dia  e pelo datetime da atividade.
	# Depois oe dicionários são salvos em arquivos do tipo "dict_cdr_sjdr_class1.pickle"
	# Dessa forma, fico com uma estrutura de dados muito mais enxuta e consigo, com facilidade, manipular uma cidade do porte de JF
	
	cdr_filename_region = '%s/cdr_regiao_imediata_%s_all_unique.txt' % (prefix,region)
	cdr_filename_region_out = '%s/cdr_regiao_imediata_%s_all_unique_filtered.txt' % (prefix,region)
	
	filename_users_residence_antenna = open('%s/dict_users_residence_antenna_%s.pickle' % (prefix,region),'rb')
	dict_users_residence_antenna = pickle.load(filename_users_residence_antenna)
	filename_users_residence_antenna.close()


	cdr_dict = []
	
	for class_index in range(7):
		cdr_dict.append( dict() )
		
	
	with open(cdr_filename_region,'r') as fin, open(cdr_filename_region_out,'w') as fout:
		reader = csv.DictReader(fin, delimiter=';')
		writer = csv.writer(fout, delimiter=';')
		fieldnames = ['date','time','duration','ddd_from','user_from','ddd_to','user_to','antenna','unknown1','type_code','type_desc','hold_from','hold_to','type_call_desc','type_call_code']
		writer.writerow(fieldnames)
		
		writer.writerow(fieldnames)
		
		count = 0
		count_except = 0
		for row in reader:
			# Usuário teve residência presumida
			if row['user_from'] in dict_users_residence_antenna:
				try:
					income_class = social_network.nodes[row['user_from']]['income_class']
					if income_class != -1:
											
						#print(row['user_from'])
						#print(row['date'])
						#print(row['time'])
						call_datetime = dt.datetime.fromisoformat('%s %s' % (row['date'], row['time']))
						#print(call_datetime)
						
						#print(call_datetime)
						#print(call_datetime.hour)
						#print(call_datetime.minute)
						
						time_interval = call_datetime.hour * 2
						if call_datetime.minute >= 30:
							time_interval += 1
							
						#print(call_datetime,type(call_datetime))
						if row['user_from'] not in cdr_dict[income_class - 1]:
							cdr_dict[income_class - 1][ row['user_from'] ] = dict()
							
						
						if row['date'] not in cdr_dict[income_class - 1][row['user_from']]:
							cdr_dict[income_class - 1][ row['user_from'] ][row['date']] = dict()
							
							
						cdr_dict[income_class - 1][row['user_from']][row['date']][call_datetime] = dict()
						cdr_dict[income_class - 1][row['user_from']][row['date']][call_datetime]['duration'] = row['duration']
						#cdr_dict[income_class - 1][row['user_from']][call_datetime]['user_to'] = row['user_to'] # não preciso do user_to para avaliar a mobilidade
						cdr_dict[income_class - 1][row['user_from']][row['date']][call_datetime]['antenna'] = row['antenna']
						
						cdr_dict[income_class - 1][row['user_from']][row['date']][call_datetime]['time_interval'] = time_interval
						
						#print(cdr_dict[income_class - 1])
						#print(count)
				except KeyError:
					count_except += 1
				
				count += 1
				#if(count == 30):
				#	break
			# end if row['user_from'] in dict_users_residence_antenna
		#end for row in reader
		
		print("\n\n\n\n\n +++++++++++")
		
		for class_index in range(7):
			#print(len(cdr_dict[class_index]))
			#print(cdr_dict[class_index])
			
			filename_dict_cdr = '%s/dict_cdr_%s_class%d.pickle' % (prefix,region,class_index+1)
			file_dict_cdr = open(filename_dict_cdr,'wb')
		
			pickle.dump(cdr_dict[class_index],file_dict_cdr)
			file_dict_cdr.close()
		#end
		
		print('count_except:', count_except)
#end def


region = 'jf' # Nome da região, para referência no código
prefix = '/media/vinicius/vinicius-HDD3TB/TODAS_UFS_CDR/%s/' % (region)

social_undirected = nx.read_gml('%s/social_networks/%s_social_undirected_no_null_outdegree_income_class.gml' %(prefix,region))
print("social_undirected ok")
cdr_df_to_dict(social_undirected,prefix,region)
#exit()
