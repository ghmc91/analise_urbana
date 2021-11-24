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



def build_antenna_lat_long_dict(df_antennas):
	dict_antenna = dict()
	
	for antenna in df_antennas.itertuples():
		dict_antenna[str(antenna.CELLID)] = dict()
		dict_antenna[str(antenna.CELLID)]['lat'] = antenna.LAT
		dict_antenna[str(antenna.CELLID)]['long'] = antenna.LONG
	#end
	print(dict_antenna)
	
	return dict_antenna
#end



def plot_mobility_property(radius_list,colors_list,labels_list,num_classes,property_name,legend_text):

	fig, ax = plt.subplots(figsize=(10,10))
	

	#ax = sns.boxplot(data=df_property)
	
	#g = sns.violinplot(data=df_property)
	
	ax.grid(color='grey', axis='y', linestyle='-', linewidth=0.45, alpha=0.5)
	
	ax.boxplot(radius_list,labels=labels_list)
	ax.set_ylabel(legend_text)
	fig.tight_layout()
	plt.savefig("results/%s/mobility_%s.png" % (region,property_name))
#end	





def run_individual_mobility(prefix,region):
	
	df_antennas = pd.read_csv("%s/antennas_%s_unique.txt" % (prefix,region), sep=";")
	
	dict_antenna = build_antenna_lat_long_dict(df_antennas)
	
	
	filename_users_residence_antenna = open('%s/dict_users_residence_antenna_%s.pickle' % (prefix,region),'rb')
	dict_users_residence_antenna = pickle.load(filename_users_residence_antenna)
	filename_users_residence_antenna.close()
	
	radius_list = []
	radius_list_all = []
	
	k_radius_list = []
	k_radius_list_all = []
	
	uncorrelated_entropy_list = []
	uncorrelated_entropy_list_all = []
	
	maximum_distance_list = []
	maximum_distance_list_all = []
	
	number_of_locations_list = []
	number_of_locations_list_all = []
	
	max_distance_from_home_list = []
	max_distance_from_home_list_all = []
	
	
	
	for class_index in range(7):
		#class_index = 2
		print('class:', class_index+1)
		
		filename_cdr_dict = open('%s/dict_cdr_%s_class%d.pickle' % (prefix,region,class_index+1),'rb')
		dict_cdr_class = pickle.load(filename_cdr_dict)
		filename_cdr_dict.close()
		
		
		#Esse usuário é de JF e tem bastante ligação
		#print(dict_cdr_class['FA95C5B07C2484ABC138BA89225B262B'])
		#exit()
		
		duration_list = []
		user_to_list = []
		antenna_list = []
		lat_list = []
		long_list = []
		datetime_list = []
		user_from_list = []
		count = 0
		for user in dict_cdr_class:
			
			user_residence_antenna = dict_users_residence_antenna[user]
			user_residence_lat = dict_antenna[user_residence_antenna]['lat']
			user_residence_long = dict_antenna[user_residence_antenna]['long']
			
			#print(user_residence_antenna)
			#print(user_residence_lat)
			#print(user_residence_long)
			
			
			
			

			# Agora é montar o df
			# Começar com ele vazio
			
			#print(dict_cdr_class[user])
			#exit()

			
			#print("======================")
			#print(count,user)
			
			
			for day in dict_cdr_class[user]:
				
				if len(day) >= 7: # usuário realizou mais que 5 atividades no dia
				
					datetime_list_user = []
					for call in dict_cdr_class[user][day]:
						
						#print(dict_cdr_class[user][day])
						
						user_from_list.append(user)
						duration_list.append(dict_cdr_class[user][day][call]['duration'])
						#user_to_list.append(dict_cdr_class[user][call]['user_to'])
						antenna_list.append(dict_cdr_class[user][day][call]['antenna'])
						lat_list.append(dict_antenna[dict_cdr_class[user][day][call]['antenna']]['lat'])
						long_list.append(dict_antenna[dict_cdr_class[user][day][call]['antenna']]['long'])
						datetime_list.append(call)
						
						
						datetime_list_user.append(call)
						
						# Colocar os dados da call
						#print(call)
						#print(dict_cdr_class[user][call])
						#print("")
					#end for
				#end if
			#end for
			
			
			# Ordenar as calls do usuário
			# Para cada dia, inserir uma atividade ants da primeira e uma depois da última
			
			#print(datetime_list_user)
			#print("++++++")
			#print(sorted(datetime_list_user))
			
			
			### Todos os indivíduos devem iniciar e terminar o dia na residência
			### Então, para cada dia, vou adicionar uma atividade 1 minuto antes da primeira e uma atividade 1 minuto depos da última
			
			datetime_list_user = sorted(datetime_list_user)
			
			current_day = datetime_list_user[0].day
			
			# Buy in
			#print("\t\t => mudou o dia")
			# Mudou o dia
			first_activity = datetime_list_user[0]
			#print("\t primeiro horário do dia:",first_activity.strftime("%H:%M:%S") ) # Jogar nas listas
			# Pronto para jogar o primeiro horário nas listas
			user_from_list.append(user)
			duration_list.append(1.00)
			antenna_list.append(user_residence_antenna)
			lat_list.append(user_residence_lat)
			long_list.append(user_residence_long)
			datetime_list.append(first_activity - datetime.timedelta(0,60))
			datetime_list_user.append(call)
						
			last_activity = first_activity
			
			for activity_time in datetime_list_user:
				if(activity_time.day != current_day): # Mudou o dia
					#print("\t último horário do dia:",last_activity.strftime("%H:%M:%S") ) # Jogar nas listas
					# Pronto para jogar o último horário nas listas
					user_from_list.append(user)
					duration_list.append(1.00)
					antenna_list.append(user_residence_antenna)
					lat_list.append(user_residence_lat)
					long_list.append(user_residence_long)
					datetime_list.append(last_activity + datetime.timedelta(0,60))
					datetime_list_user.append(call)
					
					#print("\t\t => mudou o dia")
					# Mudou o dia
					
					#print("\t primeiro horário do dia:",activity_time.strftime("%H:%M:%S") ) # Jogar nas listas
					# Pronto para jogar o primeiro horário nas listas
					user_from_list.append(user)
					duration_list.append(1.00)
					antenna_list.append(user_residence_antenna)
					lat_list.append(user_residence_lat)
					long_list.append(user_residence_long)
					datetime_list.append(first_activity - datetime.timedelta(0,60))
					datetime_list_user.append(call)
					
					
					current_day = activity_time.day
					
									
				#print(activity_time,activity_time.date)
				last_activity = activity_time
				current_time = activity_time.time
			#end
			
			#Buy out
			last_activity = datetime_list_user[-1]
			#print("\t último horário do dia:",last_activity.strftime("%H:%M:%S") ) # Jogar nas listas
			# Pronto para jogar o último horário nas listas
			user_from_list.append(user)
			duration_list.append(1.00)
			antenna_list.append(user_residence_antenna)
			lat_list.append(user_residence_lat)
			long_list.append(user_residence_long)
			datetime_list.append(last_activity + datetime.timedelta(0,60))
			datetime_list_user.append(call)
				
			
			### Fim do trecho de adição da primeira e última atividades nas listas
				
					
			
			# Agora é só jogar as calls no df
			
			#count += 1
			#if count == 3:
			#	break
		#end for
		
		
		radius_list_class = []
		k_radius_list_class = []
		uncorrelated_entropy_list_class = []
		maximum_distance_list_class = []
		number_of_locations_list_class = []
		max_distance_from_home_list_class = []
		
		
		if len(user_from_list) > 0:
			data_user = {'user_from':user_from_list, 'duration':duration_list, 'antenna':antenna_list, 'lat':lat_list, 'long':long_list, 'datetime':datetime_list}
			df_user = pd.DataFrame(data=data_user)
			#print(df_user)
		
			tdf = skmob.TrajDataFrame(df_user, latitude='lat', longitude='long', datetime='datetime', user_id='user_from')
			
			
			# Radius of gyration
			radius_list_class_pre = radius_of_gyration(tdf,show_progress=False)['radius_of_gyration'].tolist()
			radius_list_class = []
			
			k_radius_list_class_pre = k_radius_of_gyration(tdf,k=3,show_progress=False)['3k_radius_of_gyration'].tolist()
			k_radius_list_class = []
			
			uncorrelated_entropy_list_class_pre = uncorrelated_entropy(tdf, normalize=True)['norm_uncorrelated_entropy'].tolist()
			uncorrelated_entropy_list_class = []
			
			maximum_distance_list_class_pre = maximum_distance(tdf)['maximum_distance'].tolist()
			maximum_distance_list_class = []
			
			number_of_locations_list_class_pre = number_of_locations(tdf)['number_of_locations'].tolist()
			number_of_locations_list_class = []
			
			max_distance_from_home_list_class_pre = max_distance_from_home(tdf)['max_distance_from_home'].tolist()
			max_distance_from_home_list_class = []
			
			
			for i in range(len(maximum_distance_list_class_pre)):
				if maximum_distance_list_class_pre[i] < 75 and maximum_distance_list_class_pre[i] > 0.01:
					radius_list_class.append(radius_list_class_pre[i])
					k_radius_list_class.append(k_radius_list_class_pre[i])
					uncorrelated_entropy_list_class.append(uncorrelated_entropy_list_class_pre[i])
					maximum_distance_list_class.append(maximum_distance_list_class_pre[i])
					number_of_locations_list_class.append(number_of_locations_list_class_pre[i])
					max_distance_from_home_list_class.append(max_distance_from_home_list_class_pre[i])
					
					
			print("\t\t Class", class_index+1,":",len(radius_list_class)/len(radius_list_class_pre) )
			
			
			
			
			
			
				
			
			#print(type(radius_list_class))
			#exit()
			
			#print('radius:',rg)
			#print('mean:',np.mean(radius_list_class))
		#end
		
		
		radius_list.append(radius_list_class)
		k_radius_list.append(k_radius_list_class)
		uncorrelated_entropy_list.append(uncorrelated_entropy_list_class)
		maximum_distance_list.append(maximum_distance_list_class)
		number_of_locations_list.append(number_of_locations_list_class)
		max_distance_from_home_list.append(max_distance_from_home_list_class)
		
		
		if len(radius_list_class) > 0:
			
			radius_list_all = radius_list_all + radius_list_class
			k_radius_list_all = k_radius_list_all + k_radius_list_class
			uncorrelated_entropy_list_all = uncorrelated_entropy_list_all + uncorrelated_entropy_list_class
			maximum_distance_list_all = maximum_distance_list_all + maximum_distance_list_class
			number_of_locations_list_all = number_of_locations_list_all + number_of_locations_list_class
			max_distance_from_home_list_all = max_distance_from_home_list_all + max_distance_from_home_list_class
			
			
		
		
	#end for
	
	radius_list.append(radius_list_all)
	k_radius_list.append(k_radius_list_all)
	uncorrelated_entropy_list.append(uncorrelated_entropy_list_all)
	maximum_distance_list.append(maximum_distance_list_all)
	number_of_locations_list.append(number_of_locations_list_all)
	max_distance_from_home_list.append(max_distance_from_home_list_all)
	
	# Agora eu tenho uma lista de listas. Os índices 0 a 6 correspondem aos raios das classes 1 a 7 e o índice 7 corresponde a todos concatenados.
	
	return [radius_list,k_radius_list,uncorrelated_entropy_list,maximum_distance_list,number_of_locations_list,max_distance_from_home_list]
