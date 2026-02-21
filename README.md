rss-to-discord: bot do Discord para ler um feed RSS e converter em mensagens em um canal 

### Dependências:
    * feedreader
    * python-dotenv
    * requests
    * discord.py 

### Instalação
Para instalar as dependências, utilize o `uv`:

1. Instalar uv (se ainda não tiver)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Instalar as dependências do projeto
```bash
uv sync
```

### Funcionamento
O robô é dividido em dois módulos:
* `scraper`, que faz a leitura do feed RSS e oferece os `endpoints`:
  * `/`: um JSON com o status geral do `scraper` (qual foi a última manchete lida, se há alguma manchete ainda não lida)
  * `/fetch_headlines`: busca novas manchetes no RSS
  * `/post_headlines`: aceita um JSON com o parâmetro `days`, para retornar manchetes dos últimos `days` dias. O padrão é 3.
  * `/mark_headline_as_read`: marca a manchete com o `id` fornecido como lida.
  
* `bot`, que faz a postagem no Discord.

Periodicamente

### Configurações
No arquivo `.env` do diretório do `scraper`:
* `RSS_URL`: URL do feed onde o bot irá verificar 
* `DATABASE_PATH`: onde ficará o banco de dados no qual os dados do `feed` são armazenados

No arquivo `.env`do diretório do `bot`:
* `SCRAPER_URL`: a URL e porta (padrão: 8820) onde o `scraper` estará rodando. Preferencialmente, deverá rodar apenas escutando `localhost` ou o IP da máquina.
* `FORUM_ID`: o ID do canal (no app do Discord, clique com o botão direito no canal e escolha _copiar ID do canal_, então cole aqui).
* `CLIENT_PUBLIC_KEY`: o token para o bot, que é obtido na tela de Developers do Discord > Bot > Token. 
* `UPDATE_DELAY`: de quanto em quanto tempo verificar?
Exceto pelo último, esses dados devem ser adaptados para sua situação.

### A fazer
* Melhorar a segurança, possivelmente adicionando alguma forma de autenticação.
* Verificar se há casos de tratamento de erro não cobertos atualmente.

### Licença
Unlicense (equivalente a domínio público), pela trivialidade de fazer esse bot.
