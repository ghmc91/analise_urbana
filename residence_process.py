# %% codecell
import sys
import pandas as pd
import datetime
import csv
# %% codecell
def read_df_from_file(filename):
	df = pd.read_csv(filename, sep=";")
	return df
# %% codecell
def filter_cdr_duration_calls(df_cdr):
	# Essa função pega o CDR e filtra de acordo com as durações das ligações.
	# A idéia é tirar ligações muito rápidas e muito demoradas, que são consideradas outliers.
	# A função devolve o CDR filtrado.
	# A função também imprime algumas coisas básicas sobre a base.
	
	df_cdr_filter = df_cdr[df_cdr.duration <= 120]
	df_cdr_filter = df_cdr_filter[df_cdr_filter.duration >= 0.07]
	
	# Eliminando ligações "estranhas"
	print("dentro do intervalo [0.07,120]:", len(df_cdr_filter.index), "(",len(df_cdr_filter.index)/len(df_cdr.index),")")
	
	duration_max = df_cdr_filter.duration.max()
	duration_min = df_cdr_filter.duration.min()
	duration_mean = df_cdr_filter.duration.mean()
	duration_median = df_cdr_filter.duration.median()
	
	
	print("max:",duration_max,"| min:",duration_min,"| mean:",duration_mean,"| median:",duration_median)
	print("=====")
	
	"""
	# Aqui eu poderia fazer um filtro baseado em número de ligações
	groupby_user_from_duration_max = df_cdr_groupby_user_from.duration.sum().max()
	groupby_user_from_duration_min = df_cdr_groupby_user_from.duration.sum().min()
	groupby_user_from_duration_mean = df_cdr_groupby_user_from.duration.sum().mean()
	groupby_user_from_duration_median = df_cdr_groupby_user_from.duration.sum().median()
	
	print("GROUPBY max:",groupby_user_from_duration_max,"| min:",groupby_user_from_duration_min,"| mean:",groupby_user_from_duration_mean,"| median:",groupby_user_from_duration_median)
	"""
	
	return [df_cdr_filter]
	
# end filter_cdr_duration_calls
# %% codecell
def filter_cdr_duration_calls_big_file(cdr_filename_region, cdr_filename_region_out):
    
    dict_users_num_calls = dict()
    dict_users_days = dict()
    dict_users_stays_weekends = dict()
    dict_users_stays_weekdays_19_6 = dict()
    
    count = 0
    with open(cdr_filename_region,'r') as fin, open(cdr_filename_region_out,'w') as fout:
        reader = csv.DictReader(fin, delimiter=';')
        
        writer = csv.writer(fout, delimiter=';')
        fieldnames = ['date','time','duration','ddd_from','user_from','ddd_to','user_to','antenna','unknown1','type_code','type_desc','hold_from','hold_to','type_call_desc','type_call_code']
        writer.writerow(fieldnames)
                
        for row in reader:
            if float(row['duration']) >= 0.07 and float(row['duration'])<= 120: # Verifica se a chamada é válida
                writer.writerow(row.values())
                
                if row['user_from'] not in dict_users_num_calls: # Registra uma chamada
                    dict_users_num_calls['user_from'] = 1
                else:
                    dict_users_num_calls+=1
                    
                
                
                
                
                count+=1
    print(count,"records found!")
    fin.close()
    fout.close()
            
    """
    with open(cdr_filename_region,'r') as fin, open(cdr_filename_region_out,'w') as fout:
		writer = csv.writer(fout, delimiter=';')            
		for row in csv.reader(fin, delimiter=';'):
			print(row["duration"])
			exit()
			if int(row[7]) in antennas:
				#print(row[7])
				#print("achou")
				count+=1
				writer.writerow(row)
				#exit()
	print(count,"records found!")
	fin.close()
	fout.close()
    """
    
