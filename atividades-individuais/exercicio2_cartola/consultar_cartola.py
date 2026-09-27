import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "cartola_fc_db")


def conectar_mongodb():
    client = MongoClient(MONGO_URI)
    return client[MONGO_DB_NAME]


def exibir_status_mercado(db):
    print("=" * 60)
    print("STATUS ATUAL DO MERCADO")
    print("=" * 60)
    
    status = db.mercado_rodada_atual.find_one()
    if status:
        print(f"• Rodada Atual: {status.get('rodada_atual')}")
        print(f"• Status do Mercado: {'Aberto' if status.get('status_mercado') == 1 else 'Fechado'}")
        print(f"• Última Coleta: {status.get('timestamp_coleta')}")
    else:
        print("Nenhum registro de mercado encontrado.")


def listar_atletas_mais_caros(db, limite=5):
    print("\n" + "=" * 60)
    print(f"TOP {limite} ATLETAS MAIS CAROS")
    print("=" * 60)

    atletas = (
        db.atletas_rodada_atual.find({}, {"apelido": 1, "preco_num": 1, "clube_id": 1})
        .sort("preco_num", -1)
        .limit(limite)
    )

    for i, atleta in enumerate(atletas, 1):
        print(
            f"{i}º {atleta.get('apelido'):<20} | Preço: C$ {atleta.get('preco_num'):<6.2f}"
        )


def listar_atletas_maior_media(db, limite=5):
    print("\n" + "=" * 60)
    print(f"TOP {limite} ATLETAS COM MAIOR MÉDIA DE PONTOS")
    print("=" * 60)

    atletas = (
        db.atletas_rodada_atual.find({}, {"apelido": 1, "media_num": 1, "jogos_num": 1})
        .sort("media_num", -1)
        .limit(limite)
    )

    for i, atleta in enumerate(atletas, 1):
        print(
            f"{i}º {atleta.get('apelido'):<20} | Média: {atleta.get('media_num'):<5.2f} pts | Jogos: {atleta.get('jogos_num')}"
        )


def relatorio_completo_atletas_e_clubes(db, limite=5):
    print("\n" + "=" * 60)
    print(f"TOP {limite} PONTUADORES")
    print("=" * 60)

    pipeline = [
        {"$sort": {"pontos_num": -1}},
        {"$limit": limite},
        {
            "$lookup": {
                "from": "clubes_rodada_atual",
                "localField": "clube_id",
                "foreignField": "_id",
                "as": "clube_info",
            }
        },
        {"$unwind": "$clube_info"},
        {
            "$project": {
                "apelido": 1,
                "pontos_num": 1,
                "nome_clube": "$clube_info.nome",
            }
        },
    ]

    resultados = db.atletas_rodada_atual.aggregate(pipeline)

    for i, doc in enumerate(resultados, 1):
        print(
            f"{i}º {doc.get('apelido'):<18} ({doc.get('nome_clube')}) | Última Pontuação: {doc.get('pontos_num')} pts"
        )


if __name__ == "__main__":
    db = conectar_mongodb()

    exibir_status_mercado(db)
    listar_atletas_mais_caros(db, limite=5)
    listar_atletas_maior_media(db, limite=5)
    relatorio_completo_atletas_e_clubes(db, limite=5)