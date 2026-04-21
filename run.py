#!/usr/bin/env python3
import subprocess
import sys
from core.recommender import init_database

if __name__ == "__main__":
    print("🚀 Iniciando Especialista em Hardware BR - Versão Local 100%")
    print("Inicializando banco de dados local...")
    init_database()
    print("Abrindo aplicação em http://localhost:8501")
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app/main.py", "--server.port=8501"])