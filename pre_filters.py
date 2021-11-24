# %% codecell
import sys
import pandas as pd
from geopy.geocoders import Nominatim
import csv
# %% codecell
def get_antennas_municipality_from_file(municipality,antenna_filename):
	# Essa função lê o arquivo de antenas e devolve apenas as antenas de uma 
	# microrregião de interesse de um arquivo de antenas, que no caso do OSM é um atributo 
	# do 'location' denominado 'municipality'.
	# Porém, talvez essa não seja a melhor forma, pq a denominação de microrregião caiu em 
	# desuso em 2017 e o IBGE passou a usar região imediata, que não tem atributo do 'location'.
	# Então é melhor usar as cidades da região geográfica imediata como base
	# (o que é feito com outra função)
	
	# A função devolve uma lista com as antenas (na ordem em que aparecem) e 
	# uma com antenas correspondentes
	# Aqui, muito cuidado porque pode haver cidade 'unknown', que eu não consegui
	# descobrir o nome.
	# Nos casos onde a própria 'municipality' ficou 'unknown', a antena vai ser ignorada.
	
	antenna_file = open(antenna_filename,"r")
	
	df_antenas = pd.read_csv(antenna_filename, sep=";")
	
	city_list = []
	antenna_list = []
	for row in df_antenas.itertuples():
		if row.MUNICIPALITY == municipality:
			#print("Found",municipality,"(",row.CELLID,")")
			antenna_list.append(row.CELLID)
			city_list.append(row.CITY)
			
	df_filtered_antennas = df_antenas[df_antenas["MUNICIPALITY"] == municipality]
	
	return [antenna_list,city_list,df_filtered_antennas]
	#end get_antennas_from_microrregion

#end
# %% codecell
def get_antennas_cities_from_file(cities_ibge,antenna_filename):
	# Essa função lê o arquivo de antenas e devolve apenas as antenas de uma 
	# de uma lista de cidades de interesse.
		
	# A função devolve uma lista com as antenas (na ordem em que aparecem) e 
	# uma com antenas correspondentes
	# Aqui, muito cuidado porque pode haver cidade 'unknown', que eu não consegui
	# descobrir o nome.
	# Nos casos onde a própria 'municipality' ficou 'unknown', a antena vai ser ignorada.
	
	antenna_file = open(antenna_filename,"r")
	df_antenas = pd.read_csv(antenna_filename, sep=";")
	city_list = []
	antenna_list = []
	for row in df_antenas.itertuples():
		if row.CITY in cities_ibge:
			#print("Found",row.CITY,"(",row.CELLID,")")
			antenna_list.append(row.CELLID)
			city_list.append(row.CITY)
			
	df_filtered_antennas = df_antenas[df_antenas["CITY"].isin(city_list)]
	
	return [antenna_list,city_list,df_filtered_antennas]
	#end get_antennas_from_microrregion

#end
# %% codecell
def filter_cdr_antennas(cdr_filename,df_filtered_antennas,cdr_filename_out):
	# Essa função toma como base um CDR original, como veio, e um
	# data frame filtrado com as antenas de interesse 
	# (o que já foi feito com funções anteriores do script).
	# Como ela lê um CDR que pode ser muito grande, eu nem uso o pandas nessa função.
	# (uso o python CSV que, diferentemente do pandas, não carrega o CSV todo na memória).
	# A função não tem retorno. O resultado é guardado num CSV, com append.
	# Normalmente, essa função é o primeiro passo do pré-processamento do CDR.
	# Normalmente, os arquivos CDR estão em uma pasta, cada arquivo contendo as ligações de um dia.
	# Essa função pode ser chamada por um script que percorre todos os arquivos e vai guardando
	# (com append) o resultado dessa função em um CSV único grande, que vai ser usado nos
	# próximos passos.
	
	print("Entrou aqui (",cdr_filename,")!!")
	
	antennas = []
	for row in df_filtered_antennas.itertuples():
		antennas.append(row.CELLID)
	
	##cdr_filename_out = "cdr_regiao_imediata_jf.csv"
	
	count = 0
	with open(cdr_filename,'r') as fin, open(cdr_filename_out,'a') as fout:
		writer = csv.writer(fout, delimiter=';')            
		for row in csv.reader(fin, delimiter=';'):
			#print(row[7])
			if int(row[7]) in antennas:
				#print(row[7])
				#print("achou")
				count+=1
				writer.writerow(row)
				#exit()
	print(count,"records found!")
	fin.close()
	fout.close()
	
