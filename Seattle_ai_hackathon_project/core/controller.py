"""
Controller for the Smart Traffic Management System Simulation
"""
import random
import numpy as np
from agents.traffic_light import TrafficLightAgent
from agents.vehicle import VehicleAgent
from agents.drone import DroneAgent
from core.comms import MessageBus
from core.grid import Grid


class SimulationController:
    def __init__(self, grid_size=5, num_vehicles=10, num_drones=2, verbose=False):
        """
        Initialize the simulation controller
        
        Args:
            grid_size: Size of the grid (NxN)
            num_vehicles: Number of vehicles to create
            num_drones: Number of drones to deploy
            verbose: Whether to print detailed information
        """
        self.grid = Grid(grid_size)
        self.message_bus = MessageBus()
        self.verbose = verbose
        
        # Time tracking
        self.current_step = 0
        
        # Create agents
        self.traffic_lights = self._create_traffic_lights(grid_size)
        self.vehicles = self._create_vehicles(num_vehicles, grid_size)
        self.drones = self._create_drones(num_drones, grid_size)
        
        # Statistics
        self.stats = {
            'vehicles_arrived': 0,
            'total_waiting_time': 0,
            'total_travel_time': 0,
            'anomalies_detected': 0,
            'congestion_events': 0
        }
    
    def _create_traffic_lights(self, grid_size):
        """Create traffic light agents at intersections"""
        traffic_lights = []
        
        # Place traffic lights at regular intervals
        interval = max(1, grid_size // 3)
        for x in range(interval, grid_size, interval):
            for y in range(interval, grid_size, interval):
                traffic_light = TrafficLightAgent(
                    agent_id=f"TL-{len(traffic_lights) + 1}",
                    position=(x, y)
                )
                traffic_lights.append(traffic_light)
        
        print(f"Created {len(traffic_lights)} traffic lights")
        return traffic_lights
    
    def _create_vehicles(self, num_vehicles, grid_size):
        """Create vehicle agents with random start/end positions"""
        vehicles = []
        
        for i in range(num_vehicles):
            # Generate random start and destination that are different
            start = (random.randint(0, grid_size - 1), random.randint(0, grid_size - 1))
            destination = start
            
            # Ensure destination is different from start
            while destination == start:
                destination = (random.randint(0, grid_size - 1), 
                               random.randint(0, grid_size - 1))
            
            vehicle = VehicleAgent(
                agent_id=f"V-{i + 1}",
                start_position=start,
                destination=destination,
                grid_size=grid_size
            )
            vehicles.append(vehicle)
        
        print(f"Created {len(vehicles)} vehicles")
        return vehicles
    
    def _create_drones(self, num_drones, grid_size):
        """Create drone agents for traffic monitoring"""
        drones = []
        
        for i in range(num_drones):
            # Start drones at different positions
            start = (
                random.randint(0, grid_size - 1),
                random.randint(0, grid_size - 1)
            )
            
            # Assign patrol areas (quadrants of the grid)
            quadrant = i % 4
            x_min = 0 if quadrant in [0, 2] else grid_size // 2
            y_min = 0 if quadrant in [0, 1] else grid_size // 2
            x_max = grid_size // 2 - 1 if quadrant in [0, 2] else grid_size - 1
            y_max = grid_size // 2 - 1 if quadrant in [0, 1] else grid_size - 1
            
            patrol_area = [(x_min, y_min), (x_max, y_max)]
            
            drone = DroneAgent(
                agent_id=f"D-{i + 1}",
                start_position=start,
                grid_size=grid_size,
                patrol_area=patrol_area
            )
            drones.append(drone)
        
        print(f"Created {len(drones)} drones")
        return drones
    
    def step(self):
        """Execute one step of the simulation"""
        self.current_step += 1
        
        # Update all agents
        self._update_traffic_lights()
        self._update_vehicles()
        self._update_drones()
        
        # Process messages
        self._process_communications()
        
        # Update grid state
        self._update_grid()
        
        # Update statistics
        self._update_statistics()
        
        # Optional: Visualize the grid
        if self.verbose:
            self.grid.visualize()
    
    def _update_traffic_lights(self):
        """Update all traffic light agents"""
        for light in self.traffic_lights:
            # Gather nearby vehicle data
            environment_data = self._get_environment_data_for_light(light)
            
            # Update the traffic light
            light.step(environment_data)
            
            # Publish state update
            self.message_bus.publish(
                "traffic_light_update", 
                {"id": light.id, "state": light.get_state()}
            )
    
    def _update_vehicles(self):
        """Update all vehicle agents"""
        for vehicle in self.vehicles:
            if vehicle.state == "ARRIVED":
                continue
                
            # Gather nearby traffic light data
            environment_data = self._get_environment_data_for_vehicle(vehicle)
            
            # Update the vehicle
            vehicle.step(environment_data)
            
            # Publish state update
            self.message_bus.publish(
                "vehicle_update", 
                {"id": vehicle.id, "state": vehicle.get_state()}
            )
    
    def _update_drones(self):
        """Update all drone agents"""
        for drone in self.drones:
            # Gather vehicle data in drone's vicinity
            environment_data = self._get_environment_data_for_drone(drone)
            
            # Update the drone
            drone.step(environment_data)
            
            # Publish anomalies
            if drone.detected_anomalies:
                for anomaly in drone.detected_anomalies:
                    self.message_bus.publish("anomaly_detected", anomaly)
                    
                # Clear processed anomalies
                drone.detected_anomalies = []
            
            # Publish state update
            self.message_bus.publish(
                "drone_update", 
                {"id": drone.id, "state": drone.get_state()}
            )
    
    def _get_environment_data_for_light(self, light):
        """Get environment data needed by traffic light agent"""
        x, y = light.position
        vehicles_ns = 0
        vehicles_ew = 0
        
        # Count vehicles in vicinity
        for vehicle in self.vehicles:
            v_x, v_y = vehicle.position
            manhattan_dist = abs(x - v_x) + abs(y - v_y)
            
            if manhattan_dist <= 2:
                if vehicle.is_moving_north_south():
                    vehicles_ns += 1
                else:
                    vehicles_ew += 1
        
        return {
            'vehicles_ns': vehicles_ns,
            'vehicles_ew': vehicles_ew
        }
    
    def _get_environment_data_for_vehicle(self, vehicle):
        """Get environment data needed by vehicle agent"""
        # Collect nearby traffic light states
        nearby_lights = []
        
        for light in self.traffic_lights:
            l_x, l_y = light.position
            v_x, v_y = vehicle.position
            manhattan_dist = abs(l_x - v_x) + abs(l_y - v_y)
            
            if manhattan_dist <= 1:  # Traffic light is at or adjacent to vehicle
                nearby_lights.append(light.get_state())
        
        # Get congestion information from drones
        congestion_areas = []
        messages = self.message_bus.get_messages("anomaly_detected")
        
        for msg in messages:
            if msg.get('type') == 'congestion':
                congestion_areas.append({
                    'position': msg.get('position'),
                    'level': msg.get('severity', 0)
                })
        
        return {
            'traffic_lights': nearby_lights,
            'congestion': congestion_areas
        }
    
    def _get_environment_data_for_drone(self, drone):
        """Get environment data needed by drone agent"""
        # Collect nearby vehicle states
        vehicle_states = []
        
        for vehicle in self.vehicles:
            if vehicle.state == "ARRIVED":
                continue
                
            vehicle_states.append(vehicle.get_state())
        
        return {
            'vehicles': vehicle_states
        }
    
    def _process_communications(self):
        """Process all pending messages in the message bus"""
        # Process anomaly messages
        anomaly_messages = self.message_bus.get_messages("anomaly_detected")
        for msg in anomaly_messages:
            if msg.get('type') == 'congestion':
                self.stats['congestion_events'] += 1
                print(f"Congestion event detected at {msg.get('position')} "
                      f"with severity {msg.get('severity')}")
            elif msg.get('type') == 'incident':
                self.stats['anomalies_detected'] += 1
                print(f"Traffic incident detected involving vehicle {msg.get('vehicle_id')}")
        
        # Clear processed messages
        self.message_bus.clear()
    
    def _update_grid(self):
        """Update the grid representation"""
        # Clear the grid
        self.grid.clear()
        
        # Add traffic lights
        for light in self.traffic_lights:
            self.grid.add_agent(light.id, light.position, "traffic_light", light.state.value)
        
        # Add vehicles
        for vehicle in self.vehicles:
            if vehicle.state != "ARRIVED":
                self.grid.add_agent(vehicle.id, vehicle.position, "vehicle", vehicle.state)
        
        # Add drones
        for drone in self.drones:
            self.grid.add_agent(drone.id, drone.position, "drone", drone.state)
    
    def _update_statistics(self):
        """Update simulation statistics"""
        # Count arrived vehicles
        arrived_count = 0
        waiting_time = 0
        travel_time = 0
        
        for vehicle in self.vehicles:
            if vehicle.state == "ARRIVED":
                arrived_count += 1
            
            waiting_time += vehicle.waiting_time
            travel_time += vehicle.total_travel_time
        
        self.stats['vehicles_arrived'] = arrived_count
        self.stats['total_waiting_time'] = waiting_time
        self.stats['total_travel_time'] = travel_time
    
    def print_stats(self):
        """Print simulation statistics"""
        print("\n--- Simulation Statistics ---")
        print(f"Steps completed: {self.current_step}")
        print(f"Vehicles arrived at destination: {self.stats['vehicles_arrived']} "
              f"of {len(self.vehicles)} "
              f"({self.stats['vehicles_arrived'] / len(self.vehicles) * 100:.1f}%)")
        
        if len(self.vehicles) > 0:
            print(f"Average waiting time per vehicle: "
                  f"{self.stats['total_waiting_time'] / len(self.vehicles):.2f} steps")
            print(f"Average travel time per vehicle: "
                  f"{self.stats['total_travel_time'] / len(self.vehicles):.2f} steps")
        
        print(f"Total congestion events: {self.stats['congestion_events']}")
        print(f"Total anomalies detected: {self.stats['anomalies_detected']}")
        print("---------------------------")