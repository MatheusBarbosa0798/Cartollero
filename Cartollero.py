import requests
import pandas as pd
from pathlib import Path

# ==============================
# Configurações Trello
# ==============================
API_KEY = "API_KEY"
TOKEN = "TOKEN"
LIST_ID = "LIST_ID"

# ==============================
# Função para criar cartão no Trello
# ==============================
def criar_cartao(nome, descricao="", pos="top", due=None):
    url = "https://api.trello.com/1/cards"
    query = {
        "key": API_KEY,
        "token": TOKEN,
        "idList": LIST_ID,
        "name": nome,
        "desc": descricao or "",
        "pos": pos or "top"
    }

    if due:
        # Trello espera data no formato ISO (AAAA-MM-DDTHH:MM:SSZ)
        query["due"] = f"{due}T12:00:00.000Z"

    response = requests.post(url, params=query)

    if response.status_code == 200:
        print(f"✅ Cartão '{nome}' criado com sucesso!")
    else:
        print(f"❌ Erro ao criar '{nome}': {response.status_code} - {response.text}")

# ==============================
# Função para importar dados da planilha
# ==============================
def importar_planilha(caminho_planilha):
    caminho = Path(caminho_planilha)
    if not caminho.exists():
        print(f"❌ Planilha não encontrada em: {caminho}")
        return

    df = pd.read_excel(caminho)

    # Validação básica
    colunas_esperadas = {"Nome do Cartão", "Descrição", "Data de Entrega", "Posição"}
    if not colunas_esperadas.issubset(df.columns):
        print("⚠️ A planilha não contém todas as colunas esperadas:")
        print(f"   Esperadas: {colunas_esperadas}")
        print(f"   Encontradas: {set(df.columns)}")
        return

    for _, row in df.iterrows():
        nome = row.get("Nome do Cartão")
        descricao = row.get("Descrição", "")
        due = None

        # Converter datas automaticamente se existirem
        if pd.notna(row.get("Data de Entrega")):
            due = str(pd.to_datetime(row["Data de Entrega"]).date())

        pos = row.get("Posição", "top")

        if pd.notna(nome) and str(nome).strip():
            criar_cartao(str(nome).strip(), str(descricao).strip(), pos, due)
        else:
            print("⚠️ Linha ignorada (sem nome do cartão)")

# ==============================
# Execução principal
# ==============================
if __name__ == "__main__":
    importar_planilha(r"C:\dev\PythonProjects\Cartollero\cards.xlsx")
