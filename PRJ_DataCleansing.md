Cleansing & Containerization (PostgreSQL)
1. Deskripsi Proyek
Proyek ini bertujuan untuk membersihkan data mentah dari file CSV (scrap.csv) yang memiliki duplikat dan tipe data tidak tepat. Data akan diproses menggunakan Python, disimpan ke database PostgreSQL, serta diekspor menjadi file JSON (untuk data bersih) dan CSV (untuk data duplikat). Selanjutnya, aplikasi akan dibungkus ke dalam Docker agar mudah dijalankan dan dijadwalkan oleh tim engineering.

Tujuan Utama:

Membaca file CSV dari direktori /source.

Menghapus duplikat berdasarkan kolom ids (baris pertama = data bersih, duplikat = data reject).

Menyimpan data bersih ke tabel data dan data duplikat ke tabel data_reject di PostgreSQL.

Mengekspor data bersih ke JSON dengan format khusus, dan data duplikat ke CSV dengan format sama seperti file sumber.

Menyediakan Dockerfile dan docker-compose.yaml untuk menjalankan aplikasi di lingkungan container.

Aturan Penting:

Nama file output harus mengandung timestamp dengan format YYYYMMDDHHMMSS.

Kolom dates harus berformat YYYY-MM-DD, names harus UPPERCASE, genres dan feat_track_ids harus berupa array/list.

Kolom first_release dan last_release harus berupa tahun (YYYY) dan disimpan sebagai string.

Kolom numerik (monthly_listeners, popularity, followers, num_releases, num_tracks) harus integer.

2. Tools yang Digunakan
Komponen	Pilihan	Alasan
Bahasa Pemrograman	Python 3.11	Umum digunakan, library lengkap untuk manipulasi data.
Library	pandas, psycopg2-binary, sqlalchemy (opsional), pytest	pandas untuk manipulasi data, psycopg2 untuk koneksi PostgreSQL, pytest untuk unit test.
Database	PostgreSQL 16	Database relasional yang kuat, mendukung tipe array, mudah dijalankan via Docker.
Containerization	Docker, Docker Compose	Memudahkan deployment dan penjadwalan.
Version Control	Git (opsional)	Untuk manajemen kode.
3. Path dan Struktur Proyek
Struktur direktori proyek yang akan dibuat:

text
project/
│
├── main.py                    # Script utama pembersihan, insert DB, export
├── ddl.sql                    # Perintah CREATE TABLE untuk data dan data_reject
├── README.md                  # Dokumentasi lengkap
├── Dockerfile                 # Instruksi build image Docker
├── docker-compose.yaml        # Konfigurasi untuk menjalankan container (termasuk PostgreSQL)
├── requirements.txt           # Daftar dependensi Python
├── tests/
│   └── test_main.py           # Unit test menggunakan pytest
├── /source/                   # Direktori input (mount volume atau copy file scrap.csv)
└── /target/                   # Direktori output (mount volume)
Penjelasan Path:

/source : Berisi file scrap.csv yang akan diproses. Dalam Docker, direktori ini di-mount dari host agar file dapat diakses.

/target : Tempat menyimpan file hasil JSON dan CSV. Dalam Docker, direktori ini di-mount ke host agar output mudah diakses.

Database PostgreSQL berjalan sebagai service terpisah dalam docker-compose, dengan volume untuk persistensi data (pgdata).

4. Functional Requirements (FR)
FR-01: Aplikasi harus membaca file scrap.csv dari direktori /source.

FR-02: Aplikasi harus mendeteksi duplikat berdasarkan kolom ids. Baris pertama yang muncul dianggap data bersih (clean), baris berikutnya dengan ids yang sama dianggap duplikat (reject).

FR-03: Data bersih dan data duplikat harus dipisahkan ke dalam dua DataFrame atau struktur data yang berbeda.

FR-04: Aplikasi harus menyimpan data bersih ke tabel data di database PostgreSQL, dan data duplikat ke tabel data_reject.

FR-05: Struktur tabel database harus memiliki jumlah kolom yang sama dengan file CSV (13 kolom) dan tipe data yang sesuai:

dates → DATE

ids → VARCHAR

names → VARCHAR

monthly_listeners → INTEGER

popularity → INTEGER

followers → INTEGER

genres → TEXT[] (array of text)

first_release → VARCHAR(4) (tahun sebagai string)

last_release → VARCHAR(4)

num_releases → INTEGER

num_tracks → INTEGER

playlists_found → VARCHAR

feat_track_ids → TEXT[]

FR-06: Aplikasi harus mengekspor data bersih ke file JSON dengan format:

