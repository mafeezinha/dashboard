import re
import unicodedata
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

AZUL_CLARO = "#38bdf8"
AZUL_MEDIO = "#0ea5e9"
AZUL_ESCURO = "#2563eb"
BRANCO = "#FFFFFF"
FUNDO = "#0b0f19"
PALETA = [AZUL_CLARO, AZUL_MEDIO, AZUL_ESCURO, "#08B2E3", "#60a5fa", "#93c5fd", "#bae6fd"]

st.set_page_config(page_title="Dashboard de Moda", page_icon="👗", layout="wide")

st.markdown(
    f"""
    <style>
    .stApp {{ background-color: {FUNDO}; color: #e5e7eb; }}
    [data-testid="stSidebar"] {{ background-color: #111827; }}
    h1, h2, h3 {{
        color: {AZUL_CLARO} !important;
        text-shadow: 0 0 10px rgba(56, 189, 248, 0.4);
    }}
    .stTabs [data-baseweb="tab-list"] button p {{ color: {BRANCO} !important; font-weight: 500; }}
    .stTabs [data-baseweb="tab-list"] button[aria-selected="true"] p {{
        color: {AZUL_CLARO} !important;
        font-weight: bold;
    }}
    .kpi {{
        background: linear-gradient(135deg, rgba(14, 165, 233, 0.1), rgba(37, 99, 235, 0.1));
        border-left: 6px solid {AZUL_CLARO};
        border-radius: 12px;
        padding: 14px 18px;
        box-shadow: 0 0 15px rgba(56, 189, 248, 0.15);
    }}
    .kpi h2 {{ margin: 0; font-size: 2rem; text-shadow: 0 0 8px rgba(56, 189, 248, 0.6); }}
    .kpi p {{ margin: 0; color: #9ca3af; font-size: .9rem; }}
    </style>
    """,
    unsafe_allow_html=True,
)

plt.rcParams.update({
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.edgecolor": "#334155",
    "axes.titleweight": "bold",
    "axes.titlesize": 11,
    "font.size": 9,
    "text.color": BRANCO,
    "axes.labelcolor": BRANCO,
    "xtick.color": BRANCO,
    "ytick.color": BRANCO,
    "figure.facecolor": FUNDO,
    "axes.facecolor": "#111827",
})


def sem_acento(texto):
    texto = unicodedata.normalize("NFKD", str(texto))
    return "".join(c for c in texto if not unicodedata.combining(c)).lower().strip()


def dividir_multipla(valor):
    if pd.isna(valor):
        return []
    return [p.strip() for p in str(valor).split(";") if p.strip()]


def normalizar_genero(g):
    t = sem_acento(g)
    if t.startswith("masc"):
        return "Masculino"
    if t.startswith("fem"):
        return "Feminino"
    if "binario" in t:
        return "Não binário"
    return "Outro / não informou"


def normalizar_acesso(item):
    t = sem_acento(item)
    if "loja" in t and "fisic" in t:
        return "Lojas físicas"
    if "online" in t:
        return "Online"
    if "brecho" in t:
        return "Brechó"
    return "Outros (doação, família...)"


def normalizar_descarte(item):
    t = sem_acento(item)
    if "doa" in t:
        return "Doação"
    if "vend" in t or "vemd" in t:
        return "Venda"
    if "descarte" in t:
        return "Descarte (lixo)"
    return "Outros"


def formatar_renda(x):
    if pd.isna(x):
        return "Não informou"
    x = str(x).strip()
    if x.lower().startswith("menos"):
        return "Até 1.100"
    try:
        return f"{int(float(x)):,}".replace(",", ".")
    except ValueError:
        return x


