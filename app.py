import streamlit as st
from gtts import gTTS
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import io
import os
import streamlit.components.v1 as components

st.set_page_config(page_title="Lector Multimodal", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
        header {visibility: hidden;}
        footer {visibility: hidden;}
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
        div.stButton > button:active { background-color: #374151 !important; }
    </style>
""", unsafe_allow_html=True)

if 'parrafos' not in st.session_state:
    st.session_state.parrafos = []
if 'indice_actual' not in st.session_state:
    st.session_state.indice_actual = 0
if 'accion_fisica' not in st.session_state:
    st.session_state.accion_fisica = None

if not st.session_state.parrafos:
    st.title("Lector Accesible")
    archivo_subido = st.file_uploader("Carga tu libro EPUB aquí", type=["epub"])
    
    if archivo_subido is not None:
        with st.spinner("Procesando libro..."):
            with open("temp.epub", "wb") as f:
                f.write(archivo_subido.getvalue())
            
            libro = epub.read_epub("temp.epub")
            capitulos = list(libro.get_items_of_type(ebooklib.ITEM_DOCUMENT))
            
            if len(capitulos) > 1:
                sopa = BeautifulSoup(capitulos[1].get_content(), 'html.parser')
                textos = sopa.find_all('p')
                for p in textos:
                    texto_limpio = p.get_text(separator=' ', strip=True)
                    if len(texto_limpio) > 20:
                        st.session_state.parrafos.append(texto_limpio)
                
            os.remove("temp.epub")
            st.rerun()
else:
    st.write(f"Leyendo fragmento {st.session_state.indice_actual + 1} de {len(st.session_state.parrafos)}")
    
    col_izq, col_der = st.columns(2)
    
    with col_izq:
        if st.button("⬅️ ANTERIOR"):
            if st.session_state.indice_actual > 0:
                st.session_state.indice_actual -= 1
                st.session_state.accion_fisica = "anterior"

    with col_der:
        if st.button("SIGUIENTE ➡️"):
            if st.session_state.indice_actual < len(st.session_state.parrafos) - 1:
                st.session_state.indice_actual += 1
                st.session_state.accion_fisica = "siguiente"

    # --- INYECCIÓN DE RESPUESTA FÍSICA Y SONORA ---
    if st.session_state.accion_fisica:
        # JavaScript para vibración y osciladores de sonido nativos
        js_code = f"""
        <script>
            const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            
            if ("{st.session_state.accion_fisica}" === "siguiente") {{
                window.navigator.vibrate(100); // Vibración corta
                osc.type = 'triangle';
                osc.frequency.setValueAtTime(600, audioCtx.currentTime); // Tono agudo
            }} else {{
                window.navigator.vibrate([100, 50, 100]); // Doble vibración
                osc.type = 'sine';
                osc.frequency.setValueAtTime(300, audioCtx.currentTime); // Tono grave
            }}
            
            gain.gain.setValueAtTime(0.5, audioCtx.currentTime);
            gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.2);
            osc.start();
            osc.stop(audioCtx.currentTime + 0.2);
        </script>
        """
        components.html(js_code, height=0, width=0)
        st.session_state.accion_fisica = None # Reiniciamos el estado

    # --- MOTOR DE AUDIO ---
    texto_a_leer = st.session_state.parrafos[st.session_state.indice_actual]
    tts = gTTS(text=texto_a_leer, lang='es')
    audio_fp = io.BytesIO()
    tts.write_to_fp(audio_fp)
    audio_fp.seek(0)
    st.audio(audio_fp, format="audio/mp3", autoplay=True)
