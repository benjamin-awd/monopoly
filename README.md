# Install
Install using

```sh
brew bundle
```

Install the gcloud CLI
```sh
cd ~
curl -O https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-440.0.0-linux-x86_64.tar.gz
tar -xf google-cloud-cli-440.0.0-linux-x86_64.tar.gz
./google-cloud-sdk/install.sh
./google-cloud-sdk/bin/gcloud init
cd -
```

Then generate credentials with
```sh
gcloud auth application-default login
```

Enable the Gmail API and authorize access:
https://developers.google.com/gmail/api/quickstart/python

Get API credentials
```sh
python3 quickstart.py
```

# Developing
Set up the pre-commit hooks
```sh
pre-commit install
```
