.DEFAULT_GOAL := run
.PHONY: run demo hosted provision stop logs

DOCKER ?= docker
BASE = $(DOCKER) compose -f compose.yaml
ONPREM = $(BASE) -f compose.onprem.yaml

run: provision
	$(ONPREM) up --build --wait --wait-timeout 300 app
	@printf '\nHausPost: http://127.0.0.1:4377\nStop: make stop\n'

provision:
	@mkdir -p models
	$(ONPREM) run --build --rm --no-deps model-download

demo:
	LLM_BASE_URL= LLM_API_KEY= $(BASE) up --build --wait --wait-timeout 60 app
	@printf '\nHausPost demo: http://127.0.0.1:4377\n'

hosted:
	$(BASE) up --build --wait --wait-timeout 60 app
	@printf '\nHausPost hosted profile: http://127.0.0.1:4377\n'

stop:
	$(ONPREM) down --remove-orphans

logs:
	$(ONPREM) logs --tail 80 app model
