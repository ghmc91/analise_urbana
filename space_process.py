import sys
import pandas as pd
import geopandas as gpd
import datetime

import numpy as np
from geopy.distance import geodesic
import matplotlib.pyplot as plt
import scipy
from sklearn.metrics import r2_score



def read_df_from_file(filename):
	df = pd.read_csv(filename, sep=";")
	return df
	
	
def read_shapefile_region(shapefile_name,city_list):
	# Essa função apenas lê o shapefile e filtra os municípios de interesse.
	# Retorna um geodataframe para ser tratado depois.

	gdf_all = gpd.read_file(shapefile_name)#, layer='countries')
	
	print("gdf_all:",gdf_all)
	
	gdf_region = gdf_all[gdf_all.NM_MUNICIP.isin(city_list)]
	
	#print("city_list (dentro):",city_list)
	#print("gdf_region (dentro):",gdf_region)
	
	#print(gdf_all.head(10))
	#print(gdf_region)
	#print(len(gdf_region.index))
	
	return [gdf_region]
#end

def calculate_closest_antenna(gdf_region,df_antennas):
	# Essa função lê o gdf_region e o df_antennas e calcula qual é a antena mais 
	# próxima de cada região.
	# Esse esquema vai mudar completamente com o Voronoi.	
	
	# Aqui eu vou:
	#	+ criar uma lista de setores (com cada linha do gdf_region)
	#	+ obter lat e long de cada setor
	#	+ percorrer o df_antennas e ver qual a antena mais próxima do setor
	#	+ cada linha do setor/closest_antenna vai ter id do setor/id da antena mais próxima
	
	setores = []
	closest_antennas = []
	distance_antennas = []
	
	#closest_antennas = dict()
	#distance_antennas = dict()
	
	#"""
	
	for setor in gdf_region.itertuples():
				
		
		setor_long = setor.geometry.centroid.x
		setor_lat = setor.geometry.centroid.y
		#print(setor.ID, setor.CD_GEOCODI, setor_lat, setor_long)
		least_distance = np.Inf
		least_distance_same_city = np.Inf
		
		
		for antenna in df_antennas.itertuples():

			antenna_lat = antenna.LAT
			antenna_long = antenna.LONG
			
			#[distance] = calculate_distance_two_coordinates(antenna_lat,antenna_long, setor_lat, setor_long)
			#print(antenna_lat, antenna_long, setor_lat, setor_long, distance)
			
			coords_1 = (antenna_lat, antenna_long)
			coords_2 = (setor_lat, setor_long)
			distance = geodesic(coords_1, coords_2).kilometers
			#print("distância para a antena", antenna.antenna, " = ",distance)
			
			if antenna.CITY == setor.NM_MUNICIP:
				if distance < least_distance_same_city:
					least_distance_same_city = distance
					closest_antenna_same_city = antenna.antenna
			
			if distance < least_distance:
				#print("atualizou a distância")
				least_distance = distance
				closest_antenna = antenna.CELLID
				
		#end for antenna
		
			
		#print("\n\n\t\tantena mais próxima do setor",setor.CD_GEOCODI,":", closest_antenna, "(dist = ",least_distance,")")
		
		
		setores.append(setor.CD_GEOCODI)
		if least_distance_same_city != np.Inf:
			#closest_antennas[setor.CD_GEOCODI] = closest_antenna_same_city
			#distance_antennas[setor.CD_GEOCODI] = least_distance_same_city
			closest_antennas.append(closest_antenna_same_city)
			distance_antennas.append(least_distance_same_city)
		else:
			#closest_antennas[setor.CD_GEOCODI] = closest_antenna
			#distance_antennas[setor.CD_GEOCODI] = least_distance
			closest_antennas.append(closest_antenna)
			distance_antennas.append(least_distance)
		
	#end for setor
	#"""
		
	return [setores,closest_antennas,distance_antennas]
#end

def calculate_income_antenna(df_antennas,gdf_region,df_basico,setores,closest_antennas):

	#gdf_region = gdf_region.reset_index()
	#print("reset_index")
	
	#print("entrou no calculate_income_antenna:")
	#print("setores:",len(setores),setores)
	print("closest_antennas:",len(closest_antennas),closest_antennas)
	#print(gdf_region)
	
	dict_income_antenna = dict()
	for antenna in df_antennas.itertuples():
		print(antenna.CELLID)
		
		indices = [index for index, element in enumerate(closest_antennas) if element == antenna.CELLID]
		
		print("indices:",indices)
				
		setores_antenna = []
		for index in indices:
			setores_antenna.append(setores[index])
			
				
		
		#Tenho os códigos dos setores, agora preciso pegar as rendas dos setores no Basico e tirar a média. Essa vai ser a renda da antena.
		#exit()
		
				
	
		df_basico_antenna = df_basico[df_basico.Cod_setor.isin(setores_antenna)]
		
		list_income = df_basico_antenna["V007"].to_list()
		
		print("list_income",list_income)
		
		#**** parei aqui ****
		#Agora tenho que tirar a média dos valores das rendas pra definir a faixa
		
		total_income = 0
		num_setores = 0
		for income in list_income:
			#print(income)
			if type(income) != float:
				num_setores = num_setores + 1
				
				income = income.replace(',','.')
				income = float(income)
				total_income = total_income + income
		try:
			mean_income = total_income / num_setores
		except (ZeroDivisionError):
			mean_income = 0
		
		#print("antenna:",antenna.CELLID,"|","mean_income:",mean_income)
		
		
		mean_income = float(mean_income)
		income_class = get_income_class_by_income(mean_income)
		
		dict_income_antenna[antenna.CELLID] = [mean_income,income_class]
		
				
		#setores_antenna <- seleção dos indices do closest_antena == antenna.CELLID
		#for setores cujos indices estão no setores_antenna
		# income.append(renda)
		
	#exit()
	return [dict_income_antenna]
	
	
