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
```
# Spesifikasi Protokol Komunikasi

Komunikasi menggunakan **TCP Socket** dengan format payload **JSON line-delimited** (diakhiri karakter newline `\n`).

## 1. Daftar Layanan Server

- `CHAR_COUNT`: Menghitung total karakter pada teks.
- `WORD_COUNT`: Menghitung total kata pada teks.
- `REVERSE_STRING`: Membalikkan urutan karakter teks.
- `REMOVE_VOWELS`: Menghilangkan huruf vokal (`a`, `i`, `u`, `e`, `o`).
- `MATRIX_3X3`: Menghitung nilai determinan dan invers dari matriks 3x3.

## 2. Format Pertukaran Pesan

### A. Request (Klien -> Server)

Request digunakan oleh klien untuk meminta server menjalankan suatu layanan.

#### Contoh untuk Pemrosesan Teks

```json
{
  "type": "REQUEST",
  "request_id": "req-101",
  "service": "CHAR_COUNT",
  "payload": {
    "text": "Jaringan Komputer UGM"
  }
}
```

#### Contoh untuk Pemrosesan Matriks 3x3

```json
{
  "type": "REQUEST",
  "request_id": "req-102",
  "service": "MATRIX_3X3",
  "payload": {
    "matrix": [
      [1, 2, 3],
      [0, 1, 4],
      [5, 6, 0]
    ]
  }
}
```

### B. Response (Server -> Klien)

Response dikirim oleh server setelah memproses request dari klien.

#### Response Jika Layanan Aktif

```json
{
  "type": "RESPONSE",
  "request_id": "req-101",
  "service": "CHAR_COUNT",
  "status": "SUCCESS",
  "result": 21
}
```

#### Response Jika Layanan Telah Dinonaktifkan

```json
{
  "type": "RESPONSE",
  "request_id": "req-101",
  "service": "CHAR_COUNT",
  "status": "DISABLED",
  "message": "Layanan CHAR_COUNT telah dinonaktifkan oleh server."
}
```

### C. Acknowledgement / ACK (Klien -> Server)

Klien memeriksa hasil komputasi dan mengirimkan status evaluasi (`CORRECT` atau `INCORRECT`).

```json
{
  "type": "ACK",
  "request_id": "req-101",
  "service": "CHAR_COUNT",
  "status": "INCORRECT"
}
```

### D. ACK Confirmation (Server -> Klien)

Server memperbarui status layanan dan mengirimkan daftar layanan yang masih aktif.

```json
{
  "type": "ACK_CONFIRM",
  "request_id": "req-101",
  "service": "CHAR_COUNT",
  "action": "DISABLED",
  "active_services": [
    "WORD_COUNT",
    "REVERSE_STRING",
    "REMOVE_VOWELS",
    "MATRIX_3X3"
  ],
  "server_status": "RUNNING"
}
```

> Jika seluruh layanan nonaktif, nilai `server_status` berubah menjadi `TERMINATING` dan server berhenti.

## Petunjuk Penggunaan

### 1. Menjalankan Unit Test

PowerShell:

```powershell
python -m unittest discover -s tests
```

### 2. Menjalankan Server

PowerShell:

```powershell
python main.py
```

Konfigurasi bawaan:

- **Host:** `0.0.0.0`
- **Port:** `65432`
