import mesa
from mesa.visualization.modules import CanvasGrid, ChartModule
from TransportModel import TransportModel, Car, Passenger
from Agents import StepType


def agent_portrayal(agent):
    portrayal = {
        "Shape": "circle",
        "Color": "green",
        "Filled": "true",
        "Layer": 0.1,
        "r": 0.5,
    }

    if type(agent) is Car:
        portrayal["Shape"] = "Images\icons8-people-in-car-side-view-50.png"
       
    elif type(agent) is Passenger:
        portrayal["Shape"] = "Images\icons8-body-type-short-50.png"

    else:
        portrayal["Shape"] = "circle"
        portrayal["Layer"] = 0
    return portrayal


grid = mesa.visualization.CanvasGrid(agent_portrayal,10,10,500,500)


# configure and run the server
server = mesa.visualization.ModularServer(
    TransportModel, [grid], 'Transport Model', {'num_cars': 2, 'width' : 10, 'height' : 10, 'multi_pass' : False, 'seed_int': 1, 'strategy' : StepType.CLOSEST}
)

server.port = 8521 # default
server.launch()
    
