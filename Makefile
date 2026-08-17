# Makefile — build e deploy dos containers do bot do Discord (chuville-rss)
# para a VPS de produção.
#
# Uso:
#   make build                # builda as duas imagens localmente (não mexe na VPS)
#   make deploy                # builda e faz deploy do backend e do bot na VPS
#   make deploy-backend        # builda e faz deploy só do backend
#   make deploy-frontend       # builda e faz deploy só do bot
#   make rollback-backend      # volta o backend pra imagem anterior ao deploy
#   make rollback-frontend     # volta o bot pra imagem anterior ao deploy
#   make status                # mostra o status dos serviços na VPS
#   make logs-backend          # segue (journalctl -f) o log do backend na VPS
#   make logs-frontend         # segue (journalctl -f) o log do bot na VPS
#
# O deploy não builda nada na VPS: a imagem é buildada aqui (podman build),
# enviada via `podman save | ssh | podman load` e os serviços systemd --user
# (Quadlet) são reiniciados para pegar a imagem nova. Antes de carregar a
# imagem nova, a atual é retaggeada como ":previous" na VPS, então
# `make rollback-*` sempre volta pra imagem que estava rodando antes do
# último deploy (não guarda histórico além de um passo).
#
# Variáveis podem ser sobrescritas na linha de comando, ex.:
#   make deploy VPS_HOST=outro.host VPS_PORT=22

VPS_HOST ?= renanbirck.rocks
VPS_PORT ?= 2222
VPS_USER ?= renan

# ControlMaster reaproveita a mesma conexão SSH entre os vários comandos que
# um único `make deploy` dispara (evita reautenticar a cada chamada).
SSH_OPTS ?= -o ControlMaster=auto -o ControlPersist=60s \
            -o ControlPath=$${TMPDIR:-/tmp}/chuville-deploy-%r@%h:%p
SSH := ssh -p $(VPS_PORT) $(SSH_OPTS) $(VPS_USER)@$(VPS_HOST)

BACKEND_IMAGE   := localhost/discord-chuville-backend
FRONTEND_IMAGE  := localhost/discord-chuville-frontend

BACKEND_SERVICE  := chuville-backend.service
FRONTEND_SERVICE := chuville-frontend.service

SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c
.ONESHELL:

.PHONY: help build build-backend build-frontend \
        push-backend push-frontend \
        deploy deploy-backend deploy-frontend \
        rollback-backend rollback-frontend \
        status logs-backend logs-frontend

help:
	@echo "Alvos disponíveis: build, deploy, deploy-backend, deploy-frontend,"
	@echo "rollback-backend, rollback-frontend, status, logs-backend, logs-frontend"

## --- build local -----------------------------------------------------

build: build-backend build-frontend

build-backend:
	@echo "==> Buildando $(BACKEND_IMAGE):latest"
	podman build -t $(BACKEND_IMAGE):latest -f backend/Dockerfile backend/

build-frontend:
	@echo "==> Buildando $(FRONTEND_IMAGE):latest"
	podman build -t $(FRONTEND_IMAGE):latest -f bot/Dockerfile bot/

## --- envio pra VPS -----------------------------------------------------
## Guarda a imagem atual como :previous antes de carregar a nova, pra dar
## pra reverter com "make rollback-*" se o deploy sair errado.

push-backend:
	@echo "==> Enviando $(BACKEND_IMAGE):latest para $(VPS_HOST)"
	$(SSH) 'podman image exists $(BACKEND_IMAGE):latest && \
		podman tag $(BACKEND_IMAGE):latest $(BACKEND_IMAGE):previous || true'
	podman save $(BACKEND_IMAGE):latest | gzip -1 | $(SSH) 'gunzip | podman load'

push-frontend:
	@echo "==> Enviando $(FRONTEND_IMAGE):latest para $(VPS_HOST)"
	$(SSH) 'podman image exists $(FRONTEND_IMAGE):latest && \
		podman tag $(FRONTEND_IMAGE):latest $(FRONTEND_IMAGE):previous || true'
	podman save $(FRONTEND_IMAGE):latest | gzip -1 | $(SSH) 'gunzip | podman load'

## --- deploy (build + envio + restart + checagem) -----------------------

deploy: deploy-backend deploy-frontend

deploy-backend: build-backend push-backend
	@echo "==> Reiniciando $(BACKEND_SERVICE) em $(VPS_HOST)"
	$(SSH) 'systemctl --user restart $(BACKEND_SERVICE)'
	sleep 3
	echo "==> Checando http://localhost:8820/ na VPS"
	if $(SSH) 'curl -sf -o /dev/null http://localhost:8820/'; then
		echo "==> Backend no ar."
	else
		echo "==> ATENÇÃO: backend não respondeu depois do restart."
		echo "    Veja 'make logs-backend' e, se precisar, 'make rollback-backend'."
		exit 1
	fi

deploy-frontend: build-frontend push-frontend
	@echo "==> Reiniciando $(FRONTEND_SERVICE) em $(VPS_HOST)"
	$(SSH) 'systemctl --user restart $(FRONTEND_SERVICE)'
	sleep 5
	echo "==> Checando se $(FRONTEND_SERVICE) segue ativo na VPS"
	if $(SSH) 'systemctl --user is-active --quiet $(FRONTEND_SERVICE)'; then
		echo "==> $(FRONTEND_SERVICE) ativo. Últimas linhas do log:"
		$(SSH) 'journalctl --user -u $(FRONTEND_SERVICE) -n 15 --no-pager'
	else
		echo "==> ATENÇÃO: $(FRONTEND_SERVICE) não ficou ativo depois do restart."
		echo "    Veja 'make logs-frontend' e, se precisar, 'make rollback-frontend'."
		exit 1
	fi

## --- rollback -----------------------------------------------------------
## Só volta um passo: a imagem marcada como :previous no último push-*.

rollback-backend:
	@echo "==> Revertendo $(BACKEND_IMAGE) para a versão anterior ao último deploy"
	$(SSH) 'podman tag $(BACKEND_IMAGE):previous $(BACKEND_IMAGE):latest && \
		systemctl --user restart $(BACKEND_SERVICE)'

rollback-frontend:
	@echo "==> Revertendo $(FRONTEND_IMAGE) para a versão anterior ao último deploy"
	$(SSH) 'podman tag $(FRONTEND_IMAGE):previous $(FRONTEND_IMAGE):latest && \
		systemctl --user restart $(FRONTEND_SERVICE)'

## --- observação -----------------------------------------------------------

status:
	$(SSH) 'systemctl --user status $(BACKEND_SERVICE) $(FRONTEND_SERVICE) --no-pager'

logs-backend:
	$(SSH) 'journalctl --user -u $(BACKEND_SERVICE) -f'

logs-frontend:
	$(SSH) 'journalctl --user -u $(FRONTEND_SERVICE) -f'
