"""Capacited Vehicles Routing Problem (CVRP)."""

from __future__ import print_function
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
import matplotlib.pyplot as plt
from itertools import cycle
from urllib.request import urlopen

#dorobione ----------
def get_string_from_website(website):
    url = website
    output = urlopen(url).read()
    file_string = (output.decode('utf-8'))
    return file_string

def parse_file(file_string):
    file_string_split = file_string.split('\n')  # --> ['Line 1', 'Line 2', 'Line 3']
    for i in file_string_split:
        #wszystkie rzeczy potrzebne do skryptu
        if("NAME" in i):
            name = i.split(": ", 1)[1]
        if ("CAPACITY" in i):
            capacity = int(i.split(": ", 1)[1])
        if("DIMENSION" in i):
            dimension = int(i.split(": ", 1)[1])
        if("NODE_COORD_SECTION" in i):
            index_coord = file_string_split.index(i) + 1
        if("DEMAND_SECTION" in i):
            index_demand = file_string_split.index(i) + 1
        if("trucks: " in i):
            trucks = int(i.split("trucks: ", 1)[1][:1])
        if("Optimal value: " in i ):
            optimal_value = int(i.split("Optimal value: ", 1)[1][:-1])
    capacity= [capacity] * trucks
    points_string = file_string_split[index_coord:index_coord+dimension]
    demands_string = file_string_split[index_demand:index_demand+dimension]
    point_int = []
    for point in points_string:
        point = point.split(" ")
        point_int.append((float(point[1]),float(point[2])))
    demand_int = []
    for demand in demands_string:
        demand = demand.split(" ")
        demand_int.append((int(demand[1])))
    return name,capacity,dimension,point_int,demand_int,trucks,optimal_value

def compute_distance(x1, y1, x2, y2):
    return abs(x1-x2)+abs(y1-y2)

def compute_distance_matrix(points):
    distance_vector = []
    distance_matrix = []
    for point in points:
        for i in range(len(points)):
            distance_vector.append(compute_distance(point[0],point[1],points[i][0],points[i][1]))
        distance_matrix.append(distance_vector)
        distance_vector = []
    return distance_matrix

def connectpoints(x,y,p1,p2):
    x1, x2 = x[p1], x[p2]
    y1, y2 = y[p1], y[p2]
    plt.plot([x1,x2],[y1,y2],'k-')

def connectpoints2(x,y,routes):
    cycol = cycle('bgrcmk')
    for route in routes:
        color = next(cycol)
        for i in range(len(route)):
            if i is not len(route)-1:
                # print(route[i],route[i+1])
                x1, x2 = x[route[i]], x[route[i+1]]
                y1, y2 = y[route[i]], y[route[i+1]]
                plt.plot([x1,x2],[y1,y2],color+'-',label='Dupa')

def create_plot(points,routes,vehicle_distance,name,ffs, time, lso):
    x = []
    y = []
    trigger = True
    vehicles = list(range(1,len(vehicle_distance)+1))
    index = 0
    for point in points:
        x.append(point[0])
        y.append(point[1])
    plt.plot(x, y, 'ro')
    cycol = cycle('bgrcmyk')
    for route in routes:
        color = next(cycol)
        for i in range(len(route)):
            if i is not len(route) - 1:
                x1, x2 = x[route[i]], x[route[i + 1]]
                y1, y2 = y[route[i]], y[route[i + 1]]
                if trigger:
                    plt.plot([x1, x2], [y1, y2], color + '-', label='Vehicle {}'.format(vehicles[index]))
                    index+=1
                    trigger = False
                else:
                    #wykres linia pomiędzy punktami
                    plt.plot([x1, x2], [y1, y2], color + '-')
        trigger = True
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.title(name)
    plt.savefig('static\img\plot_img_'+name+'_'+str(ffs)+'_'+str(lso)+'_'+time+'.png',bbox_inches='tight')
    plt.clf()



