import numpy as np
from inference import forward, viterbi

def frame_accuracy(true_seq, pred_seq):
    correct = 0
    total = len(true_seq)

    for t in range(total):
        if true_seq[t] == pred_seq[t]:
            correct += 1

    return correct / total

def evaluate_dataset(hmm, observation_seq, label_seq_idx, method="viterbi"):
    total_correct = 0
    total_frames = 0

    all_true = []
    all_pred = []

    for i in range(len(observation_seq)):
        obs = observation_seq[i]
        true_labels = label_seq_idx[i]

        if method == "viterbi":
            pred_labels = viterbi(hmm, obs)
        elif method == "forward":
            alpha = forward(hmm, obs)
            pred_labels = np.argmax(alpha, axis=1)
        else:
            raise ValueError("method must be 'viterbi' or 'forward'")

        for t in range(len(true_labels)):
            if true_labels[t] == pred_labels[t]:
                total_correct += 1

            total_frames += 1
            all_true.append(true_labels[t])
            all_pred.append(pred_labels[t])

    accuracy = total_correct / total_frames

    return accuracy, np.array(all_true), np.array(all_pred)

def confusion_matrix(true, pred, num_states):
    cm = np.zeros((num_states, num_states), dtype=int)

    for t in range(len(true)):
        i = true[t]
        j = pred[t]
        cm[i][j] += 1

    return cm


def precision_recall(cm):
    num_states = cm.shape[0]

    precision = np.zeros(num_states)
    recall = np.zeros(num_states)

    for i in range(num_states):
        tp = cm[i][i]

        fp = np.sum(cm[:, i]) - tp
        fn = np.sum(cm[i, :]) - tp

        if tp + fp > 0:
            precision[i] = tp / (tp + fp)
        else:
            precision[i] = 0.0

        if tp + fn > 0:
            recall[i] = tp / (tp + fn)
        else:
            recall[i] = 0.0

    return precision, recall