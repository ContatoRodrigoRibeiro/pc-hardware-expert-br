def formatar_saida(texto_llm: str) -> str:
    """Garante que a saída siga o formato exato (pode ser expandido com regex se necessário)."""
    return texto_llm.strip()