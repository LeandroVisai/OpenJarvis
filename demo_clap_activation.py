#!/usr/bin/env python3
"""Demo: Clap detection with speech recording.

This script listens for claps and automatically starts recording speech.
Perfect for hands-free operation!

Requirements:
    pip install sounddevice numpy scipy
"""

import sys
import threading
import time
from pathlib import Path

import numpy as np
import sounddevice as sd

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from openjarvis.speech.clap_detection import RealTimeClapDetector


def demo_clap_detection():
    """Demo: Real-time clap detection."""
    print("\n" + "🎵 CLAP DETECTION DEMO 🎵".center(60))
    print("="*60)
    print("\nListening for claps to activate speech recording...")
    print("💡 Clap **LOUDLY and SHARPLY** to trigger recording")
    print("💡 Try to make a quick, loud sound")
    print("💡 Press Ctrl+C to exit\n")
    
    SAMPLE_RATE = 16000
    CHUNK_SIZE = 1024
    CHANNELS = 1
    
    # Use ULTRA SENSITIVE threshold for low-level audio
    detector = RealTimeClapDetector(
        sample_rate=SAMPLE_RATE,
        window_ms=300,
        clap_threshold=0.02,  # Very low threshold - raw peak detection
    )
    
    clap_count = 0
    debug_enabled = True
    frame_count = 0
    
    def audio_callback(*args):
        """Callback for audio stream - accepts variable args."""
        nonlocal clap_count, frame_count
        
        # Sounddevice passes (indata, frames, time_info, status, ...)
        if len(args) < 4:
            return
            
        indata, frames, time_info, status = args[0], args[1], args[2], args[3]
        frame_count += 1
        
        if status:
            if debug_enabled and str(status) != "<PaSampleFormatNotSupported: 0>":
                pass  # Silently ignore expected status messages
            return
        
        try:
            # Normalize audio to -1 to 1
            if indata.shape[1] > 0:
                audio_chunk = indata[:, 0].astype(np.float32)
            else:
                audio_chunk = indata[:, 0].astype(np.float32) if len(indata.shape) > 1 else indata.astype(np.float32)
            
            # Show detailed peak amplitude
            peak = np.max(np.abs(audio_chunk))
            rms = np.sqrt(np.mean(audio_chunk ** 2))
            
            # DEBUG: Show every frame to see what's happening
            print(f"  Frame {frame_count}: Peak={peak:.6f} RMS={rms:.6f} | Buf_len={len(detector.buffer)}", end="\r", flush=True)
            
            # Detect clap
            if detector.process_chunk(audio_chunk):
                clap_count += 1
                print(f"\n\n✅ CLAP #{clap_count} DETECTED!              ")
                
                # Beep to indicate activation
                beep_freq = 800
                beep_duration = 0.2
                beep = np.sin(2 * np.pi * beep_freq * np.linspace(0, beep_duration, int(beep_duration * SAMPLE_RATE)))
                beep = (beep * 0.3).astype(np.float32)
                
                try:
                    sd.play(beep, SAMPLE_RATE, blocking=True)
                except Exception as e:
                    print(f"Could not play beep: {e}")
                
                print("🎤 Recording for 3 seconds...")
                detector.reset()
                
                # Record speech using simple recording (no callback)
                speech_duration = 3.0
                speech_samples = int(speech_duration * SAMPLE_RATE)
                
                try:
                    print("   (Recording...)")
                    speech_data = sd.rec(speech_samples, samplerate=SAMPLE_RATE, channels=CHANNELS, dtype=np.float32)
                    sd.wait()
                    
                    print("✅ Recording complete!")
                    
                    # Simulate transcription
                    print(f"\n📝 Would send {len(speech_data)} samples to speech-to-text backend")
                    print("   (faster-whisper would transcribe this to text)\n")
                    print("⏳ Waiting for next clap...")
                    
                except Exception as e:
                    print(f"❌ Recording failed: {e}")
        except Exception as e:
            if debug_enabled:
                print(f"Error in callback: {e}")
    
    # Start audio stream
    try:
        with sd.Stream(
            samplerate=SAMPLE_RATE,
            channels=CHANNELS,
            blocksize=CHUNK_SIZE,
            dtype=np.float32,
            callback=audio_callback,
        ):
            print("⏳ Waiting for claps...\n")
            while True:
                time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("\n\n👋 Exiting demo...")
        print(f"Total claps detected: {clap_count}")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Make sure you have sounddevice installed:")
        print("   pip install sounddevice")


def demo_static_detection():
    """Demo: Detect claps in a pre-recorded audio file."""
    print("\n" + "🔍 STATIC CLAP DETECTION 🔍".center(60))
    print("="*60)
    
    from openjarvis.speech.clap_detection import ClapDetector
    
    # Create synthetic audio with a clap
    sample_rate = 16000
    
    # Generate white noise
    noise = np.random.normal(0, 0.05, sample_rate // 2)
    
    # Generate a clap (sharp transient + high frequency)
    clap_samples = int(0.2 * sample_rate)  # 200ms
    t = np.linspace(0, 0.2, clap_samples)
    
    # Simulate clap: starts loud, decays quickly
    clap = 0.8 * np.exp(-t * 20) * np.sin(2 * np.pi * 3000 * t)  # 3kHz sine with decay
    clap += 0.2 * np.random.normal(0, 1, clap_samples)  # Add some noise
    
    # Combine
    audio = np.concatenate([noise, clap, noise])
    audio = audio.astype(np.float32) / np.max(np.abs(audio))
    
    # Detect
    detector = ClapDetector(sample_rate=sample_rate, clap_threshold=0.4)
    
    print(f"\nGenerated synthetic audio with a clap at 0.5 seconds")
    print(f"Audio length: {len(audio) / sample_rate:.2f} seconds")
    
    # Slide window and detect
    window_size = sample_rate // 4  # 250ms windows
    clap_detected = False
    
    for i in range(0, len(audio) - window_size, window_size):
        chunk = audio[i:i+window_size]
        if detector.detect_clap(chunk):
            time_sec = i / sample_rate
            print(f"✅ Clap detected at {time_sec:.2f}s")
            clap_detected = True
    
    if clap_detected:
        print("\n✅ Clap detection working!")
    else:
        print("\n⚠️  No clap detected (you may need to adjust threshold)")


if __name__ == "__main__":
    import os
    
    # Check if running in real environment
    try:
        import sounddevice
        print("\n📦 Dependencies: ✅ sounddevice, numpy installed")
        mode = input("\nSelect mode:\n1. Real-time demo (listen for claps)\n2. Static demo (pre-recorded)\nChoice [1-2]: ").strip()
        
        if mode == "1":
            demo_clap_detection()
        else:
            demo_static_detection()
    except ImportError:
        print("\n❌ Missing dependencies. Installing...")
        os.system("pip install sounddevice")
        print("\nRun the script again!")