json
{
  "row_count": <integer>,
  "data": [
    {
      "dates": "YYYY-MM-DD",
      "ids": "string",
      "names": "UPPERCASE",
      "monthly_listeners": integer,
      "popularity": integer,
      "followers": integer,
      "genres": ["string", ...],
      "first_release": "YYYY",
      "last_release": "YYYY",
      "num_releases": integer,
      "num_tracks": integer,
      "playlists_found": "string",
      "feat_track_ids": ["string", ...]
    },
    ...
  ]
}
FR-07: Aplikasi harus mengekspor data duplikat ke file CSV dengan format yang sama persis seperti scrap.csv (header dan isi tanpa modifikasi).

FR-08: Nama file output harus mengikuti pola data_{YYYYMMDDHHMMSS}.json dan data_reject_{YYYYMMDDHHMMSS}.csv.

FR-09: Aplikasi harus menyediakan skrip DDL (ddl.sql) untuk membuat tabel data dan data_reject di PostgreSQL.

FR-10: Aplikasi harus memiliki error handling (try-except) untuk menangani kegagalan seperti file tidak ditemukan, format tidak valid, atau koneksi database gagal.

5. Non-Functional Requirements (NFR)
NFR-01 – Performa: Script harus dapat memproses file CSV dengan jumlah baris hingga 100.000 baris dalam waktu kurang dari 30 detik (di lingkungan lokal standar).

NFR-02 – Portabilitas: Aplikasi harus dapat dijalankan di sistem operasi apa pun selama Python dan dependensi terpasang, serta dapat dijalankan dalam container Docker.

NFR-03 – Error Handling: Semua potensi error (file missing, parsing error, DB error) harus ditangani dengan pesan yang jelas dan tidak menyebabkan crash mendadak.

NFR-04 – Testability: Harus ada unit test yang mencakup fungsi deduplikasi, transformasi, dan pembentukan nama file.

NFR-05 – Maintainability: Kode harus terstruktur dengan baik, menggunakan fungsi-fungsi terpisah, dan mudah dibaca.

NFR-06 – Keamanan: Kredensial database harus dikonfigurasi melalui environment variable, tidak di-hardcode dalam kode.

NFR-07 – Dokumentasi: README.md harus lengkap dan jelas, mencakup cara menjalankan, testing, dan catatan penting.

6. Langkah-Langkah Pengerjaan (Step-by-Step)
Test 1: Clean CSV Data with Python Script (PostgreSQL)
Step 1: Setup Lingkungan Pengembangan
Instalasi Python: Pastikan Python 3.10+ terpasang.

Buat virtual environment:

bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
Instal dependensi:

bash
pip install pandas psycopg2-binary pytest
Persiapkan folder:

bash
mkdir source target
Letakkan file scrap.csv di dalam folder source/.

Step 2: Analisis Data
Buka file scrap.csv menggunakan pandas atau editor teks untuk memahami struktur kolom.

Identifikasi 13 kolom:

dates (format DD/MM/YYYY, perlu diubah ke YYYY-MM-DD)
ids (string unik)
names (string, perlu uppercase)
monthly_listeners (string angka, perlu integer)
popularity (string angka, perlu integer)
followers (string angka, perlu integer)
genres (bisa berisi koma di dalam tanda kutip, perlu diubah menjadi list string)
first_release (string tahun, biarkan sebagai string)
last_release (sama)
num_releases (string angka, integer)
num_tracks (string angka, integer)
playlists_found (string)
feat_track_ids (bisa berisi koma di dalam tanda kutip, perlu list string)
Perhatikan contoh format output di /example/data_20240302101010.json untuk memastikan struktur yang benar.

Perhatikan bahwa genres dan feat_track_ids mungkin dikutip jika mengandung koma, sehingga pembacaan dengan pandas harus memperlakukan kutipan dengan benar. Gunakan parameter quotechar='"' saat membaca CSV.

Step 3: Tulis Kode main.py
Baca CSV dengan pandas:

python
import pandas as pd
df = pd.read_csv('/source/scrap.csv', quotechar='"')
Transformasi tipe data:

python
# dates: konversi ke datetime, lalu format YYYY-MM-DD
df['dates'] = pd.to_datetime(df['dates'], format='%d/%m/%Y').dt.strftime('%Y-%m-%d')

# names: uppercase
df['names'] = df['names'].str.upper()

# monthly_listeners, popularity, followers, num_releases, num_tracks: integer
for col in ['monthly_listeners', 'popularity', 'followers', 'num_releases', 'num_tracks']:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

# genres: string dipisah koma menjadi list (setelah strip spasi)
df['genres'] = df['genres'].apply(lambda x: [g.strip() for g in str(x).split(',')])

