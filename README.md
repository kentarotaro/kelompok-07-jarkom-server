# Aplikasi Jaringan Server - Kelompok 7

Implementasi aplikasi jaringan berbasis TCP Socket Server dengan Application Layer Protocol kustom. Server memiliki mekanisme state management, toleransi kesalahan acak (fault-injection), penonaktifan layanan dinamis berbasis acknowledgement (ACK) klien, serta penghentian proses otomatis (graceful shutdown).

Projek ini disusun untuk memenuhi tugas mata kuliah Jaringan Komputer.

---

## Anggota Kelompok dan Pembagian Tugas

| No | Nama Anggota | NIM | Peran | Tanggung Jawab dan Berkas Target |
|:--:|:---|:---:|:---|:---|
| 1 | Aulia Kemal Syah | 25/560358/PA/23612 | Lead Architect & Network Engineer | Arsitektur repositori, penanganan koneksi socket TCP (`network/socket_server.py`), dan entry point (`main.py`). |
| 2 | Muhammad Iqbal Hilmi | 25/559451/PA/23532 | Service Logic & Math Implementer | Komputasi 5 layanan manipulasi string dan matriks 3x3 (`core/services.py`). |
| 3 | SANDY ADIYATMA PRAMANA | 25/567854/PA/23972 | Fault Injector & QA Engineer | Mekanisme penyuntikan jawaban salah (`core/fault_injector.py`) dan pengujian unit (`tests/test_services.py`). |
| 4 | KHOIRUL ANAM | 25/565234/PA/23836 | Protocol Designer & Integration Specialist | Perancangan skema protokol JSON (`network/protocol.py`), koordinasi dengan tim klien, dan dokumentasi laporan. |

---

## Struktur Direktori

Aplikasi dirancang modular dengan pemisahan fungsi (Separation of Concerns):

```text
kelompok-07-jarkom-server/
│
├── core/
│   ├── __init__.py
│   ├── services.py        # Logika 5 layanan komputasi string dan matriks 3x3
│   └── fault_injector.py  # Mekanisme pembangkitan respon salah secara acak
│
├── network/
│   ├── __init__.py
│   ├── protocol.py        # Spesifikasi dan validasi struktur JSON pesan
│   └── socket_server.py   # Pengelolaan socket TCP dan status aktif/nonaktif layanan
│
├── tests/
│   ├── __init__.py
│   └── test_services.py   # Unit test untuk memverifikasi logika layanan secara luring
│
├── .gitignore             # Mengabaikan file cache Python dan konfigurasi lokal
├── README.md              # Dokumentasi teknis proyek
├── requirements.txt       # Informasi dependensi lingkungan kerja
└── main.py                # Titik masuk utama untuk menjalankan server