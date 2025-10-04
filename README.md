rss-to-discord: bot do Discord para ler um feed RSS e converter em mensagens em um canal 

### Funcionamento
Sempre que executado, o script `check_rss.py` lê o feed RSS especificado nas configurações e verifica se há algum post novo. Caso positivo, ele irá executar um comando para enviar para o Discord.

### Configurações
No arquivo `config.py`:
    * RSS_URL: URL do feed onde o bot irá verificar 

TODO: 
    * Integração com o Discord 
