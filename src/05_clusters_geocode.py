import pandas as pd
import os

# ------------------------------------------------------------------
# Cria a tabela de municípios por cluster
# ------------------------------------------------------------------

def create_municipios_por_cluster(arquivo_clusters_registros, arquivos_alvo):
    """
    Cria uma tabela que associa cada cluster aos municípios correspondentes.

    Args:
        arquivo_clusters_registros (str): O caminho do arquivo CSV que contém os registros com clusters.
        arquivos_alvo (list): Lista de caminhos dos arquivos CSV que receberão as novas colunas.

    Returns:
        pandas.DataFrame: Um DataFrame contendo a associação de clusters e municípios.
    """
    registros_cluster = pd.read_csv(arquivo_clusters_registros)

    ## Gera uma linha para cada combinação de cluster e geocode
    municipios_por_cluster = (
        registros_cluster[
            ["Cluster1", "geocode", "UF", "MUN"]
        ]
        .drop_duplicates(subset=['Cluster1', 'MUN','UF'])
        .sort_values(["Cluster1", "UF", "MUN"])
        .reset_index(drop=True)
    )


    # ------------------------------------------------------------------
    # Processa cada arquivo
    # ------------------------------------------------------------------

    for arquivo in arquivos_alvo:

        print(f"Processing {arquivo}...")

        df = pd.read_csv(arquivo)

        # Junta as informações dos municípios
        df_saida = df.merge(
            municipios_por_cluster,
            on="Cluster1",
            how="left"
        )

        # Nome do arquivo de saída
        arquivo_saida = arquivo.replace(".csv", "_municipios.csv")

        # Salva o resultado
        df_saida.to_csv(
            arquivo_saida,
            index=False,
            encoding="utf-8-sig"
        )

        print(f"The file containing the clusters with geocodes was saved as: {arquivo_saida}")


if __name__ == '__main__':

    # Define o nome do arquivo de entrada e saída
    path = '../data'

    output_dir = f"{path}/results"
    os.makedirs(output_dir, exist_ok=True)

    # Parâmetros de clusterização
    time_limit_days = 30
    distance_limit_km = 1

    # Arquivo que contém a associação dos registros aos clusters
    arquivo_clusters_registros = f"{output_dir}/_clusters_{time_limit_days}d_{distance_limit_km}km.csv"

    # Arquivos que receberão as novas colunas
    arquivos_alvo = [
        f"{output_dir}/_clusters_{time_limit_days}d_{distance_limit_km}km_caracterizados.csv",
        f"{output_dir}/_clusters_{time_limit_days}d_{distance_limit_km}km_normalizado.csv",
        f"{output_dir}/_clusters_{time_limit_days}d_{distance_limit_km}km_padronizado.csv"
    ]

    # Chama a função principal
    create_municipios_por_cluster(arquivo_clusters_registros, arquivos_alvo)