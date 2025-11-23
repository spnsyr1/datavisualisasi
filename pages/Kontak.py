import streamlit as st

def local_css(file_name):
    """Membaca file CSS lokal dan menyuntikkannya ke Streamlit."""
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"File CSS '{file_name}' tidak ditemukan.")

# Panggil fungsi ini di awal skrip Streamlit Anda

# --- Data Anggota Kelompok ---
anggota = [
    {
        "nama": "Risma Auliya Salsabilla",
        "nim": "2210631170100",
        "email": "2210631170100@student.unsika.ac.id", # Ganti dengan email Risma yang sebenarnya
        "foto": "assets/log-unsika.png" 
    },
    {
        "nama": "Siti Zulhi Nirma Saidah",
        "nim": "2210631170103",
        "email": "2210631170103@student.unsika.ac.id", # Ganti dengan email Siti yang sebenarnya
        "foto": "assets/log-unsika.png" 
    },
    {
        "nama": "Sopian Syauri",
        "nim": "2210631170104",
        "email": "2210631170104@student.unsika.ac.id", # Ganti dengan email Sopian yang sebenarnya
        "foto": "assets/log-unsika.png" 
    }
]

# --- Informasi Jurusan/Institusi ---
jurusan = "Informatika"
universitas = "Universitas Singaperbangsa Karawang"
logo_kelompok = "assets/logo.png" # Ganti dengan path logo kelompok Anda

def page_contact():
    local_css("pages/style.css")

    # --- Bagian Logo Kelompok (Tengah) ---
    try:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            # Gunakan logo Universitas dari sumber jika ada, atau logo kelompok
            st.image(logo_kelompok, width=520) 
            # Jika ingin menggunakan logo UNSICA dari laporan:
            # st.image("path/ke/logo/universitas.png", caption="Universitas Singaperbangsa Karawang", width=200) 
    except FileNotFoundError:
        st.warning("Gagal memuat logo kelompok. Pastikan path file benar.")
    
    st.markdown("<br>", unsafe_allow_html=True)

    # --- Bagian Daftar Anggota (3 Kolom) ---
    st.title("Pengembang & Tim Analis")
    
    # Membuat 3 kolom
    cols = st.columns(3)

    for i, member in enumerate(anggota):
        with cols[i]:
            # Foto Profil
            try:
                st.image(member["foto"], width=150)
            except FileNotFoundError:
                st.error(f"Foto {member['nama']} tidak ditemukan.")
            
            # Detail Anggota
            st.subheader(member["nama"])
            st.markdown(f"**NIM:** {member['nim']}")
            
            # Informasi Akademis dan Kontak
            st.markdown(f"**Program Studi:** {jurusan}")
            st.markdown(f"**Institusi:** {universitas}")
            st.markdown(f"**Email:** [{member['email']}](mailto:{member['email']})") # Membuat link email
            
# --- Kerangka Utama Aplikasi (Opsional, untuk Pengujian) ---

if __name__ == "__main__":
    # Harap integrasikan fungsi page_contact() ini ke dalam struktur utama aplikasi Streamlit Anda.
    page_contact()