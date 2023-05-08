# Rasa for Botfront

A fork to be used with **Botfront**, an open source chatbot platform built with Rasa.

For more information visit the [Botfront project on Github](https://github.com/botfront/botfront)

# Developer setup instruction

All steps below are required

## environment:

You will need:

- python3.6
- pip
- git
- pyenv (Or any other virtual environment creator)

You should create a virtual environment to isolate this project with others. An example using pyenv here

```
pyenv install 3.6.13
pyenv local 3.6.13
```

You can make sure that the environment is picked up by executing

```
poetry env info
```

## install poetry:

We are using poetry 1.3.1 in this project.

```
curl -sSL https://install.python-poetry.org | python3 -
```

## install project

To install dependencies and rasa itself in editable mode execute

```
make install
```

## build docker image locally

```
make build-botfront
```

After running this the rasa image is created with name: rasa:bf-localdev
You need to go to your botfront project - The project you create with botfront init. And edit .botfront/botfront.yml file. Replace the rasa image with the new image name (default rasa:bf-localdev). An example for images below:

```
images:
  default:
    botfront: 'botfront/botfront:v1.0.5'
    rasa: 'rasa:bf-localdev'
    duckling: 'botfront/duckling:latest'
    mongo: 'mongo:latest'
    actions: 'rasa/rasa-sdk:2.1.2'
  current:
    botfront: 'botfront/botfront:v1.0.5'
    rasa: 'rasa:bf-localdev'
    duckling: 'botfront/duckling:latest'
    mongo: 'mongo:latest'
    actions: 'rasa/rasa-sdk:2.1.2'
```
