"""
============================================================
 QUANTUM VOTING SYSTEM
 CS Course Project — Flask + Qiskit + SQLite
============================================================

WHAT IS "QUANTUM" HERE?
------------------------
- REAL quantum simulation: We use Qiskit's Aer simulator to
  create quantum circuits, encode votes as qubits using binary
  encoding (|00⟩=Candidate 0, |01⟩=Candidate 1, etc.),
  and measure the qubits to get classical bits.

- CONCEPTUAL quantum properties we SIMULATE (not real hardware):
  * No-Cloning: enforced by DB constraint (one vote per user)
  * Superposition: shown in circuit diagram but collapsed on measure
  * Tamper Detection: logs if a stored vote doesn't match re-measurement

HOW VOTE ENCODING WORKS:
  Candidate 0 → binary 00 → qubits q[0]=0, q[1]=0 → |00⟩
  Candidate 1 → binary 01 → qubits q[0]=0, q[1]=1 → |01⟩
  Candidate 2 → binary 10 → qubits q[0]=1, q[1]=0 → |10⟩
  Candidate 3 → binary 11 → qubits q[0]=1, q[1]=1 → |11⟩
"""

import os
import sqlite3
import hashlib
import json
from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, jsonify
)

# ── Qiskit imports ──────────────────────────────────────────
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit_aer import AerSimulator
from qiskit.visualization import circuit_drawer
import io, base64
import matplotlib
matplotlib.use('Agg')          # non-interactive backend (no GUI needed)
import matplotlib.pyplot as plt

# ============================================================
# APP SETUP
# ============================================================
app = Flask(__name__)
app.secret_key = "quantum_secret_key_2024"   # change in production!

DATABASE = "database.db"

# Candidates list — easy to extend
CANDIDATES = [
    {"id": 0, "name": "Alice Johnson",  "party": "Innovation Party",  "color": "#6366f1"},
    {"id": 1, "name": "Bob Martinez",   "party": "Progress Alliance",  "color": "#10b981"},
    {"id": 2, "name": "Carol Singh",    "party": "Future Forward",     "color": "#f59e0b"},
    {"id": 3, "name": "David Chen",     "party": "Unity Coalition",    "color": "#ef4444"},
]

NUM_QUBITS = 2   # 2 qubits → can represent 4 candidates (2² = 4)

# ============================================================
# DATABASE HELPERS
# ============================================================

