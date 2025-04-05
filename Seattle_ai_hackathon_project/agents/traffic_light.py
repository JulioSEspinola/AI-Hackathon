"""
Traffic Light Agent for the Smart Traffic Management System
"""
from enum import Enum
import random


class TrafficLightState(Enum):
    RED = "RED"
    YELLOW = "YELLOW"
    GREEN = "GREEN"


class TrafficLightAgent:
    def __init__(self, agent_id, position, initial_state=None):
        """
        Initialize a traffic light agent
        
        Args:
            agent_id: Unique identifier for this traffic light
            position: (x, y) coordinates of the intersection
            initial_state: Initial state of the traffic light (defaults to random)
        """
        self.id = agent_id
        self.position = position
        self.state = initial_state or random.choice(list(TrafficLightState))
        self.timer = 0
        
        # Default timing parameters (can be dynamically adjusted)
        self.red_duration = 30
        self.yellow_duration = 5
        self.green_duration = 30
        
        # Traffic statistics
        self.vehicles_passed = 0
        self.congestion_level = 0  # 0-10 scale
        
        # Direction (0: North-South open, 1: East-West open)
        self.direction = 0
    
    def step(self, environment_data=None):
        """
        Update the traffic light state based on current conditions
        
        Args:
            environment_data: Data from the environment (nearby vehicles, congestion)
        """
        self.timer += 1
        
        # Process incoming data to assess traffic conditions
        if environment_data:
            # Count vehicles waiting in each direction
            self._analyze_traffic(environment_data)
        
        # Simple state machine logic
        if self.state == TrafficLightState.RED:
            if self.timer >= self.red_duration:
                self.state = TrafficLightState.GREEN
                self.timer = 0
                # Toggle direction
                self.direction = 1 - self.direction
                print(f"Traffic light {self.id} at {self.position} changed to GREEN for "
                      f"{'East-West' if self.direction == 1 else 'North-South'}")
        
        elif self.state == TrafficLightState.YELLOW:
            if self.timer >= self.yellow_duration:
                self.state = TrafficLightState.RED
                self.timer = 0
                print(f"Traffic light {self.id} at {self.position} changed to RED")
        
        elif self.state == TrafficLightState.GREEN:
            if self.timer >= self.green_duration:
                self.state = TrafficLightState.YELLOW
                self.timer = 0
                print(f"Traffic light {self.id} at {self.position} changed to YELLOW")
    
    def _analyze_traffic(self, environment_data):
        """
        Analyze traffic conditions to potentially adjust timing
        """
        # Simple adaptive logic
        vehicles_ns = environment_data.get('vehicles_ns', 0)
        vehicles_ew = environment_data.get('vehicles_ew', 0)
        
        # Adjust timing based on traffic density
        if vehicles_ns > vehicles_ew * 1.5 and self.direction == 1:
            # More vehicles in North-South, reduce East-West green time
            self.green_duration = max(15, self.green_duration - 5)
            print(f"Traffic light {self.id}: Adjusting green time to {self.green_duration} due to N-S congestion")
        elif vehicles_ew > vehicles_ns * 1.5 and self.direction == 0:
            # More vehicles in East-West, reduce North-South green time
            self.green_duration = max(15, self.green_duration - 5)
            print(f"Traffic light {self.id}: Adjusting green time to {self.green_duration} due to E-W congestion")
        else:
            # Balance traffic, restore default timing
            self.green_duration = min(45, self.green_duration + 1)
    
    def get_state(self):
        """
        Get the current state of the traffic light
        """
        return {
            'id': self.id,
            'position': self.position,
            'state': self.state.value,
            'direction': 'East-West' if self.direction == 1 else 'North-South',
            'timer': self.timer,
            'congestion_level': self.congestion_level
        }