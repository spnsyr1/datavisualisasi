import streamlit as st

dashboard = st.Page(
    page="pages/Dashboard.py",
    title="Dashboard",
    icon=":material/bar_chart:",
    default=True,
)

tentang = st.Page(
    page="pages/Tentang.py",
    title="Tentang",
    icon=":material/bar_chart:",
)

kontak = st.Page(
    page="pages/Kontak.py",
    title="Kontak",
    icon=":material/bar_chart:",
)

pg = st.navigation(
    {
        "Beranda": [dashboard],
        "Informasi": [tentang, kontak],
    }
)

st.logo("assets/logo.png", size="large")

pg.run()