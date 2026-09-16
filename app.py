import streamlit as st
import numpy as np
from PIL import Image
import io
import cv2
from gtts import gTTS
import time

# Configuración de la página
st.set_page_config(page_title="Asistente Espacial", layout="centered")

# Diccionario rápido para traducir las etiquetas más comunes de YOLO al español
TRADUCCIONES = {
    "person": "persona", "bicycle": "bicicleta", "car": "carro", "motorcycle": "motocicleta",
    "airplane": "avión", "bus": "bus", "train": "tren", "truck": "camión", "boat": "bote",
    "traffic light": "semáforo", "fire hydrant": "hidrante", "stop sign": "señal de pare",
    "bench": "banca", "bird": "pájaro", "cat": "gato", "dog": "perro", "horse": "caballo",
    "sheep": "oveja", "cow": "vaca", "elephant": "elefante", "bear": "oso", "zebra": "cebra",
    "giraffe": "jirafa", "backpack": "mochila", "umbrella": "paraguas", "handbag": "bolso",
    "tie": "corbata", "suitcase": "maleta", "frisbee": "disco volador", "skis": "esquís",
    "snowboard": "tabla de nieve", "sports ball": "balón", "kite": "cometa",
    "baseball bat": "bate", "baseball glove": "guante", "skateboard": "patineta",
    "surfboard": "tabla de surf", "tennis racket": "raqueta", "bottle": "botella",
    "wine glass": "copa", "cup": "taza", "fork": "tenedor", "knife": "cuchillo",
    "spoon": "cuchara", "bowl": "tazón", "banana": "banano", "apple": "manzana",
    "sandwich": "sándwich", "orange": "naranja", "broccoli": "brócoli", "carrot": "zanahoria",
    "hot dog": "perro caliente", "pizza": "pizza", "donut": "dona", "cake": "pastel",
    "chair": "silla", "couch": "sofá", "potted plant": "planta", "bed": "cama",
    "dining table": "mesa", "toilet": "inodoro", "tv": "televisor", "laptop": "portátil",
    "mouse": "mouse", "remote": "control remoto", "keyboard": "teclado", "cell phone": "celular",
    "microwave": "microondas", "oven": "horno", "toaster": "tostadora", "sink": "lavamanos",
    "refrigerator": "nevera", "book": "libro", "clock": "reloj", "vase": "jarrón",
    "scissors": "tijeras", "teddy bear": "oso de peluche", "hair drier": "secador de pelo",
    "toothbrush": "cepillo de dientes"
}

@st.cache_resource
def load_model():
    from ultralytics import YOLO
    # Usamos el modelo nano (su) que es más rápido para prototipos web
    model = YOLO("yolov5su.pt")
    return model

st.title("👁️ Radar Espacial Sonoro")
st.write("Apunta la cámara. La aplicación detectará los objetos y te dirá en voz alta si están a tu izquierda, centro o derecha.")

with st.spinner("Cargando inteligencia artificial..."):
    model = load_model()

# Captura de imagen nativa de Streamlit
picture = st.camera_input("Toca aquí para escanear el entorno")

if picture and model:
    st.info("Procesando entorno...")
    
    # 1. Convertir la imagen para OpenCV/YOLO
    pil_img = Image.open(io.BytesIO(picture.getvalue())).convert("RGB")
    np_img  = np.array(pil_img)[..., ::-1] # RGB a BGR
    img_h, img_w, _ = np_img.shape
    
    # 2. Hacer la inferencia (confianza del 40% para evitar falsos positivos)
    results = model(np_img, conf=0.40)
    boxes = results[0].boxes
    
    if boxes is not None and len(boxes) > 0:
        descripciones = []
        
        # 3. Analizar la ubicación de cada objeto detectado
        for box in boxes:
            cat = int(box.cls.item())
            label_ingles = model.names[cat]
            label_espanol = TRADUCCIONES.get(label_ingles, label_ingles)
            
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            x_center = (x1 + x2) / 2
            
            # Lógica espacial
            if x_center < img_w / 3:
                ubicacion = "a la izquierda"
            elif x_center > (img_w / 3) * 2:
                ubicacion = "a la derecha"
            else:
                ubicacion = "al centro"
                
            descripciones.append(f"{label_espanol} {ubicacion}")
        
        # 4. Unir todas las descripciones en una sola frase
        texto_final = "Frente a ti hay: " + ", ".join(descripciones) + "."
        st.success(texto_final)
        
        # 5. Convertir el texto a voz y reproducirlo automáticamente
        with st.spinner("Generando audio..."):
            tts = gTTS(text=texto_final, lang='es')
            audio_fp = io.BytesIO()
            tts.write_to_fp(audio_fp)
            audio_fp.seek(0)
            
            # autoplay=True es vital para la accesibilidad
            st.audio(audio_fp, format="audio/mp3", autoplay=True)
            
    else:
        # Si no detecta nada, también debe informarlo por voz
        texto_vacio = "No detecté ningún objeto con claridad."
        st.warning(texto_vacio)
        tts = gTTS(text=texto_vacio, lang='es')
        audio_fp = io.BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)
        st.audio(audio_fp, format="audio/mp3", autoplay=True)
