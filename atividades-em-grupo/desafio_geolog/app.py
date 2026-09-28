import os
import random
import sqlite3
from datetime import datetime, timezone

import folium
import plotly.express as px
import pymongo
import streamlit as st
from streamlit_folium import st_folium

st.set_page_config(
    page_title="Plataforma GeoLog - Monitoramento de Frotas",
    page_icon="🚚",
    layout="wide",
)

try:
    import pandas as pd

    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

DB_PATH = "logitech.db"
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = "geolog_db"


def init_sqlite():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS motoristas (
            id INT PRIMARY KEY,
            nome TEXT,
            cnh TEXT,
            status TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS veiculos (
            id INT PRIMARY KEY,
            placa TEXT,
            modelo TEXT,
            motorista_id INT,
            FOREIGN KEY (motorista_id) REFERENCES motoristas(id)
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM motoristas")
    if cursor.fetchone()[0] == 0:
        motoristas_seed = [
            (1, "Carlos Andrade", "123456789", "Ativo"),
            (2, "Mariana Silva", "987654321", "Ativo"),
            (3, "Roberto Souza", "456789123", "Em Descanso"),
        ]
        cursor.executemany(
            "INSERT INTO motoristas VALUES (?, ?, ?, ?)", motoristas_seed
        )

    cursor.execute("SELECT COUNT(*) FROM veiculos")
    if cursor.fetchone()[0] == 0:
        veiculos_seed = [
            (101, "ABC-1A23", "Volvo FH 540", 1),
            (102, "XYZ-9876", "Scania R450", 2),
            (103, "KGB-4567", "Mercedes Actros", 3),
        ]
        cursor.executemany(
            "INSERT INTO veiculos VALUES (?, ?, ?, ?)", veiculos_seed
        )

    conn.commit()
    conn.close()


def init_mongo():
    try:
        client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
        db = client[DB_NAME]
        collection = db["telemetria"]

        collection.create_index([("location", "2dsphere")])

        if collection.count_documents({}) == 0:
            telemetria_seed = [
                {
                    "veiculo_id": 101,
                    "location": {
                        "type": "Point",
                        "coordinates": [-34.873, -7.115],
                    },
                    "temperatura": 4.2,
                    "velocidade": 65,
                    "timestamp": "2026-09-11T10:00:00Z",
                },
                {
                    "veiculo_id": 102,
                    "location": {
                        "type": "Point",
                        "coordinates": [-34.832, -7.121],
                    },
                    "temperatura": -18.5,
                    "velocidade": 85,
                    "timestamp": "2026-09-11T10:05:00Z",
                },
                {
                    "veiculo_id": 103,
                    "location": {
                        "type": "Point",
                        "coordinates": [-34.950, -7.150],
                    },
                    "temperatura": 22.0,
                    "velocidade": 0,
                    "timestamp": "2026-09-11T09:45:00Z",
                },
            ]
            collection.insert_many(telemetria_seed)
        return client, db
    except Exception:
        return None, None


init_sqlite()
mongo_client, mongo_db = init_mongo()


def get_sqlite_data():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome, cnh, status FROM motoristas")
    motoristas = [
        {"id": r[0], "nome": r[1], "cnh": r[2], "status": r[3]}
        for r in cursor.fetchall()
    ]

    cursor.execute("SELECT id, placa, modelo, motorista_id FROM veiculos")
    veiculos = [
        {"id": r[0], "placa": r[1], "modelo": r[2], "motorista_id": r[3]}
        for r in cursor.fetchall()
    ]
    conn.close()
    return motoristas, veiculos


def get_telemetria_data(query=None):
    if query is None:
        query = {}
    if mongo_db is not None:
        try:
            return list(mongo_db["telemetria"].find(query, {"_id": 0}))
        except Exception:
            pass
    return [
        {
            "veiculo_id": 101,
            "location": {"type": "Point", "coordinates": [-34.873, -7.115]},
            "temperatura": 4.2,
            "velocidade": 65,
            "timestamp": "2026-09-11T10:00:00Z",
        },
        {
            "veiculo_id": 102,
            "location": {"type": "Point", "coordinates": [-34.832, -7.121]},
            "temperatura": -18.5,
            "velocidade": 85,
            "timestamp": "2026-09-11T10:05:00Z",
        },
        {
            "veiculo_id": 103,
            "location": {"type": "Point", "coordinates": [-34.950, -7.150]},
            "temperatura": 22.0,
            "velocidade": 0,
            "timestamp": "2026-09-11T09:45:00Z",
        },
    ]


st.title("Plataforma GeoLog — Monitoramento Poliglota de Frotas")

st.sidebar.header("Parâmetros Geoespaciais")
ref_lat = st.sidebar.number_input(
    "Latitude de Referência", value=-7.1150, format="%.4f"
)
ref_lon = st.sidebar.number_input(
    "Longitude de Referência", value=-34.8631, format="%.4f"
)
radius_km = st.sidebar.slider(
    "Raio de Busca (km)", min_value=1, max_value=100, value=25
)

radius_meters = radius_km * 1000
geo_query = {
    "location": {
        "$near": {
            "$geometry": {"type": "Point", "coordinates": [ref_lon, ref_lat]},
            "$maxDistance": radius_meters,
        }
    }
}

telemetria_raw = get_telemetria_data(geo_query)
if not telemetria_raw and mongo_db is not None:
    telemetria_raw = get_telemetria_data({})

motoristas, veiculos = get_sqlite_data()

motoristas_map = {m["id"]: m for m in motoristas}
veiculos_map = {v["id"]: v for v in veiculos}

merged_data = []
for tel in telemetria_raw:
    v_id = tel["veiculo_id"]
    veh = veiculos_map.get(v_id, {})
    m_id = veh.get("motorista_id")
    mot = motoristas_map.get(m_id, {})

    coords = tel.get("location", {}).get("coordinates", [0, 0])
    merged_data.append({
        "veiculo_id": v_id,
        "Motorista": mot.get("nome", "Desconhecido"),
        "Status Motorista": mot.get("status", "N/A"),
        "Placa": veh.get("placa", "N/A"),
        "Modelo": veh.get("modelo", "N/A"),
        "Temp (°C)": tel.get("temperatura", 0.0),
        "Velocidade (km/h)": tel.get("velocidade", 0),
        "Coordenadas": f"Lat: {coords[1]:.3f}, Lon: {coords[0]:.3f}",
        "lon": coords[0],
        "lat": coords[1],
        "timestamp": tel.get("timestamp", ""),
    })

if HAS_PANDAS:
    df_merged = pd.DataFrame(merged_data)
else:
    df_merged = merged_data

st.subheader("Indicadores de Desempenho (KPIs)")
col1, col2, col3 = st.columns(3)

total_ativas = len([m for m in motoristas if m["status"] == "Ativo"])
temperaturas = [item["Temp (°C)"] for item in merged_data]
media_temp = sum(temperaturas) / len(temperaturas) if temperaturas else 0.0
alertas_vel = len(
    [item for item in merged_data if item["Velocidade (km/h)"] > 80]
)

with col1:
    st.metric(label="Frotas / Motoristas Ativos", value=total_ativas)
with col2:
    st.metric(label="Média de Temperatura", value=f"{media_temp:.1f} °C")
with col3:
    st.metric(
        label="Alertas de Velocidade (> 80 km/h)",
        value=alertas_vel,
        delta=f"{alertas_vel} alertas" if alertas_vel > 0 else "Normal",
    )

st.markdown("---")

st.subheader("Painel Unificado de Frota")
if HAS_PANDAS and isinstance(df_merged, pd.DataFrame):
    display_df = df_merged[[
        "Motorista",
        "Placa",
        "Modelo",
        "Temp (°C)",
        "Velocidade (km/h)",
        "Coordenadas",
        "Status Motorista",
    ]]
else:
    display_df = [
        {
            "Motorista": x["Motorista"],
            "Placa": x["Placa"],
            "Modelo": x["Modelo"],
            "Temp (°C)": x["Temp (°C)"],
            "Velocidade (km/h)": x["Velocidade (km/h)"],
            "Coordenadas": x["Coordenadas"],
            "Status Motorista": x["Status Motorista"],
        }
        for x in merged_data
    ]

st.dataframe(display_df, width="stretch")

st.markdown("---")
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("Temperatura por Veículo (Placa)")
    if merged_data:
        chart_data_temp = (
            pd.DataFrame(merged_data) if HAS_PANDAS else merged_data
        )
        if HAS_PANDAS:
            fig_temp = px.bar(
                chart_data_temp,
                x="Placa",
                y="Temp (°C)",
                color="Modelo",
                text="Temp (°C)",
                title="Temperatura Atual dos Veículos",
            )
        else:
            fig_temp = px.bar(
                x=[x["Placa"] for x in merged_data],
                y=[x["Temp (°C)"] for x in merged_data],
                labels={"x": "Placa", "y": "Temp (°C)"},
                title="Temperatura Atual dos Veículos",
            )
        st.plotly_chart(fig_temp, width="stretch")
    else:
        st.info("Nenhum dado de temperatura disponível.")

with col_chart2:
    st.subheader("Status dos Motoristas")
    status_counts = {}
    for m in motoristas:
        s = m["status"]
        status_counts[s] = status_counts.get(s, 0) + 1

    status_df = [
        {"Status": k, "Quantidade": v} for k, v in status_counts.items()
    ]
    if HAS_PANDAS:
        fig_status = px.pie(
            pd.DataFrame(status_df),
            names="Status",
            values="Quantidade",
            title="Distribuição de Status dos Motoristas",
            hole=0.4,
        )
    else:
        fig_status = px.pie(
            names=[x["Status"] for x in status_df],
            values=[x["Quantidade"] for x in status_df],
            title="Distribuição de Status dos Motoristas",
            hole=0.4,
        )
    st.plotly_chart(fig_status, width="stretch")

st.markdown("---")
st.subheader("Mapa Geoespacial e Raio de Cobertura")

m = folium.Map(location=[ref_lat, ref_lon], zoom_start=11)

folium.Circle(
    location=[ref_lat, ref_lon],
    radius=radius_meters,
    color="#3186cc",
    fill=True,
    fill_opacity=0.15,
    popup=f"Raio de Busca: {radius_km} km",
).add_to(m)

folium.Marker(
    location=[ref_lat, ref_lon],
    popup="Ponto de Referência",
    icon=folium.Icon(color="red", icon="crosshairs", prefix="fa"),
).add_to(m)

for item in merged_data:
    lat = item["lat"]
    lon = item["lon"]
    popup_text = (
        f"<b>Veículo:</b> {item['Placa']} ({item['Modelo']})<br><b>Motorista:</b>"
        f" {item['Motorista']}<br><b>Temp:</b>"
        f" {item['Temp (°C)']}°C<br><b>Velocidade:</b>"
        f" {item['Velocidade (km/h)']} km/h"
    )

    folium.Marker(
        location=[lat, lon],
        popup=folium.Popup(popup_text, max_width=300),
        icon=folium.Icon(
            color="green" if item["Velocidade (km/h)"] <= 80 else "orange",
            icon="truck",
            prefix="fa",
        ),
    ).add_to(m)

st_folium(m, width=1200, height=500)

st.markdown("---")
st.subheader("Simulador de Movimentação em Tempo Real")
if st.button("Simular Movimentação"):
    if mongo_db is not None:
        try:
            telemetria_coll = mongo_db["telemetria"]
            docs = list(telemetria_coll.find({}))
            for doc in docs:
                coords = doc["location"]["coordinates"]
                new_lon = coords[0] + random.uniform(-0.01, 0.01)
                new_lat = coords[1] + random.uniform(-0.01, 0.01)
                new_temp = round(
                    doc["temperatura"] + random.uniform(-1.5, 1.5), 1
                )
                new_vel = max(
                    0, int(doc["velocidade"] + random.uniform(-10, 10))
                )

                telemetria_coll.update_one(
                    {"_id": doc["_id"]},
                    {
                        "$set": {
                            "location": {
                                "type": "Point",
                                "coordinates": [new_lon, new_lat],
                            },
                            "temperatura": new_temp,
                            "velocidade": new_vel,
                            "timestamp": datetime.now(
                                timezone.utc
                            ).isoformat(),
                        }
                    },
                )
            st.success("Movimentação simulada com sucesso no MongoDB!")
        except Exception as e:
            st.error(f"Erro ao simular no MongoDB: {e}")
    else:
        st.warning(
            "MongoDB não está conectado. Simulação em memória aplicada."
        )

    st.rerun()