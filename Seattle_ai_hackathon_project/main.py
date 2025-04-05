#!/usr/bin/env python3
"""
Multi-Agent Smart Traffic Management System Prototype
Main simulation runner
"""
import argparse
import time
from core.controller import SimulationController


def main():
    parser = argparse.ArgumentParser(description="Run the traffic simulation")
    parser.add_argument("--steps", type=int, default=100, 
                        help="Number of simulation steps to run")
    parser.add_argument("--grid-size", type=int, default=5,
                        help="Size of the grid (NxN)")
    parser.add_argument("--vehicles", type=int, default=10,
                        help="Number of vehicles to simulate")
    parser.add_argument("--drones", type=int, default=2,
                        help="Number of drones to deploy")
    parser.add_argument("--delay", type=float, default=0.2,
                        help="Delay between steps (seconds)")
    parser.add_argument("--verbose", action="store_true",
                        help="Print detailed simulation information")
    args = parser.parse_args()
    
    # Create and initialize the simulation controller
    controller = SimulationController(
        grid_size=args.grid_size,
        num_vehicles=args.vehicles,
        num_drones=args.drones,
        verbose=args.verbose
    )
    
    print(f"Starting simulation with {args.vehicles} vehicles and {args.drones} drones")
    print(f"Grid size: {args.grid_size}x{args.grid_size}, running for {args.steps} steps")
    
    # Run the simulation for the specified number of steps
    for step in range(args.steps):
        print(f"\nSimulation step: {step + 1}/{args.steps}")
        controller.step()
        
        # Optional delay between steps for visualization
        if args.delay > 0:
            time.sleep(args.delay)
    
    # Print summary statistics
    controller.print_stats()
    
    print("Simulation complete")


if __name__ == "__main__":
    main()