def categorizar_frequencia(texto):
    t = sem_acento(texto)
    if re.search(r"nao sei|nao sej|varia|depend|^as vezes$|quando|precis|nunca|"
                 r"hora|inutiliz|com frequencia", t) and not re.search(r"mes|ano", t):
        return "Eventual / não sabe"
    if re.search(r"semana|duas semanas|toda hora", t):
        return "Semanal / quinzenal"
    if re.search(r"(duas|2|tres|3|umas duas)\s*vezes\s*(por|ao|no|em)\s*mes|"
                 r"(1|uma)\s*(e|a)\s*(3|duas|2).*mes|mes em mes|mensal|todo mes|"
                 r"(uma|1)\s*(vez|peca)\s*(por|no|ao|pro)\s*mes|por mes|pelo menos|"
                 r"1 mes e meio", t):
        return "Mensal"
    if re.search(r"2 mes|dois mes|2 ou 3|duas mes|2 mese", t):
        return "A cada 2 meses"
    if re.search(r"3 mes|tres mes|trimestre|3 em 3|1 a 3|em\s+meses 3", t):
        return "A cada 3 meses"
    if re.search(r"5-6|6 em 6|6 mes|6 mess|7 mes|5 mes|semestre", t):
        return "A cada 5-6 meses"
    if re.search(r"ano|final de ano|(3|tres|2|duas|quatro).*vezes.*ano", t):
        return "Anual / poucas vezes no ano"
    if "mes" in t:
        return "Mensal"
    return "Eventual / não sabe"


ESTILOS = {
    "Streetwear": ["streetwear", "streatwear", "swag", "largas", "oversized"],
    "Esportivo": ["esportiv"],
    "Delicado / romântico": ["delicad", "romantic", "leves"],
    "Básico / casual": ["basic", "casual", "confortav"],
    "Formal / elegante": ["formal", "elegante", "chique", "tradicion", "arrumad"],
    "Alternativo (gótico, boho, y2k...)": ["gotic", "boho", "alternativ", "yk2", "y2k",
                                           "baddie", "geek", "anos 2000"],
    "Variado / todos": ["todos", "varios", "variav", "mistura"],
    "Sem estilo definido": ["nao sei", "nao tenho", "sem estilo", "estilo definido"],
}


def categorizar_estilos(texto):
    t = sem_acento(texto)
    achados = [nome for nome, chaves in ESTILOS.items() if any(c in t for c in chaves)]
    return achados or ["Outros"]


@st.cache_data(show_spinner="Carregando planilha...")
def carregar(arquivo):
    xls = pd.ExcelFile(arquivo)
    abas = {nome.strip().lower(): xls.parse(nome) for nome in xls.sheet_names}
    for aba in abas.values():
        aba.columns = [str(c).strip() for c in aba.columns]

    geral = abas["geral"].copy()
    geral["Gênero"] = geral["Gênero"].map(normalizar_genero)
    geral["Renda familiar"] = geral["Renda familiar"].map(formatar_renda)
    geral["Acesso_lista"] = geral["Acesso a roupas"].map(
        lambda v: sorted({normalizar_acesso(i) for i in dividir_multipla(v)})
    )
    geral["Descarte_lista"] = geral["Descarte"].map(
        lambda v: sorted({normalizar_descarte(i) for i in dividir_multipla(v) or [v]})
    )
    geral["Comprador_lista"] = geral["Comprador"].map(
        lambda v: sorted({"Eu" if sem_acento(i).startswith("eu") else "Responsáveis"
                          for i in dividir_multipla(v)})
    )
    geral["Faixa etária"] = pd.cut(
        geral["Idade"], bins=[0, 15, 16, 17, 18, 25, 120],
        labels=["15", "16", "17", "18", "19-25", "26+"],
    )
    geral["Tem renda própria"] = geral["Sua renda"].gt(0).map({True: "Sim", False: "Não"})
    abas["geral"] = geral

    freq = abas["frequencia"].copy()
    freq["Categoria"] = freq.iloc[:, 0].astype(str).map(categorizar_frequencia)
    abas["frequencia"] = freq

    estilo = abas["planilha3"].copy()
    estilo["Estilos"] = estilo.iloc[:, 0].astype(str).map(categorizar_estilos)
    abas["planilha3"] = estilo
    return abas


def contar_lista(serie):
    return serie.explode().value_counts()


