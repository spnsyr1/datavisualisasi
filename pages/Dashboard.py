import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go

# Tentukan Color Scale bertema Merah (contoh)
# px.colors.sequential.Reds -> Skala Merah dari Plotly
# 'red' atau '#ff0000' -> Warna Merah Solid
RED_COLOR_SCALE = px.colors.sequential.Reds # Untuk Bar, Heatmap, dan Peta Kepadatan
RED_LINE_COLOR = '#E3170D' # Warna Merah Solid untuk Garis
RED_MARKER_COLOR = '#FF6347' # Warna Merah Solid untuk Marker
RED_PIE_COLORS = ['#E3170D', '#FF6347', '#FF9999', '#A80E0E'] # Palet untuk Pie Chart

# Konfigurasi Halaman Streamlit
st.set_page_config(
    page_title="Dashboard Analisis Kejahatan Los Angeles",
    layout="wide",
    initial_sidebar_state="expanded"
)

def local_css(file_name):
    """Membaca file CSS lokal dan menyuntikkannya ke Streamlit."""
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"File CSS '{file_name}' tidak ditemukan.")

# Panggil fungsi ini di awal skrip Streamlit Anda
local_css("pages/style.css")

# --- 1. Pemuatan dan Pembersihan Data (Caching) ---
@st.cache_data
def load_data(file_path):
    """Memuat dan membersihkan data."""
    try:
        df = pd.read_csv(file_path)

        # Konversi tipe data
        df['occurrence_date'] = pd.to_datetime(df['occurrence_date'])
        df['occurrence_hour'] = df['occurrence_time'].apply(lambda x: int(str(x).split(':')[0]))
        df['day_of_week'] = df['occurrence_date'].dt.day_name()
        df['month_year'] = df['occurrence_date'].dt.to_period('M').astype(str)
        df['year'] = df['occurrence_date'].dt.year

        # Mengganti nilai 'Unknown' atau ' ' menjadi 'Not Specified'
        for col in ['victim_gender', 'victim_ethnicity', 'weapon']:
            if col in df.columns:
                df[col] = df[col].replace(['Unknown', ' '], 'Not Specified')
        
        # Penanganan data 'victim_age' yang tidak masuk akal (misalnya < 0 atau sangat tinggi)
        df = df[df['victim_age'] >= 0]
        df['victim_age_group'] = pd.cut(df['victim_age'],
                                        bins=[0, 17, 24, 34, 44, 54, 64, 120],
                                        labels=['<18 (Child)', '18-24 (Young Adult)', '25-34 (Adult)', '35-44 (Middle-aged)', '45-54 (Mature Adult)', '55-64 (Senior)', '65+ (Elderly)'],
                                        right=False,
                                        # Menangani NaN yang mungkin muncul
                                        include_lowest=True).astype(str).replace('nan', 'Not Specified')

        # Drop baris dengan koordinat (latitude, longitude) yang nol atau tidak valid
        df = df[(df['latitude'] != 0) & (df['longitude'] != 0)]
        
        return df
    except FileNotFoundError:
        st.error(f"File **{file_path}** tidak ditemukan. Pastikan file berada di direktori yang sama.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Terjadi kesalahan saat memproses data: {e}")
        return pd.DataFrame()

FILE_PATH = 'pages/crime_data_clean.csv'
df = load_data(FILE_PATH)

if df.empty:
    st.stop()

# --- 2. Sidebar (Filter) ---

# Pastikan kolom 'occurrence_date' bertipe datetime
# df['occurrence_date'] = pd.to_datetime(df['occurrence_date'])

# Filter Utama: Rentang Tanggal (Slider tetap sama)
# --- 2. Sidebar (Filter) ---

# Pastikan kolom 'occurrence_date' bertipe datetime
# df['occurrence_date'] = pd.to_datetime(df['occurrence_date'])

min_timestamp = df['occurrence_date'].min().date()
max_timestamp = df['occurrence_date'].max().date()

# =====================================================================
# PERUBAHAN: Ganti st.slider dengan dua st.date_input
# =====================================================================

st.sidebar.header("Filter Analisis") 

# Menambahkan judul di atas input tanggal
st.sidebar.write("Pilih Rentang Tanggal Kejadian")

