# %% codecell
import mobility_cdr as mcdr
import pickle
import pandas as pd
import networkx as nx
# %% codecell

region = 'sjdr'
prefix = '/media/vinicius/vinicius-HDD3TB/TODAS_UFS_CDR/%s/' % region
#prefix = '/media/vinicius/c481e5d8-7446-40fe-9f30-32cfd502a796/social_mobility_data/%s/' % (region)

cdr_filename_region = '%s/cdr_regiao_imediata_%s_all_unique_filtered.txt' % (prefix,region)
antennas_filename_region = '%s/antennas_%s.txt' % (prefix,region)

df_antennas = pd.read_csv(antennas_filename_region, sep=';')
social_undirected = nx.read_gml('%s/social_networks/%s_social_undirected_no_null_outdegree.gml' % (prefix,region))

# %% codecell
traj_dict = mcdr.get_trajectory_dict_large_cdr(cdr_filename_region,df_antennas,social_undirected)

traj_filename = '%s/traj_vectors_%s.picke' % (prefix,region)
traj_file = open(traj_filename,'wb')
pickle.dump(traj_dict,traj_file)
traj_file.close()
# %% codecell
