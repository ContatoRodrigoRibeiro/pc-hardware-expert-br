#!/usr/bin/env python3
import subprocess
import sys

if __name__ == "__main__":
    print("🚀 Iniciando Especialista em Hardware BR - Versão Local 100%")

    # Inicializa o banco de dados local
    from core.recommender import init_database

    init_database()

    print("✅ Banco de dados pronto")

    # Inicia o Streamlit
    import streamlit.web.cli as stcli

    sys.argv = ["streamlit", "run", "app/main.py", "--server.port=8501", "--server.address=0.0.0.0"]
    stcli.main()