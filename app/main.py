import streamlit as st
from core.recommender import recomendar_build
import re

st.set_page_config(
    page_title="PC Builder BR • Local",
    page_icon="🛠️",
    layout="wide"
)

# CSS Profissional
st.markdown("""
<style>
    .main-header { font-size: 2.7rem; font-weight: 800; color: #FF4B4B; }
    .build-card {
        background: #161616;
        border-radius: 18px;
        padding: 28px;
        border: 1px solid #2A2A2A;
        margin-top: 20px;
    }
    .component {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 13px 0;
        border-bottom: 1px solid #2A2A2A;
    }
    .component:last-child { border-bottom: none; }
    .comp-name { font-weight: 600; font-size: 1.05rem; }
    .comp-price { font-weight: 700; color: #FF6B6B; font-size: 1.05rem; }
    .total-box {
        background: linear-gradient(135deg, #FF4B4B, #C41E3A);
        color: white;
        padding: 20px 30px;
        border-radius: 16px;
        text-align: center;
        margin: 22px 0;
        font-size: 1.3rem;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<h1 class="main-header">🛠️ PC Builder BR</h1>', unsafe_allow_html=True)
st.markdown("**100% Local • Preços Reais do Brasil • Sem API**")

# Input principal (só o texto)
objetivo = st.text_area(
    "O que você quer fazer com o PC?",
    placeholder="Ex: Computador para jogar Minecraft com shaders 4K e editar vídeos com valor de até R$ 6500",
    height=85
)

if st.button("🚀 Montar Configuração Ideal", type="primary", use_container_width=True):
    if not objetivo.strip():
        st.warning("Descreva o que você quer fazer com o PC.")
    else:
        with st.spinner("Montando a melhor configuração com preços reais do Brasil..."):
            # Extrai orçamento do texto (se mencionado)
            orcamento_match = re.search(r'R\$\s*(\d+)', objetivo)
            orcamento = int(orcamento_match.group(1)) if orcamento_match else 7000

            resultado = recomendar_build(objetivo, orcamento)

            st.success(f"✅ Build gerada com sucesso! Total: R$ {resultado['total']:,.0f}")

            # === SEÇÃO BONITA DA BUILD ===
            with st.container():
                st.markdown("### 📋 Sua Configuração Ideal")

                build = resultado.get("build", {})

                # Cards bonitos para cada componente
                components_order = ["CPU", "GPU", "Placa-Mãe", "RAM", "Armazenamento", "Fonte", "Gabinete"]

                for cat in components_order:
                    if cat in build and build[cat].get("nome"):
                        comp = build[cat]
                        st.markdown(f"""
                        <div class="component">
                            <div>
                                <span class="comp-name">{cat}: {comp['nome']}</span><br>
                                <span style="color:#888; font-size:0.9rem;">{comp.get('desempenho', '')}</span>
                            </div>
                            <div class="comp-price">R$ {comp['preco']:,.0f}</div>
                        </div>
                        """, unsafe_allow_html=True)

                # Total destacado
                st.markdown(f"""
                <div class="total-box">
                    💰 Valor Total Estimado: R$ {resultado['total']:,.0f}
                </div>
                """, unsafe_allow_html=True)

            # Botão copiar
            st.download_button(
                "📋 Copiar Build Completa",
                data=resultado["texto"],
                file_name="build_pc_ideal.txt",
                use_container_width=True
            )