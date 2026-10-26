import pandas as pd
import streamlit as st

from analysis import PowerFlowSolver
from components import Bus, Generator, Load, Storage, TransmissionLine
from network import Network
from visualization import make_dispatch_figure, make_line_loading_figure, make_network_figure


st.set_page_config(page_title="Grid Graph | Power System Simulator", page_icon="⚡", layout="wide")
st.markdown("""
<style>
  .stApp { background: #0d1016; color: #e5e7eb; }
  [data-testid="stSidebar"] { background: #11151d; border-right: 1px solid #252c38; }
  h1, h2, h3 { letter-spacing: -0.035em; }
  .eyebrow { color: #34d399; font-size: .76rem; font-weight: 700; letter-spacing: .16em; text-transform: uppercase; }
  .muted { color: #94a3b8; font-size: .9rem; }
  div[data-testid="stMetric"] { background: #141a24; border: 1px solid #252c38; padding: 14px 16px; border-radius: 12px; }
  div[data-testid="stMetricLabel"] { color: #94a3b8; }
  div[data-testid="stMetricValue"] { color: #f8fafc; }
  .section-label { color: #94a3b8; font-size: .78rem; font-weight: 700; letter-spacing: .1em; text-transform: uppercase; margin-bottom: .35rem; }
  hr { border-color: #252c38; }
</style>
""", unsafe_allow_html=True)


def build_demo_network(values):
    net = Network("Campus Power Grid")
    net.add_bus(Bus("Solar Bus", 11))
    net.add_bus(Bus("Main Grid Bus", 33))
    net.add_bus(Bus("Factory Bus", 11))
    net.add_bus(Bus("Hostel Bus", 11))

    net.add_generator(Generator("Solar Plant", "Solar Bus", values["solar_capacity"], 0))
    net.add_generator(Generator("Gas Turbine", "Main Grid Bus", values["gas_capacity"], 4000))

    net.add_load(Load("Factory Load", "Factory Bus", values["factory_demand"]))
    net.add_load(Load("Hostel Load", "Hostel Bus", values["hostel_demand"]))

    net.add_storage(Storage("Campus Battery", "Hostel Bus", 100, 25, values["battery_energy"]))

    net.add_line(TransmissionLine("L1 · Solar–Factory", "Solar Bus", "Factory Bus", values["line_1"]))
    net.add_line(TransmissionLine("L2 · Solar–Grid", "Solar Bus", "Main Grid Bus", values["line_2"]))
    net.add_line(TransmissionLine("L3 · Grid–Hostel", "Main Grid Bus", "Hostel Bus", values["line_3"]))
    net.add_line(TransmissionLine("L4 · Factory–Hostel", "Factory Bus", "Hostel Bus", values["line_4"]))
    return net


st.sidebar.markdown('<div class="eyebrow">Scenario controls</div>', unsafe_allow_html=True)
st.sidebar.caption("Adjust the grid and the results update automatically.")
with st.sidebar.expander("Generation & demand", expanded=True):
    solar_capacity = st.slider("Solar capacity (MW)", 0, 150, 100, 5)
    gas_capacity = st.slider("Gas capacity (MW)", 0, 150, 50, 5)
    factory_demand = st.slider("Factory demand (MW)", 0, 100, 50, 5)
    hostel_demand = st.slider("Hostel demand (MW)", 0, 100, 70, 5)
    battery_energy = st.slider("Battery energy at start (MWh)", 0, 100, 40, 5)

with st.sidebar.expander("Transmission limits", expanded=False):
    line_1 = st.slider("L1 · Solar–Factory (MW)", 20, 150, 80, 5)
    line_2 = st.slider("L2 · Solar–Grid (MW)", 20, 150, 100, 5)
    line_3 = st.slider("L3 · Grid–Hostel (MW)", 20, 150, 80, 5)
    line_4 = st.slider("L4 · Factory–Hostel (MW)", 20, 150, 50, 5)

with st.sidebar.expander("Network display", expanded=True):
    show_types = st.multiselect(
        "Show component types",
        ["Bus", "Generator", "Load", "Storage"],
        default=["Bus", "Generator", "Load", "Storage"],
        help="Toggle component categories on or off in the network graph.",
    )
    show_lines = st.checkbox("Show transmission lines and arrows", value=True)

values = {
    "solar_capacity": solar_capacity,
    "gas_capacity": gas_capacity,
    "factory_demand": factory_demand,
    "hostel_demand": hostel_demand,
    "battery_energy": battery_energy,
    "line_1": line_1,
    "line_2": line_2,
    "line_3": line_3,
    "line_4": line_4,
}
network = build_demo_network(values)
results = PowerFlowSolver(network).solve(hours=1.0)

