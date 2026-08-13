import pandas as pd
import numpy as np
from geopy.distance import geodesic
from itertools import combinations
import os

def calculate_spatial_extent(df):
    # Função interna para calcular a distância máxima dentro de um grupo
    def get_max_cluster_dist(group):
        # Cria uma lista de tuplas (lat, long)
        coords = list(zip(group['r_lat'], group['r_long']))
        
        # Se houver apenas um ponto, a distância é zero
        if len(coords) < 2:
            return 0.0
        
        # Calcula a distância geodésica para todos os pares possíveis e pega a máxima
        # combinations(coords, 2) gera todos os pares únicos sem repetição
        max_d = max(geodesic(p1, p2).km for p1, p2 in combinations(coords, 2))
        return max_d

    # Agrupa por Cluster1 e Cluster2 e aplica a função em cada grupo
    extensao_data = df.groupby(['Cluster1', 'Cluster2']).apply(get_max_cluster_dist).reset_index()
    
    # Renomeia a coluna de resultado (que o pandas chama de 0 por padrão)
    extensao_data.columns = ['Cluster1', 'Cluster2', 'extensao']
    
    return extensao_data.set_index(['Cluster1', 'Cluster2'])


def standardize_data(df):
    """
    Uniformização dos campos 'classificação' e 'doença' no df original
    """
    df['d_classificacao'] = np.where( df['d_classificacao'].notna() & df['d_classificacao'].str.contains('"Confirmada"'), '"Confirmada"', df['d_classificacao']) 
    df['d_classificacao'] = np.where( df['d_classificacao'].notna() & df['d_classificacao'].str.contains('"Indeterminada"'), '"Indeterminada"', df['d_classificacao']) 
    df['d_classificacao'] = np.where( df['d_classificacao'].notna() & df['d_classificacao'].str.contains('"Descartada"'), '"Descartada"', df['d_classificacao']) 
    df['d_doenca'] = np.where( df['d_doenca'].notna() & df['d_doenca'].str.contains('"Febre Amarela"'), '"Febre Amarela"', df['d_classificacao']) 

    return df


def standardize_clusters(df):

    #############
    # Calcula a padronização das colunas que poderão compor o índice de alerta ou que podem ser utilizados na detecção de anomalias
    # Normalização: Coloca os registros entre 0 e 1
    # Padronização Z-Score: Coloca os registros com média igual a zero e desvio padrão igual a 1.
    #############

    base_col = ["morto","vivo","a_quant","intervalo","num_reg","confirmado",
                "freq_num_reg","freq_morto","freq_vivo","freq_a_quant",
                "perc_mortos","perc_vivos", "perc_doente", "perc_estranho", "perc_normal", "extensao","perc_agressivo"]

    df_norm = df.copy()
    df_std = df.copy()
                
    #-- Normalização
    for col in base_col:
        df_norm[col] = ( (df[col] - df[col].min() ) / (df[col].max() - df[col].min() ) )    
    
    #-- Padronização Z-score
    for col in base_col:
        df_std[col] = ( (df[col] - df[col].mean() ) / df[col].std() )

    return df_norm, df_std

