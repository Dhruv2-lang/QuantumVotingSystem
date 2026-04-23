# ⚛ Quantum Voting System
### CS Course Project — Flask + Qiskit + SQLite

---

## 📁 Project Structure

```
quantum_voting/
├── app.py                  ← Main Flask app (all backend logic)
├── database.db             ← SQLite DB (auto-created on first run)
├── requirements.txt        ← Python dependencies
├── README.md               ← This file
└── templates/
    ├── base.html           ← Shared layout (navbar, styles)
    ├── login.html          ← Login page
    ├── register.html       ← Registration page
    ├── vote.html           ← Voting page (candidate selection)
    ├── confirmed.html      ← Post-vote confirmation + circuit diagram
    └── results.html        ← Live vote tally
```

---

## 🚀 Setup & Run (Step-by-Step)

### Step 1 — Prerequisites
Make sure you have Python 3.9+ installed:
```bash
python --version
```

### Step 2 — Create a virtual environment (recommended)
```bash
# Create
python -m venv venv

# Activate (Mac/Linux)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```
> This installs Flask, Qiskit, Qiskit-Aer, and Matplotlib.
> First install may take 2–5 minutes (Qiskit is large).

### Step 4 — Run the app
```bash
python app.py
```
You'll see:
```
╔══════════════════════════════════════╗
║   QUANTUM VOTING SYSTEM — STARTED   ║
╠══════════════════════════════════════╣
║  Open: http://127.0.0.1:5000         ║
╚══════════════════════════════════════╝
```

### Step 5 — Open in browser
Navigate to: **http://127.0.0.1:5000**

---

## 🗄️ Database Schema

```sql
-- Registered users
CREATE TABLE users (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    username  TEXT    UNIQUE NOT NULL,
    password  TEXT    NOT NULL,          -- SHA-256 hashed
    has_voted INTEGER DEFAULT 0          -- 0=no, 1=yes
);

-- Cast votes
CREATE TABLE votes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    candidate   INTEGER NOT NULL,        -- 0–3
    vote_value  TEXT    NOT NULL,        -- classical bits e.g. "10"
    circuit_img TEXT,                    -- base64 PNG of circuit
    timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Tamper detection log
CREATE TABLE tamper_log (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    vote_id   INTEGER,
    message   TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

---

## ⚛ Quantum Layer Explained

### What IS real quantum simulation?
| Component | Status | Tool |
|-----------|--------|------|
| Quantum circuit creation | ✅ REAL | Qiskit `QuantumCircuit` |
| X gate (qubit flip) | ✅ REAL | Qiskit gate operations |
| Aer simulation & measurement | ✅ REAL | `AerSimulator` |
| Circuit diagram rendering | ✅ REAL | Qiskit + Matplotlib |

### What is conceptually simulated?
| Quantum Property | How We Simulate It |
|-----------------|-------------------|
| **No-Cloning Theorem** | `has_voted = 1` prevents duplicate votes |
| **Tamper Detection** | Re-run circuit, compare measured bits |
| **Superposition** | Circuit shows H-gates conceptually; we use X-gates for deterministic encoding |

### Vote Encoding Table
```
Candidate 0 (Alice)  → binary 00 → qubits: |00⟩ → measured: "00"
Candidate 1 (Bob)    → binary 01 → qubits: |01⟩ → measured: "01"
Candidate 2 (Carol)  → binary 10 → qubits: |10⟩ → measured: "10"
Candidate 3 (David)  → binary 11 → qubits: |11⟩ → measured: "11"
```

### How a circuit is built (example: Carol, candidate 2)
```
Binary of 2 = "10"
qubit q[0] → bit 0 → stays |0⟩  (no X gate)
qubit q[1] → bit 1 → apply X   → |1⟩

Circuit:
q[0]: ─────────────■── measure → c[0]
q[1]: ──[X]─────────── measure → c[1]

Result: c[1]c[0] = "10" ✓
```

---

## 🔒 Security Notes (Course Context)

- Passwords are SHA-256 hashed (use bcrypt in production)
- Session secret key should be env-variable in production
- The quantum layer provides *conceptual* security properties
- In real quantum cryptography, BB84 or QKD protocols are used

---

## 📋 Routes Summary

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET | Redirect to login or vote |
| `/register` | GET, POST | User registration |
| `/login` | GET, POST | User login |
| `/logout` | GET | Clear session |
| `/vote` | GET, POST | Display candidates / submit vote |
| `/results` | GET | Live vote tally |

---

## 🧪 Quick Test

1. Register as `alice` / `pass1`
2. Vote for any candidate — observe the quantum circuit
3. Try voting again — you'll be blocked ✓
4. Register as `bob` / `pass2`, vote for a different candidate
5. Visit `/results` to see live tally