#end
# %% codecell
def read_df_from_file(filename):
	df = pd.read_csv(filename, sep=";")
	return df
# %% codecell
def write_df_to_file(df,filename):
	df.to_csv (r('%s' % filename), index = False, header=True, sep=";")
# %% codecell
# Precisamos filtrar apenas as antenas que desejamos, tomando como base um arquivo de antenas.
# Podemos fazer isso de duas formas (a outra deve ser comentada):
# 1) Passando o nome da 'municipality', mas isso caiu em desuso
#municipality = "Microrregião São João del-Rei"
#antenna_list,city_list,df_filtered_antennas = get_antennas_municipality_from_file(municipality,antenna_filename)
# 2) Passando uma lista de cidades de interesse
# Cidades da Região Imediata de São João del-Rei
#cities_ibge = ['São João del-Rei', 'Tiradentes', 'São Vicente de Minas', 'São Tiago', 'São João del Rei', 'Santa Cruz de Minas', 'Ritápolis', 'Resende Costa', 'Prados', 'Piedade do Rio Grande', 'Nazareno', 'Coronel Xavier Chaves', 'Conceição da Barra de Minas', 'Madre de Deus de Minas', 'Lagoa Dourada']#, '---']
# Cidades da Região Imediata do Rio de Janeiro
##cities_ibge = ['Belford Roxo','Duque de Caxias','Guapimirim','Itaboraí','Itaguaí','Japeri','Magé','Mangaratiba','Maricá','Mesquita','Nilópolis','Niterói','Nova Iguaçu','Paracambi','Queimados','Rio de Janeiro','São Gonçalo','São João de Meriti','Saquarema','Seropédica','Tanguá']
# Cidades da Região Imediata de Juiz de Fora
cities_ibge = ['Andrelândia','Aracitaba','Arantina','Belmiro Braga','Bias Fortes','Bocaina de Minas','Bom Jardim de Minas','Chácara','Chiador','Coronel Pacheco','Ewbank da Câmara','Goianá','Juiz de Fora','Liberdade','Lima Duarte','Matias Barbosa','Olaria','Oliveira Fortes','Paiva','Passa Vinte','Pedro Teixeira','Piau','Rio Novo','Rio Preto','Santa Bárbara do Monte Verde','Santa Rita de Jacutinga','Santana do Deserto','Santos Dumont','Simão Pereira']

region = 'jf' # Nome da região, para referência no código
prefix = '/media/vinicius/vinicius-HDD3TB/TODAS_UFS_CDR/%s/' % (region)
    
antenna_filename = "/media/vinicius/vinicius-HDD3TB/antennas_municipality.txt"
# %% codecell
antenna_list,city_list,df_filtered_antennas = get_antennas_cities_from_file(cities_ibge,antenna_filename)
df_filtered_antennas.to_csv ('%s/antennas_%s.txt' % (prefix,region), index = False, header=True, sep=";")
# %% codecell

"""
#### PARTE 1
cdr_filename_region = '%s/cdr_regiao_imediata_%s_parte1.txt' % (prefix,region)
cdr_filename = '/media/vinicius/vinicius-HDD3TB/TODAS_UFS_CDR/EXTRACAO_CDR_PROD_TUF_20130321.out'
filter_cdr_antennas(cdr_filename,df_filtered_antennas,cdr_filename_region)
cdr_filename = '/media/vinicius/vinicius-HDD3TB/TODAS_UFS_CDR/EXTRACAO_CDR_PROD_TUF_20130322.out'
filter_cdr_antennas(cdr_filename,df_filtered_antennas,cdr_filename_region)
cdr_filename = '/media/vinicius/vinicius-HDD3TB/TODAS_UFS_CDR/EXTRACAO_CDR_PROD_TUF_20130323.out'
filter_cdr_antennas(cdr_filename,df_filtered_antennas,cdr_filename_region)
cdr_filename = '/media/vinicius/vinicius-HDD3TB/TODAS_UFS_CDR/EXTRACAO_CDR_PROD_TUF_20130324.out'
filter_cdr_antennas(cdr_filename,df_filtered_antennas,cdr_filename_region)
"""

