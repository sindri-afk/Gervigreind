from data_loader import DataLoader
from align import Align
from hmm import HMM
from inference import forward, viterbi
from evaluation import evaluate_dataset, confusion_matrix, precision_recall

import numpy as np
import os

OUT_DIR = "../data/out"
LAB_DIR = "../data/cmu_us_slt_arctic/lab"


def prepare_data(basenames, loader, aligner, phoneme_to_idx=None):
    observation_seq = []
    label_seq = []

    for basename in basenames:
        features = loader.load_features(basename)
        lab_entries = loader.load_lab(basename)

        intervals = aligner.make_intervals(lab_entries)
        labels = aligner.align_label_to_frames(intervals, features.shape[0])

        if len(labels) != features.shape[0]:
            print("Label length mismatch for", basename)
            continue

        observation_seq.append(features)
        label_seq.append(labels)

    # build mapping ONLY if not given (train set)
    if phoneme_to_idx is None:
        phoneme_to_idx, idx_to_phoneme = aligner.build_phoneme_mappings(label_seq)
    else:
        idx_to_phoneme = None

    label_seq_idx = []
    for labels in label_seq:
        encoded = aligner.encode_labels(labels, phoneme_to_idx)
        label_seq_idx.append(encoded)

    return observation_seq, label_seq, label_seq_idx, phoneme_to_idx, idx_to_phoneme


def main():
    loader = DataLoader(OUT_DIR, LAB_DIR)
    aligner = Align()

    train_basenames = loader.load_split("train")
    test_basenames = loader.load_split("test")
    val_basenames = loader.load_split("val")

    train_obs, train_labels, train_labels_idx, phoneme_to_idx, idx_to_phoneme = \
        prepare_data(train_basenames, loader, aligner)

    print("Number of training utterances:", len(train_obs))
    print("Number of phonemes:", len(phoneme_to_idx))
    print("Example mapping:", list(phoneme_to_idx.items())[:10])
    print("Feature shape example:", train_obs[0].shape)

    test_obs, test_labels, test_labels_idx, _, _ = \
        prepare_data(test_basenames, loader, aligner, phoneme_to_idx)

    num_states = len(phoneme_to_idx)
    feature_dim = train_obs[0].shape[1]

    hmm = HMM(num_states, feature_dim)

    print("\nTraining HMM...")
    hmm.fit(train_obs, train_labels_idx)
    print("Training done.")

    print("\nSanity check on one training utterance:")
    sample_obs = train_obs[0]
    sample_true = train_labels_idx[0]

    sample_pred = viterbi(hmm, sample_obs)

    print("True:", sample_true[:20])
    print("Pred:", sample_pred[:20])

    print("\nEvaluating on TRAIN set...")
    train_acc, train_true, train_pred = evaluate_dataset(
        hmm, train_obs, train_labels_idx, method="viterbi"
    )

    print("Train accuracy:", train_acc)

    print("\nEvaluating on TEST set...")
    test_acc, test_true, test_pred = evaluate_dataset(
        hmm, test_obs, test_labels_idx, method="viterbi"
    )

    print("Test accuracy:", test_acc)

    cm = confusion_matrix(test_true, test_pred, num_states)

    precision, recall = precision_recall(cm)

    print("\nPrecision (first 10):", precision[:10])
    print("Recall (first 10):", recall[:10])

    print("\nEvaluating with FORWARD (optional)...")
    test_acc_fwd, _, _ = evaluate_dataset(
        hmm, test_obs, test_labels_idx, method="forward"
    )

    print("Test accuracy (forward):", test_acc_fwd)


if __name__ == "__main__":
    main()