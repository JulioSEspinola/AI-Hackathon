"""
Vehicle Agent for the Smart Traffic Management System
"""
import random
import numpy as np


class VehicleState:
    MOVING = "MOVING"
    WAITING = "WAITING"
    REROUTING = "REROUTING"
    ARRIVED = "ARRIVED"


class VehicleAgent:
    def __init__(self, agent_id, start_position, destination, grid_size):
        """
        Initialize a vehicle agent
        
        Args:
            agent_id: Unique identifier for this vehicle
            start_position: (x, y) starting coordinates
            destination: (x, y) destination coordinates
            grid_size: Size of the grid (for boundary checks)
        """
        self.id = agent_id
        self.position = start_position
        self.destination = destination
        self.grid_size = grid_size
        self.state = VehicleState.MOVING
        
        # Initialize a simple path (will be replaced with routing)
        self.path = self._calculate_simple_path()
        self.path_index = 0
        
        # Stats
        self.waiting_time = 0
        self.total_travel_time = 0
        self.stops = 0
        
        # Speed in grid cells per step
        self.speed = 1
    
    def _calculate_simple_path(self):
        """Calculate a simple path from start to destination"""
        path = []
        current = self.position
        
        # Simple Manhattan path
        # First move along x-axis
        x_direction = 1 if self.destination[0] > current[0] else -1
        while current[0] != self.destination[0]:
            current = (current[0] + x_direction, current[1])
            path.append(current)
        
        # Then move along y-axis
        y_direction = 1 if self.destination[1] > current[1] else -1
        while current[1] != self.destination[1]:
            current = (current[0], current[1] + y_direction)
            path.append(current)
        
        return path
    
    def step(self, environment_data=None):
        """
        Update the vehicle state and position
        
        Args:
            environment_data: Data from the environment (traffic lights, congestion)
        """
        self.total_travel_time += 1
        
        if self.state == VehicleState.ARRIVED:
            return
        
        # Check if we're at a traffic light intersection
        if environment_data and 'traffic_lights' in environment_data:
            for light in environment_data['traffic_lights']:
                if light['position'] == self.position:
                    # Check if the light is red for our direction
                    is_red_for_us = (
                        (light['state'] == 'RED') or
                        (light['state'] == 'YELLOW') or
                        (light['direction'] == 'East-West' and 
                         self.is_moving_north_south()) or
                        (light['direction'] == 'North-South' and 
                         not self.is_moving_north_south())
                    )
                    
                    if is_red_for_us:
                        self.state = VehicleState.WAITING
                        self.waiting_time += 1
                        print(f"Vehicle {self.id} waiting at traffic light {light['id']}")
                        return
        
        # Check for congestion
        if environment_data and 'congestion' in environment_data:
            for area in environment_data['congestion']:
                if area['position'] == self.position and area['level'] > 7:
                    # Consider rerouting if severe congestion
                    if random.random() < 0.3:  # 30% chance to reroute
                        self.state = VehicleState.REROUTING
                        print(f"Vehicle {self.id} rerouting due to congestion")
                        self._recalculate_path(environment_data)
                        self.state = VehicleState.MOVING
                    else:
                        # Slow down due to congestion
                        self.waiting_time += 1
                        print(f"Vehicle {self.id} slowed by congestion")
                        return
        
        # If we were waiting, count it as a stop
        if self.state == VehicleState.WAITING:
            self.stops += 1
        
        # Move to the next position in the path
        self.state = VehicleState.MOVING
        if self.path_index < len(self.path):
            self.position = self.path[self.path_index]
            self.path_index += 1
            print(f"Vehicle {self.id} moved to {self.position}")
            
            # Check if we've reached the destination
            if self.position == self.destination:
                self.state = VehicleState.ARRIVED
                print(f"Vehicle {self.id} arrived at destination {self.destination}")
        else:
            self.state = VehicleState.ARRIVED
            print(f"Vehicle {self.id} has completed its journey")
    
    def _recalculate_path(self, environment_data):
        """Recalculate path based on current traffic conditions"""
        # In a real implementation, this would use traffic data to find
        # the optimal path. For now, we'll just add some randomness.
        remaining_path = self.path[self.path_index:]
        
        # Add some random detours
        new_path = []
        current = self.position
        
        for next_pos in remaining_path:
            # 20% chance to take a detour at each step
            if random.random() < 0.2:
                # Try to find a valid detour
                for _ in range(3):  # Try up to 3 times
                    dx, dy = random.choice([(0, 1), (1, 0), (0, -1), (-1, 0)])
                    detour = (current[0] + dx, current[1] + dy)
                    
                    # Check if the detour is within grid boundaries
                    if (0 <= detour[0] < self.grid_size and 
                        0 <= detour[1] < self.grid_size):
                        new_path.append(detour)
                        current = detour
                        break
            
            new_path.append(next_pos)
            current = next_pos
        
        # Update the path
        self.path = self.path[:self.path_index] + new_path
        print(f"Vehicle {self.id} recalculated path")
    
    def is_moving_north_south(self):
        """Determine if the vehicle is currently moving north-south"""
        if self.path_index + 1 < len(self.path):
            next_pos = self.path[self.path_index]
            current_pos = self.position
            # If x coordinate is the same, we're moving north-south
            return next_pos[0] == current_pos[0]
        return False
    
    def get_state(self):
        """Get the current state of the vehicle"""
        return {
            'id': self.id,
            'position': self.position,
            'destination': self.destination,
            'state': self.state,
            'waiting_time': self.waiting_time,
            'total_travel_time': self.total_travel_time,
            'stops': self.stops,
            'progress': 
                f"{min(100, int(self.path_index / len(self.path) * 100))}%" 
                if len(self.path) > 0 else "N/A"
        }