# Data Engineering Test: CSV Cleansing with PostgreSQL

## Deskripsi
Proyek ini merupakan solusi untuk tugas teknis Data Engineer yang berfokus pada pembersihan data CSV, deduplikasi, penyimpanan ke PostgreSQL, dan ekspor data bersih ke JSON serta data duplikat ke CSV. Aplikasi dibangun menggunakan Python, pandas, psycopg2, dan dijalankan dalam lingkungan Docker.

## Fitur Utama
- Membaca file CSV mentah dari direktori `/source`
- Mendeteksi duplikat berdasarkan kolom `ids` (baris pertama dianggap data bersih, sisanya data reject)
- Transformasi data:
  - Konversi format tanggal menjadi `YYYY-MM-DD`
  - Nama artis diubah menjadi huruf kapital
  - Kolom numerik dikonversi menjadi integer
  - Kolom `genres` dan `feat_track_ids` diubah menjadi list/array
- Menyimpan data bersih ke tabel `data` dan data duplikat ke tabel `data_reject` di PostgreSQL
- Mengekspor data bersih ke file JSON dengan format khusus
- Mengekspor data duplikat ke file CSV dengan format sama seperti input
- Logging profesional menggunakan modul `logging`
- Unit test menggunakan `pytest`

## Teknologi yang Digunakan
| Komponen | Teknologi | Fungsi |
|----------|-----------|--------|
| Bahasa Pemrograman | Python 3.11 | Logika pemrosesan data |
| Library Data | pandas | Manipulasi DataFrame |
| Database Driver | psycopg2 | Koneksi dan insert ke PostgreSQL |
| Database | PostgreSQL 16 | Penyimpanan data clean dan reject |
| Containerization | Docker, Docker Compose | Isolasi lingkungan dan orkestrasi layanan |
| Testing | pytest | Unit test untuk fungsi utama |

## Struktur Direktori
```text
project/
├── main.py # Script utama
├── ddl.sql # DDL untuk tabel data dan data_reject
├── requirements.txt # Dependensi Python
├── Dockerfile # Definisi image Docker
├── docker-compose.yaml # Orkestrasi layanan PostgreSQL dan aplikasi
├── .env.example # Template environment variable
├── .gitignore # File yang diabaikan Git
├── README.md # Dokumentasi
├── tests/
│ └── test_main.py # Unit test
├── source/
│ └── scrap.csv # File input (mount volume)
├── target/ # Folder output (mount volume)
├── example/
│ └── scrap.csv # File contoh untuk testing
└── img/ # Folder screenshot
```

## Cara Menjalankan Proyek

### Prasyarat
- Docker dan Docker Compose (v2.0+)
- Python 3.10+ (untuk pengembangan lokal)
- Git (opsional)

### 1. Clone Repositori (jika ada)
```bash
git clone <url-repositori>
cd <nama-folder>
```

### 2. Siapkan File Input
Letakkan file scrap.csv di dalam folder source/. Pastikan format kolom sesuai dengan contoh pada soal.

### 3. Konfigurasi Environment
Salin .env.example menjadi .env dan sesuaikan nilainya:
```env
DB_HOST=db
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=EDTS_DE
```

### 4. Build dan Jalankan Aplikasi
```bash
docker compose up --build
```
Perintah ini akan:
- Build image aplikasi dari Dockerfile
- Menjalankan service PostgreSQL
- Menjalankan script main.py sekali
- Menyimpan output di folder target/

### 5. Verifikasi Output
Setelah proses selesai, cek folder target/:
```bash
ls -la target/
```
Akan muncul file JSON dan CSV dengan timestamp saat eksekusi.

## Cara Menjalankan Unit Test
Untuk menjalankan unit test di dalam container:
```bash
docker compose run --rm app pytest tests/test_main.py -v
```
Hasil yang diharapkan: semua test lulus (7 passed).

## Format Output
`data_YYYYMMDDHHMMSS.json`: berisi data bersih dengan struktur:
```json
{
  "row_count": 2,
  "data": [
    {
      "dates": "2024-04-01",
      "ids": "string",
      "names": "UPPERCASE",
      "monthly_listeners": 568020,
      "popularity": 49,
      "followers": 598724,
      "genres": ["alternative metal", "alternative rock"],
      "first_release": "1995",
      "last_release": "1995",
      "num_releases": 2,
      "num_tracks": 26,
      "playlists_found": "Grunge Forever",
      "feat_track_ids": ["3e2fDgC93LGc9Lbdvr6I9k", "5DRUgJmwLvCHQjiFzb4LSQ"]
    }
  ]
}
```

`data_reject_YYYYMMDDHHMMSS.csv`: berisi data duplikat dengan format sama seperti scrap.csv.

## Konfigurasi Database
Tabel data dan data_reject dibuat otomatis oleh script melalui ddl.sql. Struktur kolom:

| Kolom | Tipe Data |
|---|---|
| dates | DATE |
| ids | VARCHAR |
| names | VARCHAR |
| monthly_listeners | INTEGER |
| popularity | INTEGER |
| followers | INTEGER |
| genres | TEXT[] |
| first_release | VARCHAR(4) |
| last_release | VARCHAR(4) |
| num_releases | INTEGER |
| num_tracks | INTEGER |
| playlists_found | VARCHAR |
| feat_track_ids | TEXT[] |

## Validasi Database
Untuk memeriksa jumlah baris pada tabel:
```bash
docker compose exec db psql -U postgres -d EDTS_DE -c "SELECT COUNT(*) FROM data;"
docker compose exec db psql -U postgres -d EDTS_DE -c "SELECT COUNT(*) FROM data_reject;"
```

## Catatan Penting
- Gunakan perintah `docker compose down -v` untuk mereset database beserta volumenya.
- Pastikan volume mount `./source` dan `./target` terpasang dengan benar.
- Jika terjadi duplikasi data karena insert berulang, hapus isi tabel dengan `TRUNCATE data, data_reject;` sebelum menjalankan ulang.

## Monitoring dan Debugging
- Log aplikasi ditampilkan di terminal, dapat diakses dengan `docker compose logs app`.
- Untuk debugging interaktif, masuk ke container:
```bash
docker compose run --rm app bash
```
- Untuk memeriksa isi database secara interaktif:
```bash
docker compose exec db psql -U postgres -d EDTS_DE
```
Gunakan mode expanded display dengan perintah `\x` untuk tampilan lebih rapi.

## Pengujian Per Fungsi
Setiap fungsi pada main.py dapat diuji secara terpisah menggunakan Python shell di dalam container. Contoh pengujian fungsi read_csv:
```bash
docker compose run --rm app python -c "from main import read_csv; df = read_csv('/app/example/scrap.csv'); print(df.head())"
```
Pengujian unit test lengkap menggunakan pytest seperti dijelaskan sebelumnya.

## Improvement yang Mungkin Dilakukan
- Menambahkan logging ke file untuk audit trail
- Menambahkan retry logic untuk koneksi database
- Menggunakan environment variable untuk path input/output
- Menambahkan validasi data lebih lanjut (misal cek format tanggal)
- Memisahkan kode menjadi modul terpisah (db.py, transform.py, dll) untuk maintainability

## Referensi
- Dokumentasi pandas: https://pandas.pydata.org/docs/
- Dokumentasi psycopg2: https://www.psycopg.org/docs/
- Dokumentasi PostgreSQL: https://www.postgresql.org/docs/
- Dokumentasi Docker: https://docs.docker.com/

## Kontak
- Author: [Nama Anda]
- Email: [email@domain.com]
- LinkedIn: [linkedin.com/in/username]