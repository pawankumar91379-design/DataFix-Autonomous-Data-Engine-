import streamlit as st
import pandas as pd
import numpy as np
import re
from datetime import datetime

st.set_page_config(page_title="DataFix | Autonomous Data Engine", page_icon="⚡", layout="wide")

st.markdown("""
<style>
.main {background-color:#0e1117}
[data-testid="stMetric"] {
    background:#1b2333;padding:18px;border-radius:12px;
    border:1px solid #303b50
}
.stButton>button {border-radius:9px;font-weight:600}
h1,h2,h3 {letter-spacing:-.5px}
</style>
""", unsafe_allow_html=True)

if "df" not in st.session_state: st.session_state.df = None
if "clean" not in st.session_state: st.session_state.clean = None
if "quarantine" not in st.session_state: st.session_state.quarantine = pd.DataFrame()
if "audit" not in st.session_state: st.session_state.audit = []

def demo():
    return pd.DataFrame({
        "ID":[1,2,3,3,4,5,6,7,8,9],
        "Name":[" rahul ","PRIYA","amit","amit","NEHA",None,"KARAN","sara","John","john"],
        "Age":[20,21,None,None,250,22,-5,24,35,35],
        "Email":["rahul@gmail.com","priya@gmail.com","amit@gmail.com",
                 "amit@gmail.com","wrong-email","sara@gmail.com",
                 "karan@gmail.com","sara@gmail.com","john@gmail.com","john@gmail.com"],
        "City":["delhi","MUMBAI","pune","pune","Delhi",None,"JAIPUR","mumbai","Chennai","chennai"],
        "Salary":[25000,30000,28000,28000,None,32000,50000,35000,40000,40000]
    })

def inspect_data(df):
    return pd.DataFrame({
        "Column":df.columns,
        "Type":[str(x) for x in df.dtypes],
        "Missing":[int(x) for x in df.isna().sum()],
        "Unique":[int(df[x].nunique()) for x in df.columns]
    })

def clean_data(source, remove_duplicates, standardize, impute, validate_email, age_check, outlier_check):
    df = source.copy()
    logs = []
    quarantine = []

    if remove_duplicates:
        n = len(df)
        df = df.drop_duplicates()
        logs.append(f"Removed {n-len(df)} duplicate rows.")

    if standardize:
        for col in df.select_dtypes(include=["object","string"]).columns:
            df[col] = df[col].apply(
                lambda x: x.strip().title() if isinstance(x,str) else x
            )
        logs.append("Standardized text columns.")

    if age_check and "Age" in df.columns:
        age = pd.to_numeric(df["Age"], errors="coerce")
        bad = age.notna() & ((age < 0) | (age > 120))
        if bad.any():
            q = df.loc[bad].copy()
            q["Quarantine_Reason"] = "Age outside valid range 0-120"
            quarantine.append(q)
            df = df.loc[~bad].copy()
            logs.append(f"Quarantined {len(q)} invalid age records.")

    if validate_email and "Email" in df.columns:
        bad = df["Email"].notna() & ~df["Email"].astype(str).str.match(
            r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
        )
        if bad.any():
            q = df.loc[bad].copy()
            q["Quarantine_Reason"] = "Invalid email format"
            quarantine.append(q)
            df = df.loc[~bad].copy()
            logs.append(f"Quarantined {len(q)} invalid email records.")

    if outlier_check:
        for col in df.select_dtypes(include=np.number).columns:
            if df[col].notna().sum() >= 4:
                q1, q3 = df[col].quantile([.25,.75])
                spread = q3-q1
                if spread > 0:
                    bad = (df[col] < q1-1.5*spread) | (df[col] > q3+1.5*spread)
                    if bad.any():
                        q = df.loc[bad].copy()
                        q["Quarantine_Reason"] = f"Statistical outlier in {col}"
                        quarantine.append(q)
                        df = df.loc[~bad].copy()
                        logs.append(f"Quarantined {len(q)} outliers in {col}.")

    if impute:
        for col in df.columns:
            if df[col].isna().any():
                if pd.api.types.is_numeric_dtype(df[col]):
                    value = df[col].median()
                    df[col] = df[col].fillna(value if pd.notna(value) else 0)
                else:
                    df[col] = df[col].fillna("Unknown")
                logs.append(f"Imputed missing values in {col}.")

    qdf = pd.concat(quarantine, ignore_index=True) if quarantine else pd.DataFrame()
    return df.reset_index(drop=True), qdf, logs

st.title("⚡ DataFix")
st.caption("AUTONOMOUS DATA ENGINE  |  Detect • Clean • Repair • Export")