def create_data_model(file_string):
    """Stores the data for the problem."""
    data = {}
    name, capacity, dimension, points, demands, vehicles, optimal_value = parse_file(file_string)
    distance_matrix = compute_distance_matrix(points)
    data['distance_matrix'] = distance_matrix
    data['demands'] = demands
    data['vehicle_capacities'] = capacity
    data['num_vehicles'] = vehicles
    data['depot'] = 0
    data['points'] = points
    return data, name

def get_routes(manager, routing, solution, num_routes):
  """Get vehicle routes from a solution and store them in an array."""
  # Get vehicle routes and store them in a two dimensional array whose
  # i,j entry is the jth location visited by vehicle i along its route.
  routes = []
  for route_nbr in range(num_routes):
    index = routing.Start(route_nbr)
    route = [manager.IndexToNode(index)]
    while not routing.IsEnd(index):
      index = solution.Value(routing.NextVar(index))
      route.append(manager.IndexToNode(index))
    routes.append(route)
  return routes



def print_solution(data, manager, routing, assignment):
    """Prints assignment on console."""
    total_distance = 0
    total_load = 0
    vehicle_distance = []
    vehicle_load = []
    text = []
    for vehicle_id in range(data['num_vehicles']):
        index = routing.Start(vehicle_id)
        plan_output = 'Route for vehicle {}:\n'.format(vehicle_id+1)
        route_distance = 0
        route_load = 0
        while not routing.IsEnd(index):
            node_index = manager.IndexToNode(index)
            route_load += data['demands'][node_index]
            plan_output += ' {0} Load({1}) -> '.format(node_index, route_load)
            previous_index = index
            index = assignment.Value(routing.NextVar(index))
            route_distance += routing.GetArcCostForVehicle(
                previous_index, index, vehicle_id)
        plan_output += ' {0} Load({1})\n'.format(manager.IndexToNode(index),
                                                 route_load)
        text.append(plan_output)
        plan_output += 'Distance of the route: {}m\n'.format(route_distance)
        plan_output += 'Load of the route: {}\n'.format(route_load)
        vehicle_distance.append(route_distance)
        vehicle_load.append(route_load)
        # print(plan_output)
        total_distance += route_distance
        total_load += route_load
    # print('Total distance of all routes: {}m'.format(total_distance))
    # print('Total load of all routes: {}'.format(total_load))
    return vehicle_distance, vehicle_load, text

def cvrp_fun(file_string, ffs, time, lso):
    """Solve the CVRP problem."""
    # Instantiate the data problem.
    data, name = create_data_model(file_string)
    # Create the routing index manager.
    manager = pywrapcp.RoutingIndexManager(len(data['distance_matrix']),
                                           data['num_vehicles'], data['depot'])
    # Create Routing Model.
    routing = pywrapcp.RoutingModel(manager)
    # Create and register a transit callback.

    def distance_callback(from_index, to_index):
        """Returns the distance between the two nodes."""
        # Convert from routing variable Index to distance matrix NodeIndex.
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    # Define cost of each arc.
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)
    # Add Capacity constraint.

    def demand_callback(from_index):
        """Returns the demand of the node."""
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return data['demands'][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(
        demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # null capacity slack
        data['vehicle_capacities'],  # vehicle maximum capacities
        True,  # start cumul to zero
        'Capacity')
    # Setting first solution heuristic.
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    #metaheurystyka
    search_parameters.first_solution_strategy = getattr(routing_enums_pb2.FirstSolutionStrategy, ffs)
    search_parameters.local_search_metaheuristic = getattr(routing_enums_pb2.LocalSearchMetaheuristic, lso)
    search_parameters.time_limit.seconds = int(time)
    # Solve the problem.
    assignment = routing.SolveWithParameters(search_parameters)
    # Print solution on console.
    if assignment:
        vehicle_distance, vehicle_load, text = print_solution(data, manager, routing, assignment)
    routes = get_routes(manager, routing, assignment, data['num_vehicles'])
    # Display the routes.
    create_plot(data['points'],routes, vehicle_distance,name, ffs, time, lso)
    return vehicle_distance, vehicle_load, text, name