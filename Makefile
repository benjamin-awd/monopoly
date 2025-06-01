setup:
	# install brew dependencies
	brew bundle --verbose

	# install uv dependencies
	uv venv
	uv sync --all-extras
	source .venv/bin/activate
