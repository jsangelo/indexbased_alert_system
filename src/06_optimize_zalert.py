import os
import numpy as np
import pandas as pd
from scipy.optimize import minimize

def objective(weights, variables, mortos_weights, alpha):
    """
    Calculates the objective function to be maximized, which is a combination of the average of the weighted index values and their variance.
    The function is designed to be minimized, so it returns the negative of the objective value.
    Args:
        weights (array): The weights for each variable.
        variables (array): The values of the variables for each cluster.
        mortos_weights (array): The weights for the 'morto' variable, used to calculate the weighted average.
        alpha (float): The weight given to the average in the objective function.
    Returns:
        float: The negative of the objective value, which is a combination of the weighted average and variance of the index values.
    """
    index_values = np.dot(variables, weights)
    obj1 = np.average(index_values, weights=mortos_weights)  # Maximização da média dos casos confirmados
    obj2 = np.var(index_values)                              # Minimização da variância
    obj = alpha * obj1 - (1 - alpha) * obj2
    return -obj

def optimize_alert_index_weights(path, time_limit, distance_limit):
    """
    It loads the cluster data, performs weight optimization via SLSQP for different alpha values, 
    and saves the solution vectors and objective function values.
    """
    try:
        # Lendo os arquivos de entrada
        file_caracterizados = f"{path}/_clusters_{time_limit}d_{distance_limit}km_caracterizados.csv"
        file_padronizado = f"{path}/_clusters_{time_limit}d_{distance_limit}km_padronizado.csv"
        
        df_original = pd.read_csv(file_caracterizados, index_col=0)
        df_padronizado = pd.read_csv(file_padronizado, index_col=0)

        # Filtrar apenas por clusters que têm mais de um registro
        filtered_df_original = df_original[df_original['Cluster2'] != -1]
        filtered_df_padronizado = df_padronizado[df_padronizado['Cluster2'] != -1]

        # Filtrar os clusters confirmados
        cluster_fil = filtered_df_padronizado[filtered_df_original["confirmado"] != 0]

        col = ["num_reg", "intervalo", "freq_num_reg", "freq_a_quant", "extensao", "perc_mortos", "morto"]
        variables = cluster_fil[col].values
        var_count = len(col)

        solution = []
        solution_obj = []

        # Restrições e limites para otimização
        constraints = ({'type': 'eq', 'fun': lambda weights: np.sum(weights) - 1})
        bounds = [(0, 1) for _ in range(var_count)]
        initial_weights = np.ones(var_count) / var_count

        alphas = [0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1]

        # Executando a otimização para cada alpha
        for alpha in alphas:
            result = minimize(
                objective, 
                initial_weights, 
                args=(variables, cluster_fil['morto'], alpha), 
                method='SLSQP', 
                bounds=bounds, 
                constraints=constraints,
                options={'disp': False, 'ftol': 1e-10}
            ) 

            optimal_weights = result.x 
            
            index_values = np.dot(variables, optimal_weights) 
            obj1 = np.average(index_values, weights=cluster_fil['morto']) 
            obj2 = np.var(index_values) 
            obj = alpha * obj1 - (1 - alpha) * obj2 

            solution.append([*optimal_weights]) 
            solution_obj.append([-obj, obj1, obj2]) 

        # Avaliação com chute inicial sem otimização 
        index_values = np.dot(variables, initial_weights) 
        obj1 = np.average(index_values, weights=cluster_fil['morto']) 
        obj2 = np.var(index_values) 
        obj = alphas[-1] * obj1 - (1 - alphas[-1]) * obj2 

        solution.append([*initial_weights]) 
        solution_obj.append([-obj, obj1, obj2]) 

        # Criar diretório de saída caso não exista 
        output_dir = f'{path}' 
        os.makedirs(output_dir, exist_ok=True)

        # Salvando soluções em arquivo 
        file_solutions = f'{output_dir}/_solution_vectors_{time_limit}d_{distance_limit}km.txt'
        with open(file_solutions, 'w') as arquivo: 
            for s in solution: 
                arquivo.write(f'{s},\n') 
            
        file_objectives = f'{output_dir}/_objective_vectors_{time_limit}d_{distance_limit}km.txt'
        with open(file_objectives, 'w') as arquivo: 
            for so in solution_obj: 
                arquivo.write(f'{so},\n') 

        print(f"Solutions successfully saved in '{file_solutions}' e '{file_objectives}'.")

    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
    except Exception as e:
        print(f"An error occurred during optimization: {e}")

if __name__ == '__main__':
    # Define o nome do arquivo de entrada e saída
    path = '../data'
    output_dir = f"{path}/results"
    os.makedirs(output_dir, exist_ok=True)

    # Clustering parameters
    time_limit_days = 30
    distance_limit_km = 1

    print(f"Starting optimization of alert index weights for time limit of {time_limit_days} days and distance limit of {distance_limit_km} km.")

    # Chama a função principal de otimização
    optimize_alert_index_weights(output_dir, time_limit_days, distance_limit_km)