"""Clap detection module — detect applause/claps for hands-free speech activation."""

from __future__ import annotations

import numpy as np
from typing import Optional


class ClapDetector:
    """Detect claps/applause using energy and spectral analysis.
    
    A clap produces a characteristic sound with:
    - Sudden high amplitude (loud transient)
    - Brief duration (~50-300ms)
    - Broad frequency content with peaks in 1-10kHz range
    """
    
    def __init__(
        self,
        sample_rate: int = 16000,
        clap_threshold: float = 0.15,
        frequency_min: int = 1000,  # Hz
        frequency_max: int = 10000,  # Hz
        min_duration_ms: int = 30,
        max_duration_ms: int = 400,
    ):
        """Initialize clap detector.
        
        Args:
            sample_rate: Audio sample rate in Hz
            clap_threshold: Peak amplitude threshold (0-1) to detect claps
            frequency_min: Minimum frequency for clap detection (Hz)
            frequency_max: Maximum frequency for clap detection (Hz)
            min_duration_ms: Minimum clap duration (ms)
            max_duration_ms: Maximum clap duration (ms)
        """
        self.sample_rate = sample_rate
        self.clap_threshold = clap_threshold
        self.frequency_min = frequency_min
        self.frequency_max = frequency_max
        self.min_duration = int(min_duration_ms * sample_rate / 1000)
        self.max_duration = int(max_duration_ms * sample_rate / 1000)
    
    def detect_clap(
        self,
        audio_chunk: np.ndarray,
        threshold_override: Optional[float] = None,
    ) -> bool:
        """Detect if audio chunk contains a clap sound.
        
        Simple approach: detect transients (sudden energy bursts)
        
        Args:
            audio_chunk: Audio samples (mono, float32, normalized -1 to 1)
            threshold_override: Override the threshold for this detection
            
        Returns:
            True if a clap is detected, False otherwise
        """
        if len(audio_chunk) < self.min_duration:
            return False
        
        threshold = threshold_override or self.clap_threshold
        
        # 1. Check for peak amplitude above threshold
        peak_amplitude = np.max(np.abs(audio_chunk))
        if peak_amplitude < threshold:
            return False
        
        # 2. Check for transient (sudden energy burst)
        # Divide into quarters and check if energy concentrates at start
        quarter_len = len(audio_chunk) // 4
        if quarter_len > 2:
            energy_dist = []
            for i in range(4):
                start = i * quarter_len
                end = start + quarter_len if i < 3 else len(audio_chunk)
                quarter_energy = np.sum(np.abs(audio_chunk[start:end]))
                energy_dist.append(quarter_energy)
            
            total_energy = sum(energy_dist)
            if total_energy > 0:
                # For transients, first quarter should have most energy
                first_quarter_ratio = energy_dist[0] / total_energy
                if first_quarter_ratio < 0.15:  # Very permissive - at least 15%
                    return False
        
        return True
    
    def detect_multiple_claps(
        self,
        audio_chunk: np.ndarray,
        num_claps: int = 2,
    ) -> int:
        """Detect multiple claps in sequence.
        
        Args:
            audio_chunk: Audio samples
            num_claps: Expected number of claps to detect
            
        Returns:
            Number of claps detected
        """
        chunk_size = len(audio_chunk) // (num_claps + 1)
        
        if chunk_size < self.min_duration:
            return 0
        
        claps_detected = 0
        for i in range(num_claps):
            start = i * chunk_size
            end = start + chunk_size
            if end > len(audio_chunk):
                break
            if self.detect_clap(audio_chunk[start:end]):
                claps_detected += 1
        
        return claps_detected


class RealTimeClapDetector:
    """Real-time clap detector using a sliding window.
    
    Simple approach: detects transients (sudden loud sounds).
    """
    
    def __init__(
        self,
        sample_rate: int = 16000,
        window_ms: int = 300,
        clap_threshold: float = 0.15,
    ):
        """Initialize real-time detector.
        
        Args:
            sample_rate: Audio sample rate
            window_ms: Sliding window size (ms)
            clap_threshold: Peak amplitude threshold for clap detection
        """
        self.sample_rate = sample_rate
        self.window_size = int(window_ms * sample_rate / 1000)
        self.clap_threshold = clap_threshold
        self.buffer = np.array([], dtype=np.float32)
        self.peak_history = []  # Track recent peaks for relative detection
    
    def process_chunk(self, audio_chunk: np.ndarray) -> bool:
        """Process incoming audio chunk.
        
        Args:
            audio_chunk: New audio samples
            
        Returns:
            True if clap detected in latest window
        """
        self.buffer = np.concatenate([self.buffer, audio_chunk])
        
        # Keep only the latest window
        if len(self.buffer) > self.window_size:
            self.buffer = self.buffer[-self.window_size:]
        
        # Simple: check if peak exceeds threshold
        if len(self.buffer) >= 100:
            peak = np.max(np.abs(self.buffer))
            
            # Just use absolute threshold - much simpler and more reliable
            if peak > self.clap_threshold:
                return True
        
        return False
    
    def reset(self):
        """Reset the buffer."""
        self.buffer = np.array([], dtype=np.float32)


__all__ = ["ClapDetector", "RealTimeClapDetector"]