def get_income_class_by_income(mean_income):
	income_class = -1
	
	if mean_income <= 510:
		income_class = 1
	elif mean_income > 510 and mean_income <= 1020:
		income_class = 2
	elif mean_income > 1020 and mean_income <= 1530:
		income_class = 3
	elif mean_income > 1530 and mean_income <= 2550:
		income_class = 4
	elif mean_income > 2550 and mean_income <= 5100:
		income_class = 5
	elif mean_income > 5100 and mean_income <= 10200:
		income_class = 6
	elif mean_income > 10200:
		income_class = 7
		
	return income_class
	
def assign_income_class_network(social_network,dict_users_residence_antenna,dict_income_antenna):
	dict_income_antenna = dict_income_antenna[0]
	social_network_nodes = social_network.nodes()
	ok = 0
	nao_ok = 0
	for node in social_network_nodes:
		try:
			ok = ok + 1
			antenna = int(dict_users_residence_antenna[node])
			#print(node,antenna)
			social_network.nodes[node]['income'] = dict_income_antenna[antenna][0]
			social_network.nodes[node]['income_class'] = dict_income_antenna[antenna][1]
		except (KeyError):
			nao_ok = nao_ok + 1
			social_network.nodes[node]['income'] = -1
			social_network.nodes[node]['income_class'] = -1
	#end
	
	print("ok:",ok)
	print("nao_ok:",nao_ok)
	
	return social_network
		
#end