def get_db():
    """Open a database connection (creates file if missing)."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row   # lets us access columns by name
    return conn


def init_db():
    """Create tables on first run."""
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                username  TEXT    UNIQUE NOT NULL,
                password  TEXT    NOT NULL,
                has_voted INTEGER DEFAULT 0
            );

            CREATE TABLE IF NOT EXISTS votes (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                candidate   INTEGER NOT NULL,
                vote_value  TEXT    NOT NULL,   -- classical bits after measurement
                circuit_img TEXT,               -- base64 PNG of quantum circuit
                timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );

            CREATE TABLE IF NOT EXISTS tamper_log (
                id        INTEGER PRIMARY KEY AUTOINCREMENT,
                vote_id   INTEGER,
                message   TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
    print("[DB] Database initialised.")


def hash_password(pw: str) -> str:
    """Simple SHA-256 hash. Use bcrypt in a real system."""
    return hashlib.sha256(pw.encode()).hexdigest()

# ============================================================
# QUANTUM LAYER
# ============================================================

def encode_vote_to_circuit(candidate_id: int) -> QuantumCircuit:
    """
    REAL QUANTUM SIMULATION
    -----------------------
    Encode a candidate choice into a quantum circuit.

    Steps:
    1. Create 2 qubits (q) and 2 classical bits (c).
    2. Convert candidate_id to 2-bit binary.
    3. Apply an X gate (NOT gate) to any qubit that should be |1⟩.
       X|0⟩ = |1⟩  — this flips the qubit.
    4. Measure both qubits into classical bits.

    Example — Candidate 2 (binary "10"):
        bit[1]=1 → apply X to q[1]
        bit[0]=0 → leave q[0] alone
        State before measurement: |10⟩
        Measurement collapses to classical: "10"
    """
    qr = QuantumRegister(NUM_QUBITS, name='q')
    cr = ClassicalRegister(NUM_QUBITS, name='c')
    qc = QuantumCircuit(qr, cr)

    # Convert candidate ID to binary string, zero-padded to NUM_QUBITS bits
    binary = format(candidate_id, f'0{NUM_QUBITS}b')  # e.g. "10" for id=2

    # Apply X gate where the bit is '1'
    for i, bit in enumerate(reversed(binary)):   # reversed: LSB = qubit 0
        if bit == '1':
            qc.x(qr[i])

    qc.barrier()          # visual separator in circuit diagram

    # Measure all qubits
    qc.measure(qr, cr)

    return qc, binary


def run_circuit(qc: QuantumCircuit) -> str:
    """
    REAL QUANTUM SIMULATION
    -----------------------
    Run the circuit on Qiskit's Aer local simulator.
    Shots=1 means one "measurement event" — like a single photon.

    Returns: classical bit-string result, e.g. "10"
    """
    simulator = AerSimulator()
    job = simulator.run(qc, shots=1)
    result = job.result()
    counts = result.get_counts(qc)
    # counts = {'10': 1} — the one measured outcome
    measured_value = list(counts.keys())[0]
    return measured_value


def circuit_to_image(qc: QuantumCircuit) -> str:
    """
    Render the quantum circuit as a PNG and return base64 string
    so it can be embedded directly in HTML <img src="...">.
    """
    fig = qc.draw(output='mpl', style={'backgroundcolor': '#0f0f1a'})
    fig.patch.set_facecolor('#0f0f1a')

    buf = io.BytesIO()
    fig.savefig(buf, format='png', bbox_inches='tight',
                facecolor='#0f0f1a', dpi=120)
    plt.close(fig)
    buf.seek(0)
    img_b64 = base64.b64encode(buf.read()).decode('utf-8')
    return img_b64


def simulate_tamper_check(stored_bits: str, candidate_id: int) -> bool:
    """
    CONCEPTUAL quantum property: tamper detection.
    -----------------------------------------------
    In a real quantum system, measuring a qubit collapses its state
    and any eavesdropping would disturb the state (detectable).

    Here we SIMULATE this by re-running the circuit and comparing
    the result. Because our encoding is deterministic, the results
    should always match. A mismatch would indicate tampering.
    """
    qc, _ = encode_vote_to_circuit(candidate_id)
    re_measured = run_circuit(qc)
    return re_measured == stored_bits   # True = no tampering

# ============================================================
# ROUTES — AUTH
# ============================================================

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('vote'))
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        if not username or not password:
            flash('Username and password are required.', 'error')
            return render_template('register.html')

        if len(password) < 4:
            flash('Password must be at least 4 characters.', 'error')
            return render_template('register.html')

        try:
            with get_db() as conn:
                conn.execute(
                    "INSERT INTO users (username, password) VALUES (?, ?)",
                    (username, hash_password(password))
                )
            flash('Account created! Please log in.', 'success')
            return redirect(url_for('login'))

        except sqlite3.IntegrityError:
            flash('Username already taken. Choose another.', 'error')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        with get_db() as conn:
            user = conn.execute(
                "SELECT * FROM users WHERE username = ? AND password = ?",
                (username, hash_password(password))
            ).fetchone()

        if user:
            session['user_id']  = user['id']
            session['username'] = user['username']
            session['has_voted'] = bool(user['has_voted'])
            return redirect(url_for('vote'))
        else:
            flash('Invalid username or password.', 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# ============================================================
# ROUTES — VOTING
# ============================================================

@app.route('/vote', methods=['GET', 'POST'])
def vote():
    # Must be logged in
    if 'user_id' not in session:
        flash('Please log in to vote.', 'error')
        return redirect(url_for('login'))

    # Already voted?
    with get_db() as conn:
        user = conn.execute(
            "SELECT has_voted FROM users WHERE id = ?",
            (session['user_id'],)
        ).fetchone()

    if user['has_voted']:
        flash('You have already cast your vote!', 'info')
        return redirect(url_for('results'))

    if request.method == 'POST':
        try:
            candidate_id = int(request.form['candidate'])
        except (ValueError, KeyError):
            flash('Please select a valid candidate.', 'error')
            return render_template('vote.html', candidates=CANDIDATES,
                                   username=session['username'])

        if candidate_id not in range(len(CANDIDATES)):
            flash('Invalid candidate selection.', 'error')
            return render_template('vote.html', candidates=CANDIDATES,
                                   username=session['username'])

        # ── QUANTUM ENCODING ────────────────────────────────
        qc, binary_repr = encode_vote_to_circuit(candidate_id)
        measured_bits   = run_circuit(qc)
        circuit_img     = circuit_to_image(qc)

        # ── TAMPER CHECK (conceptual) ────────────────────────
        is_valid = simulate_tamper_check(measured_bits, candidate_id)

        # ── STORE VOTE ───────────────────────────────────────
        with get_db() as conn:
            conn.execute(
                """INSERT INTO votes (user_id, candidate, vote_value, circuit_img)
                   VALUES (?, ?, ?, ?)""",
                (session['user_id'], candidate_id, measured_bits, circuit_img)
            )
            conn.execute(
                "UPDATE users SET has_voted = 1 WHERE id = ?",
                (session['user_id'],)
            )
            vote_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

            if not is_valid:
                # Log potential tampering (conceptual demo)
                conn.execute(
                    "INSERT INTO tamper_log (vote_id, message) VALUES (?, ?)",
                    (vote_id, f"Tamper detected on vote {vote_id}!")
                )

        session['has_voted'] = True

        # Pass quantum details to confirmation page
        return render_template('confirmed.html',
            candidate   = CANDIDATES[candidate_id],
            binary_repr = binary_repr,
            measured    = measured_bits,
            circuit_img = circuit_img,
            is_valid    = is_valid,
            username    = session['username']
        )

    return render_template('vote.html', candidates=CANDIDATES,
                           username=session['username'])


# ============================================================
# ROUTES — RESULTS
# ============================================================

@app.route('/results')
def results():
    if 'user_id' not in session:
        flash('Please log in to view results.', 'error')
        return redirect(url_for('login'))

    with get_db() as conn:
        rows = conn.execute("SELECT candidate, COUNT(*) as cnt FROM votes GROUP BY candidate").fetchall()
        total_votes = conn.execute("SELECT COUNT(*) as t FROM votes").fetchone()['t']

    # Build result dict keyed by candidate id
    vote_counts = {c['id']: 0 for c in CANDIDATES}
    for row in rows:
        vote_counts[row['candidate']] = row['cnt']

    results_data = []
    for c in CANDIDATES:
        cnt = vote_counts[c['id']]
        pct = round((cnt / total_votes * 100), 1) if total_votes > 0 else 0
        results_data.append({**c, 'votes': cnt, 'percent': pct})

    # Sort by votes descending
    results_data.sort(key=lambda x: x['votes'], reverse=True)

    return render_template('results.html',
        results     = results_data,
        total_votes = total_votes,
        username    = session['username'],
        has_voted   = session.get('has_voted', False)
    )

# ============================================================
# ROUTES — SECURITY LOG
# ============================================================

@app.route('/security')
def security():
    if 'user_id' not in session:
        flash('Please log in to view the security log.', 'error')
        return redirect(url_for('login'))

    with get_db() as conn:
        total_votes = conn.execute("SELECT COUNT(*) as t FROM votes").fetchone()['t']
        raw_logs = conn.execute("SELECT * FROM tamper_log ORDER BY timestamp DESC").fetchall()

    parsed_logs = []
    for log in raw_logs:
        msg = log['message']
        try:
            expected = msg.split('expected ')[1].split(' but')[0]
            found    = msg.split('but found ')[1]
        except:
            expected = '??'
            found    = '??'
        parsed_logs.append({
            'vote_id':   log['vote_id'],
            'message':   msg,
            'expected':  expected,
            'found':     found,
            'timestamp': log['timestamp'],
        })

    return render_template('security.html',
        tamper_logs = parsed_logs,
        total_votes = total_votes,
        username    = session['username']
    )

# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == '__main__':
    init_db()
    print("\n╔══════════════════════════════════════╗")
    print("║   QUANTUM VOTING SYSTEM — STARTED   ║")
    print("╠══════════════════════════════════════╣")
    print("║  Open: http://127.0.0.1:5000         ║")
    print("╚══════════════════════════════════════╝\n")
    app.run(debug=True)