# Membuat 2 kolom di dalam sidebar
col_start, col_end = st.sidebar.columns(2)

# Input tanggal "Dari" di kolom pertama
with col_start: 
    start_date_input = st.date_input(
        "Dari", 
        min_value=min_timestamp, 
        max_value=max_timestamp, 
        value=min_timestamp, 
        key="start_date_filter",
        # Menyembunyikan label "Dari" agar lebih rapi
        # label_visibility="collapsed" 
    )

# Input tanggal "Sampai" di kolom kedua
with col_end:
    end_date_input = st.date_input(
        "Sampai", 
        min_value=min_timestamp, 
        max_value=max_timestamp, 
        value=max_timestamp, 
        key="end_date_filter",
        # Menyembunyikan label "Sampai" agar lebih rapi
        # label_visibility="collapsed"
    )

# --- Terapkan Filter Rentang Tanggal ---
# Pastikan Tanggal Awal <= Tanggal Akhir
# if start_date_input <= end_date_input:
#     start_date = pd.to_datetime(start_date_input)
#     # Tambahkan 23:59:59 ke tanggal akhir agar mencakup seluruh hari
#     end_date = pd.to_datetime(end_date_input) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1) 
    
#     df_filtered = df[(df['occurrence_date'] >= start_date) & (df['occurrence_date'] <= end_date)]
# else:
#     st.sidebar.error("Tanggal Awal harus sebelum atau sama dengan Tanggal Akhir.")
#     df_filtered = df.copy() # Gunakan data mentah jika filter tidak valid
    
# =====================================================================

# --- Terapkan Filter Rentang Tanggal ---
# Inisialisasi variabel untuk menghindari error jika filter tidak valid
# ---------------------------------------------------------------------
# BAGIAN FILTER (TEMPAT LOGIKA BARU DITAMBAHKAN)
# ---------------------------------------------------------------------

# Ambil tanggal data tertua yang tersedia (Global)
min_data_date = df['occurrence_date'].min()
# Inisialisasi variabel di luar if/else
is_delta_valid = False 
total_crimes_prev = 0
crimes_per_day_prev = 0
duration_days = 0 

if start_date_input <= end_date_input:
    start_date = pd.to_datetime(start_date_input)
    # Tambahkan 23:59:59 ke tanggal akhir
    end_date = pd.to_datetime(end_date_input) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1) 
    
    df_filtered = df[(df['occurrence_date'] >= start_date) & (df['occurrence_date'] <= end_date)]

    # --- PERHITUNGAN PERIODE SEBELUMNYA ---
    duration_days = (end_date_input - start_date_input).days + 1
    
    end_date_prev = start_date - pd.Timedelta(seconds=1) 
    start_date_prev = end_date_prev - pd.Timedelta(days=duration_days - 1)
    
    # -----------------------------------------------------------------
    # LOGIKA BARU: VALIDASI KETERSEDIAAN DATA SEBELUMNYA
    # -----------------------------------------------------------------
    
    # Cek: Apakah awal periode pembanding lebih awal dari tanggal data tertua?
    if start_date_prev < min_data_date:
        is_delta_valid = False
    else:
        is_delta_valid = True
        
        # Filter data untuk periode sebelumnya
        df_prev_period = df[(df['occurrence_date'] >= start_date_prev) & (df['occurrence_date'] <= end_date_prev)]
        
        # Hitung Metrik Periode Sebelumnya (Hanya jika valid)
        total_crimes_prev = len(df_prev_period)
        crimes_per_day_prev = round(total_crimes_prev / duration_days, 2) if duration_days > 0 else 0
        
else:
    # ... (error handling tetap di sini)
    df_filtered = df.copy() 
    
# ---------------------------------------------------------------------
# AKHIR BLOK FILTER
# ---------------------------------------------------------------------

# ... (Logika Filter Multiselect: Area, Kategori, Gender)

# --- Fungsi Bantuan untuk Filter Multiselect Tanpa Default 'Semua Data' ---
def get_unique_options(dataframe, column_name):
    """Mendapatkan opsi unik tanpa menambahkan 'Semua Data'."""
    # Mengambil semua opsi unik dari data yang sudah difilter berdasarkan tanggal
    return sorted(dataframe[column_name].unique().tolist())

