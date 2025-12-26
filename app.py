import streamlit as st
import pandas as pd
from computation.traverse import *
from exports.exporters import *
from utils.plot_traverse import *
from utils.sample_data import *

st.set_page_config(layout="wide", page_title="Survey Pro")
st.title("📐 Universal Survey Computation Pro")

mode = st.sidebar.radio("Survey Mode", ["Traverse & Area", "Leveling"])

if mode == "Traverse & Area":
    st.sidebar.download_button("Download Template", get_traverse_sample(), "traverse.csv")
    start_x = st.sidebar.number_input("Start Easting", value=0.0)
    start_y = st.sidebar.number_input("Start Northing", value=0.0)
    close_loop = st.sidebar.toggle("Close Traverse Loop")
    
    file = st.file_uploader("Upload Traverse CSV", type=['csv'])
    if file:
        df_raw = pd.read_csv(file)
        df_raw = df_raw.loc[:, ~df_raw.columns.duplicated()] # Fix duplicate error
        
        df_proc = compute_lat_depart(df_raw)
        df_fin, mis_n, mis_e, dist, prec = bowditch_adjustment_with_steps(df_proc, start_x, start_y, close_loop)
        
        area_m, ha, ac = calculate_area(df_fin)
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Area (m²)", f"{area_m:,.2f}")
        m2.metric("Precision", f"1:{int(prec)}")
        m3.metric("Length", f"{dist:.2f} m")
        
        t1, t2 = st.tabs(["Map View", "Data Table"])
        with t1: st.pyplot(plot_traverse(df_fin))
        with t2: st.dataframe(df_fin)
        
        # Exports
        pdf_file = export_pdf(df_fin, mis_n, mis_e, prec, "Site A", "Surveyor 1", "")
        st.download_button("Download PDF", pdf_file, "Report.pdf")
        st.download_button("Download DXF", export_to_dxf(df_fin), "Plan.dxf")

else:
    st.sidebar.download_button("Download Template", get_leveling_sample(), "leveling.csv")
    start_rl = st.sidebar.number_input("Start RL (m)", value=100.0)
    file = st.file_uploader("Upload Leveling CSV", type=['csv'])
    if file:
        df_l = pd.read_csv(file)
        df_res = compute_leveling(df_l, start_rl)
        
        st.pyplot(plot_vertical_profile(df_res))
        st.dataframe(df_res.style.format(precision=3))
