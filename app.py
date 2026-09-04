import io
import os
import sys
import unicodedata
from datetime import datetime

import pandas as pd
import plotly.express as px
import streamlit as st

# =========================================================
# 1. Configuración general de la página
# =========================================================
st.set_page_config(
    page_title="Dashboard Ejecutivo de Infraestructura Vial - RNC Chiapas",
    page_icon="🛣️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# 2. Paleta corporativa y Colores Personalizados
# =========================================================
COLOR_PRIMARY = "#08989C"
COLOR_SECONDARY = "#80DFD9"
COLOR_NAVY = "#003057"
COLOR_BLUE = "#4183CD"
COLOR_PURPLE = "#A590FF"
COLOR_GRAY1 = "#989898"
COLOR_GRAY2 = "#575756"
COLOR_TEXT_SECTIONS = "#3C3C3B"
COLOR_BG = "#DCDCDC"
COLOR_CARD = "#FFFFFF"

PALETA_PIE = [
    "#08989C",
    "#80DFD9",
    "#BFEFEC",
    "#003057",
    "#B7DAFA",
    "#D2ECFE",
    "#9F2578",
    "#EEB7E7",
    "#FADDF6",
    "#DB551E",
    "#FDCCA8",
    "#FFE7D8",
    "#207A63",
    "#80B7A4",
    "#A4CCBE",
    "#6342FF",
    "#C2B3FF",
    "#D8CEFF",
    "#FFAC00",
    "#FBEA9B",
    "#FDF5CE",
    "#6F00A9",
    "#BA72D6",
    "#E4D0EF",
]

# =========================================================
# 3. Catálogo oficial de colores RGB por Tipo de Vialidad
# =========================================================
TIPO_COLOR_MAP = {
    "CALLE": "#C29DD4",
    "AVENIDA": "#A900E6",
    "BOULEVARD": "#FF73DF",
    "PROLONGACION": "#E600A9",
    "EJE VIAL": "#E600A9",
    "PERIFERICO": "#E600A9",
    "VIADUCTO": "#E600A9",
    "CIRCUITO": "#BEE8FF",
    "CALZADA": "#73B2FF",
    "PRIVADA": "#ABEBC6",
    "CERRADA": "#ABEBC6",
    "RETORNO": "#ABEBC6",
    "ANDADOR": "#FFFF00",
    "AMPLIACION": "#FFAA00",
    "CALLEJON": "#FFAA00",
    "CIRCUNVALACION": "#FFAA00",
    "CONTINUACION": "#FFAA00",
    "CORREDOR": "#FFAA00",
    "DIAGONAL": "#FFAA00",
    "PASAJE": "#FFAA00",
    "PEATONAL": "#FFAA00",
    "CARRETERA": "#FF0000",
    "ENLACE": "#4CE600",
    "RETORNO U": "#38A800",
    "GLORIETA": "#0070FF",
    "CAMINO": "#C88544",
    "VEREDA": "#000000",
    "RAMPA DE FRENADO": "#000000",
    "OTRO": "#ABABAB",
}


def normalizar(texto: str) -> str:
  texto = str(texto).strip().upper()
  texto = (
      unicodedata.normalize("NFKD", texto)
      .encode("ascii", "ignore")
      .decode("utf-8")
  )
  return " ".join(texto.split())


TIPO_COLOR_MAP_NORM = {normalizar(k): v for k, v in TIPO_COLOR_MAP.items()}


def construir_mapa_colores(tipos_unicos):
  mapa = {}
  respaldo = iter(PALETA_PIE)
  for tipo in tipos_unicos:
    clave = normalizar(tipo)
    if clave in TIPO_COLOR_MAP_NORM:
      mapa[tipo] = TIPO_COLOR_MAP_NORM[clave]
    else:
      mapa[tipo] = next(respaldo, COLOR_GRAY1)
  return mapa


# =========================================================
# 4. Estilos CSS Personalizados
# =========================================================
st.markdown(
    f"""
    <style>
    .stApp {{
        background-color: {COLOR_BG};
    }}
    .block-container {{
        padding-top: 1.2rem;
        padding-bottom: 2rem;
    }}
    
    /* Títulos y Subtítulos de las Secciones */
    h1 {{
        color: {COLOR_NAVY} !important;
        font-weight: 800;
    }}
    .seccion-titulo h2, .seccion-titulo h3, h2, h3, h4, h5 {{
        color: {COLOR_TEXT_SECTIONS} !important;
        font-weight: 700;
    }}
    
    .stCaption, [data-testid="stCaptionContainer"] {{
        color: {COLOR_BLUE} !important;
        font-size: 1.05em;
    }}

    /* Encabezado Banner con fondo degradado y silueta carretera 3D */
    .banner-ejecutivo {{
        background: linear-gradient(135deg, rgba(0, 48, 87, 0.92) 0%, rgba(8, 152, 156, 0.88) 100%),
                    url('https://images.unsplash.com/photo-1519817650390-64a93db51149?auto=format&fit=crop&w=1600&q=80');
        background-size: cover;
        background-position: center;
        padding: 28px 36px;
        border-radius: 16px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.18);
        margin-bottom: 18px;
    }}
    .banner-ejecutivo h1 {{
        color: #FFFFFF !important;
        margin-bottom: 4px;
        font-size: 2.1rem;
        text-shadow: 0 2px 4px rgba(0,0,0,0.3);
    }}
    .banner-ejecutivo h3 {{
        color: #80DFD9 !important;
        margin-top: 2px;
        margin-bottom: 4px;
        font-size: 1.3rem;
        font-weight: 600;
    }}
    .banner-ejecutivo p {{
        color: #E7F6F6;
        margin: 0;
        font-size: 1.05rem;
    }}

    /* Tarjetas de métricas (KPIs) con marco blanco y borde gris #989898 */
    [data-testid="stMetric"] {{
        background-color: {COLOR_CARD};
        border-radius: 12px;
        padding: 16px 12px;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
        border: 1px solid {COLOR_GRAY1} !important;
    }}
    [data-testid="stMetricValue"] {{
        color: {COLOR_NAVY} !important;
        font-weight: 800;
    }}
    [data-testid="stMetricLabel"] {{
        color: {COLOR_GRAY2} !important;
        font-weight: 600;
    }}
    [data-testid="stMetricDelta"] {{
        color: {COLOR_PRIMARY} !important;
    }}

    /* Enmarcar cada apartado/sección con fondo blanco y borde gris #989898 */
    [data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: {COLOR_CARD} !important;
        border-radius: 14px !important;
        border: 1px solid {COLOR_GRAY1} !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06) !important;
        padding: 12px !important;
    }}

    /* Ajuste de botones de colores de las pestañas al tamaño del texto */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        display: flex;
        flex-wrap: wrap;
    }}
    .stTabs [data-baseweb="tab"] {{
        background-color: {COLOR_CARD};
        border-radius: 8px;
        border: 1px solid {COLOR_GRAY1};
        padding: 6px 14px !important;
        font-weight: 600;
        color: {COLOR_TEXT_SECTIONS} !important;
        width: auto !important;
        min-width: unset !important;
        flex-grow: 0 !important;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {COLOR_PRIMARY} !important;
        color: #FFFFFF !important;
        border-color: {COLOR_PRIMARY} !important;
    }}

    /* Tablas personalizadas con fondo blanco y texto #3C3C3B */
    [data-testid="stTable"], .stDataFrame, div[data-testid="stTable"] table {{
        background-color: #FFFFFF !important;
        color: {COLOR_TEXT_SECTIONS} !important;
    }}
    [data-testid="stTable"] td, [data-testid="stTable"] th, .stDataFrame td, .stDataFrame th {{
        color: {COLOR_TEXT_SECTIONS} !important;
        border-color: #E0E0E0 !important;
    }}

    /* Botones y descargas */
    .stDownloadButton button, .stButton button {{
        background-color: {COLOR_PRIMARY};
        color: #FFFFFF;
        border-radius: 8px;
        border: none;
        font-weight: 600;
        padding: 0.5em 1.1em;
    }}
    .stDownloadButton button:hover, .stButton button:hover {{
        background-color: {COLOR_NAVY};
        color: #FFFFFF;
    }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background-color: {COLOR_NAVY};
    }}
    [data-testid="stSidebar"] * {{
        color: #F2F2F2 !important;
    }}
    [data-testid="stSidebar"] .stButton button,
    [data-testid="stSidebar"] .stDownloadButton button {{
        background-color: {COLOR_PRIMARY};
        color: #FFFFFF !important;
        width: 100%;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# 5. Funciones auxiliares de descarga y gráficos Plotly
# =========================================================
def df_a_csv_bytes(df: pd.DataFrame) -> bytes:
  return df.to_csv(index=False).encode("utf-8-sig")


def generar_reporte_excel(
    long_total,
    num_municipios,
    num_tipos_via,
    promedio_muni,
    muni_grp,
    tipo_grp,
    pivot_df,
) -> bytes:
  buffer = io.BytesIO()
  with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
    resumen = pd.DataFrame({
        "Indicador": [
            "Longitud total de la red (km)",
            "Número de municipios",
            "Número de tipos de vialidad",
            "Promedio por municipio (km)",
        ],
        "Valor": [
            round(long_total, 2),
            num_municipios,
            num_tipos_via,
            round(promedio_muni, 2),
        ],
    })
    resumen.to_excel(writer, sheet_name="Resumen", index=False)
    muni_grp.to_excel(writer, sheet_name="Ranking Municipios", index=False)
    tipo_grp.to_excel(writer, sheet_name="Estructura por Tipo", index=False)
    pivot_df.to_excel(writer, sheet_name="Matriz Municipio-Tipo")
  return buffer.getvalue()


def aplicar_estilo_grafico_blanco(fig):
  """Fuerza que el gráfico tenga fondo blanco, borde gris #989898 y fuente #3C3C3B."""
  fig.update_layout(
      paper_bgcolor="#FFFFFF",
      plot_bgcolor="#FFFFFF",
      font=dict(color=COLOR_TEXT_SECTIONS, family="Arial, sans-serif"),
      title_font_color=COLOR_NAVY,
      legend=dict(font=dict(color=COLOR_TEXT_SECTIONS)),
      xaxis=dict(
          gridcolor="#E5E5E5",
          zerolinecolor="#CCCCCC",
          tickfont=dict(color=COLOR_TEXT_SECTIONS),
          title=dict(font=dict(color=COLOR_TEXT_SECTIONS)),
      ),
      yaxis=dict(
          gridcolor="#E5E5E5",
          zerolinecolor="#CCCCCC",
          tickfont=dict(color=COLOR_TEXT_SECTIONS),
          title=dict(font=dict(color=COLOR_TEXT_SECTIONS)),
      ),
      shapes=[
          dict(
              type="rect",
              xref="paper",
              yref="paper",
              x0=0,
              y0=0,
              x1=1,
              y1=1,
              line=dict(color=COLOR_GRAY1, width=1),
          )
      ],
  )
  return fig


def boton_descarga_grafico(fig, nombre_archivo, key):
  try:
    fig_export = aplicar_estilo_grafico_blanco(fig)
    img_bytes = fig_export.to_image(format="png", scale=2)
    st.download_button(
        "🖼️ Descargar gráfico (PNG)",
        data=img_bytes,
        file_name=nombre_archivo,
        mime="image/png",
        key=key,
        use_container_width=True,
    )
  except Exception:
    st.caption(
        "💡 Puedes descargar el gráfico directamente usando el ícono de cámara 📷"
        " en la esquina superior derecha del gráfico."
    )


CONFIG_PLOTLY = {
    "displaylogo": False,
    "displayModeBar": True,
    "toImageButtonOptions": {
        "format": "png",
        "scale": 2,
        "filename": "Grafico_Red_Vial",
    },
}


# =========================================================
# 6. Carga de datos compatible con ejecutable PyInstaller
# =========================================================
@st.cache_data
def cargar_datos():
  if getattr(sys, "frozen", False):
    ruta_base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
  else:
    ruta_base = os.path.dirname(os.path.abspath(__file__))

  nombres_archivos = [
      os.path.join(ruta_base, "Resumen_Municipal_Vialidades.xlsx"),
      os.path.join(ruta_base, "Resumen_Municipal_Vialidades.csv"),
      "Resumen_Municipal_Vialidades.xlsx",
      "Resumen_Municipal_Vialidades.csv",
  ]

  archivo_encontrado = next(
      (f for f in nombres_archivos if os.path.exists(f)), None
  )

  if not archivo_encontrado:
    return None

  if archivo_encontrado.endswith(".xlsx"):
    df_datos = pd.read_excel(archivo_encontrado)
  else:
    df_datos = pd.read_csv(archivo_encontrado)

  df_datos.columns = [str(col).strip() for col in df_datos.columns]

  col_muni = next(
      (
          c
          for c in df_datos.columns
          if c.upper().replace(" ", "_")
          in ["NOMGEO", "MUNICIPIO", "NOM_MUN", "NOM_MUNICIPIO", "NOMBRE_MUNICIPIO"]
      ),
      df_datos.columns[0],
  )
  col_tipo = next(
      (
          c
          for c in df_datos.columns
          if c.upper().replace(" ", "_")
          in ["TIPO_VIA", "TIPO_VIALIDAD", "TIPO_DE_VIALIDAD", "TIPOVIA", "TIPO"]
      ),
      df_datos.columns[1],
  )
  col_km = next(
      (
          c
          for c in df_datos.columns
          if c.upper().replace(" ", "_")
          in [
              "LONG_KM",
              "LONGITUD",
              "KM",
              "LONGITUD_KM",
              "LONGITUD_(KM)",
              "KM_TOTAL",
          ]
      ),
      df_datos.columns[-1],
  )

  df_datos = df_datos.rename(
      columns={col_muni: "NOMGEO", col_tipo: "TIPO_VIA", col_km: "LONG_KM"}
  )
  df_datos["LONG_KM"] = pd.to_numeric(
      df_datos["LONG_KM"], errors="coerce"
  ).fillna(0)

  return df_datos


df_raw = cargar_datos()

if df_raw is None:
  st.error(
      "❌ No se encontró el archivo de datos ('Resumen_Municipal_Vialidades.xlsx'"
      " o '.csv'). Asegúrate de situarlo en la misma carpeta del ejecutable."
  )
  st.stop()

# =========================================================
# 7. Barra lateral
# =========================================================
with st.sidebar:
  st.markdown("## 🛣️ Panel de Control")
  st.caption("Filtra la información y exporta reportes ejecutivos.")

  if st.button("🔄 Recargar datos", use_container_width=True):
    st.cache_data.clear()
    st.rerun()

  st.markdown("---")
  st.markdown("### 🎛️ Filtros")
  tipos_disponibles = sorted(df_raw["TIPO_VIA"].dropna().unique().tolist())
  tipos_seleccionados = st.multiselect(
      "Tipos de vialidad a incluir:",
      options=tipos_disponibles,
      default=tipos_disponibles,
  )

  st.markdown("---")
  st.markdown("### ℹ️ Acerca de")
  st.caption(
      "Departamento de Información Temática | Equipo Red Nacional de Caminos"
      " Chiapas | Subdirección Estatal de Geografía y Medio Ambiente | INEGI"
  )
  st.caption("Fuente: GDB de la RNC, versión julio 2026.")

if tipos_seleccionados:
  df = df_raw[df_raw["TIPO_VIA"].isin(tipos_seleccionados)].copy()
else:
  df = df_raw.copy()

if df.empty:
  st.warning(
      "No hay datos para los filtros seleccionados. Ajusta la selección en la"
      " barra lateral."
  )
  st.stop()

MAPA_COLORES_TIPO = construir_mapa_colores(
    sorted(df["TIPO_VIA"].dropna().unique().tolist())
)

# =========================================================
# 8. Encabezado ejecutivo
# =========================================================
st.markdown(
    """
    <div class="banner-ejecutivo">
        <h1>PANORAMA ESTATAL DE VIALIDADES DE LA RNC 2026</h1>
        <h3>Infraestructura Red Vial de Chiapas</h3>
        <p>Análisis ejecutivo de extensión en kilómetros por municipio y tipo de vialidad</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# 9. KPIs principales
# =========================================================
long_total = df["LONG_KM"].sum()
num_municipios = df["NOMGEO"].nunique()
num_tipos_via = df["TIPO_VIA"].nunique()
promedio_muni = long_total / num_municipios if num_municipios > 0 else 0

muni_grp = (
    df.groupby("NOMGEO")["LONG_KM"]
    .sum()
    .reset_index()
    .sort_values(by="LONG_KM", ascending=False)
    .reset_index(drop=True)
)

tipo_grp = (
    df.groupby("TIPO_VIA")["LONG_KM"]
    .sum()
    .reset_index()
    .sort_values(by="LONG_KM", ascending=False)
    .reset_index(drop=True)
)

muni_lider = muni_grp.iloc[0]
lider_pct = (muni_lider["LONG_KM"] / long_total) * 100 if long_total > 0 else 0

tipo_pred = tipo_grp.iloc[0]
tipo_pct = (tipo_pred["LONG_KM"] / long_total) * 100 if long_total > 0 else 0

with st.container(border=True):
  col1, col2, col3, col4, col5, col6 = st.columns(6)
  col1.metric("Longitud total de la red", f"{long_total:,.1f} km")
  col2.metric("Municipios", f"{num_municipios}")
  col3.metric("Tipos de Vialidad", f"{num_tipos_via}")
  col4.metric("Promedio / Mpio", f"{promedio_muni:,.1f} km")
  col5.metric(
      "Municipio Líder",
      f"{muni_lider['NOMGEO']}",
      delta=f"{muni_lider['LONG_KM']:,.1f} km ({lider_pct:.1f}%)",
  )
  col6.metric(
      "Vialidad Predominante",
      f"{tipo_pred['TIPO_VIA']}",
      delta=f"{tipo_pred['LONG_KM']:,.1f} km ({tipo_pct:.1f}%)",
  )

  st.download_button(
      "⬇️ Descargar Reporte Ejecutivo Completo (Excel)",
      data=generar_reporte_excel(
          long_total,
          num_municipios,
          num_tipos_via,
          promedio_muni,
          muni_grp,
          tipo_grp,
          df.pivot_table(
              index="NOMGEO",
              columns="TIPO_VIA",
              values="LONG_KM",
              aggfunc="sum",
          ).fillna(0),
      ),
      file_name="Reporte_Ejecutivo_RNC_Chiapas.xlsx",
      mime=(
          "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
      ),
  )

st.write("")

# =========================================================
# 10. Contenido organizado en pestañas ejecutivas
# =========================================================
tab_consulta, tab_ranking, tab_estructura, tab_matriz = st.tabs([
    "🔍 Consulta Municipal",
    "🏆 Ranking de Municipios",
    "🌐 Estructura de la Red",
    "📋 Matriz de Datos",
])

# ---------------------------------------------------------
# TAB 1 · Consulta Municipal
# ---------------------------------------------------------
with tab_consulta:
  with st.container(border=True):
    st.subheader("🔍 Consulta Municipal")
    municipio_sel = st.selectbox(
        "Selecciona o escribe el nombre de un municipio:",
        sorted(df["NOMGEO"].unique()),
    )

    df_muni = df[df["NOMGEO"] == municipio_sel].sort_values(
        by="LONG_KM", ascending=False
    )
    total_muni = df_muni["LONG_KM"].sum()
    pct_muni = (total_muni / long_total) * 100 if long_total > 0 else 0

    rank_muni = (
        muni_grp[muni_grp["NOMGEO"] == municipio_sel].index[0] + 1
        if municipio_sel in muni_grp["NOMGEO"].values
        else "-"
    )

    pred_muni_row = df_muni.iloc[0] if not df_muni.empty else None
    pred_muni_nombre = (
        pred_muni_row["TIPO_VIA"] if pred_muni_row is not None else "-"
    )

    col_muni_tabla, col_muni_graf = st.columns([1, 1])

    with col_muni_tabla:
      tabla_muni_data = pd.DataFrame({
          "Indicador": [
              "Ranking Estatal",
              "Longitud Total del Municipio",
              "Participación en la Red Estatal",
              "Tipo de Vialidad Predominante",
          ],
          "Valor": [
              f"#{rank_muni}",
              f"{total_muni:,.2f} km",
              f"{pct_muni:.2f}%",
              f"{pred_muni_nombre}",
          ],
      })
      st.markdown(f"**Detalle General: {municipio_sel}**")
      st.table(tabla_muni_data)
      st.download_button(
          "⬇️ Descargar detalle (CSV)",
          data=df_a_csv_bytes(df_muni[["NOMGEO", "TIPO_VIA", "LONG_KM"]]),
          file_name=f"Detalle_{municipio_sel}.csv",
          mime="text/csv",
          key="dl_detalle_muni",
          use_container_width=True,
      )

    with col_muni_graf:
      fig_pie = px.pie(
          df_muni,
          values="LONG_KM",
          names="TIPO_VIA",
          title=f"Composición Vial de {municipio_sel}",
          hole=0.45,
          color="TIPO_VIA",
          color_discrete_map=MAPA_COLORES_TIPO,
      )
      fig_pie.update_traces(
          textinfo="percent+label",
          textfont_size=12,
          hovertemplate=(
              "<b>%{label}</b><br>%{value:,.2f} km<br>%{percent}<extra></extra>"
          ),
      )
      fig_pie.update_layout(
          height=340,
          margin=dict(l=10, r=10, t=50, b=10),
          legend=dict(orientation="h", yanchor="bottom", y=-0.25),
      )
      fig_pie = aplicar_estilo_grafico_blanco(fig_pie)
      st.plotly_chart(fig_pie, use_container_width=True, config=CONFIG_PLOTLY)
      boton_descarga_grafico(
          fig_pie, f"Composicion_{municipio_sel}.png", key="png_pie_muni"
      )

# ---------------------------------------------------------
# TAB 2 · Ranking de Municipios
# ---------------------------------------------------------
with tab_ranking:
  with st.container(border=True):
    st.subheader("🏆 Ranking de Municipios")

    col_f1, col_f2 = st.columns([2, 1])
    with col_f1:
      muni_filtro = st.multiselect(
          "Filtrar municipios específicos:",
          options=muni_grp["NOMGEO"].tolist(),
          default=[],
          placeholder="Deja vacío para usar el Top N por defecto",
      )
    with col_f2:
      top_n = st.number_input(
          "Mostrar Top N",
          min_value=5,
          max_value=int(num_municipios),
          value=min(15, int(num_municipios)),
          step=5,
      )

    if muni_filtro:
      df_ranking = muni_grp[muni_grp["NOMGEO"].isin(muni_filtro)].sort_values(
          by="LONG_KM", ascending=False
      )
    else:
      df_ranking = muni_grp.head(int(top_n))

    fig_ranking = px.bar(
        df_ranking,
        x="LONG_KM",
        y="NOMGEO",
        orientation="h",
        labels={"LONG_KM": "Longitud (km)", "NOMGEO": "Municipio"},
        text="LONG_KM",
    )
    fig_ranking.update_traces(
        marker_color=COLOR_PRIMARY,
        texttemplate="%{text:,.1f} km",
        textposition="outside",
        textfont_size=11,
        hovertemplate="<b>%{y}</b><br>%{x:,.2f} km<extra></extra>",
        cliponaxis=False,
    )
    fig_ranking.update_layout(
        yaxis={"categoryorder": "total ascending"},
        showlegend=False,
        height=max(320, len(df_ranking) * 24),
        bargap=0.25,
        margin=dict(l=10, r=60, t=20, b=10),
        font=dict(size=12),
    )
    fig_ranking = aplicar_estilo_grafico_blanco(fig_ranking)
    st.plotly_chart(
        fig_ranking, use_container_width=True, config=CONFIG_PLOTLY
    )

    col_dl1, col_dl2 = st.columns(2)
    with col_dl1:
      st.download_button(
          "⬇️ Descargar ranking (CSV)",
          data=df_a_csv_bytes(df_ranking),
          file_name="Ranking_Municipios.csv",
          mime="text/csv",
          key="dl_ranking_csv",
          use_container_width=True,
      )
    with col_dl2:
      boton_descarga_grafico(
          fig_ranking, "Ranking_Municipios.png", key="png_ranking"
      )

# ---------------------------------------------------------
# TAB 3 · Estructura de la Red
# ---------------------------------------------------------
with tab_estructura:
  with st.container(border=True):
    st.subheader("🌐 Estructura de la Red")
    col_est_izq, col_est_der = st.columns([1, 1])

    with col_est_izq:
      st.markdown("##### Distribución por tipo de vialidad")
      fig_est = px.bar(
          tipo_grp,
          x="LONG_KM",
          y="TIPO_VIA",
          orientation="h",
          labels={"LONG_KM": "Longitud (km)", "TIPO_VIA": "Tipo de Vialidad"},
          text="LONG_KM",
          color="TIPO_VIA",
          color_discrete_map=MAPA_COLORES_TIPO,
      )
      fig_est.update_traces(
          texttemplate="%{text:,.1f} km",
          textposition="outside",
          textfont_size=11,
          hovertemplate="<b>%{y}</b><br>%{x:,.2f} km<extra></extra>",
          cliponaxis=False,
      )
      fig_est.update_layout(
          yaxis={"categoryorder": "total ascending"},
          showlegend=False,
          height=650,
          margin=dict(l=10, r=70, t=20, b=10),
          font=dict(size=12),
          uniformtext_minsize=9,
          uniformtext_mode="hide",
      )
      fig_est = aplicar_estilo_grafico_blanco(fig_est)
      st.plotly_chart(fig_est, use_container_width=True, config=CONFIG_PLOTLY)
      boton_descarga_grafico(
          fig_est, "Estructura_Red_por_Tipo.png", key="png_estructura"
      )

    with col_est_der:
      st.markdown("##### Detalle por tipo de vialidad")
      tipo_grp_top25 = tipo_grp.head(25).copy()
      tipo_grp_top25["% Participación"] = (
          tipo_grp_top25["LONG_KM"] / long_total
      ) * 100
      tipo_grp_top25.insert(0, "N°", range(1, len(tipo_grp_top25) + 1))
      tipo_grp_top25 = tipo_grp_top25.rename(
          columns={"TIPO_VIA": "Tipo de Vialidad", "LONG_KM": "KM"}
      )

      st.dataframe(
          tipo_grp_top25.style.format(
              {"KM": "{:,.2f}", "% Participación": "{:.2f}%"}
          ),
          use_container_width=True,
          hide_index=True,
          height=555,
      )
      st.download_button(
          "⬇️ Descargar tabla (CSV)",
          data=df_a_csv_bytes(tipo_grp_top25),
          file_name="Estructura_por_Tipo.csv",
          mime="text/csv",
          key="dl_estructura_csv",
          use_container_width=True,
      )

# ---------------------------------------------------------
# TAB 4 · Matriz de Datos
# ---------------------------------------------------------
with tab_matriz:
  with st.container(border=True):
    st.subheader("📋 Matriz de Datos")
    st.markdown("Longitudes acumuladas por municipio y tipo de vialidad (km):")

    pivot_df = df.pivot_table(
        index="NOMGEO", columns="TIPO_VIA", values="LONG_KM", aggfunc="sum"
    ).fillna(0)
    pivot_df["Total (km)"] = pivot_df.sum(axis=1)
    pivot_df = pivot_df.sort_values(by="Total (km)", ascending=False)

    st.dataframe(
        pivot_df.style.format("{:,.1f}"),
        use_container_width=True,
        height=500,
    )

    col_m1, col_m2 = st.columns(2)
    with col_m1:
      st.download_button(
          "⬇️ Descargar matriz (CSV)",
          data=df_a_csv_bytes(pivot_df.reset_index()),
          file_name="Matriz_Municipio_Tipo.csv",
          mime="text/csv",
          key="dl_matriz_csv",
          use_container_width=True,
      )
    with col_m2:
      buffer_xlsx = io.BytesIO()
      with pd.ExcelWriter(buffer_xlsx, engine="openpyxl") as writer:
        pivot_df.to_excel(writer, sheet_name="Matriz")
      st.download_button(
          "⬇️ Descargar matriz (Excel)",
          data=buffer_xlsx.getvalue(),
          file_name="Matriz_Municipio_Tipo.xlsx",
          mime=(
              "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
          ),
          key="dl_matriz_xlsx",
          use_container_width=True,
      )

# =========================================================
# 11. Pie de página y créditos
# =========================================================
st.markdown("---")
st.markdown(
    f"""
    <div style="text-align: center; color: {COLOR_GRAY2}; font-size: 0.9em;">
        <b>Departamento de Información Temática | Equipo Red Nacional de Caminos Chiapas | Subdirección Estatal de Geografía y Medio Ambiente | INEGI</b><br>
        <i>Fuente: Datos extraídos de la GDB de la RNC versión julio, 2026.</i>
    </div>
    """,
    unsafe_allow_html=True,
)