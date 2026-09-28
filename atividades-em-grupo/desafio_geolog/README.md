# 🚚 Desafio Integrador GeoLog — Plataforma de Telemetria e Persistência Poliglota

Este projeto consiste numa aplicação web desenvolvida em Streamlit para o monitoramento em tempo real de frotas logísticas, aplicando o padrão de Persistência Poliglota (SQLite para dados relacionais e MongoDB para dados geoespaciais e telemetria NoSQL).

---

## 📁 Estrutura do Projeto

desafio_geolog/
├── app.py               # Aplicação principal Streamlit com persistência poliglota
├── logitech.db          # Base de dados relacional SQLite (criada automaticamente)
├── requirements.txt     # Dependências do projeto
└── README.md            # Documentação da atividade

---

## 🛠️ Tecnologias Utilizadas

* Linguagem: Python 3.9+
* Bases de Dados:
  * SQLite (Dados cadastrais de motoristas e veículos)
  * MongoDB (Telemetria IoT e índice geoespacial 2dsphere)
* Bibliotecas Principais:
  * Streamlit (Interface web e dashboards)
  * Folium & Streamlit-Folium (Renderização de mapas geoespaciais interativos)
  * Plotly Express (Gráficos analíticos dinâmicos)
  * PyMongo (Integração NoSQL com queries $near)
  * SQLite3 (Driver relacional)

---

## ⚙️ Configuração do Ambiente

### 1. Criar e Ativar o Ambiente Virtual

# Linux / macOS
python3 -m venv venv
source venv/bin/activate

# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\activate

### 2. Instalar as Dependências

pip install -r requirements.txt

---

## 🚀 Como Executar

1. Certifique-se de que o serviço do MongoDB está a executar localmente na porta 27017 (ou configure a variável MONGO_URI no ambiente).
2. Execute a aplicação Streamlit:

streamlit run app.py

---

## 📊 Módulos da Aplicação

1. Persistência Poliglota: Integração transparente entre SQLite (logitech.db) e MongoDB (geolog_db.telemetria).
2. Busca Geoespacial: Filtro de veículos num raio de busca (km) via operador $near sobre índice 2dsphere.
3. Join em Memória: Unificação de dados transacionais (motorista e placa) com dados telemétricos (temperatura e velocidade).
4. Dashboard Analítico: KPIs de frota e gráficos Plotly de variação de temperatura e status.
5. Bónus (Simulador): Botão para simular movimentação GPS e alteração telemétrica em tempo real com atualização imediata no mapa.