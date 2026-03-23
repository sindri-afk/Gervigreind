#!/usr/bin/env python3
"""
Extract MFCC + delta + delta-delta features for each WAV file in CMU ARCTIC
and save them to disk (one .npy file per input .wav).

Assumptions:
- Audio is 16 kHz mono (CMU ARCTIC default).
- You have python_speech_features installed:
    pip install python_speech_features
- You have numpy and scipy installed.

Configuration:
- Set data_root to the root of your cmu_us_slt_arctic directory.
- Set out_dir to where you want the feature files to go.

Output:
- For each input WAV:  <relative_path>/<basename>.npy
  containing a 2D numpy array of shape (num_frames, 39) where
  39 = 13 MFCC + 13 delta + 13 delta-delta.
"""

import os
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from python_speech_features import mfcc, delta

# Get the directory of this script to make other paths relative to the script location
script_dir = Path(__file__).resolve().parent

# --------- CONFIGURE THIS ---------
data_root = script_dir.parent / "data" / "cmu_us_slt_arctic"
out_dir = script_dir.parent / "data" / "out"
# -----------------------------------

def extract_features(signal, samplerate):
    """
    Extract 13 MFCC + delta + delta-delta (= 39 dims) using
    25 ms window and 10 ms step, as described in the project.
    """
    # Ensure float
    if signal.dtype != np.float32 and signal.dtype != np.float64:
        signal = signal.astype(np.float32)

    # Parameters: 25 ms window, 10 ms step
    winlen = 0.025  # 25 ms
    winstep = 0.010 # 10 ms

    # 13 MFCCs (excluding 0th or including; here we include by default)
    mfcc_feat = mfcc(
        signal=signal,
        samplerate=samplerate,
        numcep=13,
        winlen=winlen,
        winstep=winstep,
        nfilt=26,
        nfft=512,
        preemph=0.97,
        ceplifter=22,
        appendEnergy=True
    )  # shape: (num_frames, 13)

    # First-order delta
    d_mfcc = delta(mfcc_feat, N=2)  # shape: (num_frames, 13)

    # Second-order delta (delta of delta)
    dd_mfcc = delta(d_mfcc, N=2)    # shape: (num_frames, 13)

    # Concatenate: [MFCC, delta, delta-delta] -> 39-D
    feats = np.hstack([mfcc_feat, d_mfcc, dd_mfcc])  # (num_frames, 39)
    return feats


def process_wav_file(wav_path, out_dir, data_root):
    """
    Read a wav, compute features, save .npy in a mirrored directory structure.
    """
    wav_path = Path(wav_path)
    out_path = out_dir / (wav_path.stem + ".npy")

    # Read audio
    sr, sig = wavfile.read(wav_path)

    # If stereo, take first channel
    if sig.ndim == 2:
        sig = sig[:, 0]

    feats = extract_features(sig, sr)

    np.save(out_path, feats)
    print(f"Saved features: {out_path}  (frames={feats.shape[0]}, dim={feats.shape[1]})")


def main():
    out_dir.mkdir(parents=True, exist_ok=True)

    wav_files = sorted(data_root.rglob("*.wav"))
    if not wav_files:
        raise RuntimeError(f"No .wav files found under {data_root}")

    print(f"Found {len(wav_files)} wav files. Extracting features...")

    for wav_path in wav_files:
        process_wav_file(wav_path, out_dir, data_root)

    print("Done.")


if __name__ == "__main__":
    main()
