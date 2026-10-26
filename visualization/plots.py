import math

import networkx as nx
import plotly.graph_objects as go

COLORS = {
    "Bus": "#9CA3AF",
    "Generator": "#34D399",
    "Load": "#FBBF24",
    "Storage": "#A78BFA",
    "line": "#64748B",
    "attachment": "#475569",
    "warning": "#FB7185",
    "caution": "#FBBF24",
}


def _key(kind, name):
    return f"{kind.lower()}::{name}"


def make_network_figure(network, show_types=None, show_lines=True):
    """Make a dark, force-directed network diagram with toggleable node types."""
    show_types = set(show_types or ["Bus", "Generator", "Load", "Storage"])
    graph = nx.Graph()

    for bus in network.buses:
        graph.add_node(_key("Bus", bus.name), kind="Bus", component=bus)
    for generator in network.generators:
        key = _key("Generator", generator.name)
        graph.add_node(key, kind="Generator", component=generator)
        graph.add_edge(key, _key("Bus", generator.bus), kind="attachment", weight=2.0)
    for load in network.loads:
        key = _key("Load", load.name)
        graph.add_node(key, kind="Load", component=load)
        graph.add_edge(key, _key("Bus", load.bus), kind="attachment", weight=2.0)
    for battery in network.storage_units:
        key = _key("Storage", battery.name)
        graph.add_node(key, kind="Storage", component=battery)
        graph.add_edge(key, _key("Bus", battery.bus), kind="attachment", weight=2.0)
    for line in network.lines:
        graph.add_edge(
            _key("Bus", line.from_bus), _key("Bus", line.to_bus),
            kind="line", component=line, weight=1.0,
        )

    if graph.number_of_nodes() == 0:
        return go.Figure()

    positions = nx.spring_layout(graph, seed=17, k=1.25 / math.sqrt(max(1, graph.number_of_nodes())), iterations=100, weight="weight")
    fig = go.Figure()

    # Non-directional dotted connections between each component and its bus.
    for start, end, data in graph.edges(data=True):
        if data["kind"] != "attachment":
            continue
        start_kind = graph.nodes[start]["kind"]
        end_kind = graph.nodes[end]["kind"]
        if start_kind not in show_types or end_kind not in show_types:
            continue
        x0, y0 = positions[start]
        x1, y1 = positions[end]
        fig.add_trace(go.Scatter(
            x=[x0, x1], y=[y0, y1], mode="lines",
            line=dict(color=COLORS["attachment"], width=1.2, dash="dot"),
            hoverinfo="skip", showlegend=False,
        ))

    # Transmission links: neutral when healthy, amber near capacity, red when overloaded.
    if show_lines and "Bus" in show_types:
        for line in network.lines:
            start_key = _key("Bus", line.from_bus)
            end_key = _key("Bus", line.to_bus)
            if start_key not in positions or end_key not in positions:
                continue
            x0, y0 = positions[start_key]
            x1, y1 = positions[end_key]
            loading = line.loading_percent
            color = COLORS["warning"] if loading >= 100 else (COLORS["caution"] if loading >= 80 else COLORS["line"])
            fig.add_trace(go.Scatter(
                x=[x0, x1], y=[y0, y1], mode="lines",
                line=dict(color=color, width=2.0 if loading >= 80 else 1.5),
                hoverinfo="skip", showlegend=False,
            ))

            # Flow direction is inferred from the sign of the estimated line flow.
            if line.flow_mw < -1e-6:
                sx, sy, ex, ey = x1, y1, x0, y0
            else:
                sx, sy, ex, ey = x0, y0, x1, y1
            tip_x, tip_y = sx + 0.82 * (ex - sx), sy + 0.82 * (ey - sy)
            tail_x, tail_y = sx + 0.66 * (ex - sx), sy + 0.66 * (ey - sy)
            fig.add_annotation(
                x=tip_x, y=tip_y, ax=tail_x, ay=tail_y,
                xref="x", yref="y", axref="x", ayref="y",
                text="", showarrow=True, arrowhead=3, arrowsize=1.1,
                arrowwidth=1.5, arrowcolor=color,
            )
            midpoint_x, midpoint_y = (x0 + x1) / 2, (y0 + y1) / 2
            fig.add_annotation(
                x=midpoint_x, y=midpoint_y,
                text=f"{line.name} · {abs(line.flow_mw):.0f}/{line.capacity_mw:.0f} MW",
                showarrow=False, font=dict(size=9, color="#CBD5E1"),
                bgcolor="rgba(15, 18, 24, 0.82)", borderpad=2,
            )

    symbols = {"Bus": "square", "Generator": "circle", "Load": "diamond", "Storage": "hexagon"}
    for kind in ["Bus", "Generator", "Load", "Storage"]:
        if kind not in show_types:
            continue
        xs, ys, labels, hovers = [], [], [], []
        for node, data in graph.nodes(data=True):
            if data["kind"] != kind:
                continue
            component = data["component"]
            x, y = positions[node]
            xs.append(x)
            ys.append(y)
            labels.append(component.name)
            hovers.append(_hover_text(kind, component))
        if not xs:
            continue
        fig.add_trace(go.Scatter(
            x=xs, y=ys, mode="markers+text", name=kind,
            text=labels, textposition="top center", textfont=dict(size=10, color="#E5E7EB"),
            customdata=hovers, hovertemplate="%{customdata}<extra></extra>",
            marker=dict(
                color=COLORS[kind], size=17 if kind == "Bus" else 14,
                symbol=symbols[kind], line=dict(color="#0F1218", width=1.5),
            ),
            showlegend=True,
        ))

    fig.update_layout(
        height=565, margin=dict(l=8, r=8, t=8, b=8),
        paper_bgcolor="#11151D", plot_bgcolor="#11151D",
        font=dict(color="#E5E7EB", family="Inter, Arial, sans-serif"),
        legend=dict(orientation="h", yanchor="bottom", y=0.01, xanchor="left", x=0.01,
                    bgcolor="rgba(17,21,29,0.7)", font=dict(size=10)),
        xaxis=dict(visible=False, showgrid=False, zeroline=False, fixedrange=False),
        yaxis=dict(visible=False, showgrid=False, zeroline=False, fixedrange=False, scaleanchor="x", scaleratio=1),
        hoverlabel=dict(bgcolor="#202633", bordercolor="#475569", font_color="#F8FAFC"),
    )
    return fig


