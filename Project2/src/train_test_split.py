#!/usr/bin/env python3
"""
Split CMU ARCTIC (e.g., cmu_us_slt_arctic) into train/val/test sets.

Assumptions:
- You have a directory like: /path/to/cmu_us_slt_arctic/
- Inside it (or in subdirs) you have paired files: *.wav and *.lab
  with identical basenames, e.g.:
      arctic_a0001.wav
      arctic_a0001.lab

This script:
- Finds all such pairs,
- Sorts by basename,
- Splits 70% / 10% / 20%,
- Writes three text files listing basenames (without extension):
    train.txt, val.txt, test.txt
"""

import os
import glob
import math
import random
from pathlib import Path

# Get the directory of this script to make other paths relative to the script location
script_dir = Path(__file__).resolve().parent

# --------- CONFIGURE THIS ---------
data_root = script_dir.parent / "data" / "cmu_us_slt_arctic"
out_dir = script_dir.parent / "data" / "out"
random.seed(42)   # influences the train/test split
# -----------------------------------

def main():
    out_dir.mkdir(parents=True, exist_ok=True)

    # Find wav and lab files
    wav_files = set(
        Path(p).stem for p in glob.glob(str(data_root / "**" / "*.wav"), recursive=True)
    )
    lab_files = set(
        Path(p).stem for p in glob.glob(str(data_root / "**" / "*.lab"), recursive=True)
    )

    # Intersection: only use examples that have both wav and lab
    common_basenames = sorted(wav_files.intersection(lab_files))

    if not common_basenames:
        raise RuntimeError("No matching *.wav and *.lab pairs found.")

    n = len(common_basenames)
    n_train = math.floor(0.7 * n)
    n_val = math.floor(0.1 * n)
    # Ensure all files are used
    n_test = n - n_train - n_val

    random.shuffle(common_basenames)
    train_basenames = common_basenames[:n_train]
    val_basenames   = common_basenames[n_train:n_train + n_val]
    test_basenames  = common_basenames[n_train + n_val:]

    print(f"Total files: {n}")
    print(f"Train: {n_train}, Val: {n_val}, Test: {n_test}")

    def write_list(filename, names):
        with open(out_dir / filename, "w", encoding="utf-8") as f:
            for name in names:
                f.write(name + "\n")

    write_list("train.txt", train_basenames)
    write_list("val.txt",   val_basenames)
    write_list("test.txt",  test_basenames)

    print(f"Splits written to: {out_dir}")


if __name__ == "__main__":
    main()
