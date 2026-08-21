rss-to-discord: bot do Discord para ler um feed RSS e converter em mensagens em um canal

### Dependências:
    * FastAPI (+ uvicorn) — backend
    * SQLAlchemy 2.0 — backend
    * feedparser — backend
    * aiohttp — bot
    * discord.py — bot
    * python-dotenv — backend e bot

Requer Python 3.14+.

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
* `backend`, uma API em FastAPI que faz a leitura do feed RSS e oferece os `endpoints`:
  * `/`: um JSON com o status geral do `backend` - TODO: ainda não implementado (só retorna `{"status": 200}`)
  * `/fetch_headlines`: busca novas manchetes no RSS e as grava no banco de dados. Retorna quantas entradas novas foram encontradas.
  * `/get_unposted_headlines`: aceita o parâmetro `days`, retornando as manchetes ainda não postadas dos últimos `days` dias. O padrão é 3.
    * Por exemplo, `/get_unposted_headlines?days=8` retornará as manchetes pendentes dos últimos 8 dias.
  * `/mark_headline_as_read`: aceita um JSON `{"id": <id>}` e marca a manchete correspondente como lida (não será postada de novo).

* `bot`, que consulta o backend periodicamente (via `aiohttp`) e faz a postagem no Discord, criando uma thread por manchete pendente no fórum configurado.

A cada `UPDATE_DELAY` minutos, o bot chama `/fetch_headlines`, busca o que ainda está pendente em `/get_unposted_headlines` e, para cada manchete, cria uma thread e chama `/mark_headline_as_read`. Falhas isoladas (ex.: marcar uma manchete como lida) não interrompem o ciclo — a manchete em questão pode ser postada de novo no ciclo seguinte, mas as demais seguem sendo processadas normalmente.

### Configurações
No arquivo `.env` do diretório do `backend`:
* `RSS_URL`: URL do feed onde o bot irá verificar
* `DATABASE_PATH`: onde ficará o banco de dados no qual os dados do `feed` são armazenados

No arquivo `.env` do diretório do `bot`:
* `BACKEND_TARGET`: a URL e porta (padrão: 8820) onde o `backend` estará rodando. Preferencialmente, deverá rodar apenas escutando `localhost`, o IP da máquina, ou o nome do container na rede do Podman.
* `FORUM_ID`: o ID do canal (no app do Discord, clique com o botão direito no canal e escolha _copiar ID do canal_, então cole aqui).
* `CLIENT_PUBLIC_KEY`: o token para o bot, que é obtido na tela de Developers do Discord > Bot > Token.
* `UPDATE_DELAY`: de quanto em quanto tempo verificar (em minutos)?
Exceto pelo último, esses dados devem ser adaptados para sua situação.

Se alguma variável obrigatória estiver faltando, o `backend` falha já na inicialização (em vez de subir num estado quebrado); o `bot` loga o erro a cada ciclo e tenta de novo, em vez de derrubar o processo.

### Uso com Podman
Para comunicação entre containers, deve ser criada uma rede com o comando `podman network create [NOME DA REDE]`.

Então, modifique os arquivos `.container` para indicar o nome da rede criada e outras configurações (como volumes, caminhos para arquivo `.env` etc...).

Facultativamente, pode ser criada essa rede de forma automática, criando-se um arquivo `.network` e colocando-se em `~/.config/containers/systemd/`, com o conteúdo:

    [Network]
    Label=[NOME DA REDE DESEJADO]

Os `Dockerfile`s de `backend/` e `bot/` fixam as versões dos pacotes Python instalados (sincronizadas manualmente com o `pyproject.toml`/`uv.lock` da raiz), para evitar puxar versões novas — e potencialmente quebradas — a cada build.

### Deploy em produção
Há um `Makefile` na raiz do projeto que automatiza build e deploy das imagens do `backend` e do `bot` numa VPS rodando Podman + Quadlet (systemd `--user`), sem depender de um registry:

```bash
make build              # builda as duas imagens localmente, sem tocar na VPS
make deploy              # builda, envia (podman save | ssh | podman load) e reinicia os dois serviços na VPS
make deploy-backend      # idem, só para o backend
make deploy-frontend     # idem, só para o bot
make rollback-backend    # volta o backend pra imagem anterior ao último deploy
make rollback-frontend   # volta o bot pra imagem anterior ao último deploy
make status               # mostra o status dos serviços systemd --user na VPS
make logs-backend         # segue (podman logs -f) o log do backend na VPS
make logs-frontend        # segue (podman logs -f) o log do bot na VPS
```

Antes de carregar uma imagem nova, a atual é retaggeada como `:previous` na VPS, então o rollback sempre volta um passo (não guarda histórico além disso). Depois de um `deploy-backend`, é checado um HTTP 200 em `/`; depois de um `deploy-frontend`, se o serviço segue ativo no systemd.

O host, porta e usuário da VPS têm valores padrão no `Makefile` e podem ser sobrescritos na linha de comando, ex.: `make deploy VPS_HOST=outro.host VPS_PORT=22`.

### A fazer
* Implementar de fato o endpoint `/`.
* Melhorar a segurança, possivelmente adicionando alguma forma de autenticação entre bot e backend.
* Verificar se há casos de tratamento de erro não cobertos atualmente.

### Licença
Unlicense (equivalente a domínio público), pela trivialidade de fazer esse bot.
