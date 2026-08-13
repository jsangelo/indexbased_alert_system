import pandas as pd
import numpy as np
import ast
import os


pd.set_option("mode.copy_on_write", True)


def atribuir_zalert(corte_alerta,df_validacao,df_padronizado,df_original,p_otimizado,resultados):
    """
    Executa os experimentos para cada vetor de pesos.
    """

    j = list(range(len(p_otimizado)))

    for i, pesos in enumerate(p_otimizado):

        # Calcular a coluna 'indice' para todos os clusters
        df = df_padronizado.copy()

        df["indice"] = (
            df[["num_reg","intervalo","freq_num_reg","freq_a_quant","extensao","perc_mortos","morto"]] * pesos
        ).sum(axis=1)

        # Normalizar o índice
        df["indice_norm"] = (
            (df["indice"] - df["indice"].min()) / (df["indice"].max() - df["indice"].min())
        )

        # Atribuir os índices ao dataframe original
        df_original["indice"] = df["indice"]
        df_original["indice_norm"] = df["indice_norm"]

        df_index = df_original.copy()

        # Calcular o valor de corte
        quartil_de_corte = df_index["indice"].quantile(corte_alerta)

        # Definir alertas e não alertas
        df_alerta = df_index[df_index["indice"] >= quartil_de_corte]
        df_alerta["alerta"] = 1

        df_nao_alerta = df_index[df_index["indice"] < quartil_de_corte]
        df_nao_alerta["alerta"] = 0

        # Análise dos resultados
        analise_resultados = df_alerta["indice"].describe()

        # Gerar dataframe completo
        df_completa = pd.concat(
            [df_alerta, df_nao_alerta]
        )

        # Armazenar resultados
        resultados.append(
            {
                "solucao": j[i],
                "configuracao": j[i],
                "corte": corte_alerta,
                "pesos": pesos,
                "analise": analise_resultados,
                "dataframe": df_completa.copy(),
            }
        )


def executar_experimentos(path, output_dir, time_limit, distance_limit):

    # ==========================================================
    # Leitura das bases
    # ==========================================================

    df_original = pd.read_csv(f"{path}/_clusters_{time_limit}d_{distance_limit}km_caracterizados_municipios.csv")
    df_padronizado = pd.read_csv(f"{path}/_clusters_{time_limit}d_{distance_limit}km_padronizado_municipios.csv")

    # Ajustar geocode
    df_original["geocode"] = (pd.to_numeric(df_original["geocode"]).astype("int64"))
    df_padronizado["geocode"] = (pd.to_numeric(df_padronizado["geocode"]).astype("int64"))

    # ==========================================================
    # Filtrar clusters válidos
    # ==========================================================

    df_validacao_original = (
        df_original[df_original["Cluster2"] != -1]
    )

    df_validacao_padronizado = (
        df_padronizado[df_padronizado["Cluster2"] != -1]
    )

    # ==========================================================
    # Leitura dos vetores de solução
    # ==========================================================

    arquivo = (f"{path}/_solution_vectors_{time_limit}d_{distance_limit}km.txt")

    with open(arquivo, "r") as f:

        p_otimizado = np.array(
            [
                ast.literal_eval(linha.strip())
                for linha in f
                if linha.strip()
            ]
        )

    # ==========================================================
    # Executar experimentos
    # ==========================================================

    resultados = []

    threshold_level = [0.8,0.85,0.9,0.95,0.99]

    for threshold in threshold_level:

        atribuir_zalert(threshold,df_validacao_original,df_validacao_padronizado,df_original,p_otimizado,resultados)

    # ==========================================================
    # Exportação dos resultados
    # ==========================================================

    for resultado in resultados:

        config = resultado["configuracao"]
        corte = resultado["corte"]

        print(
            f"Results: threshold_{corte} - "
            f"pareto_solution_{config}"
        )

        R = pd.DataFrame(
            resultado["dataframe"]
        )

        R.to_csv(f"{output_dir}/_clusters_zalert_{time_limit}d_{distance_limit}km_{corte}_{config}.csv")

# ==============================================================
# Execução principal
# ==============================================================

if __name__ == "__main__":

    # ==========================================================
    # Configurações
    # ==========================================================

    path = "../data/results"
    output_dir = f"{path}/final_results"
    os.makedirs(output_dir, exist_ok=True)

    # Parâmetros de clusterização
    time_limit = 30
    distance_limit = 1

    print(f"Starting experiments for time limit of {time_limit} days and distance limit of {distance_limit} km.")

    executar_experimentos(path, output_dir, time_limit, distance_limit)

    print(f"Experiments completed. Results saved in '{output_dir}'.")
