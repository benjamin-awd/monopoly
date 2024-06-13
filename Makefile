setup:
	# install brew dependencies
	brew bundle --verbose

	# install poetry dependencies
	poetry shell
	poetry install
