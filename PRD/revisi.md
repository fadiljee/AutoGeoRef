# Product Requirements Document (PRD) - AutoGeoRef v2.0

**Fokus Pembaruan:** Peningkatan Presisi Ekstraksi Teks Koordinat (OCR) Level Sub-Piksel
**Status:** Draf Prioritas
**Target Implementasi:** Memperbaiki anomali pembacaan angka bulat (truncation) menjadi presisi minimal 6 digit desimal.

## 1. Latar Belakang Masalah

Implementasi awal sistem OCR gagal menangkap nilai desimal secara utuh pada teks berukuran sangat kecil di margin peta. Mesin membulatkan koordinat (misalnya menjadi `105.5` dan `-2.0`), yang menyebabkan distorsi geospasial yang fatal saat dimuat ke QGIS. Peta skala dusun/desa memerlukan tingkat presisi koordinat minimal 6 hingga 8 angka di belakang koma untuk menghindari pergeseran lokasi di lapangan.

## 2. Tujuan Pembaruan (Objectives)

* Meningkatkan ketajaman area target di keempat sudut gambar sebelum dibaca oleh mesin OCR.
* Mengganti atau meningkatkan mesin OCR agar mampu mengenali karakter numerik berukuran mikro yang saling berdekatan.
* Menerapkan lapisan validasi matematis untuk menolak *output* berupa angka bulat atau angka yang kekurangan digit desimal.

## 3. Fitur Peningkatan Presisi (Requirements)

### A. *Advanced Image Pre-processing Pipeline* (Pra-pemrosesan Citra)

Sistem tidak boleh langsung mengirim potongan gambar mentah ke mesin OCR. Skrip harus menerapkan rantai manipulasi OpenCV berikut pada area sudut yang dipotong:

1. **Color Masking (Isolasi Warna):** Filter secara spesifik kode warna *cyan/blue* pada piksel gambar untuk memisahkan teks koordinat dari *noise* (seperti garis tepi peta, noda *scan*, atau bayangan latar belakang).
2. **Upscaling (Pembesaran Resolusi):** Perbesar (*resize*) potongan area sudut sebesar 300% hingga 400% menggunakan algoritma interpolasi seperti `cv2.INTER_CUBIC` agar bentuk angka yang pecah menjadi lebih padat.
3. **Grayscale & Adaptive Binarization:** Ubah warna hasil isolasi menjadi hitam murni dan putih murni (Biner) menggunakan *Adaptive Thresholding* atau *Otsu's Binarization*. Angka biru diubah menjadi hitam solid berlatar putih.
4. **Dilation/Erosion (Morphological Ops):** Gunakan kernel ringan untuk menebalkan garis angka yang terlalu tipis akibat proses *scan* yang pudar.

### B. *AI-Powered OCR Engine*

Mesin OCR dasar (seperti Tesseract bawaan) kurang andal untuk teks mikro. Sistem harus di- *upgrade* menggunakan salah satu opsi berikut:

1. **PaddleOCR:** Mesin berbasis *Deep Learning* yang jauh lebih tangguh membaca teks dengan format rumit dan spasi rapat dibandingkan Tesseract, serta bisa dijalankan secara lokal/gratis.
2. **Cloud Vision API (Google) / AWS Textract:** Jika akurasi absolut adalah prioritas dan ada anggaran, integrasikan API ini khusus untuk membaca 4 kotak margin tersebut.

### C. *Strict Regex & Logics Validation* (Validasi Berlapis)

Sistem harus mengkarantina pembacaan OCR yang tidak memenuhi standar geospasial melalui Regular Expression (Regex):

1. **Aturan Desimal (Bujur/X):** Regex harus memak## Dokumen Persyaratan Produk (PRD): Peningkatan Presisi Pembacaan Batas Luar (Outer Boundary Detection)

**Status:** Draft | **Tanggal:** 1 Oktober 2026 | **Pemilik Produk:** [Nama Anda/Tim]

### 1. Ringkasan Eksekutif

Inisiatif ini bertujuan untuk merombak dan meningkatkan akurasi sistem pembacaan batas luar (outer boundary/edge detection) pada produk saat ini agar mencapai tingkat presisi maksimal (pixel-perfect atau sub-pixel accuracy). Peningkatan ini dirancang untuk mengatasi masalah pemotongan area yang tidak tepat, distorsi latar belakang, dan kegagalan deteksi pada kondisi visual yang menantang, sehingga menghasilkan data atau gambar keluaran yang sempurna tanpa intervensi manual dari pengguna.

### 2. Latar Belakang & Pernyataan Masalah

Sistem deteksi batas luar saat ini sering kali gagal memberikan hasil yang presisi saat dihadapkan pada kondisi dunia nyata. Masalah utama yang teridentifikasi meliputi:

* **Pemotongan Berlebih (Over-cropping):** Sistem memotong bagian penting dari objek karena salah mengidentifikasi bayangan atau tekstur internal sebagai batas luar.
* **Penggabungan Latar Belakang (Under-cropping):** Sistem gagal membedakan batas objek dengan latar belakang yang memiliki warna atau kontras serupa (low-contrast edges).
* **Sensitivitas Pencahayaan:** Performa deteksi menurun drastis pada kondisi pencahayaan rendah, silau (glare), atau bayangan parsial.
* **Tingkat Koreksi Manual Tinggi:** Pengguna terpaksa harus menyesuaikan titik sudut atau garis batas secara manual, yang merusak pengalaman pengguna (UX) dan memperlambat proses.