# Filter Tambahan (Multiselect tanpa opsi 'Semua Data' dan tanpa default)

# Q2: Area
area_options = get_unique_options(df_filtered, 'area')
area_selection = st.sidebar.multiselect(
    "Pilih Area",
    options=area_options,
    # Tidak ada default, sehingga daftar akan kosong secara default
)

# Q4: Kategori Kejahatan
crime_options = get_unique_options(df_filtered, 'crime_category')
crime_category_selection = st.sidebar.multiselect(
    "Pilih Kategori Kejahatan",
    options=crime_options,
    # Tidak ada default, sehingga daftar akan kosong secara default
)

# Q5: Gender Korban
gender_options = get_unique_options(df_filtered, 'victim_gender')
gender_selection = st.sidebar.multiselect(
    "Pilih Gender Korban",
    options=gender_options,
    # Tidak ada default, sehingga daftar akan kosong secara default
)

# --- Terapkan filter tambahan dengan logika kosong = semua data ---
df_final = df_filtered.copy()

# Logika Filter: Jika list selection kosong, gunakan semua data pada kolom tersebut.
if area_selection: # Jika list tidak kosong (ada pilihan)
    df_final = df_final[df_final['area'].isin(area_selection)]

if crime_category_selection: # Jika list tidak kosong (ada pilihan)
    df_final = df_final[df_final['crime_category'].isin(crime_category_selection)]

if gender_selection: # Jika list tidak kosong (ada pilihan)
    df_final = df_final[df_final['victim_gender'].isin(gender_selection)]

# Sekarang df_final berisi data yang telah difilter.
# Jika `area_selection` kosong, baris filter `df_final = df_final[df_final['area'].isin(area_selection)]` dilewati,
# dan semua data pada kolom 'area' tetap dipertahankan.

# --- 3. Judul Dashboard ---
st.title("Dashboard Analisis Kejahatan Los Angeles 2020 - 2025")

# --- 4. Baris 1: Key Performance Indicators (KPI) & Peta ---
# Buat dua kolom utama: Kiri (untuk KPI) dan Kanan (untuk Peta)
col_kpi, col_map = st.columns([1, 2]) # Rasio 1:2 atau 1:1.5 akan cocok untuk KPI & Peta

# --- Kolom Kanan: Peta (Q9) ---
with col_map:
    # Gunakan Plotly Scattermapbox untuk kepadatan
    # Pastikan df_final tidak kosong sebelum sampling
    if not df_final.empty:
        # Ambil sampel jika data terlalu besar (Maks 20000 baris)
        sample_df = df_final.sample(min(20000, len(df_final)))
        
        fig_map = go.Figure(go.Densitymapbox(
            # Data koordinat
            lat=sample_df['latitude'], 
            lon=sample_df['longitude'], 
            
            # Pengaturan Radius dan Warna Kepadatan
            radius=10, # Ukuran radius kepadatan (sesuaikan nilainya)
            colorscale=RED_COLOR_SCALE, # <--- **PERUBAHAN WARNA**
            zmin=0,
            opacity=0.7,

            colorbar=dict(
                title=dict(
                    text='Kepadatan Kejahatan', 
                    side='bottom' # Posisikan judul di atas colorbar horizontal
                ),
                orientation='h', # <--- KUNCI: Membuatnya Horizontal
                x=0.5,           # <--- Posisikan di tengah horizontal plot
                y=-0.0001,         # <--- Posisikan di bawah plot (sesuaikan nilai ini)
                xanchor='center',
                yanchor='top',
                len=1,         # Panjang colorbar (70% lebar plot)
                bgcolor='rgba(0,0,0,0)', 
                thickness=15
            ),
            
            # Pengaturan Hover/Tooltip (Opsional, Densitymapbox kurang fleksibel)
            customdata=sample_df[['area', 'crime_category']],
            hovertemplate="Area: %{customdata[0]}<br>Kategori Kejahatan: %{customdata[1]}<extra></extra>"
        ))

        # Pengaturan Tata Letak Peta
        fig_map.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            # Menentukan style peta
            mapbox_style="open-street-map", # Diubah agar heatmap merah lebih menonjol
            # Menentukan lokasi awal peta
            mapbox_center={"lat": sample_df['latitude'].mean(), "lon": sample_df['longitude'].mean()},
            # Menentukan zoom
            mapbox_zoom=10,
            # Menghilangkan margin agar peta memenuhi kotak
            margin={"r":0, "t":0, "l":0, "b":0},
            # Menentukan tinggi
            height=525, # Sesuaikan kembali tinggi agar sesuai dengan 4 KPI
        )
    else:
        # Jika kosong, buat Figure kosong
        fig_map = go.Figure().update_layout(
             title="Data Filter Kosong. Tidak ada peta untuk ditampilkan.", height=600
        )
        
    st.plotly_chart(fig_map, use_container_width=True)

