def forward(hmm, observation):
    #implement: alpha_i(t) = P(O_{1:t}, X_t = i)
    # (or a scaled version for numerical stability), and from this obtain the filtering distribution
    # P(X_t \mid O_{1:t})
    pass

def viterbi(hmm, observation):
    # Compute the mosr likely state sequence for each test utterance: 
    # \hat{X}_{1:T} = argmax_x_{1:T} P(X_{1:T} \mid O_{1:T})
    # Use log-probabilities or scaling to avoid numerical underflow
    pass