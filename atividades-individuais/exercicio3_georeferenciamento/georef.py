import os
import sys
import requests
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

URL_DADOS = os.getenv("URL_DADOS", "https://s3-sa-east-1.amazonaws.com/ckan.saude.gov.br/UBS/ubs.csv")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "geodados"
COLLECTION_NAME = "unidades_saude"
TEMP_FILE = "ubs_dados.csv"


def extrair_dados(url: str, caminho_saida: str) -> bool:
    print(f"Baixando dados abertos da URL: {url}")
    try:
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        with open(caminho_saida, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        print("Download concluído com sucesso.")
        return True
    except requests.RequestException as e:
        print(f"Erro ao baixar dados da fonte: {e}")
        return False


def transformar_para_geojson(caminho_csv: str) -> list:
    print("Processando e transformando os dados em GeoJSON...")
    try:
        df = pd.read_csv(caminho_csv, sep=";", encoding="latin-1", low_memory=False)
        
        colunas_relevantes = [
            "CO_UF", "NO_UF", "CO_MUNICIPIO_GESTOR", "NO_MUNICIPIO_GESTOR",
            "CO_CNES", "NU_LATITUDE", "NU_LONGITUDE", "NO_LOGRADOURO",
            "NO_BAIRRO", "CO_CEP", "NU_TELEFONE"
        ]
        df = df[colunas_relevantes].copy()
        
        df.columns = [
            "cod_uf", "uf", "cod_municipio", "municipio",
            "cod_cnes", "latitude", "longitude", "logradouro",
            "bairro", "cep", "telefone"
        ]
        
        df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
        df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
        df = df.dropna(subset=["latitude", "longitude"])
        
        features = []
        for _, row in df.iterrows():
            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Point",
                    "coordinates": [float(row["longitude"]), float(row["latitude"])]
                },
                "properties": {
                    "cod_uf": int(row["cod_uf"]) if pd.notna(row["cod_uf"]) else None,
                    "uf": str(row["uf"]),
                    "cod_municipio": int(row["cod_municipio"]) if pd.notna(row["cod_municipio"]) else None,
                    "municipio": str(row["municipio"]),
                    "cod_cnes": int(row["cod_cnes"]) if pd.notna(row["cod_cnes"]) else None,
                    "logradouro": str(row["logradouro"]),
                    "bairro": str(row["bairro"]),
                    "cep": str(row["cep"]).replace(".0", ""),
                    "telefone": str(row["telefone"]).replace(".0", "")
                }
            }
            features.append(feature)
            
        print(f"Total de {len(features)} registros válidos convertidos para GeoJSON.")
        return features
    except Exception as e:
        print(f"Erro na etapa de transformação dos dados: {e}")
        return []


def persistir_mongodb(documentos: list) -> bool:
    if not documentos:
        print("Nenhum registro para salvar no banco.")
        return False
        
    print("Conectando ao MongoDB...")
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        db = client[DB_NAME]
        collection = db[COLLECTION_NAME]
        
        collection.delete_many({})
        resultado = collection.insert_many(documentos)
        print(f"Inseridos {len(resultado.inserted_ids)} documentos na coleção '{COLLECTION_NAME}'.")
        
        collection.create_index([("geometry", "2dsphere")])
        print("Índice geoespacial (2dsphere) criado com sucesso.")
        return True
    except Exception as e:
        print(f"Erro ao persistir os dados no MongoDB: {e}")
        return False


def main():
    print("=== Pipeline de Dados Georreferenciados (Gov.br -> MongoDB) ===")
    
    if extrair_dados(URL_DADOS, TEMP_FILE):
        documentos_geojson = transformar_para_geojson(TEMP_FILE)
        
        if documentos_geojson:
            persistir_mongodb(documentos_geojson)
            
        if os.path.exists(TEMP_FILE):
            os.remove(TEMP_FILE)
            
    print("=== Processo Concluído ===")


if __name__ == "__main__":
    main()