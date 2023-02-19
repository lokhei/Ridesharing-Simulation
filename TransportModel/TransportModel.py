import mesa

from Agents import Passenger, Car

def compute_manhattan(model):
    # TO DO: should be calculating using actual distance travelled 
    total_dist = 0
    for agent in model.schedule.agents:
        total_dist += abs(agent.src.x - agent.next_dest.x) + abs(agent.src.y - agent.next_dest.y)
    return total_dist

class TransportModel(mesa.Model):
    """A model with some number of agents."""

    def __init__(self, num_passengers, num_cars, width, height):
        super().__init__()

        self.num_agents = num_passengers
        self.num_cars = num_cars
        self.grid = mesa.space.MultiGrid(width, height, True)
        self.schedule = mesa.time.RandomActivation(self)
        self.running = True

        # Create passenger agents
        # 1 for now
        # TO DO: Don't create agents all at once? on a schedule, e.g. every 5 timesteps?
        for i in range(self.num_agents):
            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            a = Passenger(self.next_id(), self, self.grid.width, self.grid.height, x, y)
            # self.schedule.add(a)
            self.grid.place_agent(a, (x, y))

        # Create car agents
        # 1 for now
        for i in range(self.num_cars):
            # Add the agent to a random grid cell
            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            a = Car(self.next_id(), self, self.grid.width, self.grid.height, x, y)
            self.schedule.add(a)
            self.grid.place_agent(a, (x, y))

        self.datacollector = mesa.DataCollector(
            model_reporters={"Manhattan": compute_manhattan}, agent_reporters={}
        )

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
