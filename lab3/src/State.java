import java.util.HashSet;

/**
 * 
 * This class holds all information about the state of the environment and the robot
 *
 */
public class State {
		public Coordinates position;
		public int orientation; // 0,1,2,3 for north, east, south, west
		public boolean turned_on;
		public HashSet<Coordinates> dirt;

		public State() {
			position = new Coordinates(0,0);
			orientation = 0;
			turned_on = false;
			dirt = new HashSet<Coordinates>();
		}

		public State(Coordinates position, int orientation, boolean turned_on, HashSet<Coordinates> dirt) {
			this.position = position;
			this.orientation = orientation;
			this.turned_on = turned_on;
			this.dirt = dirt;
		}

		public Coordinates facingPosition() {
			Coordinates res = (Coordinates)position.clone();
			switch (orientation) {
				case 0: res.y++;
				break;
				case 1: res.x++;
				break;
				case 2: res.y--;
				break;
				case 3: res.x--;
				break;
			}
			return res;
		}

		public String toString() {
			return "State{position: " + position + ", orientation: " + orientation + ", on:" + turned_on + ", #dirt: " + dirt.size() + "}";
		}

		public boolean equals(Object o) {
			if (!(o instanceof State)) {
				return false;
			}
			State s = (State) o;
			return (s.position.equals(position) && s.orientation == orientation && s.turned_on == turned_on && s.dirt.equals(dirt));
		}

		public int hashCode() {
			return position.hashCode() ^ orientation ^ (turned_on ? 1 : 0) ^ dirt.hashCode();
		}
	}
