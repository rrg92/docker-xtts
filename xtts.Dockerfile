FROM bash

# isso instala o python e o git, que vamos precisar!
RUN apk add python3 py3-pip
RUN apk add git
RUN apk add ffmpeg

# Aqui vamos criar um diretorio dentro do container
WORKDIR /xtts-webui

# Vamos instalar as dependencias
COPY ./webui/requirements.txt ./reqs.txt 
RUN python -m pip install -r ./reqs.txt --break-system-packages

# E por fim, copiar os arquivos restantes
# Eu separei o requirments.txt em um processo acima, devido a testes
# Se tiver junto, toda vez que mexer só no WebApp.py, sem mudar os requirements, ele vai instalar tudo novamente!
# Eu nao quero isso, se eu precisar de uma biblioteca nova, atualizo o requirements  ai sim, ele refaz o install!
COPY /webui ./

CMD ["python","WebApp.py"]
