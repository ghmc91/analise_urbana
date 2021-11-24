# %% codecell
import sys
import pandas as pd
from datetime import datetime

import matplotlib.pyplot as plt
from scipy import *

import numpy as np
import networkx as nx
import pickle

import space_process as sp
# %% codecell
region = 'sjdr'
prefix = '/media/vinicius/vinicius-HDD3TB/TODAS_UFS_CDR/%s/' % (region)
#prefix = '/media/vinicius/c481e5d8-7446-40fe-9f30-32cfd502a796/social_mobility_data/%s/' % (region)
cdr_filename_region = '%s/cdr_regiao_imediata_%s_all.txt' % (prefix,region)


print("%s/antennas_%s_unique.txt")
df_antennas = pd.read_csv("%s/antennas_%s_unique.txt" % (prefix,region), sep=";")
print(df_antennas)

# Carregando residências dos usuários.
filename_users_residence_antenna = open('%s/dict_users_residence_antenna_%s.pickle' % (prefix,region),'rb')
dict_users_residence_antenna = pickle.load(filename_users_residence_antenna)
filename_users_residence_antenna.close()
#print(dict_users_residence_antenna['5B5F2C071D12AF13219DF5EBE05132AF'])

# Trabalhando com espaço.
# %% codecell
#city_list = ['SÃO JOÃO DEL REI', 'TIRADENTES', 'SÃO VICENTE DE MINAS', 'SÃO TIAGO', 'SANTA CRUZ DE MINAS', 'RITÁPOLIS', 'RESENDE COSTA', 'PRADOS', 'PIEDADE DO RIO GRANDE', 'NAZARENO', 'CORONEL XAVIER CHAVES', 'CONCEIÇÃO DA BARRA DE MINAS', 'MADRE DE DEUS DE MINAS', 'LAGOA DOURADA']
city_list = ['ANDRELÂNDIA','ARACITABA','ARANTINA','BELMIRO BRAGA','BIAS FORTES','BOCAINA DE MINAS','BOM JARDIM DE MINAS','CHÁCARA','CHIADOR','CORONEL PACHECO','EWBANK DA CÂMARA','GOIANÁ','JUIZ DE FORA','LIBERDADE','LIMA DUARTE','MATIAS BARBOSA','OLARIA','OLIVEIRA FORTES','PAIVA','PASSA VINTE','PEDRO TEIXEIRA','PIAU','RIO NOVO','RIO PRETO','SANTA BÁRBARA DO MONTE VERDE','SANTA RITA DE JACUTINGA','SANTANA DO DESERTO','SANTOS DUMONT','SIMÃO PEREIRA']

print("/media/vinicius/vinicius-HDD3TB/mg_setores_censitarios/31SEE250GC_SIR.shp")

[gdf_region] = sp.read_shapefile_region("/media/vinicius/vinicius-HDD3TB/mg_setores_censitarios/31SEE250GC_SIR.shp",city_list)
print("gdf_region",gdf_region)
print("df_antennas",df_antennas)
[setores,closest_antennas,distance_antennas] = sp.calculate_closest_antenna(gdf_region,df_antennas)
print(closest_antennas)


# Trabalhando com renda
df_basico = pd.read_csv("/media/vinicius/vinicius-HDD3TB/Basico_MG.csv", sep=";")

dict_income_antenna = sp.calculate_income_antenna(df_antennas,gdf_region,df_basico,setores,closest_antennas)
print(dict_income_antenna)

filename_dict_income_antenna = '%s/dict_income_antenna_%s.pickle' % (prefix,region)
file_dict_income_antenna = open(filename_dict_income_antenna,'wb')

pickle.dump(dict_income_antenna,file_dict_income_antenna)
file_dict_income_antenna.close()

# Atribuindo renda nas redes sociais
social_directed = nx.read_gml('%s/social_networks/%s_social_directed_no_null_outdegree.gml' % (prefix,region))
social_directed = sp.assign_income_class_network(social_directed,dict_users_residence_antenna,dict_income_antenna)
nx.write_gml(social_directed,'%s/social_networks/%s_social_directed_no_null_outdegree_income_class.gml' % (prefix,region) )

social_undirected = nx.read_gml('%s/social_networks/%s_social_undirected_no_null_outdegree.gml' % (prefix,region))
social_undirected = sp.assign_income_class_network(social_undirected,dict_users_residence_antenna,dict_income_antenna)
nx.write_gml(social_undirected,'%s/social_networks/%s_social_undirected_no_null_outdegree_income_class.gml' % (prefix,region) )


# Daqui pra baixo tem algumas coisas que eu usava antigamente
## Salvando as informações sobre as antenas mais próximas de cada setor
#d = {'setor': setores, 'closest_antenna': closest_antennas, 'distance_antenna': distance_antennas}
#df_info_setores_antennas = pd.DataFrame(data=d)
#df_info_setores_antennas.to_csv (r'info_setores_antennas.csv', index = False, header=True, sep=";")

#df_basico = pd.read_csv("Basico_SJDR.csv", sep=";")
#calculate_antenna_aggregated_information(df_antennas,df_residence_antennas,setores,closest_antennas,df_basico)
# %% codecell