def calculate_cluster_characteristics(input_csv, output_csv, output_csv_norm, output_csv_std):
    """
    Calcula as características de cada cluster a partir de um arquivo CSV
    que já contém os registros com suas respectivas atribuições de cluster.

    Args:
        input_csv (str): Caminho para o arquivo CSV de entrada com os clusters.
        output_csv (str): Caminho para salvar o arquivo CSV de saída com as
                          características dos clusters.
    """
    try:
        # Leitura do arquivo de entrada com os clusters
        data = pd.read_csv(input_csv, index_col=0)
        
        # Converter a coluna de data para o formato datetime, se ainda não estiver
        data['r_data'] = pd.to_datetime(data['r_data'])

        # Uniformizar os atributos de classificação e doença  
        #data_uniform = standardize_data(data)
            
        # df contendo os registros com os clusters        
        #df_clusters = data_uniform.copy()        
        df_clusters = data.copy()        

        # 1. Calcular a quantidade de 'mortos' e 'vivos' por cluster
        count_situacao = df_clusters.groupby(["Cluster1","Cluster2","a_situacao"])['a_quantidade'].sum().unstack(fill_value=0)
        count_situacao = count_situacao.rename(columns={'Morto': 'morto', 'Vivo': 'vivo'})

        # 2. Calcular a quantidade de 'Normal', 'Doente', 'Estranho' e 'Agressivo' por cluster
        # As categorias 'Normal', 'Doente', 'Estranho' e 'Agressivo' só aparecem quando 'a_comportamento' é diferente de nulo
        #   Essas categorias só aparecem quando tem animal vivo no cluster
        # Neste caso, criei uma catedoria 'sem_info' quando não houver informação em 'a_comportamento', ou seja,
        #   quando no cluster só tiver animais mortos.
        # Em seguida, eu deleto a coluna 'sem_info'.
        # Assim, consegui garantir o valor 'zero' em todas as colunas onde só tem animais mortos no cluster
        df = df_clusters.copy()        
        df.loc[df['a_comportamento'].isnull(), 'a_comportamento'] = 'sem_info'        
        count_comportamento = df.groupby(["Cluster1","Cluster2","a_comportamento"])["a_quantidade"].sum().unstack(fill_value=0)
        count_comportamento = count_comportamento.rename(columns={'Normal':"normal",'Estranho':"estranho", 'Doente': "doente", 'Agressivo': "agressivo"})        
        count_comportamento = count_comportamento.drop(columns='sem_info')
        #print(count_comportamento.info())

        # 3. Calcular a soma da quantidade de animais por cluster
        quant_animais = df_clusters.groupby(["Cluster1","Cluster2"])['a_quantidade'].sum().rename('a_quant')        

        # 4. Calcular o intervalo de tempo de cada cluster
        dates = df_clusters.groupby(["Cluster1","Cluster2"])['r_data'].agg(['min', 'max']).rename(columns={'min':"data_ini",'max':"data_fim"})
        dates["intervalo"] = (dates["data_fim"] - dates["data_ini"]).dt.days 
        dates["intervalo"] = dates["intervalo"].apply(lambda x: x if x > 0 else 1)                

        # 5. Calcular a extensão espacial de cada cluster 
        extensao = calculate_spatial_extent(df_clusters)

        # 6. Calcula o número de registros confirmados por alguma doença
        confirmados_por_cluster = df_clusters.groupby(["Cluster1","Cluster2"])['d_classificacao'].apply(
            lambda x: (x == '"Confirmada"').sum()
        ).rename("confirmado")                                              

        # 7. Unir todos os atributos calculados
        df_clusters_union = (
            pd.DataFrame(quant_animais)
            .join(count_situacao, on=['Cluster1','Cluster2'])
            .join(count_comportamento, on=['Cluster1','Cluster2'])
            .join(dates[['data_ini', 'data_fim', 'intervalo']], on=['Cluster1','Cluster2'])
            .join(extensao, on=['Cluster1','Cluster2'])            
            .join(confirmados_por_cluster, on=['Cluster1','Cluster2'])
        )        
        #print(df_clusters_union.head(15))

        # 8. Calcular número de registros por cluster
        df_clusters_union['num_reg'] = df_clusters.groupby(['Cluster1','Cluster2']).size()
        
        # 9. Calcular atributos de frequência
        df_clusters_union['freq_num_reg'] = df_clusters_union['num_reg'] / df_clusters_union['intervalo']
        df_clusters_union['freq_a_quant'] = df_clusters_union['a_quant'] / df_clusters_union['intervalo']
        df_clusters_union['freq_vivo'] = df_clusters_union['vivo'] / df_clusters_union['intervalo']
        df_clusters_union['freq_morto'] = df_clusters_union['morto'] / df_clusters_union['intervalo']
        
        # 10. Calcular atributos de percentual
        df_clusters_union['perc_mortos'] = (df_clusters_union['morto'] / df_clusters_union['a_quant']).fillna(0)
        df_clusters_union['perc_vivos'] = (df_clusters_union['vivo'] / df_clusters_union['a_quant']).fillna(0)        
        df_clusters_union['perc_normal'] = (df_clusters_union['normal'] / df_clusters_union['a_quant']).fillna(0)        
        df_clusters_union['perc_estranho'] = (df_clusters_union['estranho'] / df_clusters_union['a_quant']).fillna(0)        
        df_clusters_union['perc_doente'] = (df_clusters_union['doente'] / df_clusters_union['a_quant']).fillna(0)        
        df_clusters_union['perc_agressivo'] = (df_clusters_union['agressivo'] / df_clusters_union['a_quant']).fillna(0)        
        df_clusters_union.reset_index(inplace=True)        

        # 11. Salvar o dataframe resultante
        df_clusters_union.to_csv(output_csv, index=True)

        # 12. Normalizar e padronizar os atributos calculados
        df1, df2 = standardize_clusters(df_clusters_union)
        df1.to_csv(output_csv_norm, index=True)
        df2.to_csv(output_csv_std, index=True)
        
        print(f"The cluster's characterization was saved as '{output_csv}'.")
        print(f"The file with the normalized clusters was saved as '{output_csv_norm}'.")
        print(f"The file with the standardized clusters was saved as '{output_csv_std}'.")

    except FileNotFoundError:
        print(f"Error: The file '{input_csv}' was not found.")
    except Exception as e:
        print(f"Error occurred during cluster analysis: {e}")

if __name__ == '__main__':

    # Define o nome do arquivo de entrada e saída
    path = '../data'
    output_dir = f"{path}/results"
    os.makedirs(output_dir, exist_ok=True)

    # Clustering parameters
    time_limit_days = 30
    distance_limit_km = 1

    input_file = f'{output_dir}/_clusters_{time_limit_days}d_{distance_limit_km}km.csv'

    print(f"Reading data from the input file: {input_file}")

    output_file = f'{output_dir}/_clusters_{time_limit_days}d_{distance_limit_km}km_caracterizados.csv'
    output_file_norm = f'{output_dir}/_clusters_{time_limit_days}d_{distance_limit_km}km_normalizado.csv'
    output_file_std = f'{output_dir}/_clusters_{time_limit_days}d_{distance_limit_km}km_padronizado.csv'

    # Chama a função principal
    calculate_cluster_characteristics(input_file, output_file, output_file_norm, output_file_std)