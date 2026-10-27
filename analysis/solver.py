from collections import defaultdict, deque


class PowerFlowSolver:
    """
    Simplified analysis engine.

    This is NOT a full AC load-flow solver. It performs:
    - merit-order generator dispatch
    - optional battery discharge for deficits
    - simple radial-style flow allocation
    - line-capacity checking
    """

    def __init__(self, network):
        self.network = network
        self.unserved_demand = 0.0
        self.storage_discharge = 0.0
        self.dispatch = {}

    def reset(self) -> None:
        self.unserved_demand = 0.0
        self.storage_discharge = 0.0
        self.dispatch = {}
        self.network.reset_flows()

    def dispatch_generators(self) -> float:
        """Dispatch generators from cheapest to most expensive."""
        self.reset()

        demand = self.network.total_demand()

        for generator in sorted(
            self.network.generators,
            key=lambda g: g.marginal_cost
        ):
            output = min(generator.capacity, demand)
            generator.generate(output)
            demand -= output
            self.dispatch[generator.name] = output

        # Use storage if there is still a deficit.
        if demand > 1e-9:
            for storage in self.network.storage_units:
                supplied = storage.discharge(demand)
                self.storage_discharge += supplied
                demand -= supplied
                if demand <= 1e-9:
                    break

        # If there is still a deficit, record it.
        self.unserved_demand = max(0.0, demand)

        return self.unserved_demand

    def check_power_balance(self) -> dict:
        generation = self.network.total_generation()
        demand = self.network.total_demand()
        storage = self.storage_discharge
        served = generation + storage

        return {
            "generation": generation,
            "demand": demand,
            "storage": storage,
            "served": served,
            "balance": served - demand,
            "unserved": max(0.0, demand - served),
        }

    def _make_graph(self):
        """Build a NetworkX graph when available."""
        try:
            import networkx as nx
        except ImportError as exc:
            raise ImportError(
                "NetworkX is required for line-flow analysis and visualization."
            ) from exc

        graph = nx.Graph()

        for bus in self.network.buses:
            graph.add_node(bus.name, bus=bus)

        for line in self.network.lines:
            graph.add_edge(
                line.from_bus.name,
                line.to_bus.name,
                line=line,
                capacity=line.capacity,
            )

        return graph

    def calculate_simplified_flows(self) -> None:
        """
        Allocate power using a simple shortest-path model.

        Each load is supplied from the nearest generator bus in the graph.
        If multiple paths exist, the shortest path is selected.
        This is intentionally an educational simplification.
        """
        self.network.reset_flows()

        if not self.network.lines:
            return

        graph = self._make_graph()
        line_by_edge = {}

        for line in self.network.lines:
            line_by_edge[frozenset((line.from_bus.name, line.to_bus.name))] = line

        # Available generation after dispatch.
        generator_by_bus = defaultdict(float)
        for generator in self.network.generators:
            generator_by_bus[generator.bus.name] += generator.output

        # Treat battery discharge as local supply at its bus.
        for storage in self.network.storage_units:
            # Energy remaining after discharge is already updated, so the
            # discharged quantity is represented through the aggregate amount.
            pass

        # For this simplified model, route each load from the nearest
        # bus with positive generator output.
        source_buses = [
            bus_name
            for bus_name, amount in generator_by_bus.items()
            if amount > 1e-9
        ]

        if not source_buses:
            return

        for load in self.network.loads:
            try:
                distances = {
                    source: nx_shortest_path_length(graph, source, load.bus.name)
                    for source in source_buses
                }
            except Exception:
                continue

            source = min(distances, key=distances.get)

            try:
                path = shortest_path(graph, source, load.bus.name)
            except Exception:
                continue

            remaining = load.demand

            for start, end in zip(path[:-1], path[1:]):
                line = line_by_edge.get(frozenset((start, end)))
                if line is None:
                    continue

                sign = 1 if (
                    line.from_bus.name == start
                    and line.to_bus.name == end
                ) else -1

                line.set_flow(line.flow + sign * remaining)

    def check_lines(self) -> list:
        return [
            {
                "name": line.name,
                "flow": line.flow,
                "capacity": line.capacity,
                "loading_percent": line.loading_percent(),
                "status": "NORMAL" if line.check_capacity() else "OVERLOADED",
            }
            for line in self.network.lines
        ]

    def solve(self) -> dict:
        self.dispatch_generators()
        self.calculate_simplified_flows()

        return {
            "balance": self.check_power_balance(),
            "lines": self.check_lines(),
            "dispatch": dict(self.dispatch),
            "cost": self.network.total_cost(),
        }


# Small wrappers keep the algorithm readable without requiring NetworkX in
# every function signature.
def nx_shortest_path_length(graph, source, target):
    import networkx as nx
    return nx.shortest_path_length(graph, source, target)


def shortest_path(graph, source, target):
    import networkx as nx
    return nx.shortest_path(graph, source, target)
