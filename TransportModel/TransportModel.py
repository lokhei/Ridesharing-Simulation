import mesa
import random

from Agents import Passenger, Car

def compute_manhattan(model):
    total_dist = 0
    for agent in model.schedule.agents:
        if type(agent) == "Car":
            print(total_dist)
            total_dist += abs(agent.current.x - agent.next_dest.x) + abs(agent.current.y - agent.next_dest.y)
    return total_dist

class TransportModel(mesa.Model):
    """A model with some number of agents."""

    def __init__(self, num_cars, width, height, multi_pass, seed_int, strategy):
        super().__init__()

        self.num_cars = num_cars
        self.grid = mesa.space.MultiGrid(width, height, True)
        self.schedule = mesa.time.RandomActivation(self)
        self.running = True
        self.clients = []
        self.cars = []
        self.seed = random.Random(seed_int)


        # Create passenger agents
        for i in range(self.num_cars):
            # Add the agent to a random grid cell
            x = self.seed.randrange(self.grid.width)
            y = self.seed.randrange(self.grid.height)
            a = Passenger(self.next_id(), self, self.grid.width, self.grid.height, x, y, self.schedule.steps, self.seed)
            self.schedule.add(a)

            self.clients.append(a)
            self.grid.place_agent(a, (x, y))

        # Create car agents
        for i in range(self.num_cars):
            # Add the agent to a random grid cell
            x = self.seed.randrange(self.grid.width)
            y = self.seed.randrange(self.grid.height)
            a = Car(self.next_id(), self, x, y, multi_pass, step_type=strategy)
            self.schedule.add(a)
            self.cars.append(a)
            self.grid.place_agent(a, (x, y))

       

        self.datacollector = mesa.DataCollector(
            model_reporters={"Manhattan": compute_manhattan},
            agent_reporters={
            "Steps": lambda a: a.steps_taken if a.type == "Car" else None,
            "WaitingTime": lambda b: b.actual_waiting_time if b.type == "Passenger" else None
            }
        )

    def step(self):
        self.datacollector.collect(self)
        self.schedule.step()
        if (self.schedule.steps % 5 == 0):
            # Create new passenger agent
            x = self.seed.randrange(self.grid.width)
            y = self.seed.randrange(self.grid.height)
            a = Passenger(self.next_id(), self, self.grid.width, self.grid.height, x, y, self.schedule.steps, self.seed)
            self.schedule.add(a)
            self.clients.append(a)
            self.grid.place_agent(a, (x, y))



        