st.markdown('<div class="eyebrow">Object-oriented power system analysis</div>', unsafe_allow_html=True)
st.title("Grid Graph")
st.markdown('<div class="muted">A simplified PyPSA-inspired grid simulator · interactive network view · one-hour operating snapshot</div>', unsafe_allow_html=True)
st.write("")

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Total demand", f"{results['total_demand_mw']:.1f} MW")
m2.metric("Generator output", f"{results['total_generation_mw']:.1f} MW")
m3.metric("Battery discharge", f"{results['storage_discharge_mw']:.1f} MW")
m4.metric("Unserved demand", f"{results['unserved_demand_mw']:.1f} MW")
m5.metric("Operating cost", f"₹{results['operating_cost']:,.0f}")

left, right = st.columns([1.7, 1], gap="large")
with left:
    st.markdown('<div class="section-label">Live network</div>', unsafe_allow_html=True)
    st.caption("Hover over a node for its details. Component colors are shown in the legend; line arrows follow estimated power-flow direction.")
    st.plotly_chart(make_network_figure(network, show_types, show_lines), use_container_width=True, config={"displaylogo": False, "scrollZoom": True})
    st.caption("Node colors: Bus · slate   |   Generator · green   |   Load · amber   |   Storage · violet. Amber/red lines indicate high loading/overload.")

with right:
    st.markdown('<div class="section-label">Grid status</div>', unsafe_allow_html=True)
    if results["unserved_demand_mw"] > 1e-6:
        st.error("Demand is not fully supplied.")
    elif any(line.is_overloaded for line in network.lines):
        st.warning("One or more transmission lines are overloaded.")
    else:
        st.success("Demand served; no line overload detected.")

    for warning in results["warnings"]:
        st.markdown(f"- {warning}")

    st.markdown("---")
    st.markdown('<div class="section-label">Generator dispatch</div>', unsafe_allow_html=True)
    st.plotly_chart(make_dispatch_figure(network), use_container_width=True, config={"displaylogo": False})

st.markdown("---")
tab1, tab2, tab3 = st.tabs(["Generator details", "Line loading", "Storage & model notes"])
with tab1:
    generator_rows = [
        {"Generator": g.name, "Bus": g.bus, "Output (MW)": round(g.output_mw, 2),
         "Capacity (MW)": round(g.capacity_mw, 2), "Cost (₹/MWh)": round(g.marginal_cost, 2),
         "Estimated cost (₹)": round(g.calculate_cost(), 2)}
        for g in network.generators
    ]
    st.dataframe(pd.DataFrame(generator_rows), use_container_width=True, hide_index=True)
    st.caption("Generators are dispatched in order of increasing marginal cost, subject to capacity and connectivity.")
with tab2:
    line_rows = [
        {"Line": line.name, "From": line.from_bus, "To": line.to_bus,
         "Estimated flow (MW)": round(line.flow_mw, 2), "Capacity (MW)": round(line.capacity_mw, 2),
         "Loading (%)": round(line.loading_percent, 1),
         "Status": "OVERLOADED" if line.is_overloaded else ("HIGH" if line.loading_percent >= 80 else "Normal")}
        for line in network.lines
    ]
    st.dataframe(pd.DataFrame(line_rows), use_container_width=True, hide_index=True)
    st.plotly_chart(make_line_loading_figure(network), use_container_width=True, config={"displaylogo": False})
with tab3:
    for battery in network.storage_units:
        st.markdown(f"**{battery.name}** at `{battery.bus}`")
        st.write(f"Remaining energy: **{battery.energy_mwh:.1f} / {battery.capacity_mwh:.1f} MWh**")
        st.write(f"Power limit: **{battery.max_power_mw:.1f} MW** · Discharged in this snapshot: **{battery.last_discharge_mw:.1f} MW**")
    st.markdown("**Model assumptions**")
    st.markdown("- This is a simplified educational model, not a full AC power-flow or optimal power-flow solver.")
    st.markdown("- Line flows are estimated by allocating generation to loads along shortest bus paths. Line limits are checked and warnings are reported, but they are not enforced during dispatch.")
    st.markdown("- The battery simulation covers one hour. The sidebar energy value is the starting state for each recalculated scenario.")
    st.markdown("- Operating cost is estimated as generator output × marginal cost for the one-hour snapshot.")

st.markdown("---")
st.caption("Built to demonstrate abstraction, encapsulation, inheritance, composition, and modular Python design. PyPSA is the reference inspiration; this project does not recreate the full library.")
