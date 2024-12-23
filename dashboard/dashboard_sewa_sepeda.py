import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import gzip

@st.cache_data
def load_data():
    # Path absolut dinamis untuk file CSV terkompresi
    current_dir = os.path.abspath(os.path.dirname(__file__))
    hour_file_path = os.path.join(current_dir, 'cleaned_hour.csv.gz')

    # Debugging path hanya saat file tidak ditemukan
    if not os.path.isfile(hour_file_path):
        st.error(f"File tidak ditemukan: {hour_file_path}")
        st.write("Isi folder root:", os.listdir(current_dir))
        raise FileNotFoundError(f"File tidak ditemukan: {hour_file_path}")

    # Membaca data
    with gzip.open(hour_file_path, mode='rt') as f:
        hour_df = pd.read_csv(f)
        hour_df['dteday'] = pd.to_datetime(hour_df['dteday'])
        hour_df['day_type'] = hour_df['workingday'].apply(lambda x: 'Hari Kerja' if x == 1 else 'Akhir Pekan')

        # Menambahkan label cuaca dan musim
        weather_labels = {1: 'Cerah', 2: 'Mendung/Hujan Ringan', 3: 'Hujan Lebat', 4: 'Ekstrem'}
        hour_df['weathersit'] = hour_df['weathersit'].map(weather_labels)
        season_labels = {1: 'Musim Semi', 2: 'Musim Panas', 3: 'Musim Gugur', 4: 'Musim Dingin'}
        hour_df['season'] = hour_df['season'].map(season_labels)

    return hour_df

# Load data
try:
    data = load_data()
except FileNotFoundError:
    st.stop()

# Sidebar untuk Navigasi dan Filter
st.sidebar.title("Navigasi Dashboard")

