# build phoneme_to_idx 
# build idx_to_phoneme
# remember features(.npy): O[0], O[1], O[2], ..., O[T-1] --> are indexed by t =0, 1, 2, ..., 
# labels (.lab): 0.34325 → ao, 0.45575 → th ---> are in time(seconds)
# so we can do time = t * 0.01
# we want to create: [[O[0], X[0]], [O[1], X[1]], [...]]
# X = ["pau", "pau", "ao", "ao", ...]

class Align:
    def __init__(self, frame_shift=0.01):
        self.frame_shift = frame_shift
    
    def make_intervals(self, lab_entries):
        intervals = []
        start_time = 0.0

        for end_time, _, phoneme in lab_entries: # what we get from load_lab
            intervals.append((start_time, end_time, phoneme))
            start_time = end_time
        return intervals
    
    def align_label_to_frames(self, intervals, num_frames):
        labels = []
        interval_index = 0

        for t in range(num_frames):
            curr_time = t * self.frame_shift

            while(interval_index < len(intervals) -1 and curr_time >= intervals[interval_index][1]):
                interval_index += 1
            labels.append(intervals[interval_index][2]) # so we append the label e.g. pau, ao, etc. 
        
        return labels
    
    def build_phoneme_mappings(self, all_label_seq):
        phoneme_set = set()

        for label_seq in all_label_seq:
            for phoneme in label_seq:
                phoneme_set.add(phoneme)
        
        phoneme_list = sorted(list(phoneme_set))
        phoneme_to_idx = {phoneme: i for i, phoneme in enumerate(phoneme_list)}
        idx_to_phoneme = {i: phoneme for phoneme, i in phoneme_to_idx.items()}

        return phoneme_to_idx, idx_to_phoneme

    def encode_labels(self, labels, phoneme_to_idx):
        return [phoneme_to_idx[phoneme] for phoneme in labels]

