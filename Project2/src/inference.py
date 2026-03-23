import numpy as np

def forward(hmm, observation):
    #implement: alpha_i(t) = P(O_{1:t}, X_t = i)
    # (or a scaled version for numerical stability), and from this obtain the filtering distribution
    # P(X_t \mid O_{1:t})
    T = observation.shape[0]
    N = hmm.num_states
    reg = hmm.reg

    alpha = np.zeros((T, N))

    # t = 0
    x_0 = observation[0]
    for i in range(N):
        emission = np.exp(hmm.log_emission_prob(i, x_0))
        alpha[0, i] = max(hmm.pi[i], reg) * emission
    
    # normalize the first row
    row_sum = np.sum(alpha[0])
    if row_sum > 0:
        alpha[0] = alpha[0] / row_sum
    else: 
        alpha[0] = np.ones(N) / N
    
    # t = 1, 2, ..., 3
    for t in range(1, T):
        x_t = observation[t]
        for j in range(N):
            total = 0.0
            for i in range(N):
                total += alpha[t - 1, i] * max(hmm.A[i, j], reg)
            emission = np.exp(hmm.log_emission_prob(j, x_t))
            alpha[t, j] = total * emission
        
        #Normalize row t
        row_sum = np.sum(alpha[t])
        if row_sum > 0:
            alpha[t] = alpha[t] / row_sum
        else:
            alpha[t] = np.ones(N) / N
    
    return alpha

def viterbi(hmm, observation):
    # Compute the mosr likely state sequence for each test utterance: 
    # \hat{X}_{1:T} = argmax_x_{1:T} P(X_{1:T} \mid O_{1:T})
    # Use log-probabilities or scaling to avoid numerical underflow
    # observation shape: (T, D)
    T = observation.shape[0]
    N = hmm.num_states

    # delta[t, j] = best log-score of any path ending in state j at time t
    delta = np.full((T, N), -np.inf)

    # psi[t, j] = best previous state leading to state j at time t
    psi = np.zeros((T, N), dtype=int)

    # ----- t = 0 -----
    x_0 = observation[0]

    for j in range(N):
        delta[0, j] = np.log(hmm.pi[j] + hmm.reg) + hmm.log_emission_prob(j, x_0)
        psi[0, j] = 0

    # ----- recursion -----
    for t in range(1, T):
        x_t = observation[t]

        for j in range(N):
            best_score = -np.inf
            best_prev_state = 0

            for i in range(N):
                score = delta[t - 1, i] + np.log(hmm.A[i, j] + hmm.reg)

                if score > best_score:
                    best_score = score
                    best_prev_state = i

            delta[t, j] = best_score + hmm.log_emission_prob(j, x_t)
            psi[t, j] = best_prev_state

    # ----- termination -----
    best_last_state = np.argmax(delta[T - 1])

    # ----- backtracking -----
    best_path = np.zeros(T, dtype=int)
    best_path[T - 1] = best_last_state

    for t in range(T - 2, -1, -1):
        best_path[t] = psi[t + 1, best_path[t + 1]]

    return best_path