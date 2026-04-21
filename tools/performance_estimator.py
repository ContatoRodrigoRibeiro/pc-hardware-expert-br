def estimar_fps(jogo: str, resolucao: str, gpu: str) -> str:
    """Estimativa simples de FPS. Em produção usar dados de benchmarks."""
    if "4k" in resolucao.lower() and "4070" in gpu.lower():
        return "60-90 FPS em Ultra (com DLSS)"
    if "1440p" in resolucao.lower():
        return "100-140 FPS em Ultra"
    return "Excelente performance esperada"