def barras_h(contagem, titulo, cor=AZUL_CLARO, mostrar_pct=True):
    contagem = contagem.sort_values()
    fig, ax = plt.subplots(figsize=(5, max(2.0, 0.4 * len(contagem) + 0.8)))
    barras = ax.barh(contagem.index.astype(str), contagem.values, color=cor)
    total = contagem.sum()
    for barra, v in zip(barras, contagem.values):
        texto = f"{v}  ({v / total:.0%})" if mostrar_pct else f"{v}"
        ax.text(v + contagem.max() * 0.01, barra.get_y() + barra.get_height() / 2,
                texto, va="center", fontsize=8)
    ax.set_xlim(0, contagem.max() * 1.25)
    ax.set_title(titulo, loc="left", color=AZUL_CLARO)
    ax.set_xlabel("Respostas")
    fig.tight_layout()
    return fig


def barras_v(contagem, titulo, cor=AZUL_MEDIO):
    fig, ax = plt.subplots(figsize=(5, 3.2))
    barras = ax.bar(contagem.index.astype(str), contagem.values, color=cor)
    ax.bar_label(barras, padding=2, fontsize=8, color=BRANCO)
    ax.set_title(titulo, loc="left", color=AZUL_CLARO)
    ax.set_ylabel("Respostas")
    plt.setp(ax.get_xticklabels(), rotation=25, ha="right")
    fig.tight_layout()
    return fig


def rosca(contagem, titulo):
    fig, ax = plt.subplots(figsize=(4.2, 3.5))
    ax.pie(
        contagem.values, labels=contagem.index, colors=PALETA[: len(contagem)],
        autopct=lambda p: f"{p:.0f}%" if p >= 4 else "",
        startangle=90, pctdistance=0.75,
        wedgeprops=dict(width=0.45, edgecolor=FUNDO),
        textprops=dict(fontsize=8, color=BRANCO),
    )
    ax.set_title(titulo, loc="left", color=AZUL_CLARO)
    fig.tight_layout()
    return fig


def kpi(coluna, valor, rotulo):
    coluna.markdown(f'<div class="kpi"><h2>{valor}</h2><p>{rotulo}</p></div>',
                    unsafe_allow_html=True)


st.title("👗 Dashboard da Pesquisa de Moda")
st.caption("Hábitos de compra, acesso, descarte e estilo dos respondentes.")

caminho = Path(__file__).resolve().parent / "forms moda.xlsx"
enviado = st.sidebar.file_uploader("Planilha (opcional)", type="xlsx")
fonte = enviado or (caminho if caminho.exists() else None)
if fonte is None:
    st.warning("Não encontrei **forms moda.xlsx** na mesma pasta do script. Envie a planilha pela barra lateral.")
    st.stop()

abas = carregar(fonte)
geral = abas["geral"]

st.sidebar.header("Filtros")
opcoes_genero = sorted(geral["Gênero"].unique())
opcoes_renda = sorted(geral["Renda familiar"].unique())
idade_min, idade_max = int(geral["Idade"].min()), int(geral["Idade"].max())

generos = st.sidebar.multiselect("Gênero", opcoes_genero, default=opcoes_genero)
faixa = st.sidebar.slider("Idade", idade_min, idade_max, (idade_min, idade_max))
rendas = st.sidebar.multiselect("Renda familiar", opcoes_renda, default=opcoes_renda)
renda_propria = st.sidebar.radio("Tem renda própria?", ["Todos", "Sim", "Não"], horizontal=True)

df = geral[
    geral["Gênero"].isin(generos)
    & geral["Idade"].between(*faixa)
    & geral["Renda familiar"].isin(rendas)
]
if renda_propria != "Todos":
    df = df[df["Tem renda própria"] == renda_propria]

st.sidebar.metric("Respondentes filtrados", f"{len(df)} de {len(geral)}")
if df.empty:
    st.error("Nenhum respondente com esses filtros.")
    st.stop()

c1, c2, c3, c4 = st.columns(4)
kpi(c1, len(df), "respondentes")
kpi(c2, f"{df['Idade'].mean():.1f} anos", "idade média")
kpi(c3, f"{(df['Tem renda própria'] == 'Sim').mean():.0%}", "têm renda própria")
kpi(c4, f"{df['Comprador_lista'].map(lambda l: 'Responsáveis' in l).mean():.0%}",
    "têm roupas compradas por responsáveis")
st.write("")

