def verificar_compatibilidade(cpu: str, placa_mae: str, gpu: str, fonte_w: int) -> list:
    """Verifica compatibilidade básica. Expanda com regras reais."""
    erros = []
    if "ryzen" in cpu.lower() and "b650" not in placa_mae.lower() and "x670" not in placa_mae.lower():
        erros.append("Socket AM5 requer placa-mãe B650/X670")
    if "rtx 4070" in gpu.lower() and fonte_w < 650:
        erros.append("RTX 4070 recomenda fonte de pelo menos 650W")
    return erros