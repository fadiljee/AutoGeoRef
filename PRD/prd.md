# Product Requirements Document (PRD)

**Nama Produk:** AutoGeoRef - Sistem Otomatisasi Georeferencing Peta Berbasis OCR
**Status:** Draf
**Target Implementasi:** Pemrosesan Peta WSS (Wilayah Kerja Statistik) Kecamatan Parittiga dan sekitarnya.

## 1. Latar Belakang dan Tujuan

Proses *georeferencing* manual ribuan peta hasil pemindaian (format JPG) di QGIS memakan waktu yang sangat lama dan rentan terhadap *human error*. Produk ini bertujuan untuk membangun *script* otomatisasi yang dapat membaca gambar JPG, mengekstrak teks koordinat batas luar di sudut peta menggunakan *Optical Character Recognition* (OCR), dan secara otomatis menghasilkan *world file* (`.pgw`) beserta metadata spasial (`.aux.xml`) agar peta siap dioverlay di QGIS.

## 2. Ruang Lingkup (Scope)

* **In-Scope:** Pemrosesan *batch* file JPG, pemotongan sudut gambar, pembacaan teks koordinat (OCR), validasi nilai koordinat geografis (WGS 84), dan pembuatan file `.pgw` dan `.aux.xml`.
* **Out-of-Scope:** Perbaikan gambar JPG yang terlalu buram/rusak parah, dan manipulasi geometri peta (*warping* non-linear).

## 3. Fitur Utama (Requirements)

1. **Batch Processing:** Sistem mampu memindai dan memproses seluruh file `.jpg` di dalam satu folder target tanpa intervensi manual.
2. **Smart Corner Cropping:** Sistem secara otomatis memotong (crop) area spesifik di keempat sudut gambar tempat angka koordinat batas luar berada.
3. **OCR Data Extraction:** Sistem mengubah gambar piktogram angka di sudut peta menjadi data teks (numerik/desimal) titik X (Bujur) dan Y (Lintang).
4. **Spatial Transformation Calculator:** Sistem mengalkulasi resolusi piksel sumbu X dan Y berdasarkan dimensi gambar dan jarak koordinat untuk menghasilkan 6 parameter afin.
5. **Output Generator:** Sistem membuat file `.pgw` dan `.aux.xml` dengan penamaan file yang persis sama dengan nama file JPG asal (contoh: `1903051009000100_WSS.jpg` -> `1903051009000100_WSS.pgw`).
6. **Error Handling & Logging:** Sistem menolak nilai OCR yang tidak masuk akal (misalnya melenceng dari koordinat Bangka Barat) dan mencatat file yang gagal diproses ke dalam laporan untuk ditinjau manual.

---

## 4. Alur Kerja (Workflow)

1. **Tahap Persiapan (Input):** Pengguna memasukkan seluruh file gambar pemindaian peta (`.jpg`) ke dalam folder `input_data`.
2. **Tahap Pra-Pemrosesan (Image Pre-processing):**
* *Script* membaca dimensi gambar JPG (lebar x tinggi dalam piksel).
* *Script* mengisolasi warna biru (warna teks koordinat) dan memotong 4 area sudut gambar (Kiri-Atas, Kanan-Atas, Kiri-Bawah, Kanan-Bawah).


3. **Tahap Ekstraksi (OCR):** Mesin OCR membaca potongan gambar tersebut dan mengekstrak nilai angka menjadi variabel teks (`X_min`, `Y_max`, `X_max`, `Y_min`).
4. **Tahap Validasi:** Sistem mengecek apakah teks yang diekstrak berupa angka yang valid dan masuk akal untuk rentang koordinat wilayah Kepulauan Bangka Belitung (Bujur ~105.0 hingga ~108.0, Lintang ~-1.5 hingga ~-3.5).
5. **Tahap Kalkulasi Matematis:**
* Menghitung ukuran piksel X: `(X_max - X_min) / Lebar Gambar`
* Menghitung ukuran piksel Y: `(Y_min - Y_max) / Tinggi Gambar` (Biasanya bernilai negatif).


6. **Tahap Eksekusi (Output):**
* Sistem menulis 6 baris angka hasil kalkulasi ke dalam file `.pgw`.
* Sistem menyalin *template* EPSG:4326 ke dalam file `.aux.xml`.
* File dipindahkan ke folder `output_georeferenced`.


7. **Selesai:** Peta siap diseret (*drag-and-drop*) langsung ke QGIS dan akan otomatis berada di posisi yang benar.

---

## 5. Struktur Folder

Rekomendasi struktur folder proyek untuk menjaga kerapian data dan *source code*:

```text
georef-automation-project/
│
├── data/
│   ├── 1_input_raw/             # Letakkan semua file JPG peta mentah di sini
│   ├── 2_temp_crop_debug/       # (Otomatis) Hasil potongan sudut disimpan sementara untuk ngecek jika OCR salah baca
│   └── 3_output_ready/          # (Otomatis) File JPG final berserta file .pgw dan .aux.xml hasil generate
│
├── src/                         # Folder kode sumber (Python)
│   ├── config.py                # Pengaturan variabel (koordinat batas wilayah toleransi, margin crop)
│   ├── main_pipeline.py         # Script utama untuk menjalankan workflow
│   ├── module_ocr.py            # Fungsi khusus image processing OpenCV dan Pytesseract
│   └── module_geo_calc.py       # Fungsi khusus kalkulasi GDAL dan pembuatan file PGW/XML
│
├── templates/                   
│   └── base_aux.xml             # Template baku metadata XML WGS 84 untuk diduplikasi
│
├── logs/                        
│   └── processing_report.csv    # Laporan otomatis (Daftar file sukses, dan file gagal beserta alasan errornya)
│
├── requirements.txt             # Daftar library (opencv-python, pytesseract, numpy, gdal)
└── README.md                    # Panduan cara menjalankan sistem untuk operator

```