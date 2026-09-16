import streamlit as st
from gtts import gTTS
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import io
import os

# 1. Configuración a pantalla completa
st.set_page_config(page_title="Lector Accesible", layout="wide", initial_sidebar_state="collapsed")

# 2. CSS para crear las ZONAS GIGANTES
# Transformamos los botones estándar de Streamlit en bloques masivos que ocupan media pantalla
st.markdown("""
    <style>
        /* Ocultar elementos visuales innecesarios de Streamlit para limpiar la pantalla */
        header {visibility: hidden;}
        footer {visibility: hidden;}
        
        /* Estilos para las dos grandes zonas táctiles */
        div.stButton > button {
            height: 60vh !important;
            width: 100% !important;
            font-size: 2rem !important;
            font-weight: bold !important;
            border-radius: 15px !important;
            background-color: #1f2937 !important;
            color: #ffffff !important;
            border: 2px solid #374151 !important;
        }
        div.stButton > button:active {
            background-color: #374151 !important;
        }
    </style>
""", unsafe_allow_html=True)

# 3. Inicializar variables de sesión para recordar dónde vamos en el libro
if 'parrafos' not in st.session_state:
    st.session_state.parrafos = []
if 'indice_actual' not in st.session_state:
    st.session_state.indice_actual = 0

# --- LÓGICA DE INTERFAZ ---

if not st.session_state.parrafos:
    st.title("Lector Accesible (Modo Gestual)")
    archivo_subido = st.file_uploader("Carga tu libro EPUB aquí", type=["epub"])
    
    if archivo_subido is not None:
        with st.spinner("Procesando libro..."):
            with open("temp.epub", "wb") as f:
                f.write(archivo_subido.getvalue())
            
            libro = epub.read_epub("temp.epub")
            capitulos = list(libro.get_items_of_type(ebooklib.ITEM_DOCUMENT))
            
            # Extraer capítulo 2 (suele ser el primer texto real)
            if len(capitulos) > 1:
                sopa = BeautifulSoup(capitulos[1].get_content(), 'html.parser')
                
                # Dividir por párrafos reales (<p>)
                textos = sopa.find_all('p')
                for p in textos:
                    texto_limpio = p.get_text(separator=' ', strip=True)
                    if len(texto_limpio) > 20: # Ignorar párrafos vacíos
                        st.session_state.parrafos.append(texto_limpio)
                
            os.remove("temp.epub")
            st.rerun() # Recargar la app para mostrar las zonas
else:
    # --- PANTALLA DE ZONAS (Para el usuario ciego) ---
    st.write(f"Leyendo fragmento {st.session_state.indice_actual + 1} de {len(st.session_state.parrafos)}")
    
    # Dividimos la pantalla en dos columnas exactas
    col_izq, col_der = st.columns(2)
    
    with col_izq:
        if st.button("⬅️ ANTERIOR"):
            if st.session_state.indice_actual > 0:
                st.session_state.indice_actual -= 1

    with col_der:
        if st.button("SIGUIENTE ➡️"):
            if st.session_state.indice_actual < len(st.session_state.parrafos) - 1:
                st.session_state.indice_actual += 1

    # --- MOTOR DE AUDIO gTTS AUTOMÁTICO ---
    texto_a_leer = st.session_state.parrafos[st.session_state.indice_actual]
    
    # Generar el audio de ese párrafo
    tts = gTTS(text=texto_a_leer, lang='es')
    audio_fp = io.BytesIO()
    tts.write_to_fp(audio_fp)
    audio_fp.seek(0)
    
    # Reproducir inmediatamente (autoplay=True es el equivalente sonoro a la confirmación del toque)
    st.audio(audio_fp, format="audio/mp3", autoplay=True)
