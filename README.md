rss-to-discord: bot do Discord para ler um feed RSS e converter em mensagens em um canal 

### Dependências:
    * feedreader
    * requests
    * discord.py 

### Funcionamento
Sempre que executado, o script `check_rss.py` lê o feed RSS especificado nas configurações e verifica se há algum post novo. Esse script pode ser executado, por exemplo, por uma `crontab` ou um `timer` do systemd.

Para servir de _cache_, os posts ficam em um banco de dados SQLite. Na verdade, isso nem seria necessário (bastaria verificar o feed a cada hora, por exemplo, e ver se saiu algum post mais recente), mas pode ser interessante em caso de falha do Discord.

O script `discord_bot.py`, então, conecta ao servidor Discord e, a cada 60 minutos (configurável no parâmetro `UPDATE_DELAY`), verifica se há novas entradas. Se sim, ele publica elas no canal especificado por `FORUM_ID`,

### Configurações
No arquivo `config.py`:
    * RSS_URL: URL do feed onde o bot irá verificar 
No arquivo `discord_tokens.py` (intencionalmente não fornecido, porque você precisa estar registrado como desenvolvedor no Discord):
    * CLIENT_PUBLIC_KEY: o token para o bot, que é obtido na tela de Developers do Discord > Bot > Token. 
    
