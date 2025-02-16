import fitz  # PyMuPDF buat ekstrak teks dari PDF
import os
import csv
import re

# Folder PDF & Output
folder_path = "."  # Sesuaikan dengan lokasi PDF
output_csv = "hasil_pengecekan.csv"

# Pola teks buat deteksi halaman penting & ekstraksi tanggal
dokumen_penting = {
    "Lembar E-Klaim": r"KEMENTERIAN KESEHATAN REPUBLIK INDONESIA",
    "SEP BPJS": r"SURAT ELEGIBILITAS PESERTA",
    "Ringkasan Pasien Pulang": r"DISCHARGE SUMMARY",
    "Hasil USG": r"HASIL USG",
    "Asesmen Medis IGD": r"ASESMEN MEDIS IGD",
    "Triage Pasien": r"TRIAGE PASIEN",
    "Hasil Laboratorium": r"HASIL PEMERIKSAAN",
    "Rincian Tagihan BPJS": r"RINCIAN TAGIHAN"
}

# Pola regex buat ekstraksi tanggal masuk & keluar (umum & discharge summary)
tanggal_patterns = {
    "Tanggal Masuk (Umum)": r"Tanggal\s+Masuk[:\s]+(\d{2}/\d{2}/\d{4})",
    "Tanggal Keluar (Umum)": r"Tanggal\s+Keluar[:\s]+(\d{2}/\d{2}/\d{4})",
}
tanggal_discharge_patterns = {
    "Tanggal Masuk (Discharge Summary)": r"Tanggal\s+Masuk\s*[:\s]+(\d{2}/\d{2}/\d{4})",
    "Tanggal Keluar (Discharge Summary)": r"Tanggal\s+Keluar\s*[:\s]+(\d{2}/\d{2}/\d{4})",
}

# Pola buat cek tindakan 88.78 (USG) di halaman pertama
tindakan_usg_pattern = r"88\.78"

# Fungsi ekstrak teks dari PDF
def extract_text_from_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        texts = [page.get_text() for page in doc]  # Simpan semua halaman dalam list
        doc.close()
        return texts  # Balikin list teks per halaman
    except Exception as e:
        print(f"❌ Gagal membaca {pdf_path}: {e}")
        return None

# Fungsi cek elemen dalam PDF
def check_pdf_content(texts):
    results = {key: "❌" for key in dokumen_penting}  # Default semua silang ❌
    hasil_usg_wajib = False  # Default: USG gak wajib
    hasil_lab_terakhir = "✅"  # Default dianggap AMAN

    # Default tanggal masuk & keluar
    extracted_dates = {
        "Tanggal Masuk (Umum)": "Kosong",
        "Tanggal Keluar (Umum)": "Kosong",
        "Tanggal Masuk (Discharge Summary)": "Kosong",
        "Tanggal Keluar (Discharge Summary)": "Kosong",
    }

    if texts:
        full_text = "\n".join(texts)  # Gabung semua halaman buat pencarian tanggal lebih akurat

        # Ekstraksi tanggal masuk & keluar (umum)
        for key, pattern in tanggal_patterns.items():
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                extracted_dates[key] = match.group(1)  # Ambil tanggal yang ditemukan

        # Cek tindakan 88.78 di halaman pertama
        if re.search(tindakan_usg_pattern, texts[0], re.IGNORECASE):
            hasil_usg_wajib = True  # Kalau ada tindakan 88.78, Hasil USG harus ada
        
        # Loop semua halaman buat cek dokumen penting & Discharge Summary
        for page_num, page_text in enumerate(texts):
            for key, pattern in dokumen_penting.items():
                if re.search(pattern, page_text, re.IGNORECASE):
                    results[key] = "✅"  # Kalau ketemu, ganti jadi checklist ✅

                    # Cek apakah "Hasil Laboratorium" ada di halaman terakhir
                    if key == "Hasil Laboratorium" and page_num == len(texts) - 1:
                        hasil_lab_terakhir = "❌ (TIDAK BOLEH DI HALAMAN TERAKHIR!)"

            # Kalau halaman ini ada "Ringkasan Pasien Pulang", cari tanggal masuk & keluar di sini
            if results["Ringkasan Pasien Pulang"] == "✅":
                for key, pattern in tanggal_discharge_patterns.items():
                    match = re.search(pattern, page_text, re.IGNORECASE)
                    if match:
                        extracted_dates[key] = match.group(1)  # Ambil tanggal yang ditemukan

        # Kalau tindakan 88.78 ada di halaman pertama tapi hasil USG gak ada, tandai silang
        if hasil_usg_wajib and results["Hasil USG"] == "❌":
            results["Hasil USG"] = "❌ (HARUS ADA!)"

    results.update(extracted_dates)  # Tambahkan tanggal masuk & keluar ke hasil akhir
    results["Posisi Hasil Lab"] = hasil_lab_terakhir  # Tambahkan info posisi hasil lab
    return results

# Cek apakah folder PDF ada
if not os.path.exists(folder_path):
    print(f"❌ Folder {folder_path} tidak ditemukan!")
    exit()

# Ambil semua file PDF di folder
pdf_files = [f for f in os.listdir(folder_path) if f.endswith(".pdf")]

# Kalau gak ada file PDF, langsung keluar
if not pdf_files:
    print("❌ Tidak ada file PDF di dalam folder!")
    exit()

# Proses semua PDF dan simpan hasil ke CSV
with open(output_csv, mode="w", newline="") as csvfile:
    csvwriter = csv.writer(csvfile)
    header = ["Nama File", "Tanggal Masuk (Umum)", "Tanggal Keluar (Umum)", 
              "Tanggal Masuk (Discharge Summary)", "Tanggal Keluar (Discharge Summary)"] + \
             list(dokumen_penting.keys()) + ["Posisi Hasil Lab"]
    csvwriter.writerow(header)

    for filename in pdf_files:
        pdf_path = os.path.join(folder_path, filename)
        texts = extract_text_from_pdf(pdf_path)

        if texts:  # Cek apakah teks berhasil diekstrak
            results = check_pdf_content(texts)
            csvwriter.writerow([filename, results["Tanggal Masuk (Umum)"], results["Tanggal Keluar (Umum)"],
                                results["Tanggal Masuk (Discharge Summary)"], results["Tanggal Keluar (Discharge Summary)"]] +
                               [results[key] for key in dokumen_penting.keys()] + 
                               [results["Posisi Hasil Lab"]])

            # Tampilkan hasil di terminal juga
            print(f"\n📄 **Hasil Pengecekan untuk {filename}:**")
            for key, status in results.items():
                print(f"   {key}: {status}")

print(f"\n✅ Pengecekan selesai! Hasil disimpan di {output_csv}")