if not data.empty:
    # Filter Berdasarkan Tanggal
    min_date = data['dteday'].min().date()
    max_date = data['dteday'].max().date()
    start_date, end_date = st.sidebar.date_input(
        label="Pilih Rentang Tanggal",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date]
    )

    # Filter Berdasarkan Musim
    selected_season = st.sidebar.multiselect(
        "Pilih Musim",
        options=data['season'].unique(),
        default=data['season'].unique()
    )

    # Menerapkan Filter
    filtered_data = data[
        (data['dteday'] >= pd.Timestamp(start_date)) &
        (data['dteday'] <= pd.Timestamp(end_date)) &
        (data['season'].isin(selected_season))
    ]

    page = st.sidebar.radio("Pilih Halaman:", ["Beranda", "Analisis Cuaca", "Analisis Hari Kerja", "Analisis Musim", "Kesimpulan"])

    # Halaman Beranda
    if page == "Beranda":
        st.title("Dashboard Penyewaan Sepeda 🚴")
        st.write("**Dashboard ini menampilkan hasil analisis faktor cuaca, musim, dan tipe hari pada penyewaan sepeda.**")
        st.subheader("Contoh Data yang Difilter:")
        st.dataframe(filtered_data.head(10))

    # Halaman Analisis Cuaca
    elif page == "Analisis Cuaca":
        st.title("Pengaruh Cuaca terhadap Penyewaan Sepeda")
        avg_weather = filtered_data.groupby('weathersit')['cnt'].mean().reset_index()
        avg_weather.columns = ['Kondisi Cuaca', 'Rata-rata Penyewaan']

        st.subheader("Rata-rata Penyewaan Berdasarkan Kondisi Cuaca")
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.barplot(data=avg_weather, x='Kondisi Cuaca', y='Rata-rata Penyewaan', palette='Blues_d', ax=ax)
        ax.set_title("Rata-rata Penyewaan Sepeda Berdasarkan Cuaca")
        ax.set_xlabel("Kondisi Cuaca")
        ax.set_ylabel("Rata-rata Penyewaan Sepeda")
        st.pyplot(fig)

    # Halaman Analisis Hari Kerja
    elif page == "Analisis Hari Kerja":
        st.title("Perbandingan Penyewaan pada Hari Kerja dan Akhir Pekan")
        avg_day_type = filtered_data.groupby('day_type')['cnt'].mean().reset_index()
        avg_day_type.columns = ['Tipe Hari', 'Rata-rata Penyewaan']

        st.subheader("Rata-rata Penyewaan Berdasarkan Tipe Hari")
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.barplot(data=avg_day_type, x='Tipe Hari', y='Rata-rata Penyewaan', palette='muted', ax=ax)
        ax.set_title("Rata-rata Penyewaan Sepeda Berdasarkan Hari Kerja dan Akhir Pekan")
        ax.set_xlabel("Tipe Hari")
        ax.set_ylabel("Rata-rata Penyewaan Sepeda")
        st.pyplot(fig)

    # Halaman Analisis Musim
    elif page == "Analisis Musim":
        st.title("Pengaruh Musim terhadap Penyewaan Sepeda")

        selected_season_filter = st.multiselect(
            "Pilih Musim untuk Analisis",
            options=filtered_data['season'].unique(),
            default=filtered_data['season'].unique()
        )
        season_filtered_data = filtered_data[filtered_data['season'].isin(selected_season_filter)]

        avg_season = season_filtered_data.groupby('season')['cnt'].mean().reset_index()
        avg_season.columns = ['Musim', 'Rata-rata Penyewaan']

        st.subheader("Rata-rata Penyewaan Berdasarkan Musim")
        fig, ax = plt.subplots(figsize=(8, 6))
        sns.barplot(data=avg_season, x='Musim', y='Rata-rata Penyewaan', palette='coolwarm', ax=ax)
        ax.set_title("Rata-rata Penyewaan Sepeda Berdasarkan Musim")
        ax.set_xlabel("Musim")
        ax.set_ylabel("Rata-rata Penyewaan Sepeda")
        st.pyplot(fig)

    # Halaman Kesimpulan
    elif page == "Kesimpulan":
        st.title("Kesimpulan Analisis Penyewaan Sepeda")

        if not filtered_data.empty:
            cuaca_tertinggi = filtered_data.groupby('weathersit')['cnt'].mean().idxmax()
            penyewaan_tertinggi_cuaca = filtered_data.groupby('weathersit')['cnt'].mean().max()
            cuaca_terendah = filtered_data.groupby('weathersit')['cnt'].mean().idxmin()
            penyewaan_terendah_cuaca = filtered_data.groupby('weathersit')['cnt'].mean().min()

            hari_kerja_rata = filtered_data[filtered_data['day_type'] == 'Hari Kerja']['cnt'].mean()
            akhir_pekan_rata = filtered_data[filtered_data['day_type'] == 'Akhir Pekan']['cnt'].mean()

            musim_tertinggi = filtered_data.groupby('season')['cnt'].mean().idxmax()
            penyewaan_tertinggi_musim = filtered_data.groupby('season')['cnt'].mean().max()

            st.subheader("Kesimpulan Analisis Cuaca:")
            st.write(f"- Penyewaan sepeda tertinggi terjadi pada **{cuaca_tertinggi}** dengan rata-rata **{penyewaan_tertinggi_cuaca:.2f} penyewaan**.")
            st.write(f"- Penyewaan sepeda terendah terjadi pada **{cuaca_terendah}** dengan rata-rata **{penyewaan_terendah_cuaca:.2f} penyewaan**.")

            st.subheader("Kesimpulan Analisis Hari Kerja:")
            st.write(f"- Penyewaan rata-rata pada **hari kerja** adalah **{hari_kerja_rata:.2f} penyewaan**.")
            st.write(f"- Penyewaan rata-rata pada **akhir pekan** adalah **{akhir_pekan_rata:.2f} penyewaan**.")

            st.subheader("Kesimpulan Analisis Musim:")
            st.write(f"- Penyewaan tertinggi terjadi pada **{musim_tertinggi}** dengan rata-rata **{penyewaan_tertinggi_musim:.2f} penyewaan**.")
        else:
            st.write("Tidak ada data yang tersedia untuk kesimpulan.")
