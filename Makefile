SHELL := /bin/bash

.PHONY: dev-backend test-backend install install-link install-copy install-skill

dev-backend:
	cd backend && bash scripts/run_dev.sh

test-backend:
	cd backend && uv run pytest

test-skill:
	cd backend && uv run pytest ../tests/skill_memory_transfer

install:
	bash ./install-backend

install-link:
	bash ./install-backend --link

install-copy:
	bash ./install-backend --copy

install-skill:
	bash ./install-skill.sh
