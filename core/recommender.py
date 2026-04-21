import sqlite3
import random
import re
from datetime import datetime

DB_PATH = "data/pc_database.db"


def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS components (
            id INTEGER PRIMARY KEY,
            categoria TEXT,
            nome TEXT,
            preco REAL,
            loja TEXT,
            socket TEXT,
            tdp INTEGER,
            desempenho TEXT,
            link TEXT,
            atualizado TEXT
        )
    """)

    seed_data = [
        # CPUs - faixas de preço variadas
        ("CPU", "AMD Ryzen 5 5600", 699, "Kabum", "AM4", 65, "Melhor entrada 1080p", "", datetime.now().isoformat()),
        ("CPU", "Intel Core i5-13400F", 1199, "Terabyte", "LGA1700", 148, "Bom custo-benefício 1080p/1440p", "",
         datetime.now().isoformat()),
        ("CPU", "AMD Ryzen 5 7600", 1299, "Kabum", "AM5", 65, "Excelente para jogos 1440p/4K", "",
         datetime.now().isoformat()),
        ("CPU", "AMD Ryzen 7 7700", 1899, "Pichau", "AM5", 65, "Ótimo para edição + jogos", "",
         datetime.now().isoformat()),

        # GPUs - faixas de preço variadas
        ("GPU", "AMD RX 7600 8GB", 1599, "Pichau", "PCIe 4.0", 165, "Melhor 1080p custo-benefício", "",
         datetime.now().isoformat()),
        ("GPU", "NVIDIA RTX 4060 Ti 8GB", 1899, "Terabyte", "PCIe 4.0", 160, "1080p/1440p ótimo", "",
         datetime.now().isoformat()),
        ("GPU", "AMD RX 7800 XT 16GB", 2799, "Kabum", "PCIe 4.0", 263, "1440p/4K excelente", "",
         datetime.now().isoformat()),
        ("GPU", "NVIDIA RTX 4070 12GB", 2899, "Pichau", "PCIe 4.0", 200, "1440p Ultra 100+ FPS", "",
         datetime.now().isoformat()),

        # Placas-mãe
        ("Placa-Mãe", "Gigabyte B760M DS3H", 699, "Terabyte", "LGA1700", 0, "Boa para Intel i5-13400F", "",
         datetime.now().isoformat()),
        ("Placa-Mãe", "ASUS TUF B650M-Plus", 899, "Kabum", "AM5", 0, "Suporte DDR5 + PCIe 5.0", "",
         datetime.now().isoformat()),

        # RAM
        ("RAM", "32GB (2x16GB) DDR4 3200MHz CL16", 399, "Pichau", "DDR4", 0, "Ótimo para AM4 e LGA1700", "",
         datetime.now().isoformat()),
        ("RAM", "32GB (2x16GB) DDR5 6000MHz CL30", 649, "Kabum", "DDR5", 0, "Ideal para AM5", "",
         datetime.now().isoformat()),

        # Armazenamento
        ("Armazenamento", "SSD NVMe 1TB WD SN850X", 549, "Kabum", "NVMe", 0, "Melhor performance", "",
         datetime.now().isoformat()),
        ("Armazenamento", "SSD NVMe 2TB Kingston NV3", 749, "Amazon", "NVMe", 0, "Leitura 6000MB/s", "",
         datetime.now().isoformat()),

        # Fontes
        ("Fonte", "EVGA 650W 80+ Bronze", 399, "Terabyte", "ATX", 650, "Boa entrada", "", datetime.now().isoformat()),
        ("Fonte", "Corsair RM750x 750W 80+ Gold", 549, "Pichau", "ATX", 750, "Totalmente modular", "",
         datetime.now().isoformat()),

        # Gabinetes
        ("Gabinete", "NZXT H5 Flow + Cooler Master Hyper 212", 449, "Pichau", "ATX", 0, "Ótimo custo-benefício", "",
         datetime.now().isoformat()),
        ("Gabinete", "Corsair 4000D Airflow + Deepcool AK400", 599, "Kabum", "ATX", 0, "Excelente airflow", "",
         datetime.now().isoformat()),
    ]

    conn.executemany("""
        INSERT OR REPLACE INTO components 
        (categoria, nome, preco, loja, socket, tdp, desempenho, link, atualizado)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, seed_data)
    conn.commit()
    conn.close()


