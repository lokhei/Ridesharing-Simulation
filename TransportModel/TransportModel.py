import mesa

from dataclasses import dataclass

@dataclass
class Location:
    x: int
    y: int

def compute_manhattan(model):
    # TO DO: should be calculating using actual distance travelled 
    total_dist = 0
    for agent in model.schedule.agents:
        total_dist += abs(agent.src.x - agent.dest.x) + abs(agent.src.y - agent.dest.y)
    return total_dist


class PassengerAgent(mesa.Agent):
    """An agent with starting location and target destination"""

    def __init__(self, unique_id, model, grid_width, grid_height, x, y):
        super().__init__(unique_id, model)
        self.src = Location(x, y)
        self.current = self.src
        self.dest = Location(self.random.randrange(grid_width),self.random.randrange(grid_height))
        print(self.src, self.dest)

    def move(self):
        if self.current.x < self.dest.x:
            self.current = Location(self.current.x+1, self.current.y)
        elif self.current.x > self.dest.x:
            self.current = Location(self.current.x-1, self.current.y)
        elif self.current.y < self.dest.y:
            self.current = Location(self.current.x, self.current.y+1)
        else:
            self.current = Location(self.current.x, self.current.y-1)

        self.model.grid.move_agent(self, (self.current.x, self.current.y))

        
    def step(self):
        if self.current.x == self.dest.x and self.current.y == self.dest.y:            
            print("Destination Reached")
        else:
            self.move()



class TransportModel(mesa.Model):
    """A model with some number of agents."""

    def __init__(self, num_agents, width, height):
        self.num_agents = num_agents
        self.grid = mesa.space.MultiGrid(width, height, True)
        self.schedule = mesa.time.RandomActivation(self)
        self.running = True

        # Create agents
        # TO DO: Don't create agents all at once? on a schedule, e.g. every 5 timesteps?
        for i in range(self.num_agents):
            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            a = PassengerAgent(i, self, self.grid.width, self.grid.height, x, y)
            self.schedule.add(a)
            self.grid.place_agent(a, (x, y))

        self.datacollector = mesa.DataCollector(
            model_reporters={"Manhattan": compute_manhattan}, agent_reporters={}
        )

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
