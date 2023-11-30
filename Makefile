setup:
	# install brew dependencies
	brew bundle --verbose

	# install poetry dependencies
	poetry env use 3.11
	poetry shell
	poetry install
