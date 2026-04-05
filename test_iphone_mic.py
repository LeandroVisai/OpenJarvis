#!/usr/bin/env python3
"""Test audio input from iPhone microphone."""

import numpy as np
import sounddevice as sd
import time

print("\n" + "🎤 TESTING iPHONE MICROPHONE 🎤".center(60))
print("="*60)
print("\nRecording from: Micrófono de iPhone de Leandro\n")

SAMPLE_RATE = 16000
DURATION = 10  # segundos

print(f"Recording for {DURATION} seconds...\nClap, snap, make NOISE!\n")

try:
    # Use device 0 (iPhone microphone)
    audio = sd.rec(DURATION * SAMPLE_RATE, samplerate=SAMPLE_RATE, channels=1, device=0, dtype=np.float32)
    sd.wait()
    
    print('\n✅ Recording complete!')
    print(f'\nPeak level: {np.max(np.abs(audio)):.6f}')
    print(f'RMS level: {np.sqrt(np.mean(audio**2)):.6f}')
    
    peak = np.max(np.abs(audio))
    if peak > 0.1:
        print(f'\n✅ Excellent! Threshold: ~0.05')
    elif peak > 0.05:
        print(f'\n✅ Good! Threshold: ~0.02')
    elif peak > 0.01:
        print(f'\n⚠️  Weak. Threshold: ~0.005')
    else:
        print(f'\n❌ No signal detected!')
        
except Exception as e:
    print(f'❌ Error: {e}')