#end def
	
	
"""
def preprocess_mobility(prefix,region):
	# Nessa função eu faço alguns pré-processamentos nos dicionários, inspirado no
	# artigo "Daily Mobility Patterns..." (Schneider)
	# - Calculo o total de ligações por usuário por dia
	# - Adiciono a primeira e a última atividade do dia como uma ligação da residência
	# (ok, só isso mesmo)
	
	
	filename_users_residence_antenna = open('%s/dict_users_residence_antenna_%s.pickle' % (prefix,region),'rb')
	dict_users_residence_antenna = pickle.load(filename_users_residence_antenna)
	filename_users_residence_antenna.close()
	
	
	for class_index in range(7):
		class_index = 2
		print('class:', class_index+1)
		
		filename_cdr_dict = open('%s/dict_cdr_%s_class%d.pickle' % (prefix,region,class_index+1),'rb')
		dict_cdr_class = pickle.load(filename_cdr_dict)
		filename_cdr_dict.close()
		
		for user in dict_cdr_class:
"""
			
		
		





region = 'jf' # Nome da região, para referência no código
prefix = '/media/vinicius/vinicius-HDD3TB/TODAS_UFS_CDR/%s/' % (region)

[radius_list,k_radius_list,uncorrelated_entropy_list,maximum_distance_list,number_of_locations_list,max_distance_from_home_list] = run_individual_mobility(prefix,region)


