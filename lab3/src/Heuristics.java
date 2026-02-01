public interface Heuristics {

	/**
	 * inform the heuristics about the environment, needs to be called before the first call to eval()
	 * @param env
	 */
	public void init(Environment env);

	/**
	 * return an estimate of the remaining cost of reaching a goal state from state s
	 * @param s
	 * @return
	 */
	public int eval(State s);

}