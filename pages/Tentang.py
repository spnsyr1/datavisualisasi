import streamlit as st

def local_css(file_name):
    """Membaca file CSS lokal dan menyuntikkannya ke Streamlit."""
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"File CSS '{file_name}' tidak ditemukan.")

# Panggil fungsi ini di awal skrip Streamlit Anda
local_css("pages/style.css")

st.title("Tentang Dashboard Analisis Kejahatan")

# Bagian Tujuan Proyek
st.subheader("1. Tujuan Proyek")
st.markdown("""
_Dashboard_ interaktif ini dikembangkan sebagai **alat bantu pengambilan keputusan berbasis data (_data-driven decision support tool_)** untuk menganalisis pola dan tren kejahatan di Los Angeles dengan tujuan menciptakan lingkungan yang aman dan kondusif. Sasaran utamanya:
""")
st.markdown("""
* Menganalisis pola spasial dan temporal kejahatan.
* Mengidentifikasi daerah rawan kejahatan (_crime hotspots_) sebagai dasar rekomendasi strategi pencegahan.
* Mendukung proses pengambilan keputusan berbasis data bagi pihak berwenang.
""")


# Bagian Sumber & Lingkup Data
st.subheader("2. Sumber dan Lingkup Data")
st.markdown("""
* **Cakupan:** Data kejahatan yang dilaporkan di berbagai wilayah di **Los Angeles, California, Amerika Serikat**.
* **Periode Analisis:** Data mencakup insiden kejahatan mulai dari **Tahun 2020 hingga awal 2025**.
* **Sumber Data:** Data sekunder dari Kaggle, dengan judul “Crime Data from 2020 to Present”.
* **Integritas Data:** Dataset telah melalui tahap pembersihan yang signifikan, menghasilkan data bersih yang siap digunakan berjumlah **734.144** baris.
""")


# Bagian Teknologi
st.subheader("3. Teknologi yang Digunakan")
st.markdown("""
Proyek ini mengandalkan teknologi visualisasi dan analisis data modern:
* **_Dashboard_ Utama:** Streamlit.
* **Visualisasi Grafik:** Plotly Express dan Plotly Graph Objects.
* **Peta Spasial:** Folium dan HeatMap.
* **Pengolahan Data:** Python (Pandas, NumPy).
""")

st.markdown("---")

# --- 3. Konten untuk Halaman "Wawasan Kunci" ---
st.title("Wawasan Kunci (Key Insights)")

st.subheader("1. Distribusi Geografis dan Waktu")
st.markdown("""
* **Area Paling Rawan:** Area "**Central**" mencatat tingkat kejahatan tertinggi.
* **Waktu Rawan:** Kejahatan paling sering terjadi pada **pukul 12 siang** dan hari **Jumat**.
""")

st.subheader("2. Jenis Kejahatan Dominan & Profil Korban")
st.markdown("""
* **Jenis Kejahatan Terbanyak:** "**BATTERY - SIMPLE ASSAULT**" (Kekerasan Fisik).
* **Etnis Korban:** Etnis "**Hispanic/Latin/Mexican**" adalah kelompok yang paling sering menjadi korban kejahatan.
* **Senjata Terlibat:** Senjata fisik "**STRONG-ARM (HANDS, FIST, FEET OR BODILY FORCE)**" paling dominan dalam kejahatan *Battery - Simple Assault*.
""")

st.markdown("---")

st.title("Rekomendasi Strategis")
st.markdown("""
* **Optimalisasi Penempatan Sumber Daya:** Alokasikan patroli ke Area **Central** dan pusat kota, dengan penekanan pada waktu rawan (siang hari dan sore hingga malam).
* **Fokus Pencegahan Kejahatan:** Rancang strategi yang secara khusus menargetkan kejahatan **BATTERY - SIMPLE ASSAULT**.
* **Perlindungan Kelompok Rentan:** Rancang program kesadaran keamanan yang menargetkan **etnis Hispanic/Latin/Mexican** dan kelompok usia produktif **(20–50 tahun)**.
""")