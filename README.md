---
title: Xtts
emoji: 👀
colorFrom: green
colorTo: indigo
sdk: docker
pinned: false
license: apache-2.0
---

# Instruções

Você precisa configurar o seu ambiente com docker. Veja abaixo algumas orientações para isso.  

Para subir o modelo, faça clone este repo e execute um docker compose up:

```sh
git clone https://github.com/rrg92/docker-xtts
cd docker-xtts
docker compose up
```

## Pré-requisitos 

A sua máquina deve conter um docker!  
Eu já testei isso em um docker no Azure e wsl2.  
Para ubuntu, eu segui este link: https://docs.docker.com/engine/install/ubuntu/

Não tem segredos aqui. Basta configurar um docker e fazer com que o seu docker tenha acesso as placa de vídeo.  

Por exemplo, em uma máquina Ubuntu do Azure (Standard NC8as T4 v3) precisei instalar os drivers da nvidia: https://learn.microsoft.com/en-us/azure/virtual-machines/linux/n-series-driver-setup

Depois, precisei instalar isso para o docker funcionar certinho com esses drivers:
```sh
sudo apt install -y nvidia-docker2
sudo systemctl daemon-reload
sudo systemctl restart docker
```

No Windows, eu instalei com wsl2 e Docker Desktop, seguindo a instalação padrão.
Além disso, eu já tinha instalado os drivers da NVIDIA conforme este link: https://docs.nvidia.com/cuda/wsl-user-guide/



## Atualizações

* **2024-04-24**
- Eu fiz algumas customizações em relação ao original que postei no vide do canal IATalking.  
- Em tese, seguindo os mesmos passos do vídeo, vai continuar funcionando
- Porém, podem aparecer mais opções na interface, que não apareciam antes!
- Caso tenha dificuldades, pode abrir uma issue, comentar no vídeo ou no blog, que ajudo!
- Em breve gravarei um vídeo sobre as mudanças


