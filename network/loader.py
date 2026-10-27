"""
network/loader.py
-----------------
Demonstrates File Handling in Python:
Reads network definitions from JSON or CSV files and constructs Network objects.
"""

import json
import os
from components.bus import Bus
from components.generator import Generator
from components.load import Load
from components.line import TransmissionLine
from components.storage import Storage
from network.network import Network


def load_network_from_json(file_path: str) -> Network:
    """
    Build and return a Network instance by reading a JSON configuration file.
    
    Demonstrates:
    - File Handling: `with open(...) as f:` ensures the file is safely closed.
    - JSON parsing: converting file data into Python dictionaries.
    - Object Creation: instantiating Buses, Generators, Loads, Lines, and Storage.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Input file not found: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # 1. Create the Network container
    net_name = data.get("name", "Power Grid")
    network = Network(net_name)

    # 2. Load Buses and index them by name so we can link components
    bus_map: dict[str, Bus] = {}
    for b_data in data.get("buses", []):
        bus = Bus(
            name=b_data["name"],
            voltage=b_data.get("voltage", 11),
            x=b_data.get("x"),
            y=b_data.get("y"),
        )
        network.add_bus(bus)
        bus_map[bus.name] = bus

    # 3. Load Generators
    for g_data in data.get("generators", []):
        bus = bus_map[g_data["bus"]]
        gen = Generator(
            name=g_data["name"],
            bus=bus,
            capacity=float(g_data["capacity"]),
            marginal_cost=float(g_data.get("marginal_cost", 0.0)),
        )
        network.add_generator(gen)

    # 4. Load Loads
    for l_data in data.get("loads", []):
        bus = bus_map[l_data["bus"]]
        load = Load(
            name=l_data["name"],
            bus=bus,
            demand=float(l_data["demand"]),
        )
        network.add_load(load)

    # 5. Load Transmission Lines
    for line_data in data.get("lines", []):
        from_bus = bus_map[line_data["from_bus"]]
        to_bus = bus_map[line_data["to_bus"]]
        line = TransmissionLine(
            name=line_data["name"],
            from_bus=from_bus,
            to_bus=to_bus,
            capacity=float(line_data["capacity"]),
        )
        network.add_line(line)

    # 6. Load Storage Units
    for s_data in data.get("storage", []):
        bus = bus_map[s_data["bus"]]
        storage = Storage(
            name=s_data["name"],
            bus=bus,
            capacity=float(s_data["capacity"]),
            max_power=float(s_data.get("max_power", 20.0)),
            initial_energy=float(s_data.get("initial_energy", 0.0)),
        )
        network.add_storage(storage)

    return network
