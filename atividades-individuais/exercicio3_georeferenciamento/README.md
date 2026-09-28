# 🗺️ Exercício 03: Solução Completa de Dados Georreferenciados no MongoDB

Esta solução em Python realiza todo o fluxo de ETL (Extração, Transformação e Carga) de dados abertos do Governo Federal do Brasil (Unidades Básicas de Saúde - UBS), convertendo a localização geográfica para o padrão GeoJSON e estruturando uma coleção no MongoDB com índice geoespacial 2dsphere.

---

## 📁 Estrutura do Projeto

exercicio3_geojson/
├── georef_solucao.py       # Script principal autónomo (Extração, Tratamento GeoJSON e Carga no MongoDB)
├── requirements.txt        # Dependências Python do projeto
├── .env                    # Configurações de ambiente (URL do MongoDB e fonte dos dados)
└── README.md               # Documentação da atividade

---

## 🛠️ Tecnologias Utilizadas

* Linguagem: Python 3.9+
* Banco de Dados: MongoDB
* Bibliotecas:
  * requests (Download dos dados abertos)
  * pandas & geopandas (Tratamento de dados geográficos e numéricos)
  * shapely (Construção de geometrias espaciais)
  * pymongo (Conexão e criação de índice 2dsphere no MongoDB)
  * python-dotenv (Gerenciamento de credenciais e variáveis de ambiente)

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
Instale os pacotes necessários:

pip install -r requirements.txt

### 3. Configurar as Variáveis de Ambiente (.env)
Crie o arquivo .env na raiz do projeto contendo:

MONGO_URI=mongodb://localhost:27017/
URL_DADOS=https://s3-sa-east-1.amazonaws.com/ckan.saude.gov.br/UBS/ubs.csv

---

## 🚀 Como Executar

Certifique-se de que o servidor MongoDB está em execução e execute o script autônomo:

python georef_solucao.py

---

## 📊 Estrutura e Armazenamento no MongoDB

* Banco de Dados: geodados
* Coleção: unidades_saude
* Índice Criado: 2dsphere na chave geometry

Formato do Documento em GeoJSON Persistido:

{
  "type": "Feature",
  "geometry": {
    "type": "Point",
    "coordinates": [-34.8732, -7.1153]
  },
  "properties": {
    "cod_uf": 25,
    "uf": "PB",
    "cod_municipio": 250750,
    "municipio": "JOAO PESSOA",
    "cod_cnes": 123456,
    "logradouro": "RUA EXEMPLO",
    "bairro": "CENTRO",
    "cep": "58000000",
    "telefone": "8332221111"
  }
}