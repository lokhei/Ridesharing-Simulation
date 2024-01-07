import argparse
import mesa
from TransportModel import TransportModel, Driver, Passenger
from Agents import StepType


def agent_portrayal(agent):
    portrayal = {
        "Shape": "circle",
        "Color": "green",
        "Filled": "true",
        "Layer": 0.1,
        "r": 0.5,
    }
    if type(agent) is Driver:
        portrayal["Shape"] = "Images\icons8-people-in-car-side-view-50.png"
       
    elif type(agent) is Passenger:
        portrayal["Shape"] = "Images\icons8-body-type-short-50.png"

    else:
        portrayal["Shape"] = "circle"
        portrayal["Layer"] = 0
    return portrayal


def run_vis():
    parser = argparse.ArgumentParser(description='Run ridesharing simulation visualisation')

    parser.add_argument('--multi_pass', type=bool, required=False, help='Set to True for multi passenger system of False for single passenger')
    parser.add_argument('--num_drivers', type=int, required=False, help='Number of drivers in model')
    parser.add_argument('--size', type=int, required=False, help='Grid size')
    parser.add_argument('--seed', type=int, required=False, help='Random seed')
    parser.add_argument('--strategy', type=int, required=False, help='Strategy to employ: QUEUE = 1, CLOSEST = 2, WAITING = 3')
    parser.add_argument('--waiting_time', type=int, required=False, help='Passenger waiting time before they leave')
    parser.add_argument('--rate', type=int, required=False, help='Rate at which new passenger requests come in')

    args = parser.parse_args()
    multi_pass = args.multi_pass if args.multi_pass else False
    num_drivers = args.num_drivers if args.num_drivers else 5
    seed = args.seed if args.seed else 125
    size = args.size if args.size else 10
    strategy = StepType(args.strategy) if args.strategy else StepType.CLOSEST
    waiting_time = args.waiting_time if args.waiting_time else None
    rate = args.rate if args.rate else 5


    grid = mesa.visualization.CanvasGrid(agent_portrayal,10,10,500,500)


    # configure and run the server
    server = mesa.visualization.ModularServer(
        TransportModel, [grid], 'Transport Model',
        {'num_drivers': num_drivers,
         'size' : size,
         'multi_pass' : multi_pass,
         'seed_int': seed,
         'strategy' : strategy,
         'waiting_time': waiting_time,
         'rate': rate
        }
    )

    server.port = 8521 # default
    server.launch()


if __name__ == "__main__":
    run_vis()
        
