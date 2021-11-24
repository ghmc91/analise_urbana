# %% codecell
import sys
import pandas as pd
from geopy.geocoders import Nominatim
import csv
# %% codecell
def replace_duplicate_locations(df_antennas,df_cdr):
    print(df_antennas)
    print("====")
    antennas_lat = df_antennas.LAT
    print(antennas_lat)
    print("====")
    antennas_long = df_antennas.LONG
    print(antennas_long)
    print("====")
    
    unique_lat_long = list(set(tuple(zip(antennas_lat,antennas_long))))
    
    print(unique_lat_long)
    
    
    for location in unique_lat_long:
        primary_antenna = -10
        secondary_antennas = []
        for row in df_antennas.itertuples():
            if row.LAT == location[0] and row.LONG == location[1]:
                if primary_antenna == -10:
                    primary_antenna = row.CELLID
                else:
                    #row.CELLID = primary_antenna
                    secondary_antennas.append(row.CELLID)
                    df_antennas.at[row[0],'CELLID'] = primary_antenna
            #end
        #end
        
        ### Aqui substituir no df_cdr
        
        #print(df_cdr.head(2))
        #print(primary_antenna)
        #print(secondary_antennas)

        df_cdr['antenna'] = df_cdr['antenna'].replace(secondary_antennas,primary_antenna)
        #exit()
    #end
    df_antennas = df_antennas.drop_duplicates()
    #print(len(set(df_cdr.antenna)))
    return [df_antennas,df_cdr]
#end
# %% codecell
def read_df_from_file(filename):
	df = pd.read_csv(filename, sep=";")
	return df
# %% codecell
# ***** Depois da leitura do CDR, eu tinha feito um passo (que pode não ser obrigatório)   *****
# ***** e que envolve remover as antenas com localização duplicada (no arquivo de antenas) *****
# ***** e substituir as antenas pelas antenas com localizações únicas no CDR.              *****


region = 'jf' # Nome da região, para referência no código
#prefix = '/media/vinicius/vinicius-HDD3TB/TODAS_UFS_CDR/%s/' % (region)
prefix = '/media/vinicius/c481e5d8-7446-40fe-9f30-32cfd502a796/social_mobility_data/%s/' % (region)

cdr_filename_region = "%s/cdr_regiao_imediata_%s_all.txt" % (prefix,region)
df_cdr = read_df_from_file(cdr_filename_region)

antenna_filename_region = "%s/antennas_%s.txt" % (prefix,region)
df_antennas = read_df_from_file(antenna_filename_region)

print(df_cdr.head(20))
print(df_antennas)
# %% codecell
[df_antennas,df_cdr] = replace_duplicate_locations(df_antennas,df_cdr)

print(df_antennas)
print(df_cdr.head(20))

df_antennas.to_csv ("%s/antennas_%s_unique.txt" % (prefix,region), index = False, header=True, sep=";")
df_cdr.to_csv ('%s/cdr_regiao_imediata_%s_all_unique.txt' % (prefix,region), index = False, header=True, sep=";")
# %% codecell
