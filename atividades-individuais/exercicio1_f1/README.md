# 🏎️ OpenF1 Data Collector (MongoDB)

Este projeto consiste num script em Python desenvolvido para extrair dados da API pública do OpenF1 (informações de sessões, pilotos e voltas) e armazená-los de forma idempotente num banco de dados MongoDB.

---

## 📁 Estrutura do Projeto

.
├── f1_data_coletor.py      # Script principal de ingestão de dados
├── requirements.txt        # Dependências do projeto (requests, pymongo, python-dotenv)
├── .env                    # Ficheiro com variáveis de ambiente (URL do MongoDB)
└── README.md               # Documentação do projeto

---

## 🛠️ Tecnologias Utilizadas

* Linguagem: Python 3.9+
* Banco de Dados: MongoDB
* Bibliotecas:
  * requests (Chamadas HTTP para a API OpenF1)
  * pymongo (Integração e operações em lote com o MongoDB)
  * python-dotenv (Gestão de variáveis de ambiente)

---

## ⚙️ Configuração do Ambiente

### 1. Criar e Ativar o Ambiente Virtual

No terminal, execute os comandos referentes ao seu sistema operativo:

# Linux / macOS
python3 -m venv venv
source venv/bin/activate

# Windows (PowerShell)
python -m venv venv
.\venv\Scripts\activate

### 2. Instalar as Dependências

Instale as bibliotecas necessárias declaradas no ficheiro requirements.txt:

pip install -r requirements.txt

### 3. Configurar as Variáveis de Ambiente (.env)

Crie um ficheiro chamado .env na raiz do projeto e adicione a string de conexão do seu servidor MongoDB:

MONGO_URI=mongodb://localhost:27017/

---

## 🚀 Como Executar

Certifique-se de que o serviço do MongoDB está a correr e execute o script principal:

python f1_data_coletor.py

---

## 📊 Estrutura dos Dados no MongoDB

O script grava os dados na base de dados openf1_data divididos em três coleções principais:

| Coleção | Fonte (Endpoint API) | Chaves Únicas de Unicidade (upsert) |
| :--- | :--- | :--- |
| sessions | /sessions | session_key |
| drivers | /drivers | session_key + driver_number |
| laps | /laps | session_key + driver_number + lap_number |

> Nota: A gravação utiliza operações em lote (bulk_write) com upsert=True para garantir idempotência, evitando duplicados em caso de múltiplas execuções do script.