colors_list = ['tab:blue','tab:orange','tab:green','tab:red','tab:purple','tab:brown','tab:pink','tab:gray','tab:olive','tab:cyan']
labels_list = ['Class 1', 'Class 2', 'Class 3', 'Class 4', 'Class 5', 'Class 6', 'Class 7', 'All']
num_classes = 7

plot_mobility_property(radius_list,colors_list,labels_list,num_classes,"len_day7_max_dist_75_radius", "Radius of gyration (km)")
plot_mobility_property(k_radius_list,colors_list,labels_list,num_classes,"len_day7_max_dist_75_3k_radius", "Radius of gyration - 3k (km)")
plot_mobility_property(uncorrelated_entropy_list,colors_list,labels_list,num_classes,"len_day7_max_dist_75_uncorrelated_entropy", "Entropy")
plot_mobility_property(maximum_distance_list,colors_list,labels_list,num_classes,"len_day7_max_dist_75_maximum_distance", "Max. distance (km)")
plot_mobility_property(number_of_locations_list,colors_list,labels_list,num_classes,"len_day7_max_dist_75_number_of_locations", "Number of locations")
plot_mobility_property(max_distance_from_home_list,colors_list,labels_list,num_classes,"len_day7_max_dist_75_max_distance_from_home", "Max. distance from home (km)")





	

			
    
    
    
    
exit()


