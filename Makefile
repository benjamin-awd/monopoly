UNAME := $(shell uname -s)

setup:
	# install system dependencies (poppler headers/libs + a C toolchain for pdftotext)
ifeq ($(UNAME),Linux)
	sudo apt-get install -y build-essential pkg-config libpoppler-cpp-dev
else
	brew bundle --verbose
endif

	# install uv dependencies
	uv venv
	uv sync --all-extras
	@echo "Run 'source .venv/bin/activate' to activate the venv"
