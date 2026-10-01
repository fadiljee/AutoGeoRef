# AutoGeoRef - Sistem Otomatisasi Georeferencing Peta Berbasis OCR

AutoGeoRef adalah proyek untuk mengotomatisasi proses georeferencing peta wilayah hasil scan (khususnya wilayah Bangka Belitung). Sistem ini memproses sekumpulan peta dalam format `.jpg`, membaca titik-titik koordinat pada keempat sudutnya menggunakan teknologi AI PaddleOCR untuk presisi level sub-piksel, dan secara otomatis menghasilkan file koordinat world (`.pgw`) serta file metadata spasial (`.aux.xml`) agar siap dibuka dan selaras pada QGIS.

## Struktur Folder
Sistem menggunakan struktur folder ini:
* `data/1_input_raw/`: Taruh semua peta berformat `.jpg` di sini.
* `data/2_temp_crop_debug/`: Tempat menyimpan sementara hasil potongan sudut. Dapat digunakan untuk memvalidasi performa OCR jika terdapat error.
* `data/3_output_ready/`: Tempat hasil eksekusi (`.jpg`, `.pgw`, dan `.aux.xml` yang siap digunakan di QGIS).
* `logs/`: Tempat log eksekusi, akan menyimpan laporan error/sukses di file `processing_report.csv`.
* `src/`: Berisi skrip inti Python (pipeline utama, OCR, kalkulasi).
* `templates/`: Menyimpan base template untuk file `.aux.xml` berformat metadata WGS 84.

## Prasyarat Lingkungan
Pastikan library yang ada di `requirements.txt` sudah diinstall:
```bash
pip install -r requirements.txt
```
*(Catatan: Proses pertama kali menjalankan skrip akan membutuhkan koneksi internet untuk mengunduh model PaddleOCR. Sistem tidak lagi memerlukan instalasi aplikasi eksternal Tesseract.)*

## Cara Menggunakan
1. Taruh file `.jpg` ke dalam direktori `data/1_input_raw`.
2. Jalankan skrip `main_pipeline.py`
   ```bash
   python src/main_pipeline.py
   ```
3. Cek hasil file yang divalidasi pada folder `data/3_output_ready`.
4. Anda dapat *drag and drop* hasil di dalam folder `data/3_output_ready` langsung ke QGIS. Peta tersebut harusnya otomatis berada di posisinya (Georeferenced).
5. Jika ada file yang gagal, Anda dapat memeriksanya di `logs/processing_report.csv`.
