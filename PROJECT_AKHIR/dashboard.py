import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os 

# --- Halaman dan Judul ---
st.set_page_config(
    page_title="Dashboard Analisis Konten Netflix",
    layout="wide"
)

# Dapatkan path absolut ke direktori tempat skrip ini berada
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Gabungkan path direktori dengan nama file CSV
DATA_PATH = os.path.join(BASE_DIR, "netflix_cleaned.csv")

@st.cache_data
def load_data():
    data = pd.read_csv(DATA_PATH)
    return data

# --- Memuat Data ---
data = load_data()

# --- SIDEBAR UNTUK FILTER ---
st.sidebar.header("🔍 Filter Data")

# Filter berdasarkan Tipe Konten (Movie/TV Show)
type_filter = st.sidebar.multiselect(
    'Pilih Tipe Konten:',
    options=data['type'].unique(),
    default=data['type'].unique()
)

# Filter berdasarkan Negara (ambil top 20 untuk efisiensi)
top_countries = data['country'].str.split(', ').str[0].value_counts().nlargest(20).index
country_filter = st.sidebar.multiselect(
    'Pilih Negara:',
    options=top_countries,
    default=['United States', 'India', 'United Kingdom'] # Default pilihan
)

# Filter berdasarkan Tahun Rilis dengan slider
min_year, max_year = int(data['release_year'].min()), int(data['release_year'].max())
year_filter = st.sidebar.slider(
    'Pilih Rentang Tahun Rilis:',
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

# --- Menerapkan Filter ke DataFrame ---
# Kondisi untuk tipe dan negara (jika tidak ada yang dipilih, tampilkan semua)
type_condition = data['type'].isin(type_filter) if type_filter else pd.Series([True] * len(data))
country_condition = data['country'].str.contains('|'.join(country_filter), na=False) if country_filter else pd.Series([True] * len(data))

# Kondisi untuk tahun rilis
year_condition = (data['release_year'] >= year_filter[0]) & (data['release_year'] <= year_filter[1])

# Gabungkan semua filter
filtered_data = data[type_condition & country_condition & year_condition]


# --- HALAMAN UTAMA DASHBOARD ---
st.title("🎬 Dashboard Analisis Konten Netflix")
st.markdown("Dashboard ini menampilkan analisis dari katalog film dan acara TV yang tersedia di Netflix.")

# --- Metrik Utama (KPIs) ---
total_titles = filtered_data.shape[0]
total_movies = filtered_data[filtered_data['type'] == 'Movie'].shape[0]
total_tv_shows = filtered_data[filtered_data['type'] == 'TV Show'].shape[0]

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Judul", value=f"{total_titles:,}")
with col2:
    st.metric("Jumlah Film", value=f"{total_movies:,}")
with col3:
    st.metric("Jumlah Acara TV", value=f"{total_tv_shows:,}")

st.markdown("---")


# --- VISUALISASI DATA ---
col1, col2 = st.columns(2)

with col1:
    # Grafik 1: Proporsi Film vs Acara TV
    st.subheader("Proporsi Tipe Konten")
    type_counts = filtered_data['type'].value_counts()
    if not type_counts.empty:
        fig1, ax1 = plt.subplots(figsize=(7, 6))
        ax1.pie(type_counts, labels=type_counts.index, autopct='%1.1f%%', startangle=90, colors=['#B20710', '#221F1F'])
        ax1.axis('equal')
        st.pyplot(fig1)
    else:
        st.warning("Tidak ada data untuk filter yang dipilih.")

with col2:
    # Grafik 2: Distribusi Rating Konten
    st.subheader("Distribusi Rating Konten (Top 10)")
    rating_counts = filtered_data['rating'].value_counts().head(10)
    if not rating_counts.empty:
        fig2, ax2 = plt.subplots(figsize=(8, 6))
        sns.barplot(x=rating_counts.index, y=rating_counts.values, palette='Greys_r', ax=ax2)
        ax2.set_ylabel('Jumlah Konten')
        ax2.set_xlabel('Rating')
        plt.xticks(rotation=45)
        st.pyplot(fig2)
    else:
        st.warning("Tidak ada data untuk filter yang dipilih.")

st.markdown("---")

# Grafik 3: Tren Penambahan Konten per Tahun
st.subheader("Tren Penambahan Konten di Netflix")
yearly_content_counts = filtered_data['year_added'].value_counts().sort_index()
if not yearly_content_counts.empty:
    fig3, ax3 = plt.subplots(figsize=(14, 6))
    sns.lineplot(x=yearly_content_counts.index, y=yearly_content_counts.values, marker='o', color='#E50914', ax=ax3)
    ax3.set_xlabel("Tahun Penambahan")
    ax3.set_ylabel("Jumlah Konten")
    st.pyplot(fig3)
else:
    st.warning("Tidak ada data untuk filter yang dipilih.")

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    # Grafik 4: Top 10 Negara Produsen
    st.subheader("Top 10 Negara Produsen Konten")
    # Mengambil negara pertama untuk analisis
    country_data = filtered_data['country'].str.split(', ').str[0].value_counts().head(10)
    if not country_data.empty:
        fig4, ax4 = plt.subplots(figsize=(10, 8))
        sns.barplot(x=country_data.values, y=country_data.index, palette='Reds_r', ax=ax4)
        ax4.set_xlabel('Jumlah Konten')
        ax4.set_ylabel('Negara')
        st.pyplot(fig4)
    else:
        st.warning("Tidak ada data untuk filter yang dipilih.")

with col2:
    # Grafik 5: Top 10 Genre
    st.subheader("Top 10 Genre Paling Umum")
    genre_data = filtered_data['listed_in'].str.split(', ').explode().value_counts().head(10)
    if not genre_data.empty:
        fig5, ax5 = plt.subplots(figsize=(10, 8))
        sns.barplot(x=genre_data.values, y=genre_data.index, palette='dark:salmon_r', ax=ax5)
        ax5.set_xlabel('Jumlah Konten')
        ax5.set_ylabel('Genre')
        st.pyplot(fig5)
    else:
        st.warning("Tidak ada data untuk filter yang dipilih.")

# --- Menampilkan Data Mentah ---
if st.checkbox("Tampilkan data mentah yang telah difilter"):
    st.dataframe(filtered_data)