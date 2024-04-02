# Instruções

Você precisa configurar o seu ambiente com docker. Veja abaixo algumas orientações para isso.  

Para subir o modelo, faça clone este repo e execute um docker compose up:

```sh
git clone 
```

## Pré-requisitos 

A sua máquina deve conter um docker!  
Eu já testei isso em um docker no Azure e wsl2.  
Para ubuntu, eu segui este link: https://docs.docker.com/engine/install/ubuntu/

Não tem segredos aqui. Basta configurar um docker e fazer com que o seu docker tenha acesso as placa de vídeo.  
Por exemplo, em maquin Ubuntu do Azure (Standard NC8as T4 v3), eu precisei fazer isso após instalar o docker:
```sh
sudo apt install -y nvidia-docker2
sudo systemctl daemon-reload
sudo systemctl restart docker
```

No Windows, eu instalei com wsl2 e Docker Desktop, seguindo a instalação padrão.
Além disso, eu já tinha instalado os drivers da NVIDIA conforme este link: https://docs.nvidia.com/cuda/wsl-user-guide/