#end
# %% codecell
def calculate_residence_antenna(df_cdr_filter):

	# Essa função vê os usuários que atendem a uma série de critérios e, por isso, 
	# podem ter sua residência presumida. A partir disso, eu calculo qual a antena
	# mais usada por um usuário (essa vai ser considerada sua "residência").
	# A função retorna duas listas: uma de usuários e outra com suas respectivas "residências"
	
	
	# Agrupando os user_from (já que as antenas do CDR representam a origem)
	# Com base nos grupos de usuários vou aplicar os filtros.		
	df_cdr_groupby_user_from = df_cdr_filter.groupby('user_from')
	
	print(len(df_cdr_groupby_user_from),"user_from...")
	
		
	valid_users = [] # Aqui vão ficar guardados os usuários com residência calculada
	                 # Chamei de valid_users porque são os usuários que passam nos critérios.
	residence_antenna = [] # Aqui vão ficar as residências dos usuários.
	                       # Tomei como residência a antena que ele mais usa
	                       # (segundo os critérios definidos)
	
	# Critérios:
	# 1) Número mínimo e máximo de ligações
	# 2) Número de dias distintos de ligações
	# 3) Número de stay_locations
	#    (um stay_location é um local onde o usuário fica à noite ou no domingo)
	
	all_valid_users = [] # Aqui vão todos os usuários que poderiam ter residência calculada (os candidatos)
	all_count_stay_locations = [] # Aqui vão as contagens dos stay locations (para poder filtrar)
	# all_valid_users e all_count_stay_locations se referem a usuários (e localizações)
	# que passaram nos critérios 1 e 2, mas não necessariamente no 3
		
	for user in df_cdr_groupby_user_from:
		num_calls_ok = False
		#print("[0]",user[0])
		user_from = user[0]
		####print("user_from",user_from)
		df_user = user[1]
		num_calls = len(df_user.index)
		###print("num_calls:",num_calls)
		
		if num_calls >= 3 and num_calls < 500: # Atendeu ao critério 1 (número de ligações)
			 num_calls_ok = True
		#	else:
		#		invalid_more_than_max_calls.append(user_from)
		#else:
		#	invalid_less_than_min_calls.append(user_from)
		#num_calls_ok = True
		if num_calls_ok == True: # Antendeu ao número de ligações. Vamos verificar o número de dias.
			####print("\tentrou no critério num_calls")
			num_days = len(set(df_user.date))
			###print("num_days:",num_days)
			
			if num_days >= 3: # Atende ao critério 2 (número de dias distintos)
				####print("\tentrou no critério num_days")
			
				stay_locations = []
			
				###print(df_user.date)
				
				for date,time,antenna in zip(df_user.date, df_user.time, df_user.antenna):
					###print(date,time)
					#Monday is 0 and Sunday is 6.
					weekday = datetime.date.fromisoformat(date).weekday()
					if 0 <= weekday <= 4: # dia da semana
						###print("dia da semana")
						time_call = datetime.time.fromisoformat(time)
						
						time19h = datetime.time(19,0,0)
						time6h = datetime.time(6,0,0)
						
						if time_call >= time19h or time_call <= time6h:
							#print("---noite")
							stay_locations.append(antenna)
						#else:
						#	#print("---diaa")
					elif weekday == 6: # domingo
						stay_locations.append(antenna)
						###print("domingo")
				#end for date,time,antenna
				# Vamos processar o stay_locations
				
				num_stay_locations = len(stay_locations)
				all_valid_users.append(user_from)
				all_count_stay_locations.append(len(set(stay_locations)))
				
				if num_stay_locations > 0: # Antendeu ao critério 3 (número de stay_locations)
					####print("\tentrou no critério de stay locations > 0")
					###print(stay_locations)
					
					max_count_location = 0
					residence = -1
					for location in set(stay_locations):
						count_location = stay_locations.count(location)
						###print(location,count_location)
						if count_location > (num_stay_locations * 0.5):
						#if count_location > max_count_location:
							max_count_location = count_location
							
							#####print("\tachou uma location com frequência maior que a metade")
							###print("count_location",count_location)
							###print("num_stay_locations",num_stay_locations)
							###print("(num_stay_locations / 2)",(num_stay_locations / 2))
							residence = location # A residência será o local onde ele passa mais tempo. 
							####print("\t\t\t*** residência:",residence)
							
							valid_users.append(user_from)
							residence_antenna.append(residence)
						# end if count_location > (num_stay_locations / 2)
					# end for location in set(stay_locations):
						
				# end if num_stay_locations > 0		
			# end if numdays >= 3
			#else: #num_days
			#	invalid_less_than_min_days.append(user)
		#end num_calls_ok == True
	# end user in df_cdr_groupby_user_from		
	
		
	return [valid_users,residence_antenna,all_valid_users,all_count_stay_locations]