def recomendar_build(objetivo: str, orcamento: float = 0) -> dict:
    conn = get_db_connection()
    objetivo_lower = objetivo.lower()

    # Extrai orçamento do texto (mais robusto)
    orcamento_match = re.search(r'R?\$?\s*(\d+[\.,]?\d*)', objetivo_lower)
    if orcamento_match:
        orcamento = float(orcamento_match.group(1).replace('.', '').replace(',', '.'))
    elif orcamento == 0:
        orcamento = 6000  # orçamento padrão se não especificado

    # Detecta tipo de uso
    is_gaming = any(x in objetivo_lower for x in ["jogar", "game", "minecraft", "cod", "lol", "cs", "valorant"])
    is_4k = "4k" in objetivo_lower or "render" in objetivo_lower or "edição" in objetivo_lower

    # Alocação inteligente baseada no orçamento
    if orcamento <= 4000:
        alloc = {"CPU": 0.20, "GPU": 0.35, "Placa-Mãe": 0.12, "RAM": 0.10, "Armazenamento": 0.10, "Fonte": 0.08,
                 "Gabinete": 0.05}
    elif orcamento <= 6000:
        alloc = {"CPU": 0.18, "GPU": 0.38, "Placa-Mãe": 0.11, "RAM": 0.09, "Armazenamento": 0.10, "Fonte": 0.08,
                 "Gabinete": 0.06}
    else:
        alloc = {"CPU": 0.16, "GPU": 0.40, "Placa-Mãe": 0.10, "RAM": 0.08, "Armazenamento": 0.10, "Fonte": 0.08,
                 "Gabinete": 0.08}

    build = {}
    total = 0

    # Seleciona componentes
    for cat, percent in alloc.items():
        max_preco = orcamento * percent * 1.2  # margem de 20%

        cursor = conn.execute("""
            SELECT * FROM components 
            WHERE categoria = ? AND preco <= ?
            ORDER BY desempenho DESC, preco ASC
            LIMIT 5
        """, (cat, max_preco))

        opcoes = cursor.fetchall()

        if not opcoes:
            # Fallback: pega o mais barato disponível
            cursor = conn.execute("""
                SELECT * FROM components 
                WHERE categoria = ?
                ORDER BY preco ASC
                LIMIT 1
            """, (cat,))
            opcoes = cursor.fetchall()

        if opcoes:
            escolhido = random.choice(opcoes)
            build[cat] = dict(escolhido)
            total += escolhido["preco"]

    conn.close()

    # Gera texto formatado
    texto = f"""Visão Geral: Build otimizada para {objetivo} com excelente custo-benefício no mercado brasileiro atual (preços de Abril/2026).

Lista de Componentes:

* Processador (CPU): {build.get('CPU', {}).get('nome', 'N/A')} | Preço: R$ {build.get('CPU', {}).get('preco', 0):,.0f} | Desempenho: {build.get('CPU', {}).get('desempenho', 'N/A')}
  * Alternativa (AMD/Intel): AMD Ryzen 5 5600 | R$ 699

* Placa de Vídeo (GPU): {build.get('GPU', {}).get('nome', 'N/A')} | Preço: R$ {build.get('GPU', {}).get('preco', 0):,.0f} | Desempenho: {build.get('GPU', {}).get('desempenho', 'N/A')}
  * Alternativa (Nvidia/AMD): AMD RX 7600 8GB | R$ 1.599

* Placa-Mãe: {build.get('Placa-Mãe', {}).get('nome', 'N/A')} | Preço: R$ {build.get('Placa-Mãe', {}).get('preco', 0):,.0f} | Motivo: {build.get('Placa-Mãe', {}).get('desempenho', 'N/A')}

* Memória RAM: {build.get('RAM', {}).get('nome', 'N/A')} | Preço: R$ {build.get('RAM', {}).get('preco', 0):,.0f}

* Armazenamento: {build.get('Armazenamento', {}).get('nome', 'N/A')} | Preço: R$ {build.get('Armazenamento', {}).get('preco', 0):,.0f}

* Fonte de Alimentação: {build.get('Fonte', {}).get('nome', 'N/A')} | Preço: R$ {build.get('Fonte', {}).get('preco', 0):,.0f}

* Gabinete e Refrigeração: {build.get('Gabinete', {}).get('nome', 'N/A')} | Preço: R$ {build.get('Gabinete', {}).get('preco', 0):,.0f}

Valor Total Estimado: R$ {total:,.0f} (dentro do orçamento de R$ {orcamento:,.0f})"""

    return {"texto": texto, "total": total, "build": build}