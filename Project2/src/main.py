from data_loader import DataLoader
from align import Align
import os

OUT_DIR = "../data/out"
LAB_DIR = "../data/cmu_us_slt_arctic/lab"

def main():
    loader = DataLoader(OUT_DIR, LAB_DIR)
    aligner = Align()
    
    train_basenames = loader.load_split("train")
    test_basenames = loader.load_split("test")
    val_basenames = loader.load_split("val")

    observation_seq = []
    label_seq = []

    for basename in train_basenames:
        features = loader.load_features(basename)
        lab_entries = loader.load_lab(basename)

        intervals = aligner.make_intervals(lab_entries)
        labels = aligner.align_label_to_frames(intervals, features.shape[0])

        if len(labels) != features.shape[0]:
            print("Did not work, label length mismatch")
        
        observation_seq.append(features)
        label_seq.append(labels)

    phoneme_to_idx, idx_to_phoneme = aligner.build_phoneme_mappings(label_seq)

    label_seq_idx = [] 
    
    for labels in label_seq:
        encoded = aligner.encode_labels(labels, phoneme_to_idx)
        label_seq_idx.append(encoded)

    print("Number of training utterances:", len(observation_seq))
    print("Number of phonemes:", len(phoneme_to_idx))
    print("Example mapping:", phoneme_to_idx)
    print("First utterance feature shape:", observation_seq[0].shape)
    print("First utterance first 20 labels:", label_seq[0][:20])
    print("First utterance first 20 encoded labels:", label_seq_idx[0][:20])

if __name__ == "__main__":
    main()