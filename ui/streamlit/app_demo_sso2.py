# apps/streamlit/app_demo_sso.py — Mock SSO (separate screen) + DB source & table picker (demo-only)
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
        kept = [t for t in tables if random.random() > 0.2]
        if kept:
            schemas[name] = kept
    return schemas or DEMO_SCHEMAS

# -------------------------------
# Session state
# -------------------------------
if "user" not in st.session_state:
    st.session_state.user = None
if "step" not in st.session_state:
    st.session_state.step = "sso"  # sso -> source -> select
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
st.caption("Step 1: Sign in  →  Step 2: Pick data source  →  Step 3: Choose schema & tables")

# ===============================
# SCREEN 1 — SSO ONLY
# ===============================
if st.session_state.step == "sso":
    with st.container(border=True):
        st.subheader("Step 1 · Sign in (pretend SSO)")
        st.write("Choose your organization's sign-in. This is a demo—no real auth.")

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Sign in with Ping Identity"):
                st.session_state.user = {"name": "Business User", "email": "user@example.com", "provider": "Ping"}
                st.session_state.step = "source"
                st.rerun()
            if st.button("Sign in with HYPR (passwordless)"):
                st.session_state.user = {"name": "Business User", "email": "user@example.com", "provider": "HYPR"}
                st.session_state.step = "source"
                st.rerun()
        with c2:
            if st.button("Sign in with Okta"):
                st.session_state.user = {"name": "Business User", "email": "user@example.com", "provider": "Okta"}
                st.session_state.step = "source"
                st.rerun()
            if st.button("Sign in with Azure AD / Entra ID"):
                st.session_state.user = {"name": "Business User", "email": "user@example.com", "provider": "Azure AD"}
                st.session_state.step = "source"
                st.rerun()

    st.stop()

# ===============================
# SCREEN 2 — SOURCE CONNECTION (separate from SSO)
# ===============================
if st.session_state.step == "source":
    with st.container(border=True):
        st.subheader("Step 2 · Choose your product database")
        st.success(f"Signed in as **{st.session_state.user['name']}** via {st.session_state.user['provider']}")

        db_type = st.selectbox("Database engine", ["Postgres", "Redshift", "SQL Server"], index=0)
        defaults = DB_DEFAULTS[db_type]
        c1, c2 = st.columns(2)
        with c1:
            host = st.text_input("Host", value=defaults["host"])
            database = st.text_input("Database", value=defaults["database"])
        with c2:
            port = st.number_input("Port", min_value=1, max_value=65535, value=int(defaults["port"]))
            user = st.text_input("DB Username", value=st.session_state.user["email"].split("@")[0])

        demo_creds = st.checkbox("Use demo credentials (no password needed)", value=True)
        if not demo_creds:
            _ = st.text_input("Password", type="password", value="", placeholder="Demo: leave blank")

        left, right = st.columns([1,1])
        with left:
            if st.button("Connect"):
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
                    st.session_state.step = "select"
                    st.rerun()
        with right:
            if st.button("Sign out"):
                st.session_state.user = None
                st.session_state.step = "sso"
                st.rerun()

    st.stop()

# ===============================
# SCREEN 3 — SCHEMA & TABLE SELECTION
# ===============================
if st.session_state.step == "select":
    with st.container(border=True):
        st.subheader("Step 3 · Pick schema and tables to scan")
        st.caption(
            f"Connected to {st.session_state.conn['db_type']} at "
            f"{st.session_state.conn['host']} / {st.session_state.conn['database']} as {st.session_state.conn['user']}"
        )

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
            st.info("Next: Run scan → Validate results (grid) → Governance review → Export.")

    # Footer controls
    back_col, _ = st.columns([1,5])
    with back_col:
        if st.button("Back to source"):
            st.session_state.step = "source"
            st.rerun()
