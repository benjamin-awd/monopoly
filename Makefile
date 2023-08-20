image := monopoly
repository := monopoly
project := phonic-ceremony-394407
docker_url := us-central1-docker.pkg.dev

build:
	docker build --tag ${image} .

push:
	docker tag ${image} \
	${docker_url}/${project}/${repository}/${image}:main

	docker push ${docker_url}/${project}/${repository}/${image}:main
	@echo "Successfully uploaded image"
