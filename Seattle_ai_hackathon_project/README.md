# Multi-Agent Smart Traffic Management System

A Python-based simulation of an intelligent traffic management system that uses multiple types of agents to monitor and optimize traffic flow in a grid-based environment.

## Overview

This project implements a smart traffic management system that simulates the interaction between different types of agents:
- Traffic Lights: Manage intersections with dynamic timing based on traffic conditions
- Vehicles: Navigate through the grid while responding to traffic signals and congestion
- Drones: Monitor traffic conditions and detect anomalies like congestion or incidents

The simulation runs on a configurable NxN grid where agents interact to optimize traffic flow and reduce congestion.

## Features

- **Grid-based Environment**: Flexible NxN grid system for traffic simulation
- **Multi-Agent System**:
  - Smart traffic lights with dynamic timing
  - Autonomous vehicles with pathfinding capabilities
  - Surveillance drones for traffic monitoring
- **Real-time Monitoring**:
  - Traffic density tracking
  - Congestion detection
  - Incident reporting
- **Visualization**: Rich console-based visualization of the simulation state
- **Statistics Tracking**:
  - Vehicle arrival rates
  - Average waiting times
  - Congestion events
  - Traffic anomalies

## Requirements

- Python 3.x
- NumPy
- Rich (for enhanced console visualization)

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd smart-traffic-management
```

2. Install dependencies:
```bash
pip install numpy rich
```

## Usage

Run the simulation using the main script:

```bash
python main.py [options]
```

### Command Line Options

- `--steps`: Number of simulation steps to run (default: 100)
- `--grid-size`: Size of the simulation grid (NxN) (default: 5)
- `--vehicles`: Number of vehicles to simulate (default: 10)
- `--drones`: Number of drones to deploy (default: 2)
- `--delay`: Delay between steps in seconds (default: 0.2)
- `--verbose`: Enable detailed simulation output

Example:
```bash
python main.py --grid-size 8 --vehicles 15 --drones 3 --steps 200
```

## Project Structure

- `main.py`: Main simulation runner
- `core/`:
  - `controller.py`: Main simulation controller
  - `grid.py`: Grid environment implementation
  - `comms.py`: Communication system between agents
  - `visualization.py`: Visualization utilities
- `agents/`:
  - `traffic_light.py`: Traffic light agent implementation
  - `vehicle.py`: Vehicle agent implementation
  - `drone.py`: Drone agent implementation

## How It Works

1. **Initialization**:
   - Creates a grid of specified size
   - Places traffic lights at intersections
   - Spawns vehicles with random start/end points
   - Deploys drones for monitoring

2. **Simulation Loop**:
   - Updates all agents' states
   - Processes inter-agent communications
   - Updates grid state
   - Collects and displays statistics

3. **Agent Behaviors**:
   - Traffic lights adjust timing based on traffic conditions
   - Vehicles navigate using pathfinding and respond to signals
   - Drones patrol areas and report anomalies

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for improvements and bug fixes.

## License

[Insert License Information] 