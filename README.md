rss-to-discord: bot do Discord para ler um feed RSS e converter em mensagens em um canal 

### Dependências:
    * feedreader
    * requests
    * discord.py 

### Funcionamento
O script `bot.py`, conecta ao servidor Discord e, a cada 60 minutos (configurável no parâmetro `UPDATE_DELAY`), verifica se há novas entradas chamando o `rss.py`. Se sim, ele publica elas no canal especificado por `FORUM_ID`, e marca a última entrada como lida para evitar repetições.

### Configurações
No arquivo `config.py`:
    * RSS_URL: URL do feed onde o bot irá verificar 
No arquivo `discord_tokens.py` (intencionalmente não fornecido, porque você precisa estar registrado como desenvolvedor no Discord):
    * CLIENT_PUBLIC_KEY: o token para o bot, que é obtido na tela de Developers do Discord > Bot > Token. 

### TODO 
Simplificar o código, possivelmente refatorando e fazendo o `rss.py` fornecer um endpoint, tirando muita da complexidade do bot.
