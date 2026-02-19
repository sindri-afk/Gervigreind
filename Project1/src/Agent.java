
public interface Agent
{
    public void init(String role, int width, int height, int playclock, int[][] white_positions, int[][] black_positions);
    public String nextAction(int[] lastmove);
    public void cleanup();
}
