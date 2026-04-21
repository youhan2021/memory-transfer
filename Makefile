SHELL := /bin/bash

.PHONY: dev-backend test-backend install install-link install-copy install-skill

dev-backend:
	cd backend && bash scripts/run_dev.sh

test-backend:
	cd backend && uv run pytest

install:
	bash ./install.sh

install-link:
	bash ./install.sh --link

install-copy:
	bash ./install.sh --copy

install-skill:
	bash ./install-skill.sh
