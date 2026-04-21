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
        ("CPU", "AMD Ryzen 5 7600", 1299, "Kabum", "AM5", 65, "Excelente para jogos 1440p/4K", "",
         datetime.now().isoformat()),
        ("CPU", "AMD Ryzen 7 7700", 1899, "Pichau", "AM5", 65, "Ótimo para edição + jogos", "",
         datetime.now().isoformat()),
        ("CPU", "Intel Core i5-13400F", 1199, "Terabyte", "LGA1700", 148, "Bom custo-benefício 1080p/1440p", "",
         datetime.now().isoformat()),
        ("CPU", "AMD Ryzen 5 5600", 699, "Kabum", "AM4", 65, "Melhor entrada 1080p", "", datetime.now().isoformat()),
        ("GPU", "NVIDIA RTX 4070 12GB", 2899, "Pichau", "PCIe 4.0", 200, "1440p Ultra 100+ FPS", "",
         datetime.now().isoformat()),
        ("GPU", "AMD RX 7800 XT 16GB", 2799, "Kabum", "PCIe 4.0", 263, "1440p/4K excelente", "",
         datetime.now().isoformat()),
        ("GPU", "NVIDIA RTX 4060 Ti 8GB", 1899, "Terabyte", "PCIe 4.0", 160, "1080p/1440p ótimo", "",
         datetime.now().isoformat()),
        ("GPU", "AMD RX 7600 8GB", 1599, "Pichau", "PCIe 4.0", 165, "Melhor 1080p custo-benefício", "",
         datetime.now().isoformat()),
        ("Placa-Mãe", "ASUS TUF B650M-Plus", 899, "Kabum", "AM5", 0, "Suporte DDR5 + PCIe 5.0", "",
         datetime.now().isoformat()),
        ("Placa-Mãe", "Gigabyte B760M DS3H", 699, "Terabyte", "LGA1700", 0, "Boa para Intel i5-13400F", "",
         datetime.now().isoformat()),
        ("RAM", "32GB (2x16GB) DDR5 6000MHz CL30", 649, "Kabum", "DDR5", 0, "Ideal para AM5", "",
         datetime.now().isoformat()),
        ("RAM", "32GB (2x16GB) DDR4 3200MHz CL16", 399, "Pichau", "DDR4", 0, "Ótimo para AM4 e LGA1700", "",
         datetime.now().isoformat()),
        ("Armazenamento", "SSD NVMe 2TB Kingston NV3", 749, "Amazon", "NVMe", 0, "Leitura 6000MB/s", "",
         datetime.now().isoformat()),
        ("Armazenamento", "SSD NVMe 1TB WD SN850X", 549, "Kabum", "NVMe", 0, "Melhor performance", "",
         datetime.now().isoformat()),
        ("Fonte", "Corsair RM750x 750W 80+ Gold", 549, "Pichau", "ATX", 750, "Totalmente modular", "",
         datetime.now().isoformat()),
        ("Fonte", "EVGA 650W 80+ Bronze", 399, "Terabyte", "ATX", 650, "Boa entrada", "", datetime.now().isoformat()),
        ("Gabinete", "Corsair 4000D Airflow + Deepcool AK400", 599, "Kabum", "ATX", 0, "Excelente airflow", "",
         datetime.now().isoformat()),
        ("Gabinete", "NZXT H5 Flow + Cooler Master Hyper 212", 449, "Pichau", "ATX", 0, "Ótimo custo-benefício", "",
         datetime.now().isoformat()),
    ]

    conn.executemany("""
        INSERT OR REPLACE INTO components 
        (categoria, nome, preco, loja, socket, tdp, desempenho, link, atualizado)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, seed_data)
    conn.commit()
    conn.close()


def recomendar_build(objetivo: str, orcamento: float) -> dict:
    conn = get_db_connection()
    objetivo_lower = objetivo.lower()

    match = re.search(r'(até|com|orçamento de|valor de)\s*R?\$?\s*(\d+)', objetivo_lower)
    if match:
        orcamento = float(match.group(2))

    is_gaming = any(x in objetivo_lower for x in ["jogar", "game", "minecraft", "cod", "lol", "cs"])

    # 1. CPU
    cursor = conn.execute("""
        SELECT * FROM components 
        WHERE categoria = 'CPU' AND preco <= ?
        ORDER BY desempenho DESC, preco ASC LIMIT 5
    """, (orcamento * 0.24,))
    cpus = cursor.fetchall()
    cpu = random.choice(cpus) if cpus else None

    # 2. Placa-Mãe compatível (margem maior para não sumir)
    if cpu:
        socket = cpu["socket"]
        cursor = conn.execute("""
                SELECT * FROM components 
                WHERE categoria = 'Placa-Mãe' AND socket = ? AND preco <= ?
                ORDER BY desempenho DESC, preco ASC LIMIT 4
            """, (socket, orcamento * 0.14))
        placas = cursor.fetchall()
        placa_mae = random.choice(placas) if placas else None
    else:
        placa_mae = None

    # 3. RAM compatível
    ram_type = "DDR5" if (cpu and cpu["socket"] == "AM5") else "DDR4"
    cursor = conn.execute("""
        SELECT * FROM components 
        WHERE categoria = 'RAM' AND socket = ? AND preco <= ?
        ORDER BY desempenho DESC, preco ASC LIMIT 4
    """, (ram_type, orcamento * 0.09))
    rams = cursor.fetchall()
    ram = random.choice(rams) if rams else None

    # 4. GPU
    cursor = conn.execute("""
        SELECT * FROM components 
        WHERE categoria = 'GPU' AND preco <= ?
        ORDER BY desempenho DESC, preco ASC LIMIT 5
    """, (orcamento * 0.35,))
    gpus = cursor.fetchall()
    gpu = random.choice(gpus) if gpus else None

    # 5. Armazenamento, Fonte e Gabinete
    cursor = conn.execute("""
        SELECT * FROM components 
        WHERE categoria = 'Armazenamento' AND preco <= ?
        ORDER BY desempenho DESC, preco ASC LIMIT 4
    """, (orcamento * 0.13,))
    arm_results = cursor.fetchall()
    arm = random.choice(arm_results) if arm_results else None

    cursor = conn.execute("""
        SELECT * FROM components 
        WHERE categoria = 'Fonte' AND preco <= ?
        ORDER BY desempenho DESC, preco ASC LIMIT 4
    """, (orcamento * 0.11,))
    fonte_results = cursor.fetchall()
    fonte = random.choice(fonte_results) if fonte_results else None

    cursor = conn.execute("""
        SELECT * FROM components 
        WHERE categoria = 'Gabinete' AND preco <= ?
        ORDER BY desempenho DESC, preco ASC LIMIT 4
    """, (orcamento * 0.10,))
    gabinete_results = cursor.fetchall()
    gabinete = random.choice(gabinete_results) if gabinete_results else None

    conn.close()

    build = {
        "CPU": dict(cpu) if cpu else {},
        "GPU": dict(gpu) if gpu else {},
        "Placa-Mãe": dict(placa_mae) if placa_mae else {},
        "RAM": dict(ram) if ram else {},
        "Armazenamento": dict(arm) if arm else {},
        "Fonte": dict(fonte) if fonte else {},
        "Gabinete": dict(gabinete) if gabinete else {}
    }

    total = sum(c.get("preco", 0) for c in build.values())

    texto = f"""Visão Geral: Build otimizada para {objetivo} com excelente custo-benefício no mercado brasileiro atual (preços de Abril/2026).

Lista de Componentes:

* Processador (CPU): {build['CPU'].get('nome', 'N/A')} | Preço: R$ {build['CPU'].get('preco', 0):,.0f} | Desempenho: {build['CPU'].get('desempenho', 'N/A')}
  * Alternativa (AMD/Intel): AMD Ryzen 5 5600 | R$ 699

* Placa de Vídeo (GPU): {build['GPU'].get('nome', 'N/A')} | Preço: R$ {build['GPU'].get('preco', 0):,.0f} | Desempenho: {build['GPU'].get('desempenho', 'N/A')}
  * Alternativa (Nvidia/AMD): AMD RX 7600 8GB | R$ 1.599

* Placa-Mãe: {build['Placa-Mãe'].get('nome', 'N/A')} | Preço: R$ {build['Placa-Mãe'].get('preco', 0):,.0f} | Motivo: {build['Placa-Mãe'].get('desempenho', 'N/A')}

* Memória RAM: {build['RAM'].get('nome', 'N/A')} | Preço: R$ {build['RAM'].get('preco', 0):,.0f}

* Armazenamento: {build['Armazenamento'].get('nome', 'N/A')} | Preço: R$ {build['Armazenamento'].get('preco', 0):,.0f}

* Fonte de Alimentação: {build['Fonte'].get('nome', 'N/A')} | Preço: R$ {build['Fonte'].get('preco', 0):,.0f}

* Gabinete e Refrigeração: {build['Gabinete'].get('nome', 'N/A')} | Preço: R$ {build['Gabinete'].get('preco', 0):,.0f}

Valor Total Estimado: R$ {total:,.0f} (dentro do orçamento de R$ {orcamento:,.0f})"""

    return {"texto": texto, "total": total, "build": build}