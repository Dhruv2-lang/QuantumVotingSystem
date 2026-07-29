# Quantum Voting System

**CS Course Project — Flask + Qiskit + SQLite**

A web-based voting application that uses **real quantum circuit simulation** (via IBM's Qiskit) to encode and "cast" each vote, alongside conceptual demonstrations of quantum-inspired security properties like no-cloning and tamper detection.

## Team

| Name | Registration No. |
|---|---|
| Dhruv Pratap Singh | RA2411026010146 |
| Dhruv Mahajan | RA2411026010185 |

### Guide

Dr. Gayathri


## What Is "Quantum" Here?

This project combines a **real** quantum simulation layer with **conceptual** analogies to quantum security properties:

### Real Quantum Simulation
- Uses Qiskit's **Aer simulator** to build an actual quantum circuit for every vote.
- Each candidate is encoded as a qubit basis state using binary encoding:

  | Candidate | Binary | Quantum State |
  |---|---|---|
  | Candidate 0 | `00` | `\|00⟩` |
  | Candidate 1 | `01` | `\|01⟩` |
  | Candidate 2 | `10` | `\|10⟩` |
  | Candidate 3 | `11` | `\|11⟩` |

- The circuit is built with **X (NOT) gates** to flip qubits into the correct state, then **measured** to collapse it into a classical bit-string result.
- The circuit diagram is rendered and stored as an image with each vote.

### Conceptual Quantum Properties (Simulated, Not Real Hardware)
- **No-Cloning** — enforced at the database level (one vote per user).
- **Superposition** — illustrated in the circuit diagram, though it collapses upon measurement (as in real quantum mechanics).
- **Tamper Detection** — re-runs the encoding circuit for a stored vote and compares the result; a mismatch is logged as potential tampering.

## Tech Stack

- **Backend:** Python, Flask
- **Quantum Simulation:** Qiskit, Qiskit Aer
- **Database:** SQLite
- **Visualization:** Matplotlib (circuit diagrams rendered as base64 PNGs)
- **Frontend:** HTML (Jinja2 templates)
- **Auth:** Flask session-based login with SHA-256 password hashing

## Features

- **User Registration & Login** — session-based auth, passwords hashed with SHA-256
- **Quantum-Encoded Voting** — each vote is encoded into a quantum circuit, run on a simulator, and measured to produce the final recorded result
- **Circuit Visualization** — the actual quantum circuit diagram for each vote is generated and displayed on the confirmation page
- **One Vote Per User** — enforced via a `has_voted` flag in the database
- **Live Results** — vote counts and percentages per candidate, sorted by votes
- **Security / Tamper Log** — displays any detected mismatches between a stored vote and its re-measured value

## Project Structure
```

QuantumVotingSystem/
├── app.py # Main Flask application (routes, quantum logic, DB)
├── database.db # SQLite database (created on first run)
├── templates/
│ ├── base.html # Base layout
│ ├── login.html # Login page
│ ├── register.html # Registration page
│ ├── vote.html # Candidate selection / voting page
│ ├── confirmed.html # Vote confirmation with circuit diagram
│ ├── results.html # Live results dashboard
│ └── security.html # Tamper detection log
└── README.md
```
## How Vote Encoding Works

Candidate 0 → binary 00 → qubits q[0]=0, q[1]=0 → |00⟩
Candidate 1 → binary 01 → qubits q[0]=0, q[1]=1 → |01⟩
Candidate 2 → binary 10 → qubits q[0]=1, q[1]=0 → |10⟩
Candidate 3 → binary 11 → qubits q[0]=1, q[1]=1 → |11⟩

1. A 2-qubit, 2-classical-bit circuit is created.
2. The candidate ID is converted to a 2-bit binary string.
3. An **X gate** is applied to any qubit that should be `|1⟩`.
4. Both qubits are measured, collapsing them into a classical bit-string.
5. The result is stored in the database along with a rendered image of the circuit.

## Candidates

| ID | Name | Party |
|---|---|---|
| 0 | Alice Johnson | Innovation Party |
| 1 | Bob Martinez | Progress Alliance |
| 2 | Carol Singh | Future Forward |
| 3 | David Chen | Unity Coalition |

> Candidates are defined in a `CANDIDATES` list in `app.py` and can be edited or extended (up to 4 candidates with 2 qubits; more candidates would require additional qubits).

## Getting Started

### Prerequisites

- Python 3.9+
- pip

### 1. Clone the repository

```bash
git clone https://github.com/Dhruv2-lang/QuantumVotingSystem.git
cd QuantumVotingSystem
```

### 2. Install dependencies

```bash
pip install flask qiskit qiskit-aer matplotlib
```

### 3. Run the application

```bash
python app.py
```

The database (`database.db`) is created automatically on first run. The app will be available at:http://127.0.0.1:5000


## Usage

1. **Register** a new account, or **log in** if you already have one.
2. On the **Vote** page, select a candidate and submit — this triggers the quantum encoding, simulation, and measurement.
3. View your **Confirmation** page, which shows the candidate you voted for, the binary encoding, the measured result, and the rendered quantum circuit diagram.
4. Check the **Results** page for live vote counts and percentages.
5. Check the **Security** page for the tamper detection log.

## Known Limitations

- Uses SHA-256 for password hashing — not salted, and not recommended for production (use `bcrypt` or `werkzeug.security` instead).
- Vote encoding is deterministic (not truly random), so the "tamper detection" mechanism is illustrative rather than cryptographically meaningful.
- Limited to 4 candidates due to the fixed 2-qubit encoding (`NUM_QUBITS = 2`) — extending the candidate list requires increasing `NUM_QUBITS`.
- Runs Qiskit Aer as a **local classical simulator** of quantum circuits — no real quantum hardware is used.
- `debug=True` is enabled in `app.run()` — should be disabled before any deployment.

## License

This project was developed for academic purposes as a Computer Science course project.

