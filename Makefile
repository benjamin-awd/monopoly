setup:
	# install brew dependencies
	brew bundle

	# install pdftotext dependencies
	sudo apt-get update && sudo apt install build-essential libpoppler-cpp-dev pkg-config -y

	# install poetry dependencies
	poetry install