# --- Kolom Kiri: Key Performance Indicators (KPI) ---
# with col_kpi:     
#     # Hitung KPI (Mengambil perhitungan dari kode asli Anda)
#     total_crimes = len(df_final)
    
#     # Hitung selisih hari, pastikan tidak 0 untuk menghindari ZeroDivisionError
#     delta_days = (end_date - start_date).days if 'end_date' in locals() and 'start_date' in locals() else 1
#     crimes_per_day = round(total_crimes / delta_days, 2) if delta_days > 0 else 0
    
#     # KPI 3: Area dengan Kejahatan Tertinggi (Q2)
#     top_area = df_final['area'].mode().iloc[0] if not df_final.empty and not df_final['area'].mode().empty else "N/A"
    
#     # KPI 4: Jenis Kejahatan Paling Dominan (Q4)
#     # Perhatikan: Anda menggunakan 'crime' di kode asli, bukan 'crime_category'
#     top_crime = df_final['crime'].mode().iloc[0] if not df_final.empty and not df_final['crime'].mode().empty else "N/A"

#     # KPI 1: Total Jumlah Kejahatan
#     st.metric(label="Total Jumlah Kejahatan", value=f"{total_crimes:,}")

#     # KPI 2: Rata-Rata Kejahatan per Hari
#     st.metric(label="Rata-Rata Kejahatan per Hari", value=f"{crimes_per_day:.2f}")

#     # KPI 3: Area dengan Kejahatan Tertinggi (Q2)
#     st.metric(label="Area Paling Rawan", value=top_area)

#     # KPI 4: Jenis Kejahatan Paling Dominan (Q4)
#     st.metric(label="Kejahatan Paling Dominan", value=top_crime)

# --- Kolom Kiri: Key Performance Indicators (KPI) ---
with col_kpi:
    # Hitung KPI (Mengambil perhitungan dari kode asli Anda)
    total_crimes = len(df_final)
    
    # Durasi sudah dihitung di bagian filter: duration_days
    crimes_per_day = round(total_crimes / duration_days, 2) if duration_days > 0 else 0
    
    # ********************* DELTA CALCULATION *********************
    delta_total_crimes = total_crimes - total_crimes_prev
    delta_crimes_per_day = crimes_per_day - crimes_per_day_prev
    # *************************************************************

    # KPI 3: Area dengan Kejahatan Tertinggi (Q2)
    top_area = df_final['area'].mode().iloc[0] if not df_final.empty and not df_final['area'].mode().empty else "N/A"
    
    # KPI 4: Jenis Kejahatan Paling Dominan (Q4)
    top_crime = df_final['crime'].mode().iloc[0] if not df_final.empty and not df_final['crime'].mode().empty else "N/A"

    # --- Penentuan String Delta ---
    if is_delta_valid:
        delta_str_crimes = f"{delta_total_crimes:+,} dari periode sebelumnya" # + untuk memaksa tanda +
        delta_str_day = f"{delta_crimes_per_day:+.2f} dari periode sebelumnya"
    else:
        # Jika tidak valid, set delta ke None (tidak ditampilkan)
        delta_str_crimes = None 
        delta_str_day = None
        
    # KPI 1: Total Jumlah Kejahatan
    st.metric(
        label="Total Jumlah Kejahatan", 
        value=f"{total_crimes:,}",
        delta=delta_str_crimes,
        delta_color="inverse"
    )

    # KPI 2: Rata-Rata Kejahatan per Hari
    st.metric(
        label="Rata-Rata Kejahatan per Hari", 
        value=f"{crimes_per_day:.2f}",
        delta=delta_str_day,
        delta_color="inverse"
    )

    # KPI 3: Area dengan Kejahatan Tertinggi (Q2)
    st.metric(label="Area Paling Rawan", value=top_area)

    # KPI 4: Jenis Kejahatan Paling Dominan (Q4)
    st.metric(label="Kejahatan Paling Dominan", value=top_crime)

