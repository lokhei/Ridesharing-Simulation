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

    def __init__(self, num_cars, width, height, multi_pass, seed_int, strategy, total_steps=0):
        super().__init__()

        self.num_cars = num_cars
        self.grid = mesa.space.MultiGrid(width, height, True)
        self.schedule = mesa.time.RandomActivation(self)
        self.running = True
        self.clients = []
        self.cars = []
        self.seed = random.Random(seed_int)

        self.total_steps = total_steps

        # print( num_cars, width, height, multi_pass, seed_int, strategy)
        secondary_id = 0
        if self.total_steps:
            self.num_range = range(1, total_steps//5 + num_cars + 1)
            


        # Create passenger agents
        for _ in range(self.num_cars):
            # Add the agent to a random grid cell
            x = self.seed.randrange(self.grid.width)
            y = self.seed.randrange(self.grid.height)
            # secondary id
            if total_steps:
                secondary_id = self.seed.choice(self.num_range)
                # Remove the chosen number from the range
                num_list = list(self.num_range)
                num_list.remove(secondary_id)
                self.num_range = range(num_list[0], num_list[-1] + 1)
                print(secondary_id)
            a = Passenger(self.next_id(), self, self.grid.width, self.grid.height, x, y, self.schedule.steps, self.seed, secondary_id)
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
            "IdleTime": lambda b: b.idle_time if b.type == "Car" else None,
            "sec_id": lambda b: b.secondary_id if b.type == "Passenger" else None,
            "request_time": lambda b: b.request_time if b.type == "Passenger" else None,
            "pickup_time": lambda b: b.pickup_time if b.type == "Passenger" else None,
            "dropoff_time": lambda b: b.dropoff_time if b.type == "Passenger" else None,
            }
        )

    def step(self):
        self.datacollector.collect(self)
        
        self.schedule.step()
        if (self.schedule.steps % 5 == 0):
            # Create new passenger agent
            x = self.seed.randrange(self.grid.width)
            y = self.seed.randrange(self.grid.height)
            secondary_id = 0

            if self.total_steps:
                secondary_id = self.seed.choice(self.num_range)
                # Remove the chosen number from the range
                num_list = list(self.num_range)
                num_list.remove(secondary_id)
                self.num_range = range(num_list[0], num_list[-1] + 1)
                print(secondary_id)

            a = Passenger(self.next_id(), self, self.grid.width, self.grid.height, x, y, self.schedule.steps, self.seed, secondary_id)
            
            self.schedule.add(a)
            self.clients.append(a)
            self.grid.place_agent(a, (x, y))
      


        