def _hover_text(kind, component):
    if kind == "Bus":
        return f"<b>{component.name}</b><br>Type: Bus<br>Voltage: {component.voltage_kv:g} kV"
    if kind == "Generator":
        return (f"<b>{component.name}</b><br>Type: Generator<br>Bus: {component.bus}"
                f"<br>Capacity: {component.capacity_mw:g} MW<br>Output: {component.output_mw:g} MW"
                f"<br>Marginal cost: ₹{component.marginal_cost:,.0f}/MWh")
    if kind == "Load":
        return f"<b>{component.name}</b><br>Type: Load<br>Bus: {component.bus}<br>Demand: {component.demand_mw:g} MW"
    return (f"<b>{component.name}</b><br>Type: Storage<br>Bus: {component.bus}"
            f"<br>Energy: {component.energy_mwh:g}/{component.capacity_mwh:g} MWh"
            f"<br>Max power: {component.max_power_mw:g} MW")


def make_dispatch_figure(network):
    fig = go.Figure(go.Bar(
        x=[g.output_mw for g in network.generators],
        y=[g.name for g in network.generators],
        orientation="h", marker_color=[COLORS["Generator"] for _ in network.generators],
        text=[f"{g.output_mw:.1f} MW" for g in network.generators], textposition="outside",
        hovertemplate="%{y}<br>Output: %{x:.1f} MW<extra></extra>",
    ))
    fig.update_layout(
        height=220, margin=dict(l=8, r=35, t=8, b=8),
        paper_bgcolor="#11151D", plot_bgcolor="#11151D",
        font=dict(color="#E5E7EB"), xaxis=dict(title="MW", gridcolor="#252C38", zeroline=False),
        yaxis=dict(title="", autorange="reversed"), showlegend=False,
    )
    return fig


def make_line_loading_figure(network):
    lines = network.lines
    colors = [COLORS["warning"] if line.loading_percent >= 100 else
              (COLORS["caution"] if line.loading_percent >= 80 else COLORS["line"]) for line in lines]
    fig = go.Figure(go.Bar(
        x=[line.loading_percent for line in lines], y=[line.name for line in lines],
        orientation="h", marker_color=colors,
        text=[f"{line.loading_percent:.0f}%" for line in lines], textposition="outside",
        hovertemplate="%{y}<br>Loading: %{x:.1f}%<extra></extra>",
    ))
    fig.add_vline(x=100, line_dash="dash", line_color=COLORS["warning"], line_width=1.2)
    fig.add_vline(x=80, line_dash="dot", line_color=COLORS["caution"], line_width=1)
    fig.update_layout(
        height=240, margin=dict(l=8, r=35, t=8, b=8),
        paper_bgcolor="#11151D", plot_bgcolor="#11151D",
        font=dict(color="#E5E7EB"), xaxis=dict(title="Line loading (%)", gridcolor="#252C38", zeroline=False),
        yaxis=dict(title="", autorange="reversed"), showlegend=False,
    )
    return fig
