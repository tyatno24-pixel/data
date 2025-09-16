import pandas as pd
import json
import os
from datetime import datetime

# --- KONFIGURASI ---
# Pastikan path ini benar sesuai dengan lokasi file Excel Anda
EXCEL_FILE_PATH = r'C:\Users\tyatn\Downloads\daftar_belanja_wulandari.xlsx'

# Path ke file database JSON Anda (seharusnya sudah benar jika file ini ada di folder proyek)
DB_FILE_PATH = 'database.json'

# PENTING: Sesuaikan nama kolom ini jika nama kolom di file Excel Anda berbeda
KOLOM_NAMA_ITEM = 'Barang Dibeli'
KOLOM_KUANTITAS = 'Jumlah Barang'
KOLOM_HARGA = 'Harga (Rp)'
KOLOM_TANGGAL = 'Tanggal' # Tambahkan ini untuk mengambil tanggal dari Excel
# --- SELESAI KONFIGURASI ---

def import_data_from_excel():
    """
    Membaca data dari file Excel dan menambahkannya ke database.json.
    """
    # 1. Cek apakah file Excel ada
    if not os.path.exists(EXCEL_FILE_PATH):
        print(f"Error: File Excel tidak ditemukan di '{EXCEL_FILE_PATH}'")
        print("Pastikan path dan nama file sudah benar.")
        return

    # 2. Baca data dari Excel
    try:
        df = pd.read_excel(EXCEL_FILE_PATH)
        print(f"Berhasil membaca {len(df)} baris dari file Excel.\n")
    except Exception as e:
        print(f"Error saat membaca file Excel: {e}")
        return

    # Tambahan: Cetak nama kolom yang ditemukan untuk membantu debugging
    print("Nama kolom yang ditemukan di file Excel:")
    print(list(df.columns))
    print("-" * 30 + "\n")

    # 3. Load data JSON yang ada
    try:
        with open(DB_FILE_PATH, 'r', encoding='utf-8') as f:
            app_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Jika file tidak ada atau rusak, buat struktur baru
        app_data = {"theme": "superhero", "shopping_list": [], "salary_data": {"employees": [], "all_time": {}}, "font": "Arial"}

    # 4. Proses setiap baris dari Excel dan tambahkan ke shopping_list
    items_added_count = 0
    for index, row in df.iterrows():
        new_item = {
            "id": datetime.now().timestamp() + index, # Tambahkan index agar ID unik jika impor cepat
            "item": row[KOLOM_NAMA_ITEM],
            "quantity": row[KOLOM_KUANTITAS],
            "price": row[KOLOM_HARGA],
            "status": "Di beli",  # Sesuai permintaan
            "date_added": pd.to_datetime(row[KOLOM_TANGGAL]).strftime('%Y-%m-%d'), # Ambil tanggal dari Excel
            "delivery_status": "Sudah Sampai" # Sesuai permintaan
        }
        # Cek sederhana untuk menghindari duplikat jika skrip dijalankan lagi
        # (Berdasarkan nama, kuantitas, dan harga)
        if not any(d['item'] == new_item['item'] and d['quantity'] == new_item['quantity'] and d['price'] == new_item['price'] for d in app_data['shopping_list']):
            app_data['shopping_list'].append(new_item)
            items_added_count += 1

    # 5. Simpan kembali data yang sudah diperbarui ke file JSON
    with open(DB_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(app_data, f, indent=4)

    print(f"Berhasil! {items_added_count} item baru telah ditambahkan ke '{DB_FILE_PATH}'.")
    print("Anda sekarang bisa menjalankan aplikasi web Anda untuk melihat datanya.")

if __name__ == '__main__':
    import_data_from_excel()