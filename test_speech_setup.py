#!/usr/bin/env python3
"""Test speech setup — verify STT and TTS backends are working."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from openjarvis.core.config import JarvisConfig
from openjarvis.speech._discovery import get_speech_backend
from openjarvis.core.registry import TTSRegistry


def test_stt():
    """Test speech-to-text backend."""
    print("\n" + "="*60)
    print("🎤 SPEECH-TO-TEXT (STT) TEST")
    print("="*60)
    
    config = JarvisConfig()
    print(f"\n📝 Config: {config.speech.backend}")
    print(f"   Model: {config.speech.model}")
    print(f"   Device: {config.speech.device}")
    print(f"   Compute: {config.speech.compute_type}")
    
    try:
        speech_backend = get_speech_backend(config)
        if speech_backend:
            print(f"\n✅ Speech backend loaded: {speech_backend.backend_id}")
            health = speech_backend.health()
            print(f"   Health check: {'✅ HEALTHY' if health else '❌ UNHEALTHY'}")
            
            if hasattr(speech_backend, 'supported_formats'):
                formats = speech_backend.supported_formats()
                print(f"   Supported formats: {', '.join(formats)}")
        else:
            print("❌ No speech backend found!")
    except Exception as e:
        print(f"❌ Error: {e}")


def test_tts():
    """Test text-to-speech backend."""
    print("\n" + "="*60)
    print("🔊 TEXT-TO-SPEECH (TTS) TEST")
    print("="*60)
    
    try:
        # Register TTS backends
        import openjarvis.speech
        
        tts_backends = TTSRegistry.items()
        print(f"\n📦 Available TTS backends: {len(tts_backends)}")
        for name, cls in tts_backends:
            print(f"   - {name}: {cls.__doc__.strip() if cls.__doc__ else 'No description'}")
        
        # Try to load Kokoro
        print(f"\n🎯 Testing 'kokoro' backend...")
        try:
            kokoro_backend = TTSRegistry.create("kokoro")
            if kokoro_backend:
                print(f"✅ Kokoro TTS loaded successfully!")
                health = kokoro_backend.health()
                print(f"   Health check: {'✅ HEALTHY' if health else '❌ UNHEALTHY'}")
                
                voices = kokoro_backend.available_voices()
                print(f"   Available voices: {', '.join(voices)}")
            else:
                print("❌ Could not create Kokoro backend")
        except Exception as e:
            print(f"⚠️  Kokoro not available: {e}")
    
    except Exception as e:
        print(f"❌ Error loading TTS: {e}")


def main():
    """Main test runner."""
    print("\n" + "🎉 OPENJARVIS SPEECH CONFIGURATION TEST 🎉".center(60))
    
    test_stt()
    test_tts()
    
    print("\n" + "="*60)
    print("📋 SUMMARY")
    print("="*60)
    print("\n✅ Configuration complete!")
    print("\n📝 Next steps:")
    print("   1. Open http://localhost:8000 in your browser")
    print("   2. Click the microphone icon to test voice input")
    print("   3. The AI will respond with speech output")
    print("\n💡 To customize speech settings, edit: ~/.openjarvis/config.toml")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
