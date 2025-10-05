rss-to-discord: bot do Discord para ler um feed RSS e converter em mensagens em um canal 

### Dependências:
    * feedreader
    * requests

### Funcionamento
Sempre que executado, o script `check_rss.py` lê o feed RSS especificado nas configurações e verifica se há algum post novo. Caso positivo, ele irá executar um comando para enviar para o Discord.

Para servir de _cache_, os posts ficam em um banco de dados SQLite.

### Configurações
No arquivo `config.py`:
    * RSS_URL: URL do feed onde o bot irá verificar 

TODO: 
    * Integração com o Discord 
