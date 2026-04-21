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
        ("CPU", "AMD Ryzen 5 5600", 699, "Kabum", "AM4", 65, "Melhor entrada 1080p", "", datetime.now().isoformat()),
        ("CPU", "Intel Core i5-13400F", 1199, "Terabyte", "LGA1700", 148, "Bom custo-benefício 1080p/1440p", "",
         datetime.now().isoformat()),
        ("CPU", "AMD Ryzen 5 7600", 1299, "Kabum", "AM5", 65, "Excelente para jogos 1440p/4K", "",
         datetime.now().isoformat()),
        ("CPU", "AMD Ryzen 7 7700", 1899, "Pichau", "AM5", 65, "Ótimo para edição + jogos", "",
         datetime.now().isoformat()),
        ("GPU", "AMD RX 7600 8GB", 1599, "Pichau", "PCIe 4.0", 165, "Melhor 1080p custo-benefício", "",
         datetime.now().isoformat()),
        ("GPU", "NVIDIA RTX 4060 Ti 8GB", 1899, "Terabyte", "PCIe 4.0", 160, "1080p/1440p ótimo", "",
         datetime.now().isoformat()),
        ("GPU", "AMD RX 7800 XT 16GB", 2799, "Kabum", "PCIe 4.0", 263, "1440p/4K excelente", "",
         datetime.now().isoformat()),
        ("GPU", "NVIDIA RTX 4070 12GB", 2899, "Pichau", "PCIe 4.0", 200, "1440p Ultra 100+ FPS", "",
         datetime.now().isoformat()),
        ("Placa-Mãe", "Gigabyte B760M DS3H", 699, "Terabyte", "LGA1700", 0, "Boa para Intel i5-13400F", "",
         datetime.now().isoformat()),
        ("Placa-Mãe", "ASUS TUF B650M-Plus", 899, "Kabum", "AM5", 0, "Suporte DDR5 + PCIe 5.0", "",
         datetime.now().isoformat()),
        ("RAM", "32GB (2x16GB) DDR4 3200MHz CL16", 399, "Pichau", "DDR4", 0, "Ótimo para AM4 e LGA1700", "",
         datetime.now().isoformat()),
        ("RAM", "32GB (2x16GB) DDR5 6000MHz CL30", 649, "Kabum", "DDR5", 0, "Ideal para AM5", "",
         datetime.now().isoformat()),
        ("Armazenamento", "SSD NVMe 1TB WD SN850X", 549, "Kabum", "NVMe", 0, "Melhor performance", "",
         datetime.now().isoformat()),
        ("Armazenamento", "SSD NVMe 2TB Kingston NV3", 749, "Amazon", "NVMe", 0, "Leitura 6000MB/s", "",
         datetime.now().isoformat()),
        ("Fonte", "EVGA 650W 80+ Bronze", 399, "Terabyte", "ATX", 650, "Boa entrada", "", datetime.now().isoformat()),
        ("Fonte", "Corsair RM750x 750W 80+ Gold", 549, "Pichau", "ATX", 750, "Totalmente modular", "",
         datetime.now().isoformat()),
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
    print("✅ Banco de dados inicializado com 18 componentes")


def recomendar_build(objetivo: str, orcamento: float = 0) -> dict:
    print(f"\n🔍 DEBUG: Iniciando recomendação para: {objetivo}")

    conn = get_db_connection()
    objetivo_lower = objetivo.lower()

    # Extrai orçamento
    orcamento_match = re.search(r'R?\$?\s*(\d+[\.,]?\d*)', objetivo_lower)
    if orcamento_match:
        orcamento = float(orcamento_match.group(1).replace('.', '').replace(',', '.'))
        print(f"💰 Orçamento extraído do texto: R$ {orcamento}")
    elif orcamento == 0:
        orcamento = 6000
        print(f"💰 Usando orçamento padrão: R$ {orcamento}")

    # Verifica quantos componentes existem no banco
    cursor = conn.execute("SELECT COUNT(*) FROM components")
    total_componentes = cursor.fetchone()[0]
    print(f"📦 Total de componentes no banco: {total_componentes}")

    if total_componentes == 0:
        print("❌ ERRO: Banco de dados está vazio!")
        conn.close()
        return {"texto": "Erro: Banco vazio", "total": 0, "build": {}}

    # Alocação
    alloc = {"CPU": 0.18, "GPU": 0.38, "Placa-Mãe": 0.11, "RAM": 0.09, "Armazenamento": 0.10, "Fonte": 0.08,
             "Gabinete": 0.06}

    build = {}
    total = 0

    for cat, percent in alloc.items():
        max_preco = orcamento * percent * 1.3
        print(f"🔍 Buscando {cat} com preço máximo R$ {max_preco:.0f}")

        cursor = conn.execute("""
            SELECT * FROM components 
            WHERE categoria = ? AND preco <= ?
            ORDER BY desempenho DESC, preco ASC
            LIMIT 5
        """, (cat, max_preco))

        opcoes = cursor.fetchall()
        print(f"   → Encontradas {len(opcoes)} opções para {cat}")

        if not opcoes:
            cursor = conn.execute("""
                SELECT * FROM components 
                WHERE categoria = ?
                ORDER BY preco ASC
                LIMIT 1
            """, (cat,))
            opcoes = cursor.fetchall()
            print(f"   → Fallback: {len(opcoes)} opção(ões)")

        if opcoes:
            escolhido = random.choice(opcoes)
            build[cat] = dict(escolhido)
            total += escolhido["preco"]
            print(f"   ✅ Selecionado: {escolhido['nome']} - R$ {escolhido['preco']}")
        else:
            print(f"   ❌ NENHUMA opção encontrada para {cat}")

    conn.close()

    print(f"\n📊 RESUMO: Total = R$ {total}")

    if total == 0:
        print("❌ ERRO: Total zerado! Verifique o banco de dados.")

    # Texto
    texto = f"""Visão Geral: Build otimizada para {objetivo}.

Lista de Componentes:
* Processador (CPU): {build.get('CPU', {}).get('nome', 'N/A')} | R$ {build.get('CPU', {}).get('preco', 0):,.0f}
* Placa de Vídeo (GPU): {build.get('GPU', {}).get('nome', 'N/A')} | R$ {build.get('GPU', {}).get('preco', 0):,.0f}
* Placa-Mãe: {build.get('Placa-Mãe', {}).get('nome', 'N/A')} | R$ {build.get('Placa-Mãe', {}).get('preco', 0):,.0f}
* Memória RAM: {build.get('RAM', {}).get('nome', 'N/A')} | R$ {build.get('RAM', {}).get('preco', 0):,.0f}
* Armazenamento: {build.get('Armazenamento', {}).get('nome', 'N/A')} | R$ {build.get('Armazenamento', {}).get('preco', 0):,.0f}
* Fonte de Alimentação: {build.get('Fonte', {}).get('nome', 'N/A')} | R$ {build.get('Fonte', {}).get('preco', 0):,.0f}
* Gabinete e Refrigeração: {build.get('Gabinete', {}).get('nome', 'N/A')} | R$ {build.get('Gabinete', {}).get('preco', 0):,.0f}

Valor Total Estimado: R$ {total:,.0f}"""

    return {"texto": texto, "total": total, "build": build}