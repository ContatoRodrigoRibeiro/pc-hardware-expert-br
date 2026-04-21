import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
import os

DB_PATH = "data/price_cache.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS prices (
            componente TEXT PRIMARY KEY,
            preco REAL,
            loja TEXT,
            atualizado TEXT
        )
    """)
    conn.commit()
    return conn

def buscar_preco(componente: str, loja: str = "meupc") -> dict:
    """
    Busca preço atualizado. Por enquanto retorna estimativa realista 2026.
    Em produção: integrar com meupc.net ou scrapers das lojas.
    """
    # Estimativas realistas de abril/2026 (atualize conforme necessário)
    precos_estimados = {
        "ryzen 5 7600": {"preco": 1299, "loja": "Kabum"},
        "rtx 4070": {"preco": 2899, "loja": "Pichau"},
        "b650m": {"preco": 899, "loja": "Terabyte"},
        "32gb ddr5 6000": {"preco": 649, "loja": "Kabum"},
        "ssd 2tb nvme": {"preco": 749, "loja": "Amazon"},
        "rm750x": {"preco": 549, "loja": "Pichau"},
        "4000d + ak400": {"preco": 599, "loja": "Kabum"},
    }
    
    key = componente.lower()
    for k, v in precos_estimados.items():
        if k in key:
            return v
    
    # Fallback
    return {"preco": 500, "loja": "Estimativa"}