######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################
######################################################################################################################



























# Nomeando os dicionários
filename_dict_users_num_calls = '%s/dict_users_num_calls_%s.pickle' % (prefix,region)
file_dict_users_num_calls = open(filename_dict_users_num_calls,'wb')

filename_dict_users_distinct_days = '%s/dict_users_distinct_days_%s.pickle' % (prefix,region)
file_dict_users_distinct_days = open(filename_dict_users_distinct_days,'wb')

filename_dict_users_stays_weekdays_19_6 = '%s/dict_users_stays_weekdays_%s.pickle' % (prefix,region)
file_dict_users_stays_weekdays_19_6 = open(filename_dict_users_stays_weekdays_19_6,'wb')

filename_dict_users_stays_weekends = '%s/dict_users_stays_weekends_%s.pickle' % (prefix,region)
file_dict_users_stays_weekends = open(filename_dict_users_stays_weekends,'wb')


dict_users_num_calls = dict()
dict_users_distinct_days = dict()
dict_users_stays_weekdays_19_6 = dict()
dict_users_stays_weekends = dict()

# Nesse loop a mágica parte 1 acontece. Todos os filtros são setados aqui.
with open(cdr_filename_region,'r') as fin, open(cdr_filename_region_out,'w') as fout:
    reader = csv.DictReader(fin, delimiter=';')
    writer = csv.writer(fout, delimiter=';')
    fieldnames = ['date','time','duration','ddd_from','user_from','ddd_to','user_to','antenna','unknown1','type_code','type_desc','hold_from','hold_to','type_call_desc','type_call_code']
    writer.writerow(fieldnames)
    
    count = 0
    for row in reader:
        if float(row['duration']) >= 0.07 and float(row['duration'])<= 120: # Verifica se a chamada é válida
            writer.writerow(row.values())
            count+=1
            
            # Número de chamadas
            if row['user_from'] not in dict_users_num_calls:
                dict_users_num_calls[row['user_from']] = 0
            dict_users_num_calls[row['user_from']]+=1 # Apenas incrementa uma chamada
            
            # Número de dias distintos
            if row['user_from'] not in dict_users_distinct_days:
                dict_users_distinct_days[row['user_from']] = []
            if row['date'] not in dict_users_distinct_days[row['user_from']]: # Apareceu um dia distinto
                dict_users_distinct_days[row['user_from']].append(row['date'])
                
            # Chamadas nos dias de semana 19h-6h e domingos
            #Monday is 0 and Sunday is 6.
            weekday = datetime.date.fromisoformat(row['date']).weekday()
            if 0 <= weekday <= 4: # dia da semana
                time_call = datetime.time.fromisoformat(row['time'])
                time19h = datetime.time(19,0,0)
                time6h = datetime.time(6,0,0)
                if time_call >= time19h or time_call <= time6h: # Chamada no dia de semana de 19h-6h
                    if row['user_from'] not in dict_users_stays_weekdays_19_6:
                        dict_users_stays_weekdays_19_6[row['user_from']] = []
                    dict_users_stays_weekdays_19_6[row['user_from']].append(row['antenna'])
            elif weekday == 6: # domingo
                if row['user_from'] not in dict_users_stays_weekends:
                    dict_users_stays_weekends[row['user_from']] = []
                dict_users_stays_weekends[row['user_from']].append(row['antenna'])

