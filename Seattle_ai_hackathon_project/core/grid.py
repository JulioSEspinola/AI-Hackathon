"""
Grid representation for the Smart Traffic Management System
"""
import numpy as np
from rich.console import Console
from rich.table import Table


class Grid:
    def __init__(self, size):
        """
        Initialize a grid representation
        
        Args:
            size: Size of the grid (NxN)
        """
        self.size = size
        self.grid = np.zeros((size, size), dtype=object)
        self.agents = {}
        
        # Initialize empty grid
        for x in range(size):
            for y in range(size):
                self.grid[y, x] = []
    
    def add_agent(self, agent_id, position, agent_type, state):
        """
        Add an agent to the grid
        
        Args:
            agent_id: Unique identifier for the agent
            position: (x, y) position on the grid
            agent_type: Type of agent ('traffic_light', 'vehicle', 'drone')
            state: Current state of the agent
        """
        x, y = position
        
        # Ensure position is within grid boundaries
        if 0 <= x < self.size and 0 <= y < self.size:
            agent_info = {
                'id': agent_id,
                'type': agent_type,
                'state': state
            }
            
            self.grid[y, x].append(agent_info)
            self.agents[agent_id] = (position, agent_type, state)
    
    def remove_agent(self, agent_id):
        """
        Remove an agent from the grid
        
        Args:
            agent_id: Unique identifier for the agent
        """
        if agent_id in self.agents:
            position, _, _ = self.agents[agent_id]
            x, y = position
            
            # Find and remove the agent from the grid cell
            agents_at_cell = self.grid[y, x]
            for i, agent in enumerate(agents_at_cell):
                if agent['id'] == agent_id:
                    agents_at_cell.pop(i)
                    break
            
            # Remove from agents dictionary
            del self.agents[agent_id]
    
    def get_agents_at(self, position):
        """
        Get all agents at a specific position
        
        Args:
            position: (x, y) position on the grid
        
        Returns:
            List of agent information dictionaries
        """
        x, y = position
        
        # Ensure position is within grid boundaries
        if 0 <= x < self.size and 0 <= y < self.size:
            return self.grid[y, x]
        return []
    
    def clear(self):
        """Clear the grid"""
        self.grid = np.zeros((self.size, self.size), dtype=object)
        for x in range(self.size):
            for y in range(self.size):
                self.grid[y, x] = []
        self.agents = {}
    
    def visualize(self):
        """Visualize the grid using rich console"""
        try:
            from rich.console import Console
            from rich.table import Table
            
            console = Console()
            table = Table(show_header=False, show_lines=True)
            
            # Add columns
            for _ in range(self.size):
                table.add_column()
            
            # Add rows
            for y in range(self.size):
                row = []
                for x in range(self.size):
                    cell_content = ""
                    agents = self.grid[y, x]
                    
                    for agent in agents:
                        symbol = ""
                        if agent['type'] == 'traffic_light':
                            if agent['state'] == 'GREEN':
                                symbol = "🟢"
                            elif agent['state'] == 'YELLOW':
                                symbol = "🟡"
                            else:
                                symbol = "🔴"
                        elif agent['type'] == 'vehicle':
                            symbol = "🚗"
                        elif agent['type'] == 'drone':
                            symbol = "🚁"
                        
                        cell_content += f"{symbol} "
                    
                    row.append(cell_content.strip() or "·")
                
                table.add_row(*row)
            
            console.print(table)
            console.print("\n")
            
        except ImportError:
            # Fallback simple visualization if rich is not available
            for y in range(self.size):
                line = ""
                for x in range(self.size):
                    agents = self.grid[y, x]
                    if not agents:
                        line += "· "
                    else:
                        agent_types = [a['type'][0].upper() for a in agents]
                        line += "".join(agent_types) + " "
                print(line)
            print("\n")