import requests
import pandas as pd
from pathlib import Path
import sys

# ==============================
# CONFIGURAÇÕES (preencha)
# ==============================
API_KEY = "SUA_API_KEY"
TOKEN = "SEU_TOKEN"
BOARD_ID = "SEU_BOARD_ID"
LIST_ID = "SUA_LIST_ID"

EXCEL_PATH = r"C:\dev\PythonProjects\Cartollero\template_cartollero.xlsx"

# ==============================
# HELPERS DE LOG
# ==============================
def info(msg):
    print(f"ℹ️  {msg}")

def success(msg):
    print(f"✅ {msg}")

def warn(msg):
    print(f"⚠️  {msg}")

def error_and_exit(msg):
    print(f"❌ {msg}")
    sys.exit(1)

# ==============================
# BUSCAR LABELS
# ==============================
def obter_labels_existentes():
    info("Buscando labels do board...")
    url = f"https://api.trello.com/1/boards/{BOARD_ID}/labels"
    params = {"key": API_KEY, "token": TOKEN, "limit": 1000}
    r = requests.get(url, params=params)
    if r.status_code != 200:
        error_and_exit(f"Erro ao buscar labels: {r.status_code} - {r.text}")
    labels = r.json()
    mapping = {}
    for lab in labels:
        name = (lab.get("name") or "").strip().lower()
        if name:
            mapping[name] = lab.get("id")
    success(f"Labels carregadas: {len(mapping)} encontradas.")
    return mapping

# ==============================
# BUSCAR MEMBROS DO BOARD (por email)
# ==============================
def obter_membros_do_board():
    info("Buscando membros do board...")
    url = f"https://api.trello.com/1/boards/{BOARD_ID}/members"
    params = {"key": API_KEY, "token": TOKEN}
    r = requests.get(url, params=params)
    if r.status_code != 200:
        error_and_exit(f"Erro ao buscar membros do board: {r.status_code} - {r.text}")
    members = r.json()
    # Construir map email->id e username->id (por segurança)
    email_map = {}
    username_map = {}
    for m in members:
        mem_id = m.get("id")
        username = (m.get("username") or "").strip().lower()
        email = (m.get("email") or "").strip().lower()  # pode ser None dependendo do scope
        if email:
            email_map[email] = mem_id
        if username:
            username_map[username] = mem_id
    success(f"Membros carregados: emails conhecidos = {len(email_map)}, usernames = {len(username_map)}.")
    return email_map, username_map

# ==============================
# CRIAR CARTÃO
# ==============================
def criar_cartao(nome, descricao="", pos="bottom", due=None, label_ids=None, member_ids=None):
    info(f'Criando cartão: "{nome}"')
    url = "https://api.trello.com/1/cards"

    # validar pos
    if isinstance(pos, str):
        pos_str = pos.strip().lower()
        if pos_str not in ["top", "bottom"]:
            try:
                pos = float(pos)
            except Exception:
                pos = "bottom"
    elif not isinstance(pos, (int, float)):
        pos = "bottom"

    params = {
        "key": API_KEY,
        "token": TOKEN,
        "idList": LIST_ID,
        "name": nome,
        "desc": descricao or "",
        "pos": pos,
    }
    if due:
        params["due"] = f"{due}T12:00:00.000Z"
    if label_ids:
        params["idLabels"] = ",".join(label_ids)
    if member_ids:
        params["idMembers"] = ",".join(member_ids)

    r = requests.post(url, params=params)
    if r.status_code != 200:
        error_and_exit(f"Falha ao criar cartão '{nome}': {r.status_code} - {r.text}")
    card = r.json()
    card_id = card.get("id")
    success(f"Cartão criado com sucesso: id={card_id}")
    return card_id

# ==============================
# ADICIONAR ANEXO (URL)
# ==============================
def anexar_url_no_cartao(card_id, url_to_attach, name=None):
    info(f"Anexando URL ao card {card_id}: {url_to_attach}")
    url = f"https://api.trello.com/1/cards/{card_id}/attachments"
    params = {"key": API_KEY, "token": TOKEN, "url": url_to_attach}
    if name:
        params["name"] = name
    r = requests.post(url, params=params)
    if r.status_code != 200:
        error_and_exit(f"Falha ao anexar URL ao cartão {card_id}: {r.status_code} - {r.text}")
    success("Anexo criado com sucesso.")

