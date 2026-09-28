import logging
import os
import sys
from typing import Any, Dict, List
from dotenv import load_dotenv
from pymongo import MongoClient, UpdateOne
from pymongo.errors import PyMongoError
import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "openf1_data"
API_BASE_URL = "https://api.openf1.org/v1"

SESSION_KEY = 9159
MEETING_KEY = 1219


def conectar_mongodb():
    try:
        client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        logging.info("Conexão com o MongoDB estabelecida com sucesso.")
        return client[DB_NAME]
    except PyMongoError as err:
        logging.error(f"Falha ao conectar no MongoDB: {err}")
        sys.exit(1)


def fetch_data(endpoint: str, params: dict) -> list:
    url = f"{API_BASE_URL.rstrip('/')}/{endpoint.lstrip('/')}"
    headers = {
        "Accept": "application/json",
        "User-Agent": "OpenF1DataIngestor/2.0",
    }

    logging.info(
        f"Buscando dados no endpoint '{endpoint}' | Parâmetros: {params}"
    )

    try:
        with requests.Session() as session:
            response = session.get(
                url, params=params, headers=headers, timeout=30
            )
            response.raise_for_status()
            data = response.json()

            data_list = data if isinstance(data, list) else [data]
            logging.info(
                f"Retornados {len(data_list)} registros de '{endpoint}'."
            )
            return data_list

    except requests.RequestException as err:
        logging.error(f"Erro na requisição HTTP para '{endpoint}': {err}")
        return []


def save_to_collection(
    db, data: list, collection_name: str, unique_keys: list
):
    if not data:
        logging.warning(
            f"Nenhum dado a ser gravado na coleção '{collection_name}'."
        )
        return

    collection = db[collection_name]
    operacoes = []

    for item in data:
        query_filtro = {
            key: item.get(key) for key in unique_keys if item.get(key) is not None
        }

        if len(query_filtro) == len(unique_keys):
            operacoes.append(
                UpdateOne(query_filtro, {"$set": item}, upsert=True)
            )
        else:
            logging.warning(
                f"Registro ignorado na coleção '{collection_name}' por falta de chave única: {item}"
            )

    if operacoes:
        try:
            resultado = collection.bulk_write(operacoes, ordered=False)
            total_processado = (resultado.upserted_count or 0) + (
                resultado.modified_count or 0
            )
            logging.info(
                f"Coleção [{collection_name}]: {len(operacoes)} documentos processados/atualizados."
            )
        except PyMongoError as err:
            logging.error(
                f"Erro durante a gravação em lote na coleção '{collection_name}': {err}"
            )


def main():
    logging.info("=== Iniciando Pipeline de Ingestão OpenF1 ===")

    db = conectar_mongodb()

    sessions_params = {"session_key": SESSION_KEY, "meeting_key": MEETING_KEY}
    sessions_data = fetch_data("sessions", sessions_params)
    save_to_collection(db, sessions_data, "sessions", ["session_key"])

    drivers_params = {"session_key": SESSION_KEY}
    drivers_data = fetch_data("drivers", drivers_params)
    save_to_collection(
        db, drivers_data, "drivers", ["session_key", "driver_number"]
    )

    laps_params = {"session_key": SESSION_KEY}
    laps_data = fetch_data("laps", laps_params)
    save_to_collection(
        db,
        laps_data,
        "laps",
        ["session_key", "driver_number", "lap_number"],
    )

    logging.info("=== Ingestão Concluída com Sucesso! ===")


if __name__ == "__main__":
    main()