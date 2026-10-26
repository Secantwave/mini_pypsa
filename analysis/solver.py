import networkx as nx


class PowerFlowSolver:
    """A simplified, shortest-path dispatch model for classroom demonstration.

    It does not solve AC power-flow equations or enforce line limits while dispatching.
    It estimates flows from generator/load allocations and reports overloaded lines.
    """

    def __init__(self, network):
        self.network = network

    def _bus_graph(self):
        graph = nx.Graph()
        graph.add_nodes_from(bus.name for bus in self.network.buses)
        for line in self.network.lines:
            graph.add_edge(line.from_bus, line.to_bus, line=line)
        return graph

    def _add_path_flow(self, path, power_mw):
        for start, end in zip(path, path[1:]):
            line = self._line_between(start, end)
            if line is None:
                continue
            if line.from_bus == start and line.to_bus == end:
                line.flow_mw += power_mw
            else:
                line.flow_mw -= power_mw

    def _line_between(self, bus_a, bus_b):
        for line in self.network.lines:
            if {line.from_bus, line.to_bus} == {bus_a, bus_b}:
                return line
        return None

    def solve(self, hours=1.0):
        if hours <= 0:
            raise ValueError("hours must be greater than zero")
        errors = self.network.validate()
        if errors:
            raise ValueError("Network has invalid configuration: " + "; ".join(errors))

        for line in self.network.lines:
            line.flow_mw = 0.0
        for generator in self.network.generators:
            generator.output_mw = 0.0
        for battery in self.network.storage_units:
            battery.last_discharge_mw = 0.0
            battery.last_charge_mw = 0.0

        graph = self._bus_graph()
        generators = sorted(self.network.generators, key=lambda item: item.marginal_cost)
        batteries = list(self.network.storage_units)
        served_by_load = {}
        unserved_by_load = {}

        for load in self.network.loads:
            remaining = load.demand_mw

            for generator in generators:
                available = generator.capacity_mw - generator.output_mw
                if available <= 1e-9 or remaining <= 1e-9:
                    continue
                if generator.bus not in graph or load.bus not in graph:
                    continue
                try:
                    path = nx.shortest_path(graph, generator.bus, load.bus)
                except nx.NetworkXNoPath:
                    continue
                supplied = min(remaining, available)
                generator.generate(generator.output_mw + supplied)
                self._add_path_flow(path, supplied)
                remaining -= supplied

            for battery in batteries:
                if remaining <= 1e-9:
                    break
                if battery.bus not in graph or load.bus not in graph:
                    continue
                try:
                    path = nx.shortest_path(graph, battery.bus, load.bus)
                except nx.NetworkXNoPath:
                    continue
                supplied = battery.discharge(min(remaining, battery.max_power_mw), hours)
                if supplied > 0:
                    self._add_path_flow(path, supplied)
                    remaining -= supplied

            served_by_load[load.name] = load.demand_mw - remaining
            unserved_by_load[load.name] = max(0.0, remaining)

        total_demand = sum(load.demand_mw for load in self.network.loads)
        total_generation = sum(generator.output_mw for generator in self.network.generators)
        storage_discharge = sum(battery.last_discharge_mw for battery in batteries)
        total_supply = total_generation + storage_discharge
        unserved = sum(unserved_by_load.values())
        total_cost = sum(generator.calculate_cost() for generator in self.network.generators)

        warnings = []
        if unserved > 1e-6:
            warnings.append(f"Power shortage: {unserved:.1f} MW of demand could not be served.")
        for line in self.network.lines:
            if line.is_overloaded:
                warnings.append(
                    f"{line.name} is overloaded ({abs(line.flow_mw):.1f} MW / {line.capacity_mw:.1f} MW)."
                )
        if not warnings:
            warnings.append("No shortage or line overload detected in this simplified model.")

        return {
            "total_demand_mw": total_demand,
            "total_generation_mw": total_generation,
            "storage_discharge_mw": storage_discharge,
            "total_supply_mw": total_supply,
            "unserved_demand_mw": unserved,
            "balance_mw": total_supply - total_demand,
            "operating_cost": total_cost,
            "served_by_load": served_by_load,
            "unserved_by_load": unserved_by_load,
            "warnings": warnings,
            "hours": hours,
        }
