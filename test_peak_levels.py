#!/usr/bin/env python3
"""Show real-time peak levels when you make sounds."""

import numpy as np
import sounddevice as sd
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("\n" + "📊 REAL-TIME PEAK LEVEL MONITOR 📊".center(60))
print("="*60)
print("\nThis shows you the EXACT peak amplitudes as you make sounds.")
print("Make sounds, clap, snap fingers - watch the peaks!\n")

SAMPLE_RATE = 16000
CHUNK_SIZE = 1024
CHANNELS = 1

frame_count = 0
max_peak = 0
peaks = []

def audio_callback(*args):
    global frame_count, max_peak, peaks
    
    if len(args) < 4:
        return
        
    indata, frames, time_info, status = args[0], args[1], args[2], args[3]
    frame_count += 1
    
    if status:
        return
    
    try:
        if indata.shape[1] > 0:
            audio_chunk = indata[:, 0].astype(np.float32)
        else:
            audio_chunk = indata.astype(np.float32)
        
        peak = np.max(np.abs(audio_chunk))
        peaks.append(peak)
        
        if len(peaks) > 20:
            peaks.pop(0)
        
        if peak > max_peak:
            max_peak = peak
        
        avg_recent = np.mean(peaks) if peaks else 0
        
        # Print if there's any activity
        if peak > 0.003 or frame_count % 50 == 0:
            print(f"\rFrame {frame_count:4d} | Peak: {peak:.6f} | Avg recent: {avg_recent:.6f} | Max ever: {max_peak:.6f}", end="", flush=True)
    
    except Exception as e:
        print(f"Error: {e}")

print("⏳ Starting 30-second monitoring...\n")

try:
    with sd.Stream(
        samplerate=SAMPLE_RATE,
        channels=CHANNELS,
        blocksize=CHUNK_SIZE,
        dtype=np.float32,
        callback=audio_callback,
    ):
        for i in range(300):  # 30 seconds at 10 fps
            import time
            time.sleep(0.1)
except KeyboardInterrupt:
    print("\n\n⏹️  Stopped")
except Exception as e:
    print(f"Error: {e}")

print(f"\n\n📊 RESULTS:")
print(f"   Max peak detected: {max_peak:.6f}")
print(f"   Use threshold around: {max_peak * 0.5:.6f} to {max_peak * 0.8:.6f}")
print(f"\n   Recommendation:")
if max_peak > 0.1:
    print(f"   ✅ Strong signal! Use threshold ~0.05")
elif max_peak > 0.05:
    print(f"   ✅ Decent signal! Use threshold ~0.02")
elif max_peak > 0.01:
    print(f"   ⚠️  Weak signal. Use threshold ~0.005")
else:
    print(f"   ❌ Very weak signal. Check microphone gain in System Preferences!")
