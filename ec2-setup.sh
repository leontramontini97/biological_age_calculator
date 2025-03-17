#!/bin/bash
# Script de configuración para la aplicación de Calculadora de Edad Biológica en EC2
# Ejecutar como: bash ec2-setup.sh

echo "===== Iniciando configuración de la Calculadora de Edad Biológica ====="

# Actualizar sistema
echo "Actualizando el sistema..."
sudo apt update && sudo apt upgrade -y

# Instalar dependencias
echo "Instalando dependencias..."
sudo apt install -y python3-pip python3-venv git nginx

# Instalar dependencias para matplotlib
echo "Instalando dependencias para bibliotecas científicas..."
sudo apt install -y python3-dev libfreetype6-dev pkg-config

# Clonar repositorio (si no existe)
if [ ! -d "biological_age_calculator" ]; then
    echo "Clonando repositorio..."
    git clone https://github.com/leontramontini97/biological_age_calculator.git
fi

cd biological_age_calculator

# Configurar entorno virtual
echo "Configurando entorno virtual..."
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias de Python
echo "Instalando dependencias de Python..."
pip install -r requirements.txt
pip install gunicorn

# Crear directorio para resultados
echo "Configurando directorio de resultados..."
mkdir -p results
chmod 755 results

# Configurar Nginx
echo "Configurando Nginx..."
sudo tee /etc/nginx/sites-available/bioage > /dev/null << EOF
server {
    listen 80;
    server_name _;  # Reemplazar con tu dominio si lo tienes

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    location /static {
        alias /home/ubuntu/biological_age_calculator/static;
    }
}
EOF

# Habilitar sitio en Nginx
sudo ln -sf /etc/nginx/sites-available/bioage /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Configurar servicio systemd
echo "Configurando servicio systemd..."
sudo tee /etc/systemd/system/bioage.service > /dev/null << EOF
[Unit]
Description=Gunicorn instance for Biological Age Calculator
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/biological_age_calculator
Environment="PATH=/home/ubuntu/biological_age_calculator/venv/bin"
ExecStart=/home/ubuntu/biological_age_calculator/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Iniciar y habilitar el servicio
sudo systemctl daemon-reload
sudo systemctl start bioage
sudo systemctl enable bioage

# Verificar estado
echo "Verificando estado del servicio..."
sudo systemctl status bioage

echo ""
echo "===== Configuración completada ====="
echo "Tu aplicación debería estar disponible en: http://$(curl -s ifconfig.me)"
echo ""
echo "Instrucciones adicionales:"
echo "1. Asegúrate de que el puerto 80 esté abierto en tu grupo de seguridad de AWS"
echo "2. Para ver los logs: sudo journalctl -u bioage"
echo "3. Para reiniciar la aplicación: sudo systemctl restart bioage" 