with st.sidebar:
    st.title("📂 Workspace")
    uploaded = st.file_uploader("Upload your CSV dataset", type=["csv"])
    if uploaded:
        try:
            st.session_state.df = pd.read_csv(uploaded)
            st.session_state.clean = None
            st.success("Dataset uploaded!")
        except Exception as e:
            st.error(f"Upload error: {e}")

    if st.button("🧪 Load Demo Dataset", use_container_width=True):
        st.session_state.df = demo()
        st.session_state.clean = None
        st.session_state.audit = []
        st.rerun()

    st.divider()
    st.subheader("⚙️ Repair Settings")
    duplicates = st.checkbox("Remove duplicates", True)
    standardize = st.checkbox("Standardize text", True)
    impute = st.checkbox("Fill missing values", True)
    emails = st.checkbox("Validate email addresses", True)
    ages = st.checkbox("Validate age (0–120)", True)
    outliers = st.checkbox("Detect statistical outliers", False)

    st.divider()
    if st.button("🔄 Reset Workspace", use_container_width=True):
        for key in ["df","clean","quarantine","audit"]:
            st.session_state[key] = None if key in ["df","clean"] else (
                pd.DataFrame() if key=="quarantine" else []
            )
        st.rerun()

if st.session_state.df is None:
    st.info("Upload a CSV or select Load Demo Dataset in the sidebar to begin.")
    st.subheader("Your data quality workflow")
    cols = st.columns(4)
    for col, number, label in zip(cols,["01","02","03","04"],["Detect","Analyze","Repair","Export"]):
        col.metric(number,label)
    st.stop()

df = st.session_state.df
missing = int(df.isna().sum().sum())
duplicates_count = int(df.duplicated().sum())

st.subheader("📊 Dataset Health")
a,b,c,d = st.columns(4)
a.metric("Total Records",len(df))
b.metric("Columns",len(df.columns))
c.metric("Missing Cells",missing)
d.metric("Duplicate Rows",duplicates_count)

overview,scan,repair,results,audit = st.tabs([
    "📁 Dataset","🔍 Quality Scan","🛠️ Auto Repair","📥 Results","📜 Audit Log"
])

with overview:
    st.subheader("Original Dataset")
    st.dataframe(df,use_container_width=True)
    st.subheader("Column Profile")
    st.dataframe(inspect_data(df),use_container_width=True)
    st.download_button("Download Original CSV",df.to_csv(index=False).encode(),
                       "original_data.csv","text/csv")

with scan:
    st.subheader("Data Quality Analysis")
    st.write("Missing values per column")
    st.bar_chart(df.isna().sum())
    st.write("Duplicate records:",duplicates_count)
    st.write("Missing cells:",missing)
    st.write("Numeric summary")
    if len(df.select_dtypes(include=np.number).columns):
        st.dataframe(df.describe(),use_container_width=True)
    else:
        st.info("No numeric columns found.")

with repair:
    st.subheader("Autonomous Repair")
    st.write("Your selected repair settings are available in the sidebar.")
    if st.button("🚀 RUN DATAFIX ENGINE",type="primary",use_container_width=True):
        try:
            result,qdf,logs = clean_data(
                df,duplicates,standardize,impute,emails,ages,outliers
            )
            st.session_state.clean = result
            st.session_state.quarantine = qdf
            st.session_state.audit = [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")+" | "+x for x in logs
            ]
            st.success("DataFix repair completed successfully!")
        except Exception as e:
            st.error(f"Repair failed: {e}")

    if st.session_state.clean is not None:
        st.metric("Records after repair",len(st.session_state.clean))
        st.dataframe(st.session_state.clean,use_container_width=True)

with results:
    st.subheader("📥 Export Center")
    if st.session_state.clean is None:
        st.info("Run the DataFix Engine first.")
    else:
        result = st.session_state.clean
        qdf = st.session_state.quarantine
        x,y,z = st.columns(3)
        x.metric("Clean Records",len(result))
        y.metric("Quarantined Records",len(qdf))
        z.metric("Remaining Missing Cells",int(result.isna().sum().sum()))

        st.download_button("⬇️ Download Cleaned CSV",
            result.to_csv(index=False).encode("utf-8"),
            "datafix_cleaned.csv","text/csv",use_container_width=True)

        st.subheader("Quarantined Records")
        if not qdf.empty:
            st.dataframe(qdf,use_container_width=True)
            st.download_button("⬇️ Download Quarantine CSV",
                qdf.to_csv(index=False).encode("utf-8"),
                "datafix_quarantine.csv","text/csv",use_container_width=True)
        else:
            st.success("No records quarantined.")

        report = f"""DATAFIX QUALITY REPORT
Generated: {datetime.now()}
Original rows: {len(df)}
Clean rows: {len(result)}
Quarantined rows: {len(qdf)}
Original missing cells: {missing}
Original duplicates: {duplicates_count}
"""
        st.download_button("⬇️ Download Quality Report",report,
            "datafix_report.txt","text/plain",use_container_width=True)

with audit:
    st.subheader("📜 Operation History")
    if st.session_state.audit:
        for entry in st.session_state.audit:
            st.write("✅",entry)
        st.download_button("Download Audit Log",
            "\n".join(st.session_state.audit),
            "datafix_audit.txt","text/plain")
    else:
        st.info("No operations recorded yet.")

st.divider()
st.caption("DataFix Autonomous Data Engine | Streamlit • Python • Pandas • NumPy")
