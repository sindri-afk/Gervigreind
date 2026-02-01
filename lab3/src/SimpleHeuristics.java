
public class SimpleHeuristics implements Heuristics {
	/**
	 * reference to the environment to be able to figure out positions of obstacles
	 */
	private Environment env;

	/**
	 * @param solvingAgent
	 */
	SimpleHeuristics() {
	}
	
	public void init(Environment env) {
		this.env = env;
	}

	/**
	 * estimates the number of steps between locations a and b by Manhattan
	 * @param a
	 * @param b
	 * @return
	 */
	private int nbSteps(Coordinates a, Coordinates b) {
		return Math.abs(a.x - b.x) + Math.abs(a.y - b.y);
	}

	public int eval(State s) {
		int h = 0;
		// if there is dirt: max of { manhattan distance to dirt + manhattan distance from dirt to home }
		// else manhattan distance to home
		if (s.dirt.isEmpty()) {
			h = nbSteps(s.position, env.home);
		} else {
			for (Coordinates d:s.dirt) {
				int steps = nbSteps(s.position, d) + nbSteps(d, env.home);
				if (steps > h) {
					h = steps;
				}
			}
			h += s.dirt.size(); // sucking up all the dirt
		}
		if (s.turned_on) {
			h++; // to turn off
		}
		return h;
	}
}
