const uploadInput = document.getElementById('epub-upload');
const btnCargar = document.getElementById('btn-cargar');
const btnPlay = document.getElementById('btn-play');
const btnPausa = document.getElementById('btn-pausa');
const statusDiv = document.getElementById('status');

let book;
let rendition;
let currentText = "";
const synth = window.speechSynthesis;
let utterance;

// 1. Manejar la carga del archivo EPUB
uploadInput.addEventListener('change', function(e) {
    if (e.target.files.length === 0) return;
    
    const file = e.target.files[0];
    statusDiv.innerText = `Procesando: ${file.name}...`;
    
    // Leer el archivo localmente con epub.js
    const reader = new FileReader();
    reader.onload = function(event) {
        book = ePub(event.target.result);
        
        book.ready.then(() => {
            statusDiv.innerText = "Libro listo. Toca 'Reproducir'.";
            btnCargar.style.display = 'none';
            btnPlay.style.display = 'flex';
            btnPausa.style.display = 'flex';
            
            // Extraer el texto del primer capítulo/sección
            extraerTextoActual();
        });
    };
    reader.readAsArrayBuffer(file);
});

// 2. Extraer texto del EPUB
async function extraerTextoActual() {
    // Esto es un acercamiento básico: extrae el texto del lomo principal del libro
    const spine = await book.loaded.spine;
    const item = spine.get(0); // Obtener el primer capítulo
    const doc = await book.load(item.href);
    
    // Limpiar etiquetas HTML para dejar solo texto puro
    currentText = doc.body.textContent || doc.body.innerText;
}

// 3. Controles de Voz (Web Speech API)
btnPlay.addEventListener('click', () => {
    if (synth.paused) {
        synth.resume();
        statusDiv.innerText = "Reproduciendo...";
    } else if (!synth.speaking && currentText !== "") {
        utterance = new SpeechSynthesisUtterance(currentText);
        utterance.lang = 'es-ES'; // O es-MX / es-CO dependiendo de las voces de tu sistema
        utterance.rate = 1.0; // Velocidad de lectura
        
        utterance.onend = () => { statusDiv.innerText = "Lectura finalizada."; };
        
        synth.speak(utterance);
        statusDiv.innerText = "Reproduciendo...";
    }
});

btnPausa.addEventListener('click', () => {
    if (synth.speaking && !synth.paused) {
        synth.pause();
        statusDiv.innerText = "Pausado.";
    }
});
