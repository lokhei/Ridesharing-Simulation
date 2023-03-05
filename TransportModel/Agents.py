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
        self.waiting_time = self.random.randrange(5,20)
        self.request_time = step

    def step(self):
        # passenger leaves if past waiting time
        if self.pos and self.model.schedule.steps > self.request_time + self.waiting_time:
            self.model.schedule.remove(self)
            self.model.grid.remove_agent(self)
            print(f"Waited too long - passenger {self.unique_id} has left")



class Car(mesa.Agent):
    """An agent with starting location and target destination"""

    def __init__(self, unique_id, model, x, y, max_passengers=4, step_type = StepType.QUEUE):
        super().__init__(unique_id, model)
        self.step_type = step_type
        self.current =  Location(x, y)
        self.set_next_dest()
        self.passengers = []
        self.max_passengers = max_passengers
        self.model = model
        self.dest_vis = None
        self.is_waiting = False
        self.is_src = True

    def check_arrival_lte_waiting(self, passenger, dest):
        passenger_arrival_constr = passenger.waiting_time + passenger.request_time
        arrival_time = self.calc_manhattan(self.current, dest) + self.model.schedule.steps
        return arrival_time <= passenger_arrival_constr


    def set_next_dest(self):
        if self.model.clients:
            if self.step_type == StepType.QUEUE:
                passenger = self.model.clients[0]
            elif self.step_type == StepType.CLOSEST:
                passenger = self.find_closest()
            elif self.step_type == StepType.WAITING:
                passenger = self.find_closest_waiting()

            # skip passenger if not able to reach passenger location in time
            if not self.check_arrival_lte_waiting(passenger, passenger.src):
                self.model.clients.remove(passenger)
                self.set_next_dest()
            else:
                self.next_dest = passenger.src
                self.is_waiting = False
                self.is_src = True

        else:
            self.is_waiting = True
        


    def move(self):
        if self.current.x < self.next_dest.x:
            self.current = Location(self.current.x+1, self.current.y)
        elif self.current.x > self.next_dest.x:
            self.current = Location(self.current.x-1, self.current.y)
        elif self.current.y < self.next_dest.y:
            self.current = Location(self.current.x, self.current.y+1)
        elif self.current.y > self.next_dest.y:
            self.current = Location(self.current.x, self.current.y-1)

        self.model.grid.move_agent(self, (self.current.x, self.current.y))

        
    def step(self):
        if self.is_waiting and self.model.clients:
            self.set_next_dest()
        self.step_algo()


    def calc_manhattan(self, src, dest):
        return abs(src.x - dest.x) + abs(src.y - dest.y)
        

    def find_closest(self):
        closest = self.model.clients[0]
        min_distance = self.calc_manhattan(self.model.clients[0].src, self.current)
        for p_dests in self.model.clients:
            curr_dist = self.calc_manhattan(p_dests.src, self.current)
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

    def pickup_passenger(self):
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
            self.set_next_dest()
            

    def step_algo(self):
        # if at destination point
        if self.current.x == self.next_dest.x and self.current.y == self.next_dest.y:            
            print("Destination Reached")
            if self.is_src:
                self.pickup_passenger()
                
            elif not self.is_waiting:
                del_pass = self.passengers.pop(0)
                self.model.grid.remove_agent(self.dest_vis)
                self.model.clients.remove(del_pass)
                if self.model.clients:
                    self.set_next_dest()
                    self.is_src = True
                else:
                    self.is_waiting = True
                
            if self.is_waiting:
                print("Waiting for new client")
        
        if not self.is_waiting:
            self.move()

   
    

       

       


       


