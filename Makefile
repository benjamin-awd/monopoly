setup:
	# install brew dependencies
	brew bundle --verbose

	# install uv dependencies
	uv venv
	uv sync --all-extras
	@echo "Run 'source .venv/bin/activate' to activate the venv"