#end calculate_residence_antenna

"""
# %% codecell
def calculate_residence_antenna_big_file(df_cdr_filter):

	# Essa função vê os usuários que atendem a uma série de critérios e, por isso, 
	# podem ter sua residência presumida. A partir disso, eu calculo qual a antena
	# mais usada por um usuário (essa vai ser considerada sua "residência").
	# A função retorna duas listas: uma de usuários e outra com suas respectivas "residências"
	
	
    for df_cdr in pd.read_csv(cdr_filename_region, sep=';', iterator=True, chunksize=1000000):
    
    
	# Agrupando os user_from (já que as antenas do CDR representam a origem)
	# Com base nos grupos de usuários vou aplicar os filtros.		
	df_cdr_groupby_user_from = df_cdr_filter.groupby('user_from')
	
	print(len(df_cdr_groupby_user_from),"user_from...")
	
		
	valid_users = [] # Aqui vão ficar guardados os usuários com residência calculada
	                 # Chamei de valid_users porque são os usuários que passam nos critérios.
	residence_antenna = [] # Aqui vão ficar as residências dos usuários.
	                       # Tomei como residência a antena que ele mais usa
	                       # (segundo os critérios definidos)
	
	# Critérios:
	# 1) Número mínimo e máximo de ligações
	# 2) Número de dias distintos de ligações
	# 3) Número de stay_locations
	#    (um stay_location é um local onde o usuário fica à noite ou no domingo)
	
	all_valid_users = [] # Aqui vão todos os usuários que poderiam ter residência calculada (os candidatos)
	all_count_stay_locations = [] # Aqui vão as contagens dos stay locations (para poder filtrar)
	# all_valid_users e all_count_stay_locations se referem a usuários (e localizações)
	# que passaram nos critérios 1 e 2, mas não necessariamente no 3
		
	for user in df_cdr_groupby_user_from:
		num_calls_ok = False
		#print("[0]",user[0])
		user_from = user[0]
		####print("user_from",user_from)
		df_user = user[1]
		num_calls = len(df_user.index)
		###print("num_calls:",num_calls)
		
		if num_calls >= 3 and num_calls < 500: # Atendeu ao critério 1 (número de ligações)
			 num_calls_ok = True
		#	else:
		#		invalid_more_than_max_calls.append(user_from)
		#else:
		#	invalid_less_than_min_calls.append(user_from)
		#num_calls_ok = True
		if num_calls_ok == True: # Antendeu ao número de ligações. Vamos verificar o número de dias.
			####print("\tentrou no critério num_calls")
			num_days = len(set(df_user.date))
			###print("num_days:",num_days)
			
			if num_days >= 3: # Atende ao critério 2 (número de dias distintos)
				####print("\tentrou no critério num_days")
			
				stay_locations = []
			
				###print(df_user.date)
				
				for date,time,antenna in zip(df_user.date, df_user.time, df_user.antenna):
					###print(date,time)
					#Monday is 0 and Sunday is 6.
					weekday = datetime.date.fromisoformat(date).weekday()
					if 0 <= weekday <= 4: # dia da semana
						###print("dia da semana")
						time_call = datetime.time.fromisoformat(time)
						
						time19h = datetime.time(19,0,0)
						time6h = datetime.time(6,0,0)
						
						if time_call >= time19h or time_call <= time6h:
							#print("---noite")
							stay_locations.append(antenna)
						#else:
						#	#print("---diaa")
					elif weekday == 6: # domingo
						stay_locations.append(antenna)
						###print("domingo")
				#end for date,time,antenna
				# Vamos processar o stay_locations
				
				num_stay_locations = len(stay_locations)
				all_valid_users.append(user_from)
				all_count_stay_locations.append(len(set(stay_locations)))
				
				if num_stay_locations > 0: # Antendeu ao critério 3 (número de stay_locations)
					####print("\tentrou no critério de stay locations > 0")
					###print(stay_locations)
					
					max_count_location = 0
					residence = -1
					for location in set(stay_locations):
						count_location = stay_locations.count(location)
						###print(location,count_location)
						if count_location > (num_stay_locations * 0.5):
						#if count_location > max_count_location:
							max_count_location = count_location
							
							#####print("\tachou uma location com frequência maior que a metade")
							###print("count_location",count_location)
							###print("num_stay_locations",num_stay_locations)
							###print("(num_stay_locations / 2)",(num_stay_locations / 2))
							residence = location # A residência será o local onde ele passa mais tempo. 
							####print("\t\t\t*** residência:",residence)
							
							valid_users.append(user_from)
							residence_antenna.append(residence)
						# end if count_location > (num_stay_locations / 2)
					# end for location in set(stay_locations):
						
				# end if num_stay_locations > 0		
			# end if numdays >= 3
			#else: #num_days
			#	invalid_less_than_min_days.append(user)
		#end num_calls_ok == True
	# end user in df_cdr_groupby_user_from		
	
		
	return [valid_users,residence_antenna,all_valid_users,all_count_stay_locations]
	
	
	
#end calculate_residence_antenna
"""
# %% codecell
# Nesse momento, eu já preciso ter o df_cdr e o df_antennas
# em arquivos para serem lidos

