import requests

# === CONFIGURAÇÕES ===
API_KEY = "API_KEY"
TOKEN = "TOKEN"

# === FUNÇÕES ===

def listar_boards():
    """Lista todos os quadros do usuário autenticado."""
    url = f"https://api.trello.com/1/members/me/boards?key={API_KEY}&token={TOKEN}"
    response = requests.get(url)
    if response.status_code == 200:
        boards = response.json()
        print("\n=== QUADROS DISPONÍVEIS ===")
        for b in boards:
            print(f"- {b['name']} (ID: {b['id']})")
        return boards
    else:
        print("❌ Erro ao listar boards:", response.text)
        return []


def listar_listas(board_id):
    """Lista todas as listas de um quadro."""
    url = f"https://api.trello.com/1/boards/{board_id}/lists?key={API_KEY}&token={TOKEN}"
    response = requests.get(url)
    if response.status_code == 200:
        listas = response.json()
        print(f"\n=== LISTAS DO BOARD {board_id} ===")
        for l in listas:
            print(f"- {l['name']} (ID: {l['id']})")
        return listas
    else:
        print("❌ Erro ao listar listas:", response.text)
        return []


# === EXECUÇÃO PRINCIPAL ===
if __name__ == "__main__":
    boards = listar_boards()

    if boards:
        board_id = input("\nDigite o ID do quadro que deseja inspecionar: ").strip()
        listar_listas(board_id)
