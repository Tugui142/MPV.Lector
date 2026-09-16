import streamlit as st
from gtts import gTTS
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
import io
import os

# Configuración de la página
st.set_page_config(page_title="Lector Accesible", layout="centered")

st.title("Lector de Libros Accesible")
st.write("Sube tu archivo EPUB para escucharlo en voz alta.")

# 1. Cargar el archivo
archivo_subido = st.file_uploader("Selecciona un archivo .epub", type=["epub"])

if archivo_subido is not None:
    # Guardar el archivo temporalmente (EbookLib requiere leer desde una ruta física)
    with open("temp.epub", "wb") as f:
        f.write(archivo_subido.getvalue())
    
    # 2. Leer el EPUB
    libro = epub.read_epub("temp.epub")
    
    # Extraer los documentos (capítulos) del libro
    capitulos = list(libro.get_items_of_type(ebooklib.ITEM_DOCUMENT))
    
    if len(capitulos) > 1:
        # Usamos el índice 1 o 2 para evitar extraer la portada vacía
        capitulo_actual = capitulos[1]
        
        # 3. Limpiar el HTML para obtener texto puro
        sopa = BeautifulSoup(capitulo_actual.get_content(), 'html.parser')
        texto_puro = sopa.get_text(separator=' ', strip=True)
        
        if texto_puro:
            st.success("¡Capítulo cargado correctamente!")
            
            # Mostrar un fragmento del texto (opcional, para debug)
            with st.expander("Ver texto extraído"):
                st.write(texto_puro[:1000] + "...")
            
            st.markdown("---")
            
            # 4. Botón para generar y reproducir la voz
            if st.button("▶ Generar Audio del Capítulo", use_container_width=True):
                with st.spinner("Procesando la voz con gTTS..."):
                    # Cortamos el texto para la prueba (gTTS puede tardar mucho con un capítulo entero)
                    texto_prueba = texto_puro[:1000]
                    
                    tts = gTTS(text=texto_prueba, lang='es')
                    
                    # Guardar el audio en memoria
                    audio_fp = io.BytesIO()
                    tts.write_to_fp(audio_fp)
                    audio_fp.seek(0)
                    
                    # 5. Reproductor nativo de Streamlit
                    st.audio(audio_fp, format="audio/mp3")
        else:
            st.error("No se encontró texto en este capítulo.")
    
    # Limpiar el archivo temporal
    os.remove("temp.epub")