# feat_track_ids: sama
df['feat_track_ids'] = df['feat_track_ids'].apply(lambda x: [t.strip() for t in str(x).split(',')])

# first_release, last_release: pastikan string tahun (sudah string, tapi bersihkan)
df['first_release'] = df['first_release'].astype(str)
df['last_release'] = df['last_release'].astype(str)
Deduplikasi:

python
duplicate_mask = df.duplicated(subset='ids', keep='first')
df_clean = df[~duplicate_mask].reset_index(drop=True)
df_reject = df[duplicate_mask].reset_index(drop=True)
Koneksi ke PostgreSQL:
Gunakan psycopg2. Parameter koneksi diambil dari environment variable:

python
import psycopg2
import os

conn = psycopg2.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    port=os.getenv('DB_PORT', '5432'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD', 'postgres'),
    dbname=os.getenv('DB_NAME', 'mydb')
)
conn.autocommit = True
cur = conn.cursor()
Buat tabel jika belum ada (gunakan ddl.sql atau langsung):
Baca dan eksekusi ddl.sql:

python
with open('ddl.sql', 'r') as f:
    ddl_script = f.read()
cur.execute(ddl_script)
Insert data:
Karena genres dan feat_track_ids adalah list, kita perlu menyesuaikan format insert. Gunakan psycopg2.extras.execute_values atau lakukan iterasi:

python
from psycopg2.extras import execute_values

# Untuk df_clean
clean_records = [tuple(row) for row in df_clean.to_numpy()]
insert_query = """
    INSERT INTO data (dates, ids, names, monthly_listeners, popularity, followers, genres, first_release, last_release, num_releases, num_tracks, playlists_found, feat_track_ids)
    VALUES %s
"""
execute_values(cur, insert_query, clean_records)
Namun, list perlu dikonversi ke format yang sesuai untuk PostgreSQL array. psycopg2 dapat mengadaptasi list Python jika kita menggunakan psycopg2.extensions.register_adapter. Alternatifnya, ubah list menjadi string dengan format {item1,item2} (PostgreSQL array literal). Kita bisa menggunakan fungsi helper:

python
def list_to_pgarray(lst):
    return '{' + ','.join(lst) + '}'
Lalu sebelum insert, ubah kolom genres dan feat_track_ids menjadi string format array. Namun, lebih baik menggunakan psycopg2.extras.Json atau langsung mengubah menjadi list of strings yang didukung oleh psycopg2 jika menggunakan sqlalchemy. Untuk kesederhanaan, kita akan mengonversi list menjadi string PostgreSQL array literal.

Contoh:

python
df_clean['genres'] = df_clean['genres'].apply(lambda x: '{' + ','.join(x) + '}')
df_clean['feat_track_ids'] = df_clean['feat_track_ids'].apply(lambda x: '{' + ','.join(x) + '}')
Setelah itu, insert seperti biasa.

Ekspor JSON:

python
import json
from datetime import datetime

timestamp = datetime.now().strftime('%Y%m%d%H%M%S')

# Kembalikan genres dan feat_track_ids menjadi list sebelum export JSON
df_clean_export = df_clean.copy()
df_clean_export['genres'] = df_clean_export['genres'].apply(lambda x: x.strip('{}').split(',') if x != '{}' else [])
df_clean_export['feat_track_ids'] = df_clean_export['feat_track_ids'].apply(lambda x: x.strip('{}').split(',') if x != '{}' else [])

json_data = {
    "row_count": len(df_clean_export),
    "data": df_clean_export.to_dict(orient='records')
}
with open(f'/target/data_{timestamp}.json', 'w') as f:
    json.dump(json_data, f, indent=2)
Ekspor CSV:

python
# Untuk CSV reject, gunakan data asli (sebelum transformasi) agar format sama persis dengan scrap.csv
# Maka kita harus menyimpan df asli sebelum transformasi, lalu ambil baris duplikatnya.
Penting: File CSV reject harus sama persis dengan format raw CSV (termasuk format tanggal, nama lowercase, dll). Jadi kita harus menyimpan salinan df awal sebelum transformasi, lalu ambil baris duplikat dari sana. Sebaiknya proses deduplikasi dilakukan pada data mentah terlebih dahulu, lalu lakukan transformasi terpisah untuk clean dan reject.

Revisi alur:

Baca CSV mentah sebagai df_raw.
Deteksi duplikat berdasarkan ids di df_raw → df_clean_raw, df_reject_raw.
Lakukan transformasi pada df_clean_raw untuk menghasilkan data clean siap DB & JSON.
df_reject_raw langsung diekspor ke CSV tanpa perubahan (kecuali mungkin perlu menghapus index).
Ini lebih sesuai persyaratan.

