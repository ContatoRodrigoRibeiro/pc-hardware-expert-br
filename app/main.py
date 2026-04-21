import streamlit as st
import re
import sys
import os

# ============================================
# FIX PARA STREAMLIT CLOUD - ADICIONA O DIRETÓRIO RAIZ AO PATH
# ============================================
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Agora os imports do core vão funcionar
from core.recommender import recomendar_build, init_database

# Inicializa o banco de dados local
init_database()

st.set_page_config(page_title="PC Builder BR", page_icon="🛠️", layout="wide")

st.title("🛠️ PC Builder BR")
st.caption("100% Local • Preços Reais do Brasil • Sem API")

objetivo = st.text_area(
    "O que você quer fazer com o PC?",
    placeholder="Ex: computador para renderizar vídeos em 4k de R$6000",
    height=100
)

if st.button("🚀 Montar Configuração Ideal", type="primary", use_container_width=True):
    if not objetivo.strip():
        st.warning("Por favor, descreva o que você quer fazer com o PC.")
    else:
        with st.spinner("Montando a melhor configuração com preços reais..."):
            resultado = recomendar_build(objetivo, 0)

            st.success(f"✅ Build gerada com sucesso! Total: R$ {resultado['total']:,.0f}")

            st.subheader("📋 Sua Configuração Ideal")

            for cat, comp in resultado.get("build", {}).items():
                if comp and comp.get("nome"):
                    st.markdown(f"""
                    **{cat}:** {comp['nome']}  
                    *{comp.get('desempenho', '')}*  
                    **R$ {comp['preco']:,.0f}**
                    """)

            st.divider()
            st.markdown(f"**💰 Valor Total Estimado: R$ {resultado['total']:,.0f}**")

            st.download_button(
                "📋 Copiar Build Completa",
                data=resultado["texto"],
                file_name="minha_build_pc.txt",
                mime="text/plain"
            )