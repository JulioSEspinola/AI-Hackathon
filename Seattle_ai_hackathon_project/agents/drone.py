"""
Drone Agent for the Smart Traffic Management System
"""
import random
import numpy as np


class DroneState:
    PATROLLING = "PATROLLING"
    MONITORING = "MONITORING"
    REPORTING = "REPORTING"
    RETURNING = "RETURNING"


class DroneAgent:
    def __init__(self, agent_id, start_position, grid_size, patrol_area=None):
        """
        Initialize a drone agent
        
        Args:
            agent_id: Unique identifier for this drone
            start_position: (x, y) starting coordinates
            grid_size: Size of the grid (for boundary checks)
            patrol_area: Area to patrol [(x1,y1), (x2,y2)] or None for random patrol
        """
        self.id = agent_id
        self.position = start_position
        self.grid_size = grid_size
        self.state = DroneState.PATROLLING
        
        # Set patrol area (default is the entire grid)
        self.patrol_area = patrol_area or [(0, 0), (grid_size - 1, grid_size - 1)]
        
        # Movement parameters
        self.speed = 1  # Grid cells per step
        self.battery = 100  # Battery level (decreases over time)
        self.battery_drain_rate = 0.5
        
        # Patrol waypoints
        self.waypoints = self._generate_patrol_waypoints()
        self.current_waypoint_index = 0
        
        # Observations
        self.detected_anomalies = []
        self.traffic_density_map = np.zeros((grid_size, grid_size))
    
    def _generate_patrol_waypoints(self):
        """Generate waypoints for the patrol route"""
        x_min, y_min = self.patrol_area[0]
        x_max, y_max = self.patrol_area[1]
        
        # Generate waypoints around the perimeter with some randomness
        waypoints = []
        
        # Add corners and midpoints with slight randomness
        corners = [
            (x_min, y_min), (x_max, y_min),
            (x_max, y_max), (x_min, y_max)
        ]
        
        # Add corners and some random points
        waypoints.extend(corners)
        
        # Add some random waypoints within the area
        num_random_points = random.randint(3, 6)
        for _ in range(num_random_points):
            x = random.randint(x_min, x_max)
            y = random.randint(y_min, y_max)
            waypoints.append((x, y))
        
        # Shuffle the waypoints for more realistic patrol
        random.shuffle(waypoints)
        
        # Add start position at the beginning to close the loop
        waypoints.append(self.position)
        
        return waypoints
    
    def step(self, environment_data=None):
        """
        Update the drone state and position
        
        Args:
            environment_data: Data from the environment (vehicle positions, etc.)
        """
        # Reduce battery level
        self.battery -= self.battery_drain_rate
        
        # Handle low battery
        if self.battery < 20 and self.state != DroneState.RETURNING:
            self.state = DroneState.RETURNING
            print(f"Drone {self.id} has low battery ({self.battery:.1f}%), returning to base")
            # Set waypoint to return to base
            self.waypoints = [self.position, (0, 0)]
            self.current_waypoint_index = 0
        
        # Reset battery if returned to base
        if self.state == DroneState.RETURNING and self.position == (0, 0):
            self.battery = 100
            self.state = DroneState.PATROLLING
            print(f"Drone {self.id} recharged at base, resuming patrol")
            self.waypoints = self._generate_patrol_waypoints()
            self.current_waypoint_index = 0
        
        # Process environment data
        if environment_data and 'vehicles' in environment_data:
            self._monitor_traffic(environment_data['vehicles'])
        
        # Move towards current waypoint
        if self.current_waypoint_index < len(self.waypoints):
            target = self.waypoints[self.current_waypoint_index]
            
            # Calculate direction vector
            dx = target[0] - self.position[0]
            dy = target[1] - self.position[1]
            
            # Normalize and scale by speed
            distance = max(1, (dx**2 + dy**2)**0.5)
            move_x = int(round(dx / distance * self.speed))
            move_y = int(round(dy / distance * self.speed))
            
            # Update position
            new_x = self.position[0] + move_x
            new_y = self.position[1] + move_y
            
            # Ensure we stay within grid boundaries
            new_x = max(0, min(self.grid_size - 1, new_x))
            new_y = max(0, min(self.grid_size - 1, new_y))
            
            self.position = (new_x, new_y)
            
            # Check if we've reached the waypoint
            if abs(self.position[0] - target[0]) <= 1 and abs(self.position[1] - target[1]) <= 1:
                self.current_waypoint_index += 1
                if self.current_waypoint_index >= len(self.waypoints):
                    # Start over the patrol route
                    self.current_waypoint_index = 0
                    self.waypoints = self._generate_patrol_waypoints()
                
                print(f"Drone {self.id} reached waypoint, heading to next point")
    
    def _monitor_traffic(self, vehicles):
        """Monitor traffic density and detect anomalies"""
        # Reset density at current position
        x, y = self.position
        self.traffic_density_map[y, x] = 0
        
        # Count vehicles in the vicinity (Manhattan distance <= 2)
        nearby_vehicles = []
        for vehicle in vehicles:
            v_x, v_y = vehicle['position']
            manhattan_dist = abs(x - v_x) + abs(y - v_y)
            if manhattan_dist <= 2:
                nearby_vehicles.append(vehicle)
                # Update traffic density
                self.traffic_density_map[y, x] += 1
        
        # Detect congestion (more than 3 vehicles in close proximity)
        if len(nearby_vehicles) > 3:
            self.state = DroneState.REPORTING
            congestion = {
                'type': 'congestion',
                'position': self.position,
                'vehicles': len(nearby_vehicles),
                'severity': min(10, len(nearby_vehicles))
            }
            self.detected_anomalies.append(congestion)
            print(f"Drone {self.id} detected congestion at {self.position} "
                  f"with {len(nearby_vehicles)} vehicles")
            
            # Report, then go back to patrolling
            self.state = DroneState.PATROLLING
        
        # Detect vehicles in WAITING state for too long (potential incident)
        for vehicle in nearby_vehicles:
            if vehicle['state'] == 'WAITING' and vehicle['waiting_time'] > 10:
                self.state = DroneState.REPORTING
                incident = {
                    'type': 'incident',
                    'position': vehicle['position'],
                    'vehicle_id': vehicle['id'],
                    'waiting_time': vehicle['waiting_time']
                }
                self.detected_anomalies.append(incident)
                print(f"Drone {self.id} detected potential incident: "
                      f"Vehicle {vehicle['id']} waiting too long at {vehicle['position']}")
                
                # Report, then go back to patrolling
                self.state = DroneState.PATROLLING
    
    def get_state(self):
        """Get the current state of the drone"""
        return {
            'id': self.id,
            'position': self.position,
            'state': self.state,
            'battery': f"{self.battery:.1f}%",
            'anomalies_detected': len(self.detected_anomalies),
            'current_waypoint': 
                self.waypoints[self.current_waypoint_index] 
                if self.current_waypoint_index < len(self.waypoints) else None
        }