# ==============================
# FUNÇÃO PRINCIPAL DE IMPORT
# ==============================
def importar_planilha(caminho_planilha):
    caminho = Path(caminho_planilha)
    if not caminho.exists():
        error_and_exit(f"Planilha não encontrada em: {caminho}")

    df = pd.read_excel(caminho)

    # Aceita 'Título' ou 'Nome do Cartão' (prioriza 'Título')
    if "Título" in df.columns:
        title_col = "Título"
    elif "Nome do Cartão" in df.columns:
        title_col = "Nome do Cartão"
    else:
        error_and_exit("Coluna 'Título' ou 'Nome do Cartão' não encontrada na planilha.")

    # Colunas obrigatórias
    obrigatorias = {title_col, "Descrição", "Labels", "Membros"}
    if not obrigatorias.issubset(set(df.columns)):
        missing = obrigatorias.difference(set(df.columns))
        error_and_exit(f"Colunas obrigatórias faltando: {missing}")

    info("Preparando dados do board (labels e membros)...")
    labels_map = obter_labels_existentes()
    email_map, username_map = obter_membros_do_board()

    # Processar cada linha; parar no primeiro erro
    total = len(df)
    info(f"Iniciando importação de {total} linhas...")
    for idx, row in df.iterrows():
        linha_num = idx + 2  # +2 (1-based + header)
        titulo = row.get(title_col)
        descricao = row.get("Descrição", "") or ""
        labels_raw = row.get("Labels", "") or ""
        membros_raw = row.get("Membros", "") or ""
        url_anexo = row.get("URL Anexada", "") or ""
        pos = row.get("Posição", "bottom")
        due = None
        if pd.notna(row.get("Data de Entrega")):
            due = str(pd.to_datetime(row["Data de Entrega"]).date())

        # Validar título
        if pd.isna(titulo) or str(titulo).strip() == "":
            error_and_exit(f"Linha {linha_num}: Título vazio — importação interrompida.")

        titulo = str(titulo).strip()
        info(f"\n--- Linha {linha_num} — Título: {titulo}")

        # Processar labels
        label_ids = []
        if isinstance(labels_raw, str) and labels_raw.strip():
            label_names = [l.strip() for l in labels_raw.split(",") if l.strip()]
            info(f"Labels solicitadas: {label_names}")
            for ln in label_names:
                key = ln.lower()
                if key in labels_map:
                    label_ids.append(labels_map[key])
                else:
                    error_and_exit(f"Linha {linha_num}: Label '{ln}' não encontrada no board — interrompendo.")
            success(f"Labels resolvidas: {len(label_ids)}")

        else:
            error_and_exit(f"Linha {linha_num}: coluna 'Labels' vazia — obrigatório.")

        # Processar membros por email (vírgula-separados)
        member_ids = []
        if isinstance(membros_raw, str) and membros_raw.strip():
            member_entries = [m.strip().lower() for m in membros_raw.split(",") if m.strip()]
            info(f"Membros solicitados (raw): {member_entries}")
            for me in member_entries:
                # tentar por email primeiro
                if me in email_map:
                    member_ids.append(email_map[me])
                elif me in username_map:
                    member_ids.append(username_map[me])
                else:
                    error_and_exit(f"Linha {linha_num}: Membro '{me}' não encontrado por email/username — interrompendo.")
            success(f"Membros resolvidos: {len(member_ids)}")
        else:
            error_and_exit(f"Linha {linha_num}: coluna 'Membros' vazia — obrigatório.")

        # Criar cartão
        card_id = criar_cartao(
            nome=titulo,
            descricao=descricao,
            pos=pos,
            due=due,
            label_ids=label_ids,
            member_ids=member_ids
        )

        # Anexar URL se fornecida
        if isinstance(url_anexo, str) and url_anexo.strip():
            anexar_url_no_cartao(card_id, url_anexo.strip(), name=titulo)

        success(f"Linha {linha_num}: Importada com sucesso.\n")

    success("Importação finalizada com sucesso (todas as linhas processadas).")

# ==============================
# ENTRYPOINT
# ==============================
if __name__ == "__main__":
    importar_planilha(EXCEL_PATH)