# Nesse momento eu tenho os dicionários todos completos
print(count,"records found!")
fin.close()
fout.close()

pickle.dump(dict_users_num_calls,file_dict_users_num_calls)
file_dict_users_num_calls.close()

pickle.dump(dict_users_distinct_days,file_dict_users_distinct_days)
file_dict_users_distinct_days.close()

pickle.dump(dict_users_stays_weekdays_19_6,file_dict_users_stays_weekdays_19_6)
file_dict_users_stays_weekdays_19_6.close()

pickle.dump(dict_users_stays_weekends,file_dict_users_stays_weekends)
file_dict_users_stays_weekends.close()


# %% codecell
# Agora eu posso processar os dicionários e verificar as residências
# Meus dicionários:
#   dict_users_num_calls
#   dict_users_distinct_days
#   dict_users_stays_weekdays_19_6
#   dict_users_stays_weekends

filename_dict_users_residence_antenna = '%s/dict_users_residence_antenna_%s.pickle' % (prefix,region)
file_dict_users_residence_antenna = open(filename_dict_users_residence_antenna,'wb')

dict_users_residence_antenna = dict()
# Nesse loop a mágica parte 2 acontece. Aqui são calculadas as residências.
for user in dict_users_num_calls:
    #print(user)
    # Verificando o número de ligações
    if dict_users_num_calls[user] >= 3 and dict_users_num_calls[user] <= 500: # user fez mais que 3 e menos que 500 ligações
        #print(dict_users_num_calls[user])
        if len(dict_users_distinct_days[user]) >= 3: # user fez ligações em mais que 3 dias distintos
            #print(dict_users_distinct_days[user])
            #print(dict_users_stays_weekdays_19_6[user])
                        
            try:
                dict_users_stays_weekdays_19_6_user = dict_users_stays_weekdays_19_6[user]
            except KeyError:
                dict_users_stays_weekdays_19_6_user = []
                
            try:
                dict_users_stays_weekends_user = dict_users_stays_weekends[user]
            except KeyError:
                dict_users_stays_weekends_user = []
            
            
            locations_of_interest = dict_users_stays_weekdays_19_6_user + dict_users_stays_weekends_user
            #print(locations_of_interest)
            
            set_locations_of_interest = set(locations_of_interest)
            num_locations = len(locations_of_interest)
            max_count_location = 0
            residence_antenna = -1
            
            for location in set_locations_of_interest:
                count_location = locations_of_interest.count(location)
                if count_location > (num_locations * 0.5):
                    max_count_location = count_location
                    residence_antenna = location
                #end
            #end
            
            if residence_antenna != -1:
                dict_users_residence_antenna[user] = residence_antenna
            #print(residence_antenna)
        #end
    #end
#end

# Agora o dict_users_residence_antenna tem as residências dos usuários
print(len(dict_users_residence_antenna),"usuários com residência presumida")

pickle.dump(dict_users_residence_antenna,file_dict_users_residence_antenna)
file_dict_users_residence_antenna.close()


