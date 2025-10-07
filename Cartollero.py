import requests
import pandas as pd
from pathlib import Path

# ==============================
# Configurações Trello
# ==============================
API_KEY = "API_KEY"
TOKEN = "TOKEN"
BOARD_ID = "BOARD_ID"
LIST_ID = "LIST_ID"

# ==============================
# Função: Obter labels existentes no quadro
# ==============================
def obter_labels_existentes():
    url = f"https://api.trello.com/1/boards/{BOARD_ID}/labels"
    params = {"key": API_KEY, "token": TOKEN, "limit": 1000}

    response = requests.get(url, params=params)
    if response.status_code == 200:
        labels = response.json()
        # Dicionário: nome minúsculo → id
        return {label["name"].strip().lower(): label["id"] for label in labels if label["name"]}
    else:
        print(f"⚠️ Erro ao buscar labels: {response.status_code} - {response.text}")
        return {}

# ==============================
# Função: Criar cartão no Trello
# ==============================
def criar_cartao(nome, descricao="", pos="bottom", due=None, label_ids=None):
    url = "https://api.trello.com/1/cards"

    # Validar posição
    if isinstance(pos, str):
        pos_str = pos.strip().lower()
        if pos_str not in ["top", "bottom"]:
            try:
                pos = float(pos)
            except ValueError:
                pos = "bottom"
    elif not isinstance(pos, (int, float)):
        pos = "bottom"

    query = {
        "key": API_KEY,
        "token": TOKEN,
        "idList": LIST_ID,
        "name": nome,
        "desc": descricao or "",
        "pos": pos,
    }

    if due:
        query["due"] = f"{due}T12:00:00.000Z"

    if label_ids:
        query["idLabels"] = ",".join(label_ids)

    response = requests.post(url, params=query)

    if response.status_code == 200:
        print(f"✅ Cartão '{nome}' criado com sucesso!")
    else:
        print(f"❌ Erro ao criar '{nome}': {response.status_code} - {response.text}")

# ==============================
# Função: Importar dados da planilha
# ==============================
def importar_planilha(caminho_planilha):
    caminho = Path(caminho_planilha)
    if not caminho.exists():
        print(f"❌ Planilha não encontrada em: {caminho}")
        return

    df = pd.read_excel(caminho)

    colunas_esperadas = {"Nome do Cartão", "Descrição", "Data de Entrega", "Posição", "Labels"}
    if not colunas_esperadas.issubset(df.columns):
        print("⚠️ A planilha não contém todas as colunas esperadas:")
        print(f"   Esperadas: {colunas_esperadas}")
        print(f"   Encontradas: {set(df.columns)}")
        return

    print("🔍 Buscando labels existentes no Trello...")
    labels_existentes = obter_labels_existentes()

    for _, row in df.iterrows():
        nome = row.get("Nome do Cartão")
        descricao = row.get("Descrição", "")
        due = None

        if pd.notna(row.get("Data de Entrega")):
            due = str(pd.to_datetime(row["Data de Entrega"]).date())

        pos = row.get("Posição", "bottom")

        # Processar labels (nomes separados por vírgula)
        label_col = row.get("Labels", "")
        label_ids = []
        if isinstance(label_col, str) and label_col.strip():
            for label_nome in label_col.split(","):
                nome_label = label_nome.strip().lower()
                if nome_label in labels_existentes:
                    label_ids.append(labels_existentes[nome_label])
                else:
                    print(f"⚠️ Label '{label_nome}' não encontrada no board — ignorada.")

        if pd.notna(nome) and str(nome).strip():
            criar_cartao(str(nome).strip(), str(descricao).strip(), pos, due, label_ids)
        else:
            print("⚠️ Linha ignorada (sem nome do cartão)")

# ==============================
# Execução principal
# ==============================
if __name__ == "__main__":
    importar_planilha(r"C:\dev\PythonProjects\Cartollero\cards.xlsx")
