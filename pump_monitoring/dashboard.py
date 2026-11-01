import os
import pandas as pd
import requests
import streamlit as st

API_URL = os.getenv("PUMP_API_URL", "http://127.0.0.1:8001").rstrip("/")
st.set_page_config(page_title="Pump Condition Monitor", page_icon="⚙️", layout="wide")
st.title("Pump Condition Monitoring – Predictive Maintenance Demo")
st.caption("Synthetic telemetry and a classifier trained on synthetic scenarios. Not a validated diagnostic tool.")

try:
    summary = requests.get(f"{API_URL}/summary", timeout=4)
    summary.raise_for_status()
    summary = summary.json()
    response = requests.get(f"{API_URL}/telemetry?limit=500", timeout=4)
    response.raise_for_status()
    df = pd.DataFrame(response.json())
except requests.RequestException as exc:
    st.error(f"Cannot reach API at {API_URL}: {exc}. Start the API and seed sample data first.")
    st.stop()

if df.empty:
    st.info("No readings yet. Run: python -m pump_monitoring.cli seed --count 240")
    st.stop()

df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True)
df = df.sort_values("timestamp")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Records", summary["records"])
c2.metric("Flagged readings", summary["flagged_records"])
c3.metric("Average vibration", f"{summary['avg_vibration']:.2f} mm/s")
c4.metric("Average bearing temperature", f"{summary['avg_temperature']:.1f} °C")

st.subheader("Sensor trends")
left, right = st.columns(2)
with left:
    st.line_chart(df.set_index("timestamp")[["vibration_rms_mm_s", "bearing_temp_c"]])
    st.line_chart(df.set_index("timestamp")[["motor_current_a"]])
with right:
    st.line_chart(df.set_index("timestamp")[["flow_m3_h", "discharge_pressure_bar"]])
    st.line_chart(df.set_index("timestamp")[["anomaly_score"]])

st.subheader("Condition classifications")
st.bar_chart(df["predicted_condition"].value_counts())
st.subheader("Latest observations")
latest = df.sort_values("timestamp", ascending=False).head(50)
for _, row in latest.iterrows():
    if row["severity"] == "high":
        st.error(f"{row['timestamp']}: {row['predicted_condition']} – {row['explanation']}")
    elif row["severity"] == "warning":
        st.warning(f"{row['timestamp']}: {row['predicted_condition']} – {row['explanation']}")

st.dataframe(latest, use_container_width=True, hide_index=True)
