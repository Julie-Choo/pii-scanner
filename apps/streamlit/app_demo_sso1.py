# apps/streamlit/app_demo_sso.py — Mock SSO + DB source & table picker (demo-only)
# Run: streamlit run apps/streamlit/app_demo_sso.py

import time
import random
from typing import Dict, List
import streamlit as st

# -------------------------------
# Page setup
# -------------------------------
st.set_page_config(page_title="PII Scanner – Demo", page_icon="🕵️", layout="centered")

# -------------------------------
# Utilities (mock data + helpers)
# -------------------------------
DEMO_SCHEMAS: Dict[str, List[str]] = {
    "public": ["users", "orders", "products", "events", "reviews"],
    "sales": ["customers", "payments", "invoices", "transactions"],
    "hr": ["employees", "compensation", "benefits", "recruiting"],
    "ops": ["tickets", "assets", "work_orders", "sites"],
}

DB_DEFAULTS = {
    "Postgres": {"host": "demo-db.internal", "port": 5432, "database": "product"},
    "Redshift": {"host": "demo-redshift.cluster", "port": 5439, "database": "lake"},
    "SQL Server": {"host": "demo-sql.internal", "port": 1433, "database": "product"},
}


def fake_connect(db_type: str, host: str, port: int, database: str, user: str) -> bool:
    """Pretend to connect. Always succeeds after a short delay."""
    with st.spinner(f"Connecting to {db_type} at {host}:{port} / {database}…"):
        time.sleep(0.8)
    return True


def fake_fetch_schemas_and_tables(db_type: str, database: str) -> Dict[str, List[str]]:
    """Return a stable-but-randomized slice of DEMO_SCHEMAS to look real-ish."""
    random.seed(hash((db_type, database)) & 0xFFFFFFFF)
    schemas = {}
    for name, tables in DEMO_SCHEMAS.items():
        # Randomly drop/keep some tables so different DBs look unique
        kept = [t for t in tables if random.random() > 0.2]
        if kept:
            schemas[name] = kept
    return schemas or DEMO_SCHEMAS


# -------------------------------
# Session state
# -------------------------------
if "user" not in st.session_state:
    st.session_state.user = None
if "conn" not in st.session_state:
    st.session_state.conn = None
if "schemas" not in st.session_state:
    st.session_state.schemas = None
if "selected_schema" not in st.session_state:
    st.session_state.selected_schema = None
if "selected_tables" not in st.session_state:
    st.session_state.selected_tables = []
if "selection_confirmed" not in st.session_state:
    st.session_state.selection_confirmed = False

# -------------------------------
# Header
# -------------------------------
st.title("🧪 PII Scanner – Concept Demo")
st.caption("Step 1: Sign in → pick data source → choose schema & tables")

# -------------------------------
# SSO (pretend)
# -------------------------------
with st.container(border=True):
    st.subheader("Sign in (pretend SSO)")
    if st.session_state.user:
        colA, colB = st.columns([3, 1])
        with colA:
            st.success(f"Signed in as **{st.session_state.user['name']}** · {st.session_state.user['email']}")
        with colB:
            if st.button("Sign out"):
                st.session_state.user = None
                st.session_state.conn = None
                st.session_state.schemas = None
                st.session_state.selected_schema = None
                st.session_state.selected_tables = []
                st.session_state.selection_confirmed = False
                st.rerun()
    else:
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Sign in with Okta"):
                st.session_state.user = {"name": "Business User", "email": "user@example.com", "provider": "Okta"}
                st.rerun()
        with col2:
            if st.button("Sign in with Azure AD"):
                st.session_state.user = {"name": "Business User", "email": "user@example.com", "provider": "Azure AD"}
                st.rerun()
        with col3:
            st.caption("(Demo only – no real authentication)")

if not st.session_state.user:
    st.info("Please sign in to continue.")
    st.stop()

# -------------------------------
# Connection form (demo-only)
# -------------------------------
with st.container(border=True):
    st.subheader("Choose your product database")
    db_type = st.selectbox("Database engine", ["Postgres", "Redshift", "SQL Server"], index=0)

    defaults = DB_DEFAULTS[db_type]
    c1, c2 = st.columns(2)
    with c1:
        host = st.text_input("Host", value=defaults["host"])
        database = st.text_input("Database", value=defaults["database"])
    with c2:
        port = st.number_input("Port", min_value=1, max_value=65535, value=int(defaults["port"]))
        user = st.text_input("Username", value=st.session_state.user["email"].split("@")[0])

    demo_creds = st.checkbox("Use demo credentials (no password needed)", value=True)
    if not demo_creds:
        _ = st.text_input("Password", type="password", value="", placeholder="Demo: leave blank")

    connect_clicked = st.button("Connect")
    if connect_clicked:
        ok = fake_connect(db_type, host, port, database, user)
        if ok:
            st.session_state.conn = {
                "db_type": db_type,
                "host": host,
                "port": port,
                "database": database,
                "user": user,
            }
            st.session_state.schemas = fake_fetch_schemas_and_tables(db_type, database)
            st.toast("Connected. Schemas loaded.")
        else:
            st.error("Could not connect. (Demo always succeeds.)")

if not st.session_state.conn or not st.session_state.schemas:
    st.stop()

# -------------------------------
# Schema & table selection
# -------------------------------
with st.container(border=True):
    st.subheader("Pick schema and tables to scan")

    schema_names = sorted(st.session_state.schemas.keys())
    st.session_state.selected_schema = st.selectbox("Schema", schema_names, index=0)

    available_tables = st.session_state.schemas.get(st.session_state.selected_schema, [])

    st.write(":mag: _Tip: search inside the list by typing._")
    st.session_state.selected_tables = st.multiselect(
        "Tables in selected schema",
        options=available_tables,
        default=available_tables[:2],
    )

    colx, coly = st.columns([1, 3])
    with colx:
        confirm = st.button("Confirm selection", disabled=len(st.session_state.selected_tables) == 0)
    with coly:
        st.progress(
            int(100 * (len(st.session_state.selected_tables) > 0)),
            text=("Ready" if len(st.session_state.selected_tables) > 0 else "Select at least one table"),
        )

    if confirm:
        st.session_state.selection_confirmed = True
        st.success(
            f"Selection locked: schema **{st.session_state.selected_schema}**, "
            f"tables {', '.join(st.session_state.selected_tables)}"
        )

# Summary / Next step (placeholder for scan page)
with st.container(border=True):
    st.subheader("Summary")
    if st.session_state.selection_confirmed:
        st.write(
            {
                "user": st.session_state.user,
                "connection": st.session_state.conn,
                "schema": st.session_state.selected_schema,
                "tables": st.session_state.selected_tables,
            }
        )
        st.success("Next: Run scan → Validate results (grid) → Governance review → Export.")
    else:
        st.info("Confirm your selection to continue to scanning (not implemented in this demo).")