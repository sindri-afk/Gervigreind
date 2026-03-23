import numpy as np
import os

# this file is responsible for:
# reading: train.txt, val.txt, test.txt
# loading: .npy feature files
# loading: .lab phoneme files

# this is just input/output. No HMM logic here 
# this file will be called by the main file

class DataLoader:
    def __init__(self, out_dir, lab_dir):
        self.out_dir = out_dir
        self.lab_dir = lab_dir
    
    def load_split(self, split_name): # train, test or val
        split_path = os.path.join(self.out_dir, f"{split_name}.txt")
        with open(split_path, "r") as f:
            return [line.strip() for line in f if line.strip()]
        # Ex output: ["arctic_a0001", "arctic_a0002", ...]:: this is just for the basenames
    
    def load_features(self, basename):
        feature_path = os.path.join(self.out_dir, f"{basename}.npy")
        features = np.load(feature_path)
        return features
        # Ex output: A 2D numpy array, with shape = (T, 39)
    

    def load_lab(self, basename):
        lab_path = os.path.join(self.lab_dir, f"{basename}.lab")
        entries = []

        with open(lab_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line == "#":
                    continue
                parts = line.split()
                if len(parts) != 3:
                    continue
                boundary_time, frame_code, phoneme = parts
                entries.append((float(boundary_time), float(frame_code), phoneme)) # laga nöfnin hér 
        return entries
        # Ex output: [[0.16825, 125, "pau"], [...]]