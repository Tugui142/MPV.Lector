from fastapi import FastAPI
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from gtts import gTTS
import io

app = FastAPI()

# Configurar CORS para permitir que tu frontend en GitHub Pages se conecte a esta API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción, cambia "*" por tu URL de GitHub Pages
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/generar-audio/")
async def generar_audio(texto: dict):
    # Extraer el texto de la petición
    contenido = texto.get("texto", "")
    
    if not contenido:
        return {"error": "No se envió texto"}

    # Generar el audio con gTTS en español
    tts = gTTS(text=contenido, lang='es')
    
    # Guardar el audio en memoria en lugar de crear un archivo físico
    mp3_fp = io.BytesIO()
    tts.write_to_fp(mp3_fp)
    mp3_fp.seek(0)
    
    # Devolver el archivo de audio directamente
    return Response(content=mp3_fp.read(), media_type="audio/mpeg")