# --- 5. Baris 2: Tren Waktu (Line Chart) ---
# Q1: Bagaimana tren jumlah kejahatan? (Line Chart)
# Gunakan st.container() atau langsung di body utama (di luar kolom sebelumnya)     
# Pastikan data frame tidak kosong sebelum grouping
if not df_final.empty:
    df_trend = df_final.groupby('month_year').size().reset_index(name='Jumlah Kejahatan')
    df_trend['occurrence_date'] = pd.to_datetime(df_trend['month_year']) # Untuk sorting
    df_trend = df_trend.sort_values('occurrence_date')
else:
    # Buat dataframe kosong agar chart tidak error jika df_final kosong
    df_trend = pd.DataFrame({'month_year': [], 'Jumlah Kejahatan': [], 'occurrence_date': []})
    
fig_trend = px.line(
    df_trend, 
    x='month_year', 
    y='Jumlah Kejahatan', 
    title='Kejahatan per Bulan',
    markers=True,
    labels={'month_year': 'Bulan-Tahun', 'Jumlah Kejahatan': 'Jumlah Kejahatan'}
)
# <--- **PERUBAHAN WARNA LINE CHART**
fig_trend.update_traces(line=dict(color=RED_LINE_COLOR), marker=dict(color=RED_MARKER_COLOR))
# fig_trend.update_xaxes(tickangle=45)
fig_trend.update_layout(
    title={
        'text': fig_trend.layout.title.text, # Menggunakan kembali judul yang sudah ada
        'x': 0.5,
        'xanchor': 'center'
    }
)
st.plotly_chart(fig_trend, use_container_width=True)

# st.markdown("---")

# --- 6. Baris 3: Area, Jenis Kejahatan, dan Waktu Rawan ---
col5, col6 = st.columns(2)

# Q2: Area mana yang memiliki tingkat kejahatan tertinggi dan terendah? (Bar Chart Area)
with col5:
    df_area = df_final.groupby('area').size().reset_index(name='Jumlah Kejahatan').sort_values(by='Jumlah Kejahatan', ascending=False)
    
    fig_area = px.bar(
        df_area,
        x='Jumlah Kejahatan',
        y='area',
        title='Tingkat Kejahatan Berdasarkan Area',
        orientation='h',
        color='Jumlah Kejahatan',
        color_continuous_scale=RED_COLOR_SCALE, # <--- **PERUBAHAN WARNA BAR CHART**
        labels={'area': 'Area', 'Jumlah Kejahatan': 'Jumlah Kejahatan'}
    )
    fig_area.update_yaxes(categoryorder='total ascending')
    fig_area.update_layout(
        title={
            'text': fig_area.layout.title.text, # Menggunakan kembali judul yang sudah ada
            'x': 0.5,
            'xanchor': 'center'
        }
    )
    st.plotly_chart(fig_area, use_container_width=True)

# Q4: Jenis kejahatan apa yang paling dominan dan paling jarang terjadi? (Bar Chart Crime Type)
with col6:
    df_crime = df_final['crime_category'].value_counts().reset_index(name='Jumlah Kejahatan')
    df_crime.columns = ['Kategori Kejahatan', 'Jumlah Kejahatan']
    
    fig_crime = px.bar(
        df_crime,
        x='Jumlah Kejahatan',
        y='Kategori Kejahatan',
        title='Jenis Kejahatan Paling Dominan',
        orientation='h',
        color='Jumlah Kejahatan',
        color_continuous_scale=RED_COLOR_SCALE, # <--- **PERUBAHAN WARNA BAR CHART**
        labels={'Kategori Kejahatan': 'Kategori Kejahatan', 'Jumlah Kejahatan': 'Jumlah Kejahatan'}
    )
    fig_crime.update_yaxes(categoryorder='total ascending')
    fig_crime.update_layout(
        title={
            'text': fig_crime.layout.title.text, # Menggunakan kembali judul yang sudah ada
            'x': 0.5,
            'xanchor': 'center'
        }
    )
    st.plotly_chart(fig_crime, use_container_width=True)