Error handling:

python
try:
    # seluruh proses
except FileNotFoundError:
    print("File scrap.csv tidak ditemukan di /source")
except psycopg2.Error as e:
    print(f"Database error: {e}")
except Exception as e:
    print(f"Terjadi error: {e}")
finally:
    if conn:
        cur.close()
        conn.close()
Step 4: Buat ddl.sql
Sesuaikan dengan PostgreSQL:

sql
CREATE TABLE IF NOT EXISTS data (
    dates DATE,
    ids VARCHAR,
    names VARCHAR,
    monthly_listeners INTEGER,
    popularity INTEGER,
    followers INTEGER,
    genres TEXT[],
    first_release VARCHAR(4),
    last_release VARCHAR(4),
    num_releases INTEGER,
    num_tracks INTEGER,
    playlists_found VARCHAR,
    feat_track_ids TEXT[]
);

CREATE TABLE IF NOT EXISTS data_reject (
    dates DATE,
    ids VARCHAR,
    names VARCHAR,
    monthly_listeners INTEGER,
    popularity INTEGER,
    followers INTEGER,
    genres TEXT[],
    first_release VARCHAR(4),
    last_release VARCHAR(4),
    num_releases INTEGER,
    num_tracks INTEGER,
    playlists_found VARCHAR,
    feat_track_ids TEXT[]
);
Catatan: Tabel data_reject akan menyimpan data duplikat yang sudah ditransformasi atau masih mentah? Requirement: "Insert clean and duplicate record to database table". Tabel harus memiliki kolom yang sesuai dengan CSV, tapi tipe data mungkin harus disesuaikan juga. Karena data reject akan diekspor ke CSV dengan format raw, sebaiknya tabel data_reject juga menyimpan data yang sudah ditransformasi (seperti clean) agar konsisten. Namun, bisa juga menyimpan data mentah asli. Untuk memudahkan, kita akan menyimpan data reject yang sudah ditransformasi juga (karena tipe data sesuai dengan definisi). Tapi saat ekspor CSV, gunakan data mentah dari df_reject_raw. Ini akan lebih rapi.

Step 5: Unit Test dengan pytest
Buat file tests/test_main.py.

Gunakan fixture untuk membuat DataFrame contoh kecil.

Test fungsi deduplikasi: pastikan baris pertama sebagai clean, duplikat sebagai reject.

Test transformasi: pastikan names uppercase, genres list, dates format YYYY-MM-DD.

Test pembentukan nama file: mock datetime.now().

Step 6: Dokumentasi README.md
Sertakan:

Deskripsi singkat proyek.

Cara menjalankan script secara lokal (dengan asumsi PostgreSQL sudah berjalan).

Cara menjalankan unit test.

Penjelasan tentang file output.

Catatan tentang database dan tipe data.

Improvement yang mungkin (misal: logging, konfigurasi env).

Step 7: Screenshot
Jalankan script, lalu query SELECT COUNT(*) FROM data; dan SELECT COUNT(*) FROM data_reject; di psql atau klien PostgreSQL.

Ambil screenshot hasil query dan simpan sebagai bukti.

Test 2: Containerize the Application with Docker (PostgreSQL)
Step 8: Buat Dockerfile
dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependensi
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy semua file proyek
COPY main.py .
COPY ddl.sql .
COPY tests/ ./tests/

# Buat direktori untuk volume
RUN mkdir -p /source /target

# Command default
CMD ["python", "main.py"]
Step 9: Buat docker-compose.yaml
yaml
version: '3.8'
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: mydb
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 10s
      timeout: 5s
      retries: 5

  app:
    build: .
    environment:
      DB_HOST: db
      DB_PORT: 5432
      DB_USER: postgres
      DB_PASSWORD: postgres
      DB_NAME: mydb
    volumes:
      - ./source:/source
      - ./target:/target
    depends_on:
      db:
        condition: service_healthy

volumes:
  pgdata:
Step 10: Build dan Run
Build image:

bash
docker-compose build
Jalankan container:

bash
docker-compose up
Pastikan output JSON dan CSV muncul di folder target/ di host.

Step 11: Debugging
Jika terjadi error, gunakan docker-compose logs untuk melihat log.

Bisa juga masuk ke container dengan docker-compose run app bash untuk menjalankan perintah manual.

Step 12: Update README
Tambahkan instruksi Docker: docker-compose build && docker-compose up.

Jelaskan volume mount dan cara mengakses database.