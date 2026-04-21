import requests
from bs4 import BeautifulSoup
import time

def buscar_preco_kabum(termo: str):
    """Scraper básico para Kabum.com.br"""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        url = f"https://www.kabum.com.br/busca/{termo.replace(' ', '%20')}"
        resp = requests.get(url, headers=headers, timeout=10)
        # TODO: Implementar parsing real do HTML do Kabum
        return {"preco": None, "loja": "Kabum", "status": "placeholder"}
    except:
        return {"preco": None, "loja": "Kabum", "status": "erro"}