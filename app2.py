import fitz  # PyMuPDF untuk ekstraksi teks akurat
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

# Cek semua elemen penting dari PDF berdasarkan pola teks
def check_fields(text):
    patterns = {
        'Nomor SEP': r'No\.SEP.*?(\d+)',
        'Surat Eligibilitas': r'SURAT ELEGIBILITAS PESERTA',
        'Nomor Rekam Medis': r'Nomor RM.*?(\d+)',
        'Nama Pasien': r'Nama Pasien.*?(\w+)',
        'DPJP': r'DPJP.*?dr\.',
        'Diagnosa Utama': r'Diagnosa Utama.*?([A-Z0-9]+)',
        'Diagnosa Sekunder': r'Diagnosa Sekunder.*?([A-Z0-9]+)',
        'Tindakan': r'Tindakan.*?\n.*',
        'Hasil Radiologi': r'Radiologi.*',
        'Hasil Laboratorium': r'Laboratorium.*',
        'Resep Obat': r'(?:RACIK|PARASETAMOL|N-ACETYLCYSTEINE)',
        'Pemeriksaan Fisik': r'Pemeriksaan Fisik.*',
        'Instruksi/Tindak Lanjut': r'Instruksi.*'
    }
    results = {}
    for field, pattern in patterns.items():
        results[field] = 'Lengkap' if re.search(pattern, text, re.IGNORECASE) else 'Kosong'
    return results

# Proses batch dan simpan hasil pengecekan ke CSV
with open(output_csv, mode='w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(['Nama File'] + list(check_fields('Test').keys()))

    for filename in os.listdir(folder_path):
        if filename.endswith('.pdf'):
            text = extract_text_from_pdf(os.path.join(folder_path, filename))
            results = check_fields(text)
            csvwriter.writerow([filename] + [results[field] for field in results])

print(f'Pengecekan lengkap selesai! Hasil disimpan di {output_csv}')
