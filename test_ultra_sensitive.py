#!/usr/bin/env python3
"""Ultra-sensitive clap detector - detects ANY loud transient."""

import sys
from pathlib import Path
import numpy as np
import sounddevice as sd
import time

sys.path.insert(0, str(Path(__file__).parent / "src"))

print("\n" + "🎵 ULTRA-SENSITIVE CLAP DETECTION 🎵".center(60))
print("="*60)
print("\nThis version detects ANY loud sound (not just claps).")
print("Good for testing if audio is being captured.\n")

SAMPLE_RATE = 16000
CHUNK_SIZE = 1024
CHANNELS = 1

detection_count = 0
frame_count = 0
peak_history = []

def audio_callback(*args):
    """Very simple callback - just check for peaks."""
    global detection_count, frame_count, peak_history
    
    if len(args) < 1:
        return
    
    indata = args[0]
    frame_count += 1
    
    try:
        # Extract audio
        if len(indata.shape) > 1 and indata.shape[1] > 0:
            audio_chunk = indata[:, 0].astype(np.float32)
        else:
            audio_chunk = indata.astype(np.float32) if len(indata.shape) == 1 else indata[:, 0].astype(np.float32)
        
        peak = np.max(np.abs(audio_chunk))
        peak_history.append(peak)
        
        # Keep only last 100 peaks
        if len(peak_history) > 100:
            peak_history.pop(0)
        
        # Calculate average
        avg_peak = np.mean(peak_history) if peak_history else 0
        
        # Print every 20 frames
        if frame_count % 20 == 0:
            print(f"  Frame {frame_count}: Peak={peak:.6f} | Avg={avg_peak:.6f}", end="\r")
        
        # Simple detection: if peak is 5x higher than average, it's a transient
        if len(peak_history) > 20:
            threshold = avg_peak * 3
            if peak > threshold and peak > 0.01:
                detection_count += 1
                print(f"\n\n✅ TRANSIENT DETECTED! (#{detection_count}) Peak={peak:.6f}")
                time.sleep(0.5)  # Avoid double-detection
    
    except Exception as e:
        print(f"Error: {e}")

try:
    with sd.Stream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        blocksize=CHUNK_SIZE,
        dtype=np.float32,
        callback=audio_callback,
    ):
        print("⏳ Waiting for loud sounds...\n")
        print("Clap, snap your fingers, whistle, or make any loud noise!\n")
        while True:
            time.sleep(0.1)

except KeyboardInterrupt:
    print(f"\n\n👋 Exiting...")
    print(f"Total transients detected: {detection_count}")
    print(f"Total frames processed: {frame_count}")
    if peak_history:
        print(f"Max peak level: {np.max(peak_history):.6f}")
        print(f"Average peak level: {np.mean(peak_history):.6f}")
except Exception as e:
    print(f"❌ Error: {e}")
