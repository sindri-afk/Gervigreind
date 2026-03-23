import numpy as np

class HMM:
    def __init__(self, num_states, feature_dim):
        self.num_states = num_states
        self.pi = None
        self.A = None
        self.mu = None
        self.Sigma = None
        self.feature_dim = feature_dim
        self.reg = 0.0001 # add just a bit of noise

    def estimate_pi(self, label_seq_idx):
        pi_counts = [0] * self.num_states
        for labels in label_seq_idx:
            first_state = labels[0]
            pi_counts[first_state] += 1
        
        total = sum(pi_counts)
        self.pi = [count / total for count in pi_counts]
        return self.pi
    
    def estimate_A(self, label_seq_idx):
        A_counts = np.zeros((self.num_states, self.num_states)) 
        for labels in label_seq_idx:
            for t in range(len(labels) - 1):
                i = labels[t]
                j = labels[t + 1]
                A_counts[i][j] += 1
        
        A = np.zeros_like(A_counts)

        for i in range(self.num_states):
            row_sum = A_counts[i].sum()
            if row_sum > 0:
                A[i] = A_counts[i] / row_sum
        self.A = A
        return self.A
    
    def estimate_mu(self, label_seq_idx, observation_seq):
        # 1. collect all features per state
        state_features = [[] for _ in range(self.num_states)]

        for features, labels, in zip(observation_seq, label_seq_idx):
            for x_t, state in zip(features, labels):
                state_features[state].append(x_t)
        
        # 2. compute mean per state
        mu = np.zeros((self.num_states, self.feature_dim))
        for state in range(self.num_states):
            if len(state_features[state]) == 0:
                continue
            X = np.array(state_features[state])
            mu[state] = np.mean(X, axis=0)
        
        self.mu = mu
        return self.mu

    def estimate_sigma(self, label_seq_idx, observation_seq):
        # for each state (phoneme) we want: "How do the 39 features vary together?"
        # not just average (mu), but spread and relationships
        state_features = [[] for _ in range(self.num_states)]

        for features, labels in zip(observation_seq, label_seq_idx):
            for x_t, state in zip(features, labels):
                state_features[state].append(x_t)
        
        Sigma = np.zeros((self.num_states, self.feature_dim, self.feature_dim))

        for state in range(self.num_states):
            X = np.array(state_features[state])

            if len(X) == 0:
                continue

            if len(X) == 1:
                Sigma[state] = np.eye(self.feature_dim) * self.reg
            else:
                cov = np.cov(X, rowvar=False)
                cov += np.eye(self.feature_dim) * self.reg
                Sigma[state] = cov
        self.Sigma = Sigma
        return self.Sigma
    
    def fit(self, observation_seq, label_seq_idx):
        # the method that does the training.
        self.pi = self.estimate_pi(label_seq_idx)
        self.A = self.estimate_A(label_seq_idx)
        self.mu = self.estimate_mu(label_seq_idx, observation_seq)
        self.Sigma = self.estimate_sigma(label_seq_idx, observation_seq)

    def log_emission_prob(self, state, x_t):
        # get parameters for this state
        mu_i = self.mu[state] # shape: (d)
        Sigma_i = self.Sigma[state] # shape: (d, d)

        # difference between observation and mean
        diff = x_t - mu_i

        # inverse and determinant of covariance
        Sigma_inv = np.linalg.inv(Sigma_i)
        det_Sigma = np.linalg.det(Sigma_i)

        # in case numerical issues make det non-positive
        if det_Sigma <= 0:
            det_Sigma += 0.0001
        
        d = self.feature_dim

        # quadratic term: (x-mu)^T Sigma^{-1} {x-mu}
        quad = diff.T @ Sigma_inv @ diff

        # log Gaussian probability
        log_prob = -0.5 * (
            d * np.log(2 * np.pi)
            + np.log(det_Sigma)
            + quad
        )

        return log_prob