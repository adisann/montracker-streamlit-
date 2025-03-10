import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import os
import io

# Konfigurasi halaman
st.set_page_config(
    page_title="Pelacak Keuangan",
    page_icon="💰",
    layout="wide",
)

# Tambahkan CSS untuk styling tabs dan elements
st.markdown(
    """
    <style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 1px;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 10px 20px;
        border-radius: 4px;
        background-color: #F0F2F6;
        box-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    .stTabs [aria-selected="true"] {
        background-color: #1976D2 !important;
        color: white !important;
    }
    /* Styling untuk tombol pagination */
    .pagination-container {
        display: flex;
        justify-content: center;
        margin-top: 20px;
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Fungsi untuk memuat data
@st.cache_data
def load_data():
    if os.path.exists('keuangan.csv'):
        df = pd.read_csv('keuangan.csv')
        # Pastikan konversi tanggal selalu dilakukan
        if 'tanggal' in df.columns:
            df['tanggal'] = pd.to_datetime(df['tanggal'], errors='coerce')
        return df
    return pd.DataFrame(columns=['tanggal', 'jenis', 'kategori', 'jumlah', 'deskripsi'])

# Fungsi untuk menyimpan data
def save_data(df):
    # Pastikan kolom tanggal dalam format yang tepat sebelum menyimpan
    if 'tanggal' in df.columns and not pd.api.types.is_datetime64_any_dtype(df['tanggal']):
        df['tanggal'] = pd.to_datetime(df['tanggal'], errors='coerce')
    df.to_csv('keuangan.csv', index=False)
    st.cache_data.clear()

# Fungsi untuk menampilkan kartu ringkasan
def display_summary_cards(df):
    # Pastikan df tidak kosong dan tanggal dalam format datetime
    if df.empty:
        # Tampilkan kartu ringkasan kosong
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown(
                """
                <div style='background-color:#E0F7FA;padding:20px;border-radius:10px;box-shadow:0 4px 6px rgba(0,0,0,0.1);'>
                    <h3 style='margin:0;color:#0277BD;'>📈 Total Pemasukan</h3>
                    <h2 style='margin:10px 0;color:#00838F;'>Rp 0</h2>
                    <p style='margin:0;color:#0277BD;'>Belum ada data</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        with col2:
            st.markdown(
                """
                <div style='background-color:#FFEBEE;padding:20px;border-radius:10px;box-shadow:0 4px 6px rgba(0,0,0,0.1);'>
                    <h3 style='margin:0;color:#C62828;'>📉 Total Pengeluaran</h3>
                    <h2 style='margin:10px 0;color:#B71C1C;'>Rp 0</h2>
                    <p style='margin:0;color:#C62828;'>Belum ada data</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
        
        with col3:
            st.markdown(
                """
                <div style='background-color:#E8F5E9;padding:20px;border-radius:10px;box-shadow:0 4px 6px rgba(0,0,0,0.1);'>
                    <h3 style='margin:0;color:#2E7D32;'>💰 Saldo</h3>
                    <h2 style='margin:10px 0;color:#1B5E20;'>Rp 0</h2>
                    <p style='margin:0;color:#2E7D32;'>Belum ada data</p>
                </div>
                """, 
                unsafe_allow_html=True
            )
        return

    # Pastikan tanggal dalam format datetime
    if not pd.api.types.is_datetime64_any_dtype(df['tanggal']):
        df['tanggal'] = pd.to_datetime(df['tanggal'], errors='coerce')
    
    bulan_ini = datetime.now().month
    tahun_ini = datetime.now().year
    
    # Filter data untuk bulan ini
    df_bulan_ini = df[(df['tanggal'].dt.month == bulan_ini) & (df['tanggal'].dt.year == tahun_ini)]
    
    # Hitung total pemasukan dan pengeluaran
    pemasukan = df_bulan_ini[df_bulan_ini['jenis'] == 'Pemasukan']['jumlah'].sum()
    pengeluaran = df_bulan_ini[df_bulan_ini['jenis'] == 'Pengeluaran']['jumlah'].sum()
    saldo = pemasukan - pengeluaran
    
    # Tampilkan kartu ringkasan
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(
            f"""
            <div style='background-color:#E0F7FA;padding:20px;border-radius:10px;box-shadow:0 4px 6px rgba(0,0,0,0.1);'>
                <h3 style='margin:0;color:#0277BD;'>📈 Total Pemasukan</h3>
                <h2 style='margin:10px 0;color:#00838F;'>Rp {pemasukan:,.0f}</h2>
                <p style='margin:0;color:#0277BD;'>Bulan {bulan_ini}, {tahun_ini}</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(
            f"""
            <div style='background-color:#FFEBEE;padding:20px;border-radius:10px;box-shadow:0 4px 6px rgba(0,0,0,0.1);'>
                <h3 style='margin:0;color:#C62828;'>📉 Total Pengeluaran</h3>
                <h2 style='margin:10px 0;color:#B71C1C;'>Rp {pengeluaran:,.0f}</h2>
                <p style='margin:0;color:#C62828;'>Bulan {bulan_ini}, {tahun_ini}</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
    
    with col3:
        bg_color = "#E8F5E9" if saldo >= 0 else "#FFEBEE"
        text_color = "#2E7D32" if saldo >= 0 else "#C62828"
        text_color2 = "#1B5E20" if saldo >= 0 else "#B71C1C"
        icon = "💰" if saldo >= 0 else "⚠️"
        
        st.markdown(
            f"""
            <div style='background-color:{bg_color};padding:20px;border-radius:10px;box-shadow:0 4px 6px rgba(0,0,0,0.1);'>
                <h3 style='margin:0;color:{text_color};'>{icon} Saldo</h3>
                <h2 style='margin:10px 0;color:{text_color2};'>Rp {saldo:,.0f}</h2>
                <p style='margin:0;color:{text_color};'>Bulan {bulan_ini}, {tahun_ini}</p>
            </div>
            """, 
            unsafe_allow_html=True
        )

# Fungsi untuk menampilkan grafik distribusi pengeluaran
def display_charts(df):
    # Pastikan dataframe tidak kosong
    if df.empty:
        st.info("🔍 Belum ada data keuangan")
        return
        
    # Pastikan tanggal dalam format datetime
    if not pd.api.types.is_datetime64_any_dtype(df['tanggal']):
        df['tanggal'] = pd.to_datetime(df['tanggal'], errors='coerce')
    
    bulan_ini = datetime.now().month
    tahun_ini = datetime.now().year
    
    # Filter data untuk bulan ini
    df_bulan_ini = df[(df['tanggal'].dt.month == bulan_ini) & (df['tanggal'].dt.year == tahun_ini)]
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Grafik pengeluaran per kategori (dengan maksimal 5 kategori)
        if not df_bulan_ini[df_bulan_ini['jenis'] == 'Pengeluaran'].empty:
            kategori_pengeluaran = df_bulan_ini[df_bulan_ini['jenis'] == 'Pengeluaran'].groupby('kategori')['jumlah'].sum().reset_index()
            
            # Jika ada lebih dari 5 kategori, ambil 5 terbesar dan kelompokkan sisanya sebagai "Lainnya"
            if len(kategori_pengeluaran) > 5:
                # Urutkan berdasarkan jumlah
                kategori_pengeluaran = kategori_pengeluaran.sort_values('jumlah', ascending=False)
                
                # Ambil 5 kategori teratas
                top_kategori = kategori_pengeluaran.head(5)
                
                # Hitung total untuk "Lainnya"
                others_sum = kategori_pengeluaran.iloc[5:]['jumlah'].sum()
                
                # Buat baris untuk "Lainnya"
                others_row = pd.DataFrame({'kategori': ['Lainnya'], 'jumlah': [others_sum]})
                
                # Gabungkan kembali
                kategori_pengeluaran = pd.concat([top_kategori, others_row])
            
            # Gunakan colorscale yang menarik
            fig = px.pie(
                kategori_pengeluaran, 
                values='jumlah', 
                names='kategori', 
                title='📊 Distribusi Pengeluaran per Kategori',
                color_discrete_sequence=px.colors.sequential.Viridis,
                hole=0.3
            )
            
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(
                margin=dict(t=40, b=0, l=0, r=0),
                # Ubah orientasi legend menjadi vertikal
                legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="right", x=1.1)
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("🔍 Belum ada data pengeluaran bulan ini")
    
    with col2:
        # Grafik tren pemasukan vs pengeluaran harian
        if not df_bulan_ini.empty:
            daily_summary = df_bulan_ini.groupby(['tanggal', 'jenis'])['jumlah'].sum().reset_index()
            fig = px.line(
                daily_summary, 
                x='tanggal', 
                y='jumlah', 
                color='jenis',
                title='📈 Tren Pemasukan vs Pengeluaran',
                color_discrete_map={'Pemasukan': '#4CAF50', 'Pengeluaran': '#F44336'}
            )
            fig.update_layout(
                margin=dict(t=40, b=0, l=0, r=0),
                xaxis_title="Tanggal",
                yaxis_title="Jumlah (Rp)"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("🔍 Belum ada data keuangan bulan ini")

# Fungsi untuk menambahkan transaksi baru
def add_transaction(df):
    st.markdown("### ➕ Tambah Transaksi Baru")
    
    with st.form("transaksi_baru", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            tanggal = st.date_input("📅 Tanggal", datetime.now())
            jenis = st.selectbox("📝 Jenis", ["Pemasukan", "Pengeluaran"])
            
        with col2:
            kategori_options = {
                "Pemasukan": ["Gaji", "Bonus", "Investasi", "Proyek", "Penjualan", "Lainnya"],
                "Pengeluaran": ["Makanan", "Transportasi", "Hiburan", "Belanja", "Kesehatan", 
                                "Tagihan", "Pendidikan", "Rumah", "Asuransi", "Lainnya"]
            }
            
            kategori = st.selectbox("🏷️ Kategori", kategori_options[jenis])
            jumlah = st.number_input("💲 Jumlah (Rp)", min_value=1000, step=1000)
        
        deskripsi = st.text_area("📝 Deskripsi (Opsional)")
        submit = st.form_submit_button("💾 Simpan Transaksi", type="primary")
        
        if submit:
            # Tambahkan transaksi baru
            new_row = pd.DataFrame({
                'tanggal': [tanggal],
                'jenis': [jenis],
                'kategori': [kategori],
                'jumlah': [jumlah],
                'deskripsi': [deskripsi]
            })
            
            # Pastikan tanggal dalam format datetime
            new_row['tanggal'] = pd.to_datetime(new_row['tanggal'])
            
            # Gabungkan data baru dengan yang ada
            if df.empty:
                df_new = new_row
            else:
                # Pastikan tanggal di df juga dalam format datetime
                if not pd.api.types.is_datetime64_any_dtype(df['tanggal']):
                    df['tanggal'] = pd.to_datetime(df['tanggal'], errors='coerce')
                df_new = pd.concat([df, new_row], ignore_index=True)
            
            save_data(df_new)
            st.success("✅ Transaksi berhasil ditambahkan!")
            return df_new
    
    return df

# Fungsi untuk menampilkan tabel dengan tombol hapus per baris (alternatif)
def display_table(df):
    st.markdown("### 📋 Daftar Transaksi")
    
    # Cek apakah dataframe kosong
    if df.empty:
        st.info("❌ Belum ada transaksi yang ditambahkan.")
        return df
    
    # Pastikan tanggal dalam format datetime
    # This is where the fix is needed - force conversion to datetime
    df['tanggal'] = pd.to_datetime(df['tanggal'], errors='coerce')
    
    # Filter dan pengurutan
    col1, col2, col3 = st.columns(3)
    
    with col1:
        bulan = st.selectbox(
            "📅 Pilih Bulan", 
            list(range(1, 13)),
            index=datetime.now().month - 1
        )
    
    with col2:
        tahun = st.selectbox(
            "🗓️ Pilih Tahun",
            list(range(2023, 2026)),
            index=2
        )
    
    with col3:
        jenis_filter = st.selectbox(
            "🔍 Jenis Transaksi",
            ["Semua", "Pemasukan", "Pengeluaran"]
        )
    
    # Make sure df['tanggal'] is datetime before applying dt accessor
    if not pd.api.types.is_datetime64_any_dtype(df['tanggal']):
        df['tanggal'] = pd.to_datetime(df['tanggal'], errors='coerce')
        
    # Filter data berdasarkan bulan dan tahun
    df_filtered = df[(df['tanggal'].dt.month == bulan) & (df['tanggal'].dt.year == tahun)]
    
    # Jika tidak ada data
    if df_filtered.empty:
        st.info("❌ Tidak ada transaksi untuk periode yang dipilih.")
        return df
    
    # Reset index untuk df_filtered agar digunakan sebagai referensi
    df_filtered = df_filtered.reset_index(drop=True)
    
    # Konversi format tanggal untuk tampilan
    df_display = df_filtered.copy()
    df_display['tanggal'] = df_display['tanggal'].dt.strftime('%d-%m-%Y')
    df_display['jumlah'] = df_display['jumlah'].apply(lambda x: f"Rp {x:,.0f}")
    
    # Pagination (10 transaksi per halaman)
    total_pages = (len(df_display) - 1) // 10 + 1
    
    # Menampilkan tabel
    start_idx = 0
    end_idx = min(start_idx + 10, len(df_display))
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1
    
    # Menggunakan nilai dari session state untuk pagination
    page = st.session_state.current_page
    start_idx = (page - 1) * 10
    end_idx = min(start_idx + 10, len(df_display))
    
    # Tampilkan informasi pagination
    st.markdown(f"**Menampilkan {start_idx+1}-{end_idx} dari {len(df_display)} transaksi**")
    
    # Tampilkan tabel
    edited_data = st.data_editor(
        df_display.iloc[start_idx:end_idx],
        column_config={
            "tanggal": "Tanggal",
            "jenis": "Jenis",
            "kategori": "Kategori",
            "jumlah": "Jumlah",
            "deskripsi": "Deskripsi"
        },
        use_container_width=True,
        num_rows="fixed",
        key="data_editor"
    )
    
    # Tombol pagination di bagian bawah
    if total_pages > 1:
        st.markdown("<div class='pagination-container'>", unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        
        with col1:
            if st.button("⏮️ Pertama", disabled=(page <= 1)):
                st.session_state.current_page = 1
                st.rerun()
        
        with col2:
            if st.button("⬅️ Sebelumnya", disabled=(page <= 1)):
                st.session_state.current_page -= 1
                st.rerun()
        
        with col3:
            if st.button("➡️ Berikutnya", disabled=(page >= total_pages)):
                st.session_state.current_page += 1
                st.rerun()
                
        with col4:
            if st.button("⏭️ Terakhir", disabled=(page >= total_pages)):
                st.session_state.current_page = total_pages
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Tampilkan juga nomor halaman saat ini
        st.markdown(f"<div style='text-align: center;'>Halaman {page} dari {total_pages}</div>", unsafe_allow_html=True)
    
    # Centered Hapus Transaksi section
    st.markdown("<h3 style='text-align: center;'>🗑️ Hapus Transaksi</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Tampilkan dropdown untuk memilih transaksi
        # Gunakan index+1 untuk membuat penomoran mulai dari 1 bukan 0
        options = [f"{i+start_idx+1}. {row['kategori']} - {row['jumlah']}" 
                for i, row in enumerate(df_display.iloc[start_idx:end_idx].to_dict('records'))]
        
        if options:
            selected_item = st.selectbox("Pilih transaksi yang akan dihapus:", options)
            # Ekstrak dan konversi indeks kembali ke 0-based untuk pengolahan internal
            selected_idx = int(selected_item.split('.')[0]) - 1
        else:
            st.info("Tidak ada transaksi untuk dihapus.")
            selected_idx = None
        
        if selected_idx is not None:
            if st.button("❌ Hapus Transaksi", type="primary", use_container_width=True):
                # Tampilkan dialog konfirmasi
                st.session_state.show_delete_confirmation = True
                st.session_state.idx_to_delete = selected_idx
    
    # Konfirmasi hapus
    if st.session_state.get("show_delete_confirmation", False):
        with st.expander("⚠️ Konfirmasi Hapus", expanded=True):
            row_to_delete = df_display.iloc[st.session_state.idx_to_delete - start_idx]
            
            st.warning(f"Yakin ingin menghapus transaksi `{row_to_delete['kategori']}` sebesar `{row_to_delete['jumlah']}`?")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("❌ Batal", key="cancel_delete", use_container_width=True):
                    st.session_state.show_delete_confirmation = False
                    st.rerun()
            
            with col2:
                if st.button("✅ Konfirmasi", key="confirm_delete", use_container_width=True):
                    try:
                        # Dapatkan indeks asli
                        original_idx = df_filtered.index[st.session_state.idx_to_delete - start_idx]
                        # Dapatkan original indeks di data utama
                        main_df_idx = df[df['tanggal'] == df_filtered.loc[original_idx, 'tanggal']]
                        main_df_idx = main_df_idx[main_df_idx['jumlah'] == df_filtered.loc[original_idx, 'jumlah']]
                        main_df_idx = main_df_idx[main_df_idx['kategori'] == df_filtered.loc[original_idx, 'kategori']]
                        
                        if not main_df_idx.empty:
                            df = df.drop(main_df_idx.index[0]).reset_index(drop=True)
                            save_data(df)
                            st.success(f"✅ Transaksi berhasil dihapus!")
                            st.session_state.show_delete_confirmation = False
                            st.rerun()
                        else:
                            st.error("Terjadi kesalahan saat menghapus transaksi.")
                    except Exception as e:
                        st.error(f"Kesalahan: {e}")
    
    # Simpan perubahan
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("💾 Simpan Perubahan", type="primary", use_container_width=True):
            updated = False
            
            try:
                # Konversi DataFrame yang diedit kembali ke format asli
                for i, (_, row) in enumerate(edited_data.iterrows()):
                    idx = start_idx + i
                    if idx >= len(df_filtered):
                        continue
                        
                    original_idx = df_filtered.index[i]
                    
                    # Konversi format jumlah uang kembali ke angka
                    if isinstance(row['jumlah'], str):
                        row_jumlah = int(row['jumlah'].replace('Rp ', '').replace(',', '').replace('.', ''))
                    else:
                        row_jumlah = row['jumlah']
                    
                    # Konversi format tanggal kembali ke datetime
                    if isinstance(row['tanggal'], str):
                        try:
                            row_tanggal = datetime.strptime(row['tanggal'], '%d-%m-%Y')
                        except ValueError:
                            row_tanggal = df_filtered.loc[original_idx, 'tanggal']
                    else:
                        row_tanggal = row['tanggal']
                    
                    # Verifikasi apakah data berubah
                    if (row_tanggal != df_filtered.loc[original_idx, 'tanggal'] or
                        row['jenis'] != df_filtered.loc[original_idx, 'jenis'] or
                        row['kategori'] != df_filtered.loc[original_idx, 'kategori'] or
                        row_jumlah != df_filtered.loc[original_idx, 'jumlah'] or
                        row['deskripsi'] != df_filtered.loc[original_idx, 'deskripsi']):
                        
                        # Temukan dan perbarui di dataframe utama
                        main_df_idx = df[df['tanggal'] == df_filtered.loc[original_idx, 'tanggal']]
                        main_df_idx = main_df_idx[main_df_idx['jumlah'] == df_filtered.loc[original_idx, 'jumlah']]
                        main_df_idx = main_df_idx[main_df_idx['kategori'] == df_filtered.loc[original_idx, 'kategori']]
                        
                        if not main_df_idx.empty:
                            df.loc[main_df_idx.index[0], 'tanggal'] = row_tanggal
                            df.loc[main_df_idx.index[0], 'jenis'] = row['jenis']
                            df.loc[main_df_idx.index[0], 'kategori'] = row['kategori']
                            df.loc[main_df_idx.index[0], 'jumlah'] = row_jumlah
                            df.loc[main_df_idx.index[0], 'deskripsi'] = row['deskripsi']
                            updated = True
                
                if updated:
                    save_data(df)
                    st.success("✅ Data transaksi berhasil diperbarui!")
                else:
                    st.info("Tidak ada perubahan yang dilakukan.")
            except Exception as e:
                st.error(f"Kesalahan saat menyimpan perubahan: {e}")
    
    return df

# Fungsi untuk ekspor data
def export_data(df):
    if df.empty:
        st.info("❌ Belum ada transaksi yang bisa diekspor.")
        return
        
    # Pastikan tanggal dalam format datetime
    if not pd.api.types.is_datetime64_any_dtype(df['tanggal']):
        df['tanggal'] = pd.to_datetime(df['tanggal'], errors='coerce')
        
    with st.expander("📤 Ekspor Data"):
        col1, col2 = st.columns(2)
        
        with col1:
            bulan_export = st.selectbox(
                "📅 Bulan", 
                list(range(1, 13)),
                index=datetime.now().month - 1,
                key="export_month"
            )
        
        with col2:
            tahun_export = st.selectbox(
                "🗓️ Tahun",
                list(range(2023, 2026)),
                index=2,
                key="export_year"
            )
        
        # Filter data untuk ekspor
        df_export = df[(df['tanggal'].dt.month == bulan_export) & (df['tanggal'].dt.year == tahun_export)]
        
        if df_export.empty:
            st.warning("⚠️ Tidak ada data untuk periode yang dipilih.")
        else:
            # Konversi ke format CSV
            csv = df_export.to_csv(index=False)
            
            filename = f"keuangan_{bulan_export}_{tahun_export}.csv"
            
            st.download_button(
                label="📥 Unduh CSV",
                data=csv,
                file_name=filename,
                mime="text/csv",
                type="primary",
                use_container_width=True
            )

# Aplikasi utama
def main():
    # Inisialisasi state
    if 'show_delete_confirmation' not in st.session_state:
        st.session_state.show_delete_confirmation = False
    if 'idx_to_delete' not in st.session_state:
        st.session_state.idx_to_delete = None
    if 'current_page' not in st.session_state:
        st.session_state.current_page = 1
    
    # Tampilkan judul
    st.markdown(
        """
        <h1 style='text-align: center; color: #1976D2; margin-bottom: 30px;'>
            💰 PELACAK KEUANGAN
        </h1>
        """, 
        unsafe_allow_html=True
    )
    
    # Buat tabs untuk navigasi 
    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "➕ Tambah Transaksi", "📋 Kelola Transaksi"])
    
    # Load data
    df = load_data()
    
    # Tab 1: Dashboard
    with tab1:
        st.markdown("## 📊 Dashboard Keuangan")
        display_summary_cards(df)
        st.markdown("---")
        display_charts(df)
    
    # Tab 2: Tambah Transaksi
    with tab2:
        df = add_transaction(df)
    
    # Tab 3: Kelola Transaksi
    with tab3:
        df = display_table(df)
        st.markdown("---")
        export_data(df)

# Jalankan aplikasi
if __name__ == "__main__":
    main()