def calculate_antenna_aggregated_information(df_antennas,df_residence_antennas,setores,closest_antennas,df_basico):

	#for setor,closest_antenna in zip(setores,closest_antennas):
	#	print(setor,closest_antenna)
		
	#print("\n\n")
	
	ids_antennas = df_antennas.CELLID
	#print(ids_antennas)
	
	residence_antenna = df_residence_antennas['residence_antenna'].tolist()
	
	
	domicilios_setores_antenna = []
	residentes_setores_antenna = []
	presumidos_antenna = []
	
	for id_antenna in ids_antennas:
		"""
		- descobrir uma lista com as linhas do closest_antennas que têm valor igual a id_antenna (setores_id_antenna)
		- usar a lista de setores_filtrados para filtrar o df_basico (df_basico_antenna)
		- fazer os cálculos em cima do df_basico_antenna
		"""
		
		setores_id_antenna = [setores[i] for i, value in enumerate(closest_antennas) if value == id_antenna]
		
		#print(id_antenna)
		#print(setores_id_antenna)
		
		df_basico_antenna = df_basico[df_basico.Cod_setor.isin(setores_id_antenna)]
		
		domicilios_setor = df_basico_antenna.V001.sum()
		residencias_setor = df_basico_antenna.V002.sum()
		
		domicilios_setores_antenna.append(domicilios_setor)
		residentes_setores_antenna.append(residencias_setor)
			
		presumidos_antenna.append(residence_antenna.count(id_antenna))
		
		
	#for id_antenna in ids_antennas:
	
	
	
	print("\n\n\n")
	
	market_share = dict()
	market_share[27711] = 0.48 # Madre de Deus de Minas
	market_share[23441] = 0.16 # São João del-Rei
	market_share[23461] = 0.16 # São João del-Rei
	market_share[23471] = 0.16 # São João del-Rei
	market_share[23451]	= 0.16 # São João del-Rei
	market_share[50141]	= 0.16 # São João del-Rei
	market_share[29941]	= 0.16 # Tiradentes
	market_share[29011]	= 0.16 # Tiradentes
	market_share[49592]	= 0.04 # Lagoa Dourada
	market_share[51601]	= 0.04 # Ritápolis
	market_share[60761] = 0.11 # São Vicente de Minas
	market_share[49593] = 0.04 # Lagoa Dourada
	market_share[51371] = 0.03 # São Tiago
	
	
	"""
	print("antenna\tpresumidos\tdomicilios\tresidentes\tresidentes (corr.)\tpres \ res.corr")
	for antenna,presumidos,domicilios,residentes in zip(ids_antennas,presumidos_antenna,domicilios_setores_antenna,residentes_setores_antenna):
		print(antenna,"\t",presumidos,"\t",domicilios,"\t",residentes,"\t",residentes * market_share[antenna], "\t", presumidos / (residentes * market_share[antenna]) )
	"""
		
	"""
	residentes_corrigido = []
	for antenna,residentes in zip(ids_antennas,residentes_setores_antenna):
		residentes_corrigido.append(residentes*market_share[antenna])
	"""
	
	fator_expansao = []
	for antenna,residentes,presumidos in zip(ids_antennas,residentes_setores_antenna,presumidos_antenna):
		fator_expansao.append(residentes/presumidos)
		
	
	print("antenna\tpresumidos\tresidentes\tfator_expansao")
	for antenna, presumidos, residentes, expansao in zip(ids_antennas,presumidos_antenna,residentes_setores_antenna,fator_expansao):
		print(antenna,"\t",presumidos,"\t",residentes,expansao)
		
		
	d = {'id_antenna': ids_antennas, 'presumidos': presumidos_antenna, 'residentes': residentes_setores_antenna, 'fator_expansao': fator_expansao}
	df_info_residence_antenna = pd.DataFrame(data=d)
	
	df_info_residence_antenna.to_csv (r'info_residence_antenna.csv', index = False, header=True, sep=";")
		
	
		
		
		
	plt.clf()
	plt.cla()
	plt.close()
	
	#r2 = r2_score(presumidos_antenna, domicilios_setores_antenna)
	#print("R2 = ", r2, "(presumidos X domicilios)")
	
	"""
	correlation = scipy.stats.pearsonr(presumidos_antenna, domicilios_setores_antenna)
	print("Pearson = ", correlation, "(presumidos X domicilios)")
	#axes = plt.gca()
	fig= plt.figure(figsize=(12,12))
	textlabel = "Pearson = %.4f" % correlation[0]
	plt.plot(presumidos_antenna,domicilios_setores_antenna,'o',label = textlabel, color='tab:blue')
	plt.xlabel('Presumidos')
	plt.ylabel('Domicilios')
	leg = plt.legend(loc=1,fontsize='large')
	plt.show()
	#plt.savefig("legenda.png")
	plt.clf()
	plt.cla()
	plt.close()
	"""
	
	
	correlation = scipy.stats.pearsonr(presumidos_antenna, residentes_setores_antenna)
	print("Pearson = ", correlation, "(presumidos X residentes)")
	#axes = plt.gca()
	fig= plt.figure(figsize=(12,12))
	textlabel = "Pearson = %.4f" % correlation[0]
	plt.plot(presumidos_antenna,residentes_setores_antenna,'o',label = textlabel, color='tab:red')
	plt.xlabel('Presumidos')
	plt.ylabel('Residentes')
	leg = plt.legend(loc=1,fontsize='large')
	plt.show()
	plt.clf()
	plt.cla()
	plt.close()
	
	"""
	correlation = scipy.stats.pearsonr(presumidos_antenna, residentes_corrigido)
	print("Pearson = ", correlation, "(presumidos X residentes corrigido)")
	#axes = plt.gca()
	fig= plt.figure(figsize=(12,12))
	textlabel = "Pearson = %.4f" % correlation[0]
	plt.plot(presumidos_antenna,residentes_corrigido,'o',label = textlabel, color='tab:green')
	plt.xlabel('Presumidos')
	plt.ylabel('Residentes corrigido')
	leg = plt.legend(loc=1,fontsize='large')
	plt.show()
	plt.clf()
	plt.cla()
	plt.close()
	"""
	
	
	
	exit()
		
		

#calculate_antenna_aggregated_information

"""
if __name__ == "__main__":

	# Lista de cidades (como descrito no shapefile)
	city_list = ['SÃO JOÃO DEL REI', 'TIRADENTES', 'SÃO VICENTE DE MINAS', 'SÃO TIAGO', 'SANTA CRUZ DE MINAS', 'RITÁPOLIS', 'RESENDE COSTA', 'PRADOS', 'PIEDADE DO RIO GRANDE', 'NAZARENO', 'CORONEL XAVIER CHAVES', 'CONCEIÇÃO DA BARRA DE MINAS', 'MADRE DE DEUS DE MINAS', 'LAGOA DOURADA']
	[gdf_region] = read_shapefile_region("mg_setores_censitarios/31SEE250GC_SIR.shp",city_list)
	
	df_residence_antennas = pd.read_csv("residence_antenna.csv", sep=";")
	df_antennas = pd.read_csv("antennas_sjdr.txt", sep=";")
	
	[setores,closest_antennas,distance_antennas] = calculate_closest_antenna(gdf_region,df_antennas)
	
	# Salvando as informações sobre as antenas mais próximas de cada setor
	d = {'setor': setores, 'closest_antenna': closest_antennas, 'distance_antenna': distance_antennas}
	df_info_setores_antennas = pd.DataFrame(data=d)
	df_info_setores_antennas.to_csv (r'info_setores_antennas.csv', index = False, header=True, sep=";")
	
	
	df_basico = pd.read_csv("Basico_SJDR.csv", sep=";")
	calculate_antenna_aggregated_information(df_antennas,df_residence_antennas,setores,closest_antennas,df_basico)
	
	
	
#end main
"""