"""
#### PARTE 2
cdr_filename_region = '%s/cdr_regiao_imediata_%s_parte2.txt' % (prefix,region)
cdr_filename = '/media/vinicius/vinicius-HDD3TB/TODAS_UFS_CDR/EXTRACAO_CDR_PROD_TUF_20130325.out'
filter_cdr_antennas(cdr_filename,df_filtered_antennas,cdr_filename_region)
cdr_filename = '/media/vinicius/vinicius-HDD3TB/TODAS_UFS_CDR/EXTRACAO_CDR_PROD_TUF_20130326.out'
filter_cdr_antennas(cdr_filename,df_filtered_antennas,cdr_filename_region)
cdr_filename = '/media/vinicius/vinicius-HDD3TB/TODAS_UFS_CDR/EXTRACAO_CDR_PROD_TUF_20130327.out'
filter_cdr_antennas(cdr_filename,df_filtered_antennas,cdr_filename_region)
cdr_filename = '/media/vinicius/vinicius-HDD3TB/TODAS_UFS_CDR/EXTRACAO_CDR_PROD_TUF_20130328.out'
filter_cdr_antennas(cdr_filename,df_filtered_antennas,cdr_filename_region)
"""

"""
#### PARTE 3
cdr_filename_region = '%s/cdr_regiao_imediata_%s_parte3.txt' % (prefix,region)
cdr_filename = '/media/vinicius/vinicius-HDD3TB/TODAS_UFS_CDR/EXTRACAO_CDR_PROD_TUF_20130329.out'
filter_cdr_antennas(cdr_filename,df_filtered_antennas,cdr_filename_region)
cdr_filename = '/media/vinicius/vinicius-HDD3TB/TODAS_UFS_CDR/EXTRACAO_CDR_PROD_TUF_20130330.out'
filter_cdr_antennas(cdr_filename,df_filtered_antennas,cdr_filename_region)
cdr_filename = '/media/vinicius/vinicius-HDD3TB/TODAS_UFS_CDR/EXTRACAO_CDR_PROD_TUF_20130331.out'
filter_cdr_antennas(cdr_filename,df_filtered_antennas,cdr_filename_region)
cdr_filename = '/media/vinicius/vinicius-HDD3TB/TODAS_UFS_CDR/EXTRACAO_CDR_PROD_TUF_20130401.out'
filter_cdr_antennas(cdr_filename,df_filtered_antennas,cdr_filename_region)
"""

"""
#### PARTE 4
cdr_filename_region = '%s/cdr_regiao_imediata_%s_parte4.txt' % (prefix,region)
cdr_filename = '/media/vinicius/vinicius-HDD3TB/TODAS_UFS_CDR/EXTRACAO_CDR_PROD_TUF_20130402.out'
filter_cdr_antennas(cdr_filename,df_filtered_antennas,cdr_filename_region)
cdr_filename = '/media/vinicius/vinicius-HDD3TB/TODAS_UFS_CDR/EXTRACAO_CDR_PROD_TUF_20130403.out'
filter_cdr_antennas(cdr_filename,df_filtered_antennas,cdr_filename_region)
cdr_filename = '/media/vinicius/vinicius-HDD3TB/TODAS_UFS_CDR/EXTRACAO_CDR_PROD_TUF_20130404.out'
filter_cdr_antennas(cdr_filename,df_filtered_antennas,cdr_filename_region)
cdr_filename = '/media/vinicius/vinicius-HDD3TB/TODAS_UFS_CDR/EXTRACAO_CDR_PROD_TUF_20130405.out'
filter_cdr_antennas(cdr_filename,df_filtered_antennas,cdr_filename_region)
"""

