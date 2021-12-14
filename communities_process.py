import networkx as nx
from cdlib.algorithms import louvain
import pickle

def get_communities(path_network):
    """
    get_communities recebe uma rede com a claase de renda de cada nó 
    e retorna um dicionário onde a chave é o número da comunidade e os 
    valores são a classe de renda de cada usuário dentro da comunidade
    """
    G = nx.read_gml(path_network)
    dict_income = dict()
    for node in G.nodes():
        dict_income[node] = G.nodes[node]
    comm = louvain(G)
    dict_communities = dict()
    j = 0 
    for c in comm.communities:
        list_income = []
        for i in c:
            list_income.append(dict_income.get(i)['incomeclass'])
        dict_communities[j] = list_income
        j += 1  
    print('Comunidades divididas')
    return dict_communities

def get_percent_of_income_class_in_comm(dict_communities, path_out):
    """
    get_percent_of_income_class_in_comm recebe um dicionário com as 
    comunidades e classe de renda de cada indivíduo e contabiliza a 
    porcentagem de cada classe de renda dentro de cada comunidade
    """
    dict_count = dict()
    
    for k, v in dict_communities.items():
        dict_count[k] = {i: v.count(i) for i in v}
    
    for key, value in dict_count.items():
        dict_values = []
        for _value in value.values():
            dict_values.append(_value)
        value['Size'] = sum(dict_values)
    dict_percent_full = dict()
    
    for key, value in dict_count.items():
        dict_percent = dict()
        for k, v in value.items():
            dict_percent[k] = round(v/value['Size'], 2)
        dict_percent_full[key] = dict_percent
        dict_percent_full[key]['Size'] = value['Size']
    
    for key,value in dict_percent_full.items():
        for k,v in value.items():
            if k == None:
                value[0] = value.pop(k)
    with open(path_out, 'wb') as handle:
        print('Gerando o arquivo pickle')
        pickle.dump(dict_percent_full, handle, protocol=pickle.HIGHEST_PROTOCOL)
    
    return dict_percent_full

dict_comm = get_communities('/home/gustavo/Desktop/Mestrado/mestrado_dados/assign_income_class/sjdr/social_networks/sjdr_social_undirected_no_null_outdegree_income_class.gml')
get_percent_of_income_class_in_comm(dict_comm,'/home/gustavo/Desktop/Mestrado/mestrado_dados/dict_comm_sjdr_.pickle')



