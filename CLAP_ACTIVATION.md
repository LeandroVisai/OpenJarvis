# 🎤 Hands-Free Speech Activation with Clap Detection

OpenJarvis ahora soporta **activación por aplausos** para un control totalmente hands-free.

## 🎯 Características

- ✅ Detección de aplausos en tiempo real
- ✅ Registro automático de voz al detectar clap
- ✅ Sin necesidad de hacer click en el micrófono
- ✅ Funciona localmente (sin APIs externas)
- ✅ Personalizable (umbral, frecuencia, duración)

## 📦 Instalación

La funcionalidad ya está incluida. Solo necesitas tener `sounddevice` instalado:

```bash
pip install sounddevice
```

## 🚀 Uso Básico

### Modo Interactivo

```bash
# Ejecutar el demo interactivo
python demo_clap_activation.py
```

Selecciona el modo:
- **1**: Real-time (escucha aplausos del micrófono)
- **2**: Static (demuestra con audio sintético)

### En tu Código

```python
from openjarvis.speech.clap_detection import RealTimeClapDetector
import sounddevice as sd
import numpy as np

# Crear detector
detector = RealTimeClapDetector(
    sample_rate=16000,
    window_ms=300,  # Ventana de 300ms
    clap_threshold=0.15  # Sensibilidad
)

# Procesar audio en tiempo real
def audio_callback(indata, frames, time_info, status):
    audio_chunk = indata[:, 0].astype(np.float32)
    
    if detector.process_chunk(audio_chunk):
        print("👏 ¡APLAUSO DETECTADO!")
        # Aquí iniciar grabación de voz

# Stream de audio
with sd.Stream(samplerate=16000, channels=1, callback=audio_callback):
    sd.sleep(10000)  # Mantener abierto
```

## ⚙️ Ajustar la Sensibilidad

### Aumentar Sensibilidad (detecta aplausos más suaves)

```python
detector = RealTimeClapDetector(
    clap_threshold=0.10,  # Más bajo = más sensible
    window_ms=300
)
```

### Disminuir Sensibilidad (menos falsos positivos)

```python
detector = RealTimeClapDetector(
    clap_threshold=0.25,  # Más alto = menos sensible
    window_ms=300
)
```

## 📊 Cómo Funciona

El detector analiza:

1. **Amplitud**: Detecta picos de sonido (transientes)
2. **Ataque Rápido**: Los aplausos tienen un inicio muy rápido
3. **Contenido Espectral**: Busca frecuencias en rango 1-10kHz
4. **Duración**: Valida que sea corto (30-400ms)

```
Audio Input
    ↓
┌─────────────────────────┐
│ Sliding Window (300ms)  │
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│ Peak Amplitude Check    │ (>0.15)
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│ Fast Attack Check       │ (20% energy en primer 25%)
└─────────────────────────┘
    ↓
┌─────────────────────────┐
│ Spectral Analysis       │ (1-10kHz content)
└─────────────────────────┘
    ↓
[CLAP DETECTED] or [NOT A CLAP]
```

## 🎙️ Integración con Speech

Combinar clap detection con STT/TTS:

```python
import asyncio
from openjarvis.speech.clap_detection import RealTimeClapDetector
from openjarvis.speech._discovery import get_speech_backend
from openjarvis.core.config import JarvisConfig

config = JarvisConfig()
stt_backend = get_speech_backend(config)
detector = RealTimeClapDetector()

async def clap_activated_speech():
    """Listen for claps, then record and transcribe speech."""
    while True:
        # ... process audio chunks ...
        if detector.process_chunk(chunk):
            print("👏 Recording speech...")
            
            # Record for 5 seconds
            speech_audio = record_audio(duration=5)
            
            # Transcribe
            result = stt_backend.transcribe(speech_audio)
            print(f"You said: {result.text}")
```

## 🔧 Parámetros de Configuración

### ClapDetector

```python
detector = ClapDetector(
    sample_rate=16000,           # Hz
    clap_threshold=0.15,         # 0-1 (peak amplitude)
    frequency_min=1000,          # Hz (minimum frequency)
    frequency_max=10000,         # Hz (maximum frequency)
    min_duration_ms=30,          # ms (minimum clap duration)
    max_duration_ms=400,         # ms (maximum clap duration)
)
```

### RealTimeClapDetector

```python
detector = RealTimeClapDetector(
    sample_rate=16000,           # Hz
    window_ms=300,               # Sliding window size
    clap_threshold=0.15,         # 0-1 (peak amplitude)
)
```

## 📝 Ejemplos Prácticos

### Ejemplo 1: Detectar 2 Aplausos

```python
from openjarvis.speech.clap_detection import ClapDetector
import numpy as np

detector = ClapDetector(sample_rate=16000)

# Audio con 2 aplausos
audio = np.concatenate([clap1, silence, clap2, silence])

# Detectar múltiples
count = detector.detect_multiple_claps(audio, num_claps=2)
print(f"Detected {count} claps")  # Output: 2
```

### Ejemplo 2: Custom Sensitivity Profile

```python
# Modo "Muy Sensible" - para ambientes silenciosos
sensitive = RealTimeClapDetector(
    clap_threshold=0.08,
    window_ms=200
)

# Modo "Normal" - para uso diario
normal = RealTimeClapDetector(
    clap_threshold=0.15,
    window_ms=300
)

# Modo "Robusto" - para ambientes ruidosos
robust = RealTimeClapDetector(
    clap_threshold=0.30,
    window_ms=400
)
```

## 🐛 Solución de Problemas

### No detecta aplausos

**Soluciones:**
1. ↓ Baja el `clap_threshold` (p.ej. 0.10 en lugar de 0.15)
2. ✅ Aplaude más fuerte
3. 🎙️ Verifica que el micrófono esté bien conectado
4. 📊 Revisa niveles de audio con un medidor

### Demasiados falsos positivos

**Soluciones:**
1. ↑ Sube el `clap_threshold` (p.ej. 0.25)
2. 📏 Aumenta `window_ms` (más contexto)
3. 🔇 Reduce ruido de fondo
4. 🎵 Evita música con sonidos similares

### Demo Static Not Detecting

La versión sintética puede ser difícil de detectar. Usa la versión real-time:

```bash
python demo_clap_activation.py
# Selecciona opción 1 (real-time)
```

## 📚 Documentación Relacionada

- [Speech Configuration](./user-guide/speech.md)
- [STT/TTS Backends](./architecture/channels.md)
- [Event Bus](./architecture/events.md)

---

**¿Preguntas?** Consulta los ejemplos en `examples/clap_activation/` o abre un issue en GitHub.
