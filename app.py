import fitz  # PyMuPDF untuk ekstraksi teks lebih akurat
import os
import csv
import re

# Folder PDF dan output
folder_path = './klaim_pdf'
output_csv = 'hasil_pengecekan.csv'

# Fungsi baca teks dari PDF
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = "".join(page.get_text() for page in doc)
    doc.close()
    return text

# Fungsi cek kolom dengan pola regex untuk hasil lebih akurat
def check_fields(text):
    patterns = {
        'Nomor SEP': r'Nomor SEP[:\s]*(\S+)',
        'Nomor Rekam Medis': r'Nomor Rekam Medis[:\s]*(\S+)',
        'Nama Pasien': r'Nama Pasien[:\s]*(\S+)',
        'Tanggal Masuk': r'Tanggal Masuk[:\s]*(\S+)',
        'Tanggal Keluar': r'Tanggal Keluar[:\s]*(\S+)',
        'DPJP': r'DPJP[:\s]*(\S+)',
        'Diagnosa Utama': r'Diagnosa Utama[:\s]*(\S+)',
        'Diagnosa Sekunder': r'Diagnosa Sekunder[:\s]*(\S+)',
        'Tindakan': r'Tindakan Yang Diberikan[:\s]*(.+)',
        'Hasil Rontgen': r'Pemeriksaan Diagnostik[:\s]*(.+)',
        'Hasil Laboratorium': r'Laboratorium[:\s]*(.+)',
        'Resep Obat': r'RACIK[:\s]*(.+)',
        'Surat Eligibilitas Peserta': r'SURAT ELEGIBILITAS PESERTA'
    }
    results = {}
    for field, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        results[field] = 'Lengkap' if match else 'Kosong'
    return results

# Simpan hasil pengecekan ke CSV
with open(output_csv, mode='w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['Nama File'] + list(check_fields('Test').keys()))

    for filename in os.listdir(folder_path):
        if filename.endswith('.pdf'):
            text = extract_text_from_pdf(os.path.join(folder_path, filename))
            results = check_fields(text)
            csvwriter.writerow([filename] + [results[field] for field in results])

print(f'Pengecekan selesai! Hasil lengkap disimpan di {output_csv}')