region = 'sjdr' # Nome da região, para referência no código
prefix = '/media/vinicius/vinicius-HDD3TB/TODAS_UFS_CDR/%s/' % (region)

cdr_filename_region = '%s/cdr_regiao_imediata_%s_all_unique.txt' % (prefix,region)
cdr_filename_region_out = '%s/cdr_regiao_imediata_%s_all_unique_filtered.txt' % (prefix,region)
df_antennas_region_filename = '%s/antennas_%s_unique.txt' % (prefix,region)


# %% codecell
"""
# Acho que foi esse trecho que eliminei e implementei uma versão "memory friendly"
#df_cdr = df_cdr.head(1000)
#[df_cdr_filter] = filter_cdr_duration_calls(df_cdr) # <==== MEXER AQUI PARA SETAR FILTROS!!
cdr_filename_region_out = '%s/cdr_regiao_imediata_%s_all_unique_calls_filtered.txt' % (prefix,region)
filter_cdr_duration_calls_big_file(cdr_filename_region, cdr_filename_region_out)

cdr_filename_region_calls_filtered = cdr_filename_region_out

#print(df_cdr.head(20))
#print(df_antennas)
"""
# %% codecell




import pickle

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

# %% codecell
"""
# Esse trecho eu não uso mais. Substituí pelo trecho acima, que é "memory friendly"
#[valid_users,residence_antenna,all_valid_users,all_count_stay_locations] = calculate_residence_antenna(df_cdr_filter) # <==== MEXER AQUI PARA SETAR FILTROS!!
[valid_users,residence_antenna,all_valid_users,all_count_stay_locations] = calculate_residence_antenna(cdr_filename_region_calls_filtered) # <==== MEXER AQUI PARA SETAR FILTROS!!
"""

"""
# Acho que não precisa salvar isso... muito grande e pesado de abrir
# %% codecell
d = {'user': dict_users_residence_antenna.keys(), 'residence_antenna': dict_users_residence_antenna.values()}
df_residence_antenna = pd.DataFrame(data=d)
df_residence_antenna.to_csv ('%s/residence_antenna_%s.csv' % (prefix,region), index = False, header=True, sep=";")
# Agora eu tenho a residência presumida de cada usuário. Posso finalizar o o script.
# ALERTA!! ABRIR ESSE CSV É TRETA. SALVEI TB UM DICIONÁRIO, MUITO MAIS EFICIENTE.
"""
# %% codecell
