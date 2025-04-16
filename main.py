import streamlit as st
import pandas as pd
from datetime import datetime
import os

# Konfigurasi dasar
st.set_page_config(page_title="PT. JKL Digital Credit System", layout="wide")

# Simulasi database sederhana
if 'applications' not in st.session_state:
    st.session_state.applications = pd.DataFrame(columns=[
        'id', 'nama', 'nik', 'tanggal_lahir', 'status_perkawinan', 
        'tipe_kendaraan', 'harga', 'down_payment', 'tenor', 'status', 'tanggal'
    ])

if 'users' not in st.session_state:
    st.session_state.users = {
        'konsumen1': 'password',
        'marketing1': 'password',
        'admin1': 'password'
    }

if 'user_roles' not in st.session_state:
    st.session_state.user_roles = {
        'konsumen1': 'konsumen',
        'marketing1': 'marketing',
        'admin1': 'admin'
    }

if 'current_user' not in st.session_state:
    st.session_state.current_user = None
    st.session_state.current_role = None

# Fungsi login sederhana
def login(username, password):
    if username in st.session_state.users and st.session_state.users[username] == password:
        st.session_state.current_user = username
        st.session_state.current_role = st.session_state.user_roles[username]
        return True
    return False

# Halaman login
def login_page():
    st.title("PT. JKL Digital Credit System")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            if login(username, password):
                st.success(f"Login berhasil sebagai {st.session_state.current_role}")
                st.rerun()
            else:
                st.error("Username atau password salah")

# Form pengajuan kredit
def application_form():
    st.title("Form Pengajuan Kredit Kendaraan")
    
    with st.form("credit_application"):
        # Data Konsumen
        st.subheader("Data Konsumen")
        col1, col2 = st.columns(2)
        with col1:
            nama = st.text_input("Nama Lengkap")
            nik = st.text_input("NIK")
            tanggal_lahir = st.date_input("Tanggal Lahir")
        with col2:
            status_perkawinan = st.selectbox("Status Perkawinan", ["Belum Menikah", "Menikah", "Cerai"])
            alamat = st.text_area("Alamat")
            telepon = st.text_input("No. Telepon")
        
        # Data Kendaraan
        st.subheader("Data Kendaraan")
        col1, col2 = st.columns(2)
        with col1:
            merk_kendaraan = st.selectbox("Merk Kendaraan", ["Toyota", "Honda", "Suzuki", "Daihatsu", "Lainnya"])
            model_kendaraan = st.text_input("Model Kendaraan")
            tipe_kendaraan = st.selectbox("Tipe Kendaraan", ["Sedan", "SUV", "MPV", "LCGC", "Sport", "Lainnya"])
        with col2:
            warna_kendaraan = st.text_input("Warna Kendaraan")
            harga_kendaraan = st.number_input("Harga Kendaraan", min_value=0, step=1000000)
            dealer = st.text_input("Dealer")
            
        # Data Pinjaman
        st.subheader("Data Pinjaman")
        col1, col2 = st.columns(2)
        with col1:
            down_payment = st.number_input("Down Payment", min_value=0, step=1000000)
            tenor = st.selectbox("Tenor (Bulan)", [12, 24, 36, 48, 60])
        with col2:
            asuransi = st.selectbox("Jenis Asuransi", ["All Risk", "Total Loss Only", "Tidak Ada"])
            
        # Upload Dokumen
        st.subheader("Upload Dokumen")
        ktp_file = st.file_uploader("Upload KTP", type=["jpg", "jpeg", "png", "pdf"])
        bukti_bayar = st.file_uploader("Upload Bukti Bayar DP", type=["jpg", "jpeg", "png", "pdf"])
        
        submitted = st.form_submit_button("Submit Pengajuan")
        
        if submitted:
            if not (nama and nik and tipe_kendaraan and harga_kendaraan and down_payment):
                st.error("Mohon lengkapi data yang diperlukan")
            else:
                # Tambahkan aplikasi baru ke database
                new_application = {
                    'id': f"APP{len(st.session_state.applications) + 1:04d}",
                    'nama': nama,
                    'nik': nik,
                    'tanggal_lahir': tanggal_lahir.strftime("%Y-%m-%d"),
                    'status_perkawinan': status_perkawinan,
                    'tipe_kendaraan': tipe_kendaraan,
                    'harga': harga_kendaraan,
                    'down_payment': down_payment,
                    'tenor': tenor,
                    'status': 'Menunggu Review',
                    'tanggal': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                st.session_state.applications = pd.concat([
                    st.session_state.applications, 
                    pd.DataFrame([new_application])
                ], ignore_index=True)
                
                # Simpan file dokumen (dalam implementasi nyata akan disimpan ke cloud/server)
                if ktp_file is not None:
                    st.success(f"KTP berhasil diupload")
                if bukti_bayar is not None:
                    st.success(f"Bukti bayar berhasil diupload")
                    
                st.success(f"Pengajuan berhasil dengan ID: {new_application['id']}")

# Dashboard status pengajuan
def application_dashboard():
    st.title("Dashboard Pengajuan Kredit")
    
    role = st.session_state.current_role
    
    # Filter berdasarkan role
    if role == 'konsumen':
        df = st.session_state.applications[st.session_state.applications['nama'] == st.session_state.current_user]
    else:
        df = st.session_state.applications
    
    # Tampilkan dashboard
    st.write(f"Total pengajuan: {len(df)}")
    
    # Status count
    if not df.empty:
        status_counts = df['status'].value_counts().reset_index()
        status_counts.columns = ['Status', 'Jumlah']
        col1, col2 = st.columns([1, 2])
        with col1:
            st.subheader("Status Pengajuan")
            st.dataframe(status_counts)
        with col2:
            st.subheader("Data Pengajuan")
            st.dataframe(df)
    else:
        st.info("Belum ada data pengajuan")
    
    # Fitur approval untuk admin dan marketing
    if role in ['admin', 'marketing'] and not df.empty:
        st.subheader("Approval Pengajuan")
        with st.form("approval_form"):
            app_id = st.selectbox("Pilih ID Pengajuan", df['id'].tolist())
            new_status = st.selectbox("Update Status", [
                "Menunggu Review", "Dokumen Kurang", "Disetujui", "Ditolak", 
                "Proses Pencairan", "Selesai"
            ])
            notes = st.text_area("Catatan")
            submitted = st.form_submit_button("Update Status")
            
            if submitted:
                # Update status
                idx = df[df['id'] == app_id].index[0]
                st.session_state.applications.at[idx, 'status'] = new_status
                st.success(f"Status pengajuan {app_id} diubah menjadi {new_status}")
                st.rerun()

# Main app
def main():
    # Sidebar navigation
    if st.session_state.current_user:
        st.sidebar.title(f"Halo, {st.session_state.current_user}")
        st.sidebar.write(f"Role: {st.session_state.current_role}")
        
        if st.session_state.current_role == 'konsumen':
            menu = st.sidebar.radio("Menu", ["Form Pengajuan", "Status Pengajuan"])
        else:
            menu = st.sidebar.radio("Menu", ["Dashboard Pengajuan"])
            
        if st.sidebar.button("Logout"):
            st.session_state.current_user = None
            st.session_state.current_role = None
            st.rerun()
            
        # Render halaman sesuai menu
        if menu == "Form Pengajuan":
            application_form()
        elif menu == "Status Pengajuan" or menu == "Dashboard Pengajuan":
            application_dashboard()
    else:
        login_page()

if __name__ == "__main__":
    main()