### 3. Tujuan dan Metrik Kesuksesan (OKRs)

Fokus utama adalah mencapai presisi deteksi tertinggi dengan meminimalisir kesalahan margin batas.

| Metrik Kesuksesan | Kondisi Saat Ini | Target Baru | Deskripsi |
| --- | --- | --- | --- |
| **Intersection over Union (IoU)** | ~82% | **> 98%** | Akurasi area yang terdeteksi dibandingkan dengan batas objek aslinya. |
| **Tingkat Intervensi Manual** | 35% pengguna | **< 5%** | Persentase pengguna yang harus memperbaiki batas secara manual. |
| **Edge Margin Error** | ± 15 pixel | **< 2 pixel** | Toleransi deviasi garis batas dari tepi objek sebenarnya. |
| **Waktu Pemrosesan (Latency)** | 1.2 detik | **< 0.5 detik** | Waktu yang dibutuhkan sistem untuk mendeteksi dan merender batas (real-time). |

### 4. Persyaratan Fungsional (Fokus Presisi Tinggi)

Untuk mencapai target presisi ekstrem, sistem harus mengimplementasikan lapisan teknologi berikut:

* **Deteksi Tepi Tingkat Sub-Piksel (Sub-pixel Edge Detection):** Algoritma tidak lagi membulatkan batas pada grid piksel, melainkan menghitung nilai interpolasi antar piksel untuk menemukan garis batas sejati dengan akurasi matematis tertinggi.
* **Segmentasi Semantik Berbasis AI (Semantic Instance Segmentation):** Mengganti/memperkuat pendekatan heuristik tradisional (seperti Canny edge atau Hough transform) dengan model *deep learning* (seperti varian Mask R-CNN atau U-Net yang dioptimalkan) untuk memahami konteks objek, bukan hanya mencari perbedaan kontras warna.
* **Koreksi Perspektif dan Distorsi Otomatis:** Sistem harus mampu membaca batas luar dari sudut pandang yang ekstrem (kemiringan hingga 45 derajat) dan secara otomatis meluruskan proyeksi (dewarping/keystone correction) tanpa mendistorsi rasio asli objek.
* **Active Contour / Model Snake:** Implementasi algoritma yang memungkinkan garis pembatas menempel erat pada lengkungan atau ketidakteraturan tepi objek yang tidak berbentuk kotak sempurna.
* **Kecerdasan Kontekstual Latar Belakang:** Algoritma harus memiliki fungsi *background rejection* yang kebal terhadap pola latar belakang yang rumit (misalnya objek putih di atas meja marmer putih).

### 5. Persyaratan Non-Fungsional

* **Kinerja & Latensi:** Inferensi model batas luar harus berjalan secara lokal di perangkat pengguna (On-Device Processing/Edge Computing) untuk menghindari latensi jaringan, dengan alokasi memori maksimal 50MB.
* **Skalabilitas Model:** Model AI harus dilatih dengan augmentasi data yang ekstensif, mencakup 50+ kondisi pencahayaan dan 100+ jenis tekstur latar belakang.

### 6. Pengalaman Pengguna (User Experience)

* **Panduan Visual Real-Time:** Menampilkan garis batas atau *bounding box* dinamis yang berubah warna (misalnya dari merah ke hijau) saat sistem telah mengunci batas presisi tertinggi secara *real-time* melalui antarmuka kamera.
* **Auto-Capture Magnetik:** Saat sistem mendeteksi stabilitas dan IoU di atas 98%, sistem otomatis mengambil data/gambar tanpa pengguna harus menekan tombol, mencegah guncangan tangan (micro-jitter) yang dapat menggeser batas yang sudah presisi.
* **Kaca Pembesar (Magnifier UI) untuk Koreksi Manual:** Jika pengguna (dalam kasus <5%) harus melakukan koreksi manual, UI akan menampilkan *loupe* atau kaca pembesar di ujung jari agar pengguna dapat melihat piksel batas secara presisi tanpa terhalang jari mereka.

### 7. Rencana Fase Rilis

| Fase | Inisiatif Utama | Estimasi Waktu |
| --- | --- | --- |
| **Fase 1: R&D & Pengumpulan Data** | Pelatihan model AI dengan dataset batas objek yang memiliki kemiripan warna latar belakang tinggi (low-contrast). | Minggu 1-3 |
| **Fase 2: Prototyping Engine** | Menguji akurasi sub-piksel secara internal. Fokus murni pada peningkatan metrik IoU hingga mencapai target 98%. | Minggu 4-6 |
| **Fase 3: Integrasi UX** | Menggabungkan model deteksi baru dengan antarmuka *real-time preview* dan *magnifier tool*. | Minggu 7-8 |
| **Fase 4: Beta Testing** | Rilis terbatas ke kelompok pengguna terpilih untuk mengukur penurunan tingkat intervensi manual. | Minggu 9-10 |

Apakah implementasi PRD ini difokuskan untuk pembacaan dokumen fisik (seperti KTP/Kertas), batas lahan geografis, atau pemotongan objek bebas dalam gambar, agar saya dapat menyesuaikan spesifikasi teknis model AI yang digunakan?