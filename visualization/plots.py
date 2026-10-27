"""
visualization/plots.py
----------------------
Simple, publication-clean graph visualization on a white background.
Draws buses, connected generators/loads, transmission lines, and overload highlights.
"""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx


def plot_network(network) -> None:
    """
    Draw a clean, informative single-line diagram of the power grid on a white screen.
    
    Highlights:
    - Normal lines in grey, Overloaded lines in bold RED.
    - Annotates connected Generators [G] and Loads [L] below each bus.
    - Shows line flow and capacity on the edges.
    """
    G = nx.Graph()
    for bus in network.buses:
        G.add_node(bus.name)

    edge_colors = []
    edge_widths = []
    for line in network.lines:
        G.add_edge(line.from_bus.name, line.to_bus.name, line=line)
        # Highlight overloaded lines in red, normal lines in dark slate
        is_overloaded = abs(line.flow) > line.capacity
        edge_colors.append("#EF4444" if is_overloaded else "#64748B")
        edge_widths.append(3.0 if is_overloaded else 1.8)

    # 1. Determine positions (use bus coordinates if defined, else layout algorithm)
    has_coords = all(getattr(b, "x", None) is not None and getattr(b, "y", None) is not None for b in network.buses)
    if has_coords:
        pos = {b.name: (float(b.x), float(b.y)) for b in network.buses}
    else:
        pos = nx.spring_layout(G, seed=42)

    # 2. Setup figure on pure white background
    plt.figure(figsize=(10, 7), facecolor="white")
    ax = plt.gca()
    ax.set_facecolor("white")
    plt.title(f"{network.name} - Single-Line Diagram", fontsize=13, fontweight="bold", pad=15)

    # 3. Draw Buses (Nodes)
    nx.draw_networkx_nodes(G, pos, node_color="#E0F2FE", node_size=1800, edgecolors="#0284C7", linewidths=2.2, ax=ax)
    nx.draw_networkx_labels(G, pos, font_size=9, font_weight="bold", font_color="#0F172A", ax=ax)

    # 4. Draw Transmission Lines (Edges)
    nx.draw_networkx_edges(G, pos, edge_color=edge_colors, width=edge_widths, ax=ax)

    # Edge labels showing Flow / Capacity
    edge_labels = {}
    for line in network.lines:
        status_tag = " [OVERLOAD]" if abs(line.flow) > line.capacity else ""
        edge_labels[(line.from_bus.name, line.to_bus.name)] = f"{line.name}: {abs(line.flow):.0f}/{line.capacity:.0f} MW{status_tag}"
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=8, font_color="#1E293B", ax=ax)

    # 5. Draw attached Generator and Load badges near each bus
    for bus in network.buses:
        x, y = pos[bus.name]
        gens = [g for g in network.generators if g.bus is bus]
        loads = [l for l in network.loads if l.bus is bus]

        info_lines = []
        for g in gens:
            info_lines.append(f"[G] {g.name}: {g.output:.0f}/{g.capacity:.0f}MW (Rs.{g.marginal_cost:g})")
        for l in loads:
            info_lines.append(f"[L] {l.name}: {l.demand:.0f}MW")

        if info_lines:
            badge_text = "\n".join(info_lines)
            ax.text(
                x, y - 0.18, badge_text,
                ha="center", va="top", fontsize=7.5,
                bbox=dict(boxstyle="round,pad=0.3", fc="#F8FAFC", ec="#CBD5E1", lw=1.0),
            )

    # 6. Simple legend
    legend_elements = [
        mpatches.Patch(color="#64748B", label="Normal Line"),
        mpatches.Patch(color="#EF4444", label="Overloaded Line (>100%)"),
    ]
    ax.legend(handles=legend_elements, loc="upper right", fontsize=8, frameon=True)

    plt.axis("off")
    plt.tight_layout()
    plt.show()
