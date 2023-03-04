import mesa

from dataclasses import dataclass
from enum import Enum

@dataclass
class Location:
    x: int
    y: int

@dataclass
class PassengerLoc:
    src: Location
    dest: Location

class StepType(Enum):
    QUEUE = 1
    CLOSEST = 2
    WAITING = 3


class destVis(mesa.Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)


class Passenger(mesa.Agent):
    """An agent with starting location and target destination"""

    def __init__(self, unique_id, model, grid_width, grid_height, x, y, step, num_people = 1):
        super().__init__(unique_id, model)
        self.src = Location(x, y)

        self.dest = Location(self.random.randrange(grid_width),self.random.randrange(grid_height))
        while self.src == self.dest:
            self.dest = Location(self.random.randrange(grid_width),self.random.randrange(grid_height))
        self.num_people = num_people
        print(f"Agent {unique_id}: {self.src} to {self.dest}")
        self.waiting_time = self.random.randrange(5,50)
        self.request_time = step

    def step(self):
        # passenger leaves if past waiting time
        if self.pos and self.model.schedule.steps > self.request_time + self.waiting_time:
            self.model.schedule.remove(self)
            self.model.grid.remove_agent(self)
            self.model.clients.remove(self)
            print(f"Waited too long - passenger {self.unique_id} has left")



class Car(mesa.Agent):
    """An agent with starting location and target destination"""

    def __init__(self, unique_id, model, x, y, max_passengers=4, step_type = StepType.QUEUE):
        super().__init__(unique_id, model)
        self.step_type = step_type
        self.current =  Location(x, y)
        self.destinations = self.get_destinations()
        if self.step_type == StepType.QUEUE:
            self.next_dest = self.destinations[0].src
        elif self.step_type == StepType.CLOSEST:
            self.next_dest = self.find_closest().src
        elif self.step_type == StepType.WAITING:
            self.next_dest = self.find_closest_waiting().src
        self.passengers = []
        self.max_passengers = max_passengers
        self.model = model
        self.dest_vis = None
        self.is_src = True


    def get_destinations(self):
        destinations = []
        for client in self.model.clients:
            destinations.append(PassengerLoc(client.src, client.dest))

        return destinations
    
    def update_destinations(self, passenger):
        if passenger.num_people < self.max_passengers:
            self.destinations.append(PassengerLoc(passenger.src, passenger.dest))
            if len(self.destinations)==1:
                self.next_dest = passenger.src
                self.is_src = True


    def move(self):
        if self.current.x < self.next_dest.x:
            self.current = Location(self.current.x+1, self.current.y)
        elif self.current.x > self.next_dest.x:
            self.current = Location(self.current.x-1, self.current.y)
        elif self.current.y < self.next_dest.y:
            self.current = Location(self.current.x, self.current.y+1)
        else:
            self.current = Location(self.current.x, self.current.y-1)

        self.model.grid.move_agent(self, (self.current.x, self.current.y))

        
    def step(self):
        if self.step_type == StepType.QUEUE:
            self.step_queue()
        elif self.step_type == StepType.CLOSEST or self.step_type == StepType.WAITING:
            self.step_closest_waiting()

        
    def step_queue(self):
        if self.current.x == self.next_dest.x and self.current.y == self.next_dest.y:            
            print("Destination Reached")
            if self.destinations and self.next_dest == self.destinations[0].src:
                self.next_dest = self.destinations[0].dest
                self.dest_vis = destVis(self.model.next_id(), self)
                self.model.grid.place_agent(self.dest_vis, (self.next_dest.x, self.next_dest.y))

                this_cell = self.model.grid.get_cell_list_contents([self.pos])
                potential_passengers = [obj for obj in this_cell if isinstance(obj, Passenger)]

                if len(potential_passengers) > 0 and sum(client.num_people for client in potential_passengers) < self.max_passengers:
                    passenger = potential_passengers[0]
                    self.model.grid.remove_agent(passenger)
                    self.model.clients.remove(passenger)
                    self.passengers.append(passenger)

            elif self.destinations and self.next_dest == self.destinations[0].dest:
                self.destinations.pop(0)
                self.model.grid.remove_agent(self.dest_vis)
                self.passengers.pop(0)

                if self.destinations:
                    self.next_dest = self.destinations[0].src
                    
            if not self.destinations:
                print("Waiting for new client")
        if self.destinations:
            self.move()

        

    def find_closest(self):
        closest = self.destinations[0]
        min_distance = abs(self.destinations[0].src.x - self.current.x) + abs(self.destinations[0].src.y - self.current.y)
        for p_dests in self.destinations:
            curr_dist = abs(p_dests.src.x - self.current.x) + abs(p_dests.src.y - self.current.y)
            if min_distance > curr_dist:
                min_distance = curr_dist
                closest = p_dests

        return closest
    
    def find_closest_waiting(self):
        most_urgent = self.model.clients[0]
        min_waiting = self.model.clients[0].waiting_time + self.model.clients[0].request_time
        for passenger in self.model.clients:
            curr_wait = passenger.waiting_time + passenger.request_time
            if min_waiting > curr_wait:
                min_waiting = curr_wait
                most_urgent = passenger

        return most_urgent



    def step_closest_waiting(self):
        # if at destination point
        if self.current.x == self.next_dest.x and self.current.y == self.next_dest.y:            
            print("Destination Reached")
            if self.is_src:
                this_cell = self.model.grid.get_cell_list_contents([self.pos])
                potential_passengers = [obj for obj in this_cell if isinstance(obj, Passenger)]
                if len(potential_passengers) > 0 and sum(client.num_people for client in potential_passengers) < self.max_passengers:
                    passenger = potential_passengers[0]
                    self.model.grid.remove_agent(passenger)
                    self.passengers.append(passenger)
                
                    self.next_dest = self.passengers[0].dest
                    self.dest_vis = destVis(self.model.next_id(), self)
                    self.model.grid.place_agent(self.dest_vis, (self.next_dest.x, self.next_dest.y))
                    self.is_src = False
                else:
                    if self.step_type == StepType.CLOSEST:
                        self.next_dest = self.find_closest().src
                    elif self.step_type == StepType.WAITING:
                        self.next_dest = self.find_closest_waiting().src
                
            else:
                del_pass = self.passengers.pop(0)
                self.destinations.remove(PassengerLoc(del_pass.src, del_pass.dest))
                self.model.grid.remove_agent(self.dest_vis)
                self.model.clients.remove(del_pass)

                if self.destinations:
                    if self.step_type == StepType.CLOSEST:
                        self.next_dest = self.find_closest().src
                    elif self.step_type == StepType.WAITING:
                        self.next_dest = self.find_closest_waiting().src
                self.is_src = True
                
            if not self.destinations:
                print("Waiting for new client")
        
        if self.destinations:
            self.move()

   
    

       

       


       