col7, col8 = st.columns(2)

# Q3: Pada jam berapa dan hari apa kejahatan paling sering terjadi? (Time Analysis)
with col7:
    df_hour = df_final['occurrence_hour'].value_counts().reset_index(name='Jumlah Kejahatan')
    df_hour.columns = ['Jam Kejadian', 'Jumlah Kejahatan']
    df_hour = df_hour.sort_values(by='Jam Kejadian')

    # --- PERUBAHAN UNTUK INDIKATOR WARNA SKALA ---
    fig_hour = px.bar(
        df_hour,
        x='Jam Kejadian',
        y='Jumlah Kejahatan',
        title='Kejahatan per Jam (24h)',
        # TAMBAHKAN: Menggunakan kolom Jumlah Kejahatan untuk menentukan warna
        color='Jumlah Kejahatan', 
        # TAMBAHKAN: Menggunakan skala warna untuk gradien
        color_continuous_scale=RED_COLOR_SCALE
    )
    # CATATAN: Karena sudah menggunakan 'color' dan 'color_continuous_scale', 
    # update_traces(marker_color=...) sudah tidak diperlukan.
    
    # Menyesuaikan label dan tampilan axis
    fig_hour.update_layout(coloraxis_showscale=True) # Pastikan color bar ditampilkan
    fig_hour.update_xaxes(tick0=0, dtick=1)
    fig_hour.update_layout(
        title={
            'text': fig_hour.layout.title.text, # Menggunakan kembali judul yang sudah ada
            'x': 0.5,
            'xanchor': 'center'
        }
    )
    st.plotly_chart(fig_hour, use_container_width=True)

with col8:
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    df_day = df_final['day_of_week'].value_counts().reindex(day_order).fillna(0).reset_index(name='Jumlah Kejahatan')
    df_day.columns = ['Hari', 'Jumlah Kejahatan']

    fig_day = px.bar(
        df_day,
        x='Hari',
        y='Jumlah Kejahatan',
        title='Kejahatan per Hari dalam Seminggu',
        color='Jumlah Kejahatan',
        color_continuous_scale=RED_COLOR_SCALE # <--- **PERUBAHAN WARNA BAR CHART**
    )

    fig_day.update_layout(
        title={
            'text': fig_day.layout.title.text, # Menggunakan kembali judul yang sudah ada
            'x': 0.5,
            'xanchor': 'center'
        }
    )
    st.plotly_chart(fig_day, use_container_width=True)

# st.markdown("---")

# --- 7. Baris 4: Profil Korban dan Konteks Kejadian ---
col9, col10, col11 = st.columns(3)

# Q5 & Q6: Distribusi Kejahatan berdasarkan Gender, Usia, dan Etnis Korban
with col9:
    df_gender = df_final['victim_gender'].value_counts().reset_index(name='Jumlah')
    df_gender.columns = ['Gender', 'Jumlah']
    
    fig_gender = px.pie(
        df_gender,
        values='Jumlah',
        names='Gender',
        title='Proporsi Gender Korban',
        hole=.3,
        color_discrete_sequence=RED_PIE_COLORS # <--- **PERUBAHAN WARNA PIE CHART**
    )

    fig_gender.update_layout(
        title={
            'text': fig_trend.layout.title.text, # Menggunakan kembali judul yang sudah ada
            'x': 0.5,
            'xanchor': 'center'
        }
    )
    st.plotly_chart(fig_gender, use_container_width=True)

with col10:
    df_age = df_final['victim_age_group'].value_counts().reset_index(name='Jumlah')
    df_age.columns = ['Kelompok Usia', 'Jumlah']

    # Urutan kelompok usia
    age_order = ['<18 (Child)', '18-24 (Young Adult)', '25-34 (Adult)', '35-44 (Middle-aged)', '45-54 (Mature Adult)', '55-64 (Senior)', '65+ (Elderly)', 'Not Specified']
    df_age['Kelompok Usia'] = pd.Categorical(df_age['Kelompok Usia'], categories=age_order, ordered=True)
    df_age = df_age.sort_values('Kelompok Usia')
    
    fig_age = px.bar(
        df_age,
        x='Kelompok Usia',
        y='Jumlah',
        title='Kejahatan per Kelompok Usia',
        color='Jumlah', # Tambahkan color agar bisa menggunakan color_continuous_scale
        color_continuous_scale=RED_COLOR_SCALE # <--- **PERUBAHAN WARNA BAR CHART**
    )
    fig_age.update_xaxes(tickangle=45)
    fig_age.update_layout(
        title={
            'text': fig_age.layout.title.text, # Menggunakan kembali judul yang sudah ada
            'x': 0.5,
            'xanchor': 'center'
        }
    )
    st.plotly_chart(fig_age, use_container_width=True)

