# ⚽ Exercício 2: Consulta e Análise de Dados do Cartola FC no MongoDB

Este projeto contém scripts em Python desenvolvidos para realizar consultas, análises e relatórios agregados sobre os dados do Cartola FC armazenados no MongoDB (coletados da API do Cartola FC).

---

## 📁 Estrutura do Projeto

exercicio2_cartola/
├── consultar_cartola.py    # Script principal para consulta e análise de dados no MongoDB
├── requirements.txt        # Dependências Python do projeto
├── image.png               # Imagem de demonstração / evidência de execução
└── image2.png              # Imagem de demonstração / evidência de execução

---

## 🛠️ Tecnologias Utilizadas

* Language: Python 3.9+
* Database: MongoDB
* Driver / Libraries:
  * pymongo (Integração e consultas com o MongoDB)
  * python-dotenv (Gerenciamento de variáveis de ambiente)
  * requests (Requisições HTTP)

---

## ⚙️ Pré-requisitos e Configuração

### 1. Clonar ou Acessar a Pasta
Certifique-se de estar dentro do diretório do projeto:

cd exercicio2_cartola

### 2. Criar e Ativar o Ambiente Virtual

# Linux / macOS
python3 -m venv .venv
source .venv/bin/activate

# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1

### 3. Instalar as Dependências
Instale os pacotes listados no arquivo requirements.txt:

pip install -r requirements.txt

### 4. Configurar as Variáveis de Ambiente
Crie um arquivo chamado .env na raiz do projeto com as credenciais do seu banco de dados:

MONGO_URI=mongodb://localhost:27017
MONGO_DB_NAME=cartola_fc_db

---

## 🚀 Como Executar

Certifique-se de que o serviço do MongoDB está ativo e com os dados populados. Em seguida, execute o script de consulta:

python3 consultar_cartola.py

---

## 📊 Funcionalidades do Script (consultar_cartola.py)

Ao ser executado, o script realiza as seguintes consultas no banco de dados cartola_fc_db:

* Status do Mercado: Exibe a rodada atual e se o mercado está aberto ou fechado.
* Top Atletas Mais Caros: Consulta e ordena os jogadores com maior valor em cartoletas (preco_num).
* Top Atletas por Média: Lista os atletas com melhores médias de pontuação por partida.
* Relatório Agregado ($lookup): Executa uma pipeline de agregação para cruzar os dados dos atletas (atletas_rodada_atual) com as informações de seus respectivos clubes (clubes_rodada_atual) em tempo de execução.