"""
#### PARTE 5
cdr_filename_region = '%s/cdr_regiao_imediata_%s_parte5.txt' % (prefix,region)
cdr_filename = '/media/vinicius/vinicius-HDD3TB/TODAS_UFS_CDR/EXTRACAO_CDR_PROD_TUF_20130406.out'
filter_cdr_antennas(cdr_filename,df_filtered_antennas,cdr_filename_region)
cdr_filename = '/media/vinicius/vinicius-HDD3TB/TODAS_UFS_CDR/EXTRACAO_CDR_PROD_TUF_20130407.out'
filter_cdr_antennas(cdr_filename,df_filtered_antennas,cdr_filename_region)
cdr_filename = '/media/vinicius/vinicius-HDD3TB/TODAS_UFS_CDR/EXTRACAO_CDR_PROD_TUF_20130408.out'
filter_cdr_antennas(cdr_filename,df_filtered_antennas,cdr_filename_region)
cdr_filename = '/media/vinicius/vinicius-HDD3TB/TODAS_UFS_CDR/EXTRACAO_CDR_PROD_TUF_20130409.out'
filter_cdr_antennas(cdr_filename,df_filtered_antennas,cdr_filename_region)
"""

"""
#### PARTE 6
cdr_filename_region = '%s/cdr_regiao_imediata_%s_parte6.txt' % (prefix,region)
cdr_filename = '/media/vinicius/vinicius-HDD3TB/TODAS_UFS_CDR/EXTRACAO_CDR_PROD_TUF_20130410.out'
filter_cdr_antennas(cdr_filename,df_filtered_antennas,cdr_filename_region)
cdr_filename = '/media/vinicius/vinicius-HDD3TB/TODAS_UFS_CDR/EXTRACAO_CDR_PROD_TUF_20130411.out'
filter_cdr_antennas(cdr_filename,df_filtered_antennas,cdr_filename_region)
cdr_filename = '/media/vinicius/vinicius-HDD3TB/TODAS_UFS_CDR/EXTRACAO_CDR_PROD_TUF_20130412.out'
filter_cdr_antennas(cdr_filename,df_filtered_antennas,cdr_filename_region)
cdr_filename = '/media/vinicius/vinicius-HDD3TB/TODAS_UFS_CDR/EXTRACAO_CDR_PROD_TUF_20130413.out'
filter_cdr_antennas(cdr_filename,df_filtered_antennas,cdr_filename_region)
"""

"""
#### PARTE 7
cdr_filename_region = '%s/cdr_regiao_imediata_%s_parte7.txt' % (prefix,region)
cdr_filename = '/media/vinicius/vinicius-HDD3TB/TODAS_UFS_CDR/EXTRACAO_CDR_PROD_TUF_20130414.out'
filter_cdr_antennas(cdr_filename,df_filtered_antennas,cdr_filename_region)
cdr_filename = '/media/vinicius/vinicius-HDD3TB/TODAS_UFS_CDR/EXTRACAO_CDR_PROD_TUF_20130415.out'
filter_cdr_antennas(cdr_filename,df_filtered_antennas,cdr_filename_region)
cdr_filename = '/media/vinicius/vinicius-HDD3TB/TODAS_UFS_CDR/EXTRACAO_CDR_PROD_TUF_20130416.out'
filter_cdr_antennas(cdr_filename,df_filtered_antennas,cdr_filename_region)
"""

#"""
#### PARTE 8
cdr_filename_region = '%s/cdr_regiao_imediata_%s_parte8.txt' % (prefix,region)
cdr_filename = '/media/vinicius/vinicius-HDD3TB/TODAS_UFS_CDR/EXTRACAO_CDR_PROD_TUF_20130417.out'
filter_cdr_antennas(cdr_filename,df_filtered_antennas,cdr_filename_region)
cdr_filename = '/media/vinicius/vinicius-HDD3TB/TODAS_UFS_CDR/EXTRACAO_CDR_PROD_TUF_20130418.out'
filter_cdr_antennas(cdr_filename,df_filtered_antennas,cdr_filename_region)
cdr_filename = '/media/vinicius/vinicius-HDD3TB/TODAS_UFS_CDR/EXTRACAO_CDR_PROD_TUF_20130419.out'
filter_cdr_antennas(cdr_filename,df_filtered_antennas,cdr_filename_region)
#"""
