"""
Visualization utilities for the Smart Traffic Management System
"""
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.table import Table
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class Visualizer:
    def __init__(self):
        """Initialize the visualizer"""
        self.console = Console() if RICH_AVAILABLE else None
    
    def display_system_state(self, grid, traffic_lights, vehicles, drones, stats):
        """
        Display the current state of the traffic management system
        
        Args:
            grid: Grid instance
            traffic_lights: List of TrafficLightAgent instances
            vehicles: List of VehicleAgent instances
            drones: List of DroneAgent instances
            stats: Statistics dictionary
        """
        if not RICH_AVAILABLE:
            self._fallback_display(grid, traffic_lights, vehicles, drones, stats)
            return
        
        layout = Layout()
        layout.split(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=10)
        )
        
        layout["main"].split_row(
            Layout(name="grid"),
            Layout(name="agents")
        )
        
        layout["agents"].split(
            Layout(name="traffic_lights"),
            Layout(name="vehicles"),
            Layout(name="drones")
        )
        
        # Header
        layout["header"].update(
            Panel("Smart Traffic Management System Simulation", 
                 style="bold white on blue")
        )
        
        # Grid view
        grid_table = Table(show_header=False, show_lines=True)
        for _ in range(grid.size):
            grid_table.add_column()
        
        for y in range(grid.size):
            row = []
            for x in range(grid.size):
                cell_content = ""
                agents = grid.grid[y, x]
                
                for agent in agents:
                    symbol = ""
                    if agent['type'] == 'traffic_light':
                        color = {
                            'GREEN': 'green',
                            'YELLOW': 'yellow',
                            'RED': 'red'
                        }.get(agent['state'], 'white')
                        
                        symbol = f"[{color}]◉[/{color}]"
                    elif agent['type'] == 'vehicle':
                        symbol = "[blue]🚗[/blue]"
                    elif agent['type'] == 'drone':
                        symbol = "[magenta]🚁[/magenta]"
                    
                    cell_content += f"{symbol} "
                
                row.append(cell_content.strip() or "·")
            
            grid_table.add_row(*row)
        
        layout["grid"].update(Panel(grid_table, title="Traffic Grid"))
        
        # Traffic lights table
        tl_table = Table(show_header=True)
        tl_table.add_column("ID")
        tl_table.add_column("Position")
        tl_table.add_column("State")
        tl_table.add_column("Direction")
        
        for light in traffic_lights:
            state = light.get_state()
            tl_table.add_row(
                state['id'],
                str(state['position']),
                state['state'],
                state['direction']
            )
        
        layout["traffic_lights"].update(Panel(tl_table, title="Traffic Lights"))
        
        # Vehicles table
        v_table = Table(show_header=True)
        v_table.add_column("ID")
        v_table.add_column("Position")
        v_table.add_column("State")
        v_table.add_column("Progress")
        
        active_vehicles = [v for v in vehicles if v.state != "ARRIVED"]
        for vehicle in active_vehicles[:10]:  # Show only the first 10 for brevity
            state = vehicle.get_state()
            v_table.add_row(
                state['id'],
                str(state['position']),
                state['state'],
                state['progress']
            )
        if len(active_vehicles) > 10:
            v_table.add_row("...", "...", "...", "...")
        
        layout["vehicles"].update(Panel(v_table, title=f"Vehicles ({len(active_vehicles)} active)"))
        
        # Drones table
        d_table = Table(show_header=True)
        d_table.add_column("ID")
        d_table.add_column("Position")
        d_table.add_column("State")
        d_table.add_column("Battery")
        
        for drone in drones:
            state = drone.get_state()
            d_table.add_row(
                state['id'],
                str(state['position']),
                state['state'],
                state['battery']
            )
        
        layout["drones"].update(Panel(d_table, title="Drones"))
        
        # Footer with stats
        stats_table = Table(show_header=False)
        stats_table.add_column("Stat")
        stats_table.add_column("Value")
        
        stats_table.add_row("Vehicles Arrived", str(stats['vehicles_arrived']))
        stats_table.add_row("Average Waiting Time", 
                      f"{stats['total_waiting_time'] / len(vehicles):.2f} steps" 
                      if len(vehicles) > 0 else "N/A")
        stats_table.add_row("Congestion Events", str(stats['congestion_events']))
        stats_table.add_row("Anomalies Detected", str(stats['anomalies_detected']))
        
        layout["footer"].update(Panel(stats_table, title="Statistics"))
        
        # Print the layout
        self.console.clear()
        self.console.print(layout)
    
    def _fallback_display(self, grid, traffic_lights, vehicles, drones, stats):
        """Simple text-based visualization fallback"""
        print("\n=== Smart Traffic Management System ===")
        
        # Print grid
        print("\nTraffic Grid:")
        for y in range(grid.size):
            line = ""
            for x in range(grid.size):
                agents = grid.grid[y, x]
                if not agents:
                    line += "· "
                else:
                    symbols = []
                    for agent in agents:
                        if agent['type'] == 'traffic_light':
                            if agent['state'] == 'GREEN':
                                symbols.append('G')
                            elif agent['state'] == 'YELLOW':
                                symbols.append('Y')
                            else:
                                symbols.append('R')
                        elif agent['type'] == 'vehicle':
                            symbols.append('V')
                        elif agent['type'] == 'drone':
                            symbols.append('D')
                    line += "".join(symbols) + " "
            print(line)
        
        # Print stats
        print("\nStatistics:")
        print(f"Vehicles Arrived: {stats['vehicles_arrived']}")
        if len(vehicles) > 0:
            print(f"Average Waiting Time: "
                  f"{stats['total_waiting_time'] / len(vehicles):.2f} steps")
        print(f"Congestion Events: {stats['congestion_events']}")
        print(f"Anomalies Detected: {stats['anomalies_detected']}")
        
        print("\n=======================================\n")