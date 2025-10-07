# Cartollero

## ⚙️ Setup

Acesse o link a seguir para criar um power-up na sua área de trabalho:
👉 https://developer.atlassian.com/cloud/trello/power-ups/admin/
Isto é necessário para permitir a autenticação com a API do Trello.

Clique em “Create a new Power-Up”.
Dê um nome e coloque qualquer URL (pode ser https://localhost se for só para uso pessoal), também pode deixar a URL em branco por enquanto.

Após criar, vá até a aba API Key no menu do Power-Up.
Copie a chave da API (API Key) que aparece lá.

Para gerar o token para sua conta (autorizando seu Power-Up).
Use este link no navegador, substituindo YOUR_API_KEY pela chave da api que voce acabou de copiar:

https://trello.com/1/authorize?expiration=never&name=Cartollero&scope=read,write&response_type=token&key=YOUR_API_KEY

→ Clique em “Allow” para autorizar.
→ A próxima tela mostrará seu token. Copie e salve este token.

Teste no navegador(substitua as variaveis SUA_NOVA_KEY e SEU_NOVO_TOKEN pela chave da sua API e o token que voce acabou de gerar e autorizar:

https://api.trello.com/1/members/me?key=SUA_NOVA_KEY&token=SEU_NOVO_TOKEN

Um JSON retornará seus dados de usuário caso esteja tudo certo.