aba_perfil, aba_compras, aba_descarte, aba_estilo, aba_dados = st.tabs(
    ["Perfil", "Compras", "Descarte", "Estilo e status", "Dados"]
)

with aba_perfil:
    a, b = st.columns(2)
    a.pyplot(rosca(df["Gênero"].value_counts(), "Gênero"))
    b.pyplot(barras_v(df["Faixa etária"].value_counts().sort_index(), "Idade dos respondentes"))

    a, b = st.columns(2)
    ordem_renda = [r for r in ["Até 1.100", "1.550", "2.500", "3.500", "5.000", "Não informou"]
                   if r in df["Renda familiar"].values]
    a.pyplot(barras_v(df["Renda familiar"].value_counts().reindex(ordem_renda),
                      "Renda familiar (R$)"))
    b.pyplot(barras_v(df["Sua renda"].value_counts().sort_index(), "Renda própria (R$)", AZUL_CLARO))

with aba_compras:
    a, b = st.columns(2)
    a.pyplot(barras_h(contar_lista(df["Comprador_lista"]), "Quem compra suas roupas?", AZUL_ESCURO))
    b.pyplot(barras_h(contar_lista(df["Acesso_lista"]), "Onde acessam roupas?"))

    st.subheader("Frequência de compra")
    st.caption("A aba de frequência não tem ligação com as demais, então não responde aos filtros.")
    freq_df = abas["frequencia"]
    ordem = ["Semanal / quinzenal", "Mensal", "A cada 2 meses", "A cada 3 meses",
             "A cada 5-6 meses", "Anual / poucas vezes no ano", "Eventual / não sabe"]
    freq = freq_df["Categoria"].value_counts()
    freq = freq.reindex([o for o in ordem if o in freq.index])

    a, b = st.columns([2, 1])
    a.pyplot(barras_v(freq, "Com que frequência compram roupa?", AZUL_CLARO))
    with b.expander("Ver respostas originais por categoria"):
        categoria = st.selectbox("Categoria", freq.index)
        st.write(freq_df.loc[freq_df["Categoria"] == categoria].iloc[:, 0].str.strip().tolist())

with aba_descarte:
    a, b = st.columns(2)
    a.pyplot(rosca(contar_lista(df["Descarte_lista"]), "O que fazem com roupas que não usam?"))

    cruzamento = (df.explode("Acesso_lista").explode("Descarte_lista")
                  .groupby(["Acesso_lista", "Descarte_lista"]).size().unstack(fill_value=0))
    fig, ax = plt.subplots(figsize=(5, 3.5))
    cruzamento.plot(kind="bar", stacked=True, ax=ax, color=PALETA[: cruzamento.shape[1]], width=0.7)
    ax.set_title("Acesso × destino das roupas", loc="left", color=AZUL_CLARO)
    ax.set_xlabel("")
    ax.legend(title="", frameon=False, fontsize=8, labelcolor=BRANCO)
    plt.setp(ax.get_xticklabels(), rotation=25, ha="right")
    fig.tight_layout()
    b.pyplot(fig)

    st.info("Doação é de longe o destino mais comum. Use os filtros para ver se muda por renda ou gênero.")

with aba_estilo:
    a, b = st.columns(2)
    estilos = abas["planilha3"]["Estilos"].explode().value_counts()
    a.pyplot(barras_h(estilos, "Estilos citados", mostrar_pct=False))

    social = abas["planilha4"].copy()
    social.columns = ["Resposta", "Contagem"]
    b.pyplot(rosca(social.set_index("Resposta")["Contagem"], "Marcas refletem status social?"))

    st.caption("Estilo e status social vêm de abas separadas, por isso não respondem aos filtros.")
    with st.expander("Ver respostas originais de estilo"):
        st.dataframe(abas["planilha3"].iloc[:, 0].str.strip(), use_container_width=True)

with aba_dados:
    tabela = df.drop(columns=["Acesso_lista", "Descarte_lista", "Comprador_lista"])
    st.dataframe(tabela, use_container_width=True)
    st.download_button("Baixar dados filtrados (CSV)", tabela.to_csv(index=False).encode("utf-8-sig"),
                       "dados_filtrados.csv", "text/csv")
