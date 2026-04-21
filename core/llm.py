import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def get_llm_client():
    """
    Cliente compatível com Grok (xAI) via OpenAI SDK.
    Defina XAI_API_KEY no .env ou use OPENAI_API_KEY com base_url custom.
    """
    api_key = os.getenv("XAI_API_KEY") or os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Defina XAI_API_KEY ou OPENAI_API_KEY no arquivo .env")
    
    # Grok usa o mesmo endpoint da OpenAI
    base_url = os.getenv("XAI_BASE_URL", "https://api.x.ai/v1")
    
    return OpenAI(
        api_key=api_key,
        base_url=base_url
    )

def gerar_build(objetivo: str, orcamento: float) -> str:
    """Gera a build usando o LLM com o system prompt exato."""
    client = get_llm_client()
    system_prompt = open("prompts/system_hardware_expert.txt", "r", encoding="utf-8").read()
    
    user_message = f"Objetivo do cliente: {objetivo}\nOrçamento máximo: R${orcamento:,.0f}"
    
    response = client.chat.completions.create(
        model="grok-3",  # ou "grok-3-mini" para mais barato/rápido
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        temperature=0.2,
        max_tokens=2000
    )
    return response.choices[0].message.content