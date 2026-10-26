<<<<<<< HEAD
# mini_pypsa
=======
# Grid Graph — Simplified PyPSA-Inspired Power Grid Simulator

A small modular OOP project for a classroom case study. It models buses, generators, loads, transmission lines and a battery; performs a simple generator-dispatch and shortest-path flow estimate; checks line loading; estimates operating cost; and visualizes the network in an Obsidian-inspired dark style.

## Run it

Use Python 3.10 or newer. From this folder, run:

```bash
python -m venv .venv
```

Activate the environment, then install the dependencies:

```bash
pip install -r requirements.txt
```

Start the app:

```bash
streamlit run app.py
```

Streamlit opens the dashboard in your browser. Adjust generator capacities, demand, battery energy and line limits in the sidebar. In **Network display**, toggle Bus, Generator, Load and Storage nodes. Hover over a node to inspect its values. Transmission-line arrows show the direction of the estimated net flow; line colors change from slate to amber/red as loading approaches or exceeds capacity.

## Project structure

```text
mini_pypsa/
├── app.py
├── components/
│   ├── component.py
│   ├── bus.py
│   ├── generator.py
│   ├── load.py
│   ├── line.py
│   └── storage.py
├── network/
│   └── network.py
├── analysis/
│   └── solver.py
├── visualization/
│   └── plots.py
├── requirements.txt
└── .streamlit/config.toml
```

- **Components:** OOP classes for each grid element.
- **Network:** stores and validates components and their connections.
- **Analysis:** performs merit-order dispatch, estimates line flows and reports shortages/overloads.
- **Visualization:** draws the interactive graph and analysis charts.
- **app.py:** collects scenario inputs and displays the dashboard.

## OOP concepts demonstrated

- **Abstraction:** the solver and UI operate through simple component/network methods rather than exposing every implementation detail.
- **Encapsulation:** each component stores its own parameters and provides methods to modify or validate them.
- **Inheritance:** concrete components inherit common state and behaviour from the abstract `Component` base class and implement `validate()`.
- **Composition:** a `Network` contains lists of Bus, Generator, Load, TransmissionLine and Storage objects.
- **Polymorphism:** the network can call `validate()` on different component objects through the common interface.

## Important limitation

This is an educational approximation, **not** a full electrical load-flow solver. It does not model voltage magnitude/angle, reactive power, losses, or Kirchhoff-based AC equations. Estimated line flows are allocated along shortest paths and line capacity limits are checked after allocation, rather than constrained during dispatch. State these limitations in the report/presentation.
>>>>>>> 5b6ac5e (Commit)