with col11:
    df_ethnic = df_final['victim_ethnicity'].value_counts().reset_index(name='Jumlah')
    df_ethnic.columns = ['Etnis Korban', 'Jumlah']
    
    fig_ethnic = px.bar(
        df_ethnic.head(10),
        x='Jumlah',
        y='Etnis Korban',
        orientation='h',
        title='Top 10 Etnis Korban',
        color='Jumlah', # Tambahkan color agar bisa menggunakan color_continuous_scale
        color_continuous_scale=RED_COLOR_SCALE # <--- **PERUBAHAN WARNA BAR CHART**
    )
    fig_ethnic.update_yaxes(categoryorder='total ascending')
    fig_ethnic.update_layout(
        title={
            'text': fig_ethnic.layout.title.text, # Menggunakan kembali judul yang sudah ada
            'x': 0.5,
            'xanchor': 'center'
        }
    )
    st.plotly_chart(fig_ethnic, use_container_width=True)

# st.markdown("---")

# --- 8. Baris 5: Senjata dan Tempat Kejadian ---
col12, col13 = st.columns(2)

# Q7: Jenis senjata apa yang paling sering digunakan? (Bar Chart Weapon)
with col12:
    df_weapon = df_final['weapon'].value_counts().reset_index(name='Jumlah')
    df_weapon.columns = ['Senjata', 'Jumlah']

    # Filter 'Unknown'/'Not Specified' karena sering mendominasi
    df_weapon_clean = df_weapon[~df_weapon['Senjata'].isin(['Not Specified', 'Unknown'])].head(10)
    
    fig_weapon = px.bar(
        df_weapon_clean,
        x='Jumlah',
        y='Senjata',
        orientation='h',
        color='Jumlah',
        color_continuous_scale=RED_COLOR_SCALE, # <--- **PERUBAHAN WARNA BAR CHART**
        title='Top 10 Senjata (Exclude Not Specified)'
    )
    fig_weapon.update_yaxes(categoryorder='total ascending')
    fig_weapon.update_layout(
        title={
            'text': fig_weapon.layout.title.text, # Menggunakan kembali judul yang sudah ada
            'x': 0.5,
            'xanchor': 'center'
        }
    )
    st.plotly_chart(fig_weapon, use_container_width=True)

# Q8: Bagaimana hubungan antara jenis tempat kejadian dengan jenis kejahatan? (Heatmap Premise vs Crime)
with col13:
    # Hitung frekuensi gabungan (Crosstab)
    df_cross = pd.crosstab(df_final['premise'], df_final['crime_category'])
    
    # Ambil 10 tempat kejadian teratas
    top_premises = df_final['premise'].value_counts().head(10).index
    df_cross_filtered = df_cross.loc[top_premises]

    # Buat Heatmap
    fig_heatmap = px.imshow(
        df_cross_filtered, 
        text_auto=True,
        aspect="auto",
        labels=dict(x="Kategori Kejahatan", y="Tempat Kejadian (Premise)", color="Jumlah Kejahatan"),
        x=df_cross_filtered.columns.tolist(),
        y=df_cross_filtered.index.tolist(),
        color_continuous_scale=RED_COLOR_SCALE, # <--- **PERUBAHAN WARNA HEATMAP**
        title='Hubungan Jenis Tempat Kejadian vs Kategori Kejahatan'
    )
    fig_heatmap.update_xaxes(tickangle=45)
    fig_heatmap.update_layout(
        title={
            'text': fig_heatmap.layout.title.text, # Menggunakan kembali judul yang sudah ada
            'x': 0.5,
            'xanchor': 'center'
        }
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)