import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from tkinter import messagebox
import json
import os
import time

DB_FILE = "database.json"

class ShoppingListPage(ttk.Frame):
    def __init__(self, parent, controller, initial_data=None):
        super().__init__(parent)
        self.controller = controller
        self.last_modified_time = 0 # Untuk melacak perubahan file
        
        # --- UI Setup ---
        page_frame = ttk.Frame(self, padding=10)
        page_frame.pack(fill=BOTH, expand=True)
        title_label = ttk.Label(page_frame, text="Daftar Belanja", font=("Helvetica", 18, "bold"), bootstyle=PRIMARY)
        title_label.pack(pady=10)

        input_frame = ttk.LabelFrame(page_frame, text="Input Barang", padding=10, bootstyle=INFO)
        input_frame.pack(fill=X, pady=10)

        ttk.Label(input_frame, text="Barang:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.item_entry = ttk.Entry(input_frame, width=30)
        self.item_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(input_frame, text="Jumlah:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.qty_entry = ttk.Entry(input_frame, width=15)
        self.qty_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        ttk.Label(input_frame, text="Harga:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.price_entry = ttk.Entry(input_frame, width=15)
        self.price_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        add_button = ttk.Button(input_frame, text="Tambah ke Daftar", command=self.add_item, bootstyle=SUCCESS)
        add_button.grid(row=0, column=2, rowspan=3, padx=20, sticky="ns")
        input_frame.columnconfigure(1, weight=1)

        total_frame = ttk.Frame(page_frame)
        total_frame.pack(fill=X, pady=5)
        self.total_label = ttk.Label(total_frame, text="Total Belanjaan: Rp 0.00", font=("Helvetica", 14, "bold"), bootstyle=SECONDARY)
        self.total_label.pack(anchor="e", padx=10)
        self.total_unbought_label = ttk.Label(total_frame, text="Total Belanja Belum Dibeli: Rp 0.00", font=("Helvetica", 12), bootstyle=WARNING)
        self.total_unbought_label.pack(anchor="e", padx=10)

        table_frame = ttk.LabelFrame(page_frame, text="Daftar Belanjaan", padding=10, bootstyle=INFO)
        table_frame.pack(fill=BOTH, expand=True, pady=10)

        cols = ["Barang", "Jumlah", "Harga Satuan", "Total Harga", "Status"]
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings", bootstyle=PRIMARY)
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="w", width=100)
        self.tree.column("Jumlah", anchor="center", width=60)
        self.tree.column("Harga Satuan", anchor="e", width=100)
        self.tree.column("Total Harga", anchor="e", width=100)
        self.tree.column("Status", anchor="center", width=100)

        scrollbar = ttk.Scrollbar(table_frame, orient=VERTICAL, command=self.tree.yview, bootstyle=ROUND)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.tree.pack(side=LEFT, fill=BOTH, expand=True)

        self.popup_menu = ttk.Menu(self, tearoff=0)
        self.popup_menu.add_command(label="Salin", command=self.copy_item)
        self.popup_menu.add_command(label="Hapus", command=self.delete_item)
        
        # Tags for status coloring
        self.tree.tag_configure('not_bought', foreground='#F44336') # Red
        self.tree.tag_configure('bought', foreground='#4CAF50') # Green

        self.tree.bind("<ButtonRelease-1>", self.toggle_status)
        self.tree.bind("<Button-3>", self.show_popup)

        back_button = ttk.Button(page_frame, text="Kembali ke Home", command=lambda: controller.show_frame("HomePage"), bootstyle=SECONDARY)
        back_button.pack(pady=10)
        
        # Muat data awal dari DB
        self._load_data_from_db_and_update_tree()
        # Mulai polling untuk update
        self._start_polling()

    def _load_data_from_db(self):
        if not os.path.exists(DB_FILE):
            return {"theme": "superhero", "shopping_list": [], "salary_data": {}, "font": "Arial"}
        try:
            with open(DB_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            messagebox.showwarning("Peringatan", "File database.json rusak atau tidak ditemukan. Menggunakan data default.")
            return {"theme": "superhero", "shopping_list": [], "salary_data": {}, "font": "Arial"}

    def _save_data_to_db(self, data):
        with open(DB_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        self.last_modified_time = os.path.getmtime(DB_FILE) # Update last modified time

    def _load_data_from_db_and_update_tree(self):
        app_data = self._load_data_from_db()
        self.load_items_into_tree(app_data.get("shopping_list", []))
        self.controller.app_data = app_data # Update controller's app_data

    def _start_polling(self):
        self.after(5000, self._check_for_updates) # Cek setiap 5 detik

    def _check_for_updates(self):
        if os.path.exists(DB_FILE):
            current_modified_time = os.path.getmtime(DB_FILE)
            if current_modified_time > self.last_modified_time:
                print("Perubahan terdeteksi di database.json, memperbarui UI desktop.")
                self._load_data_from_db_and_update_tree()
                self.last_modified_time = current_modified_time
        self.after(5000, self._check_for_updates) # Jadwalkan cek berikutnya

    def load_items_into_tree(self, items):
        # Hapus data lama sebelum memuat
        for i in self.tree.get_children():
            self.tree.delete(i)
        # Muat data baru
        total_belanja = 0.0
        total_belanja_unbought = 0.0
        for item_data in items:
            item = item_data.get('item', '')
            qty = item_data.get('quantity', 0)
            price = item_data.get('price', 0.0)
            status = item_data.get('status', 'Belum di beli')
            
            total_price = qty * price
            total_belanja += total_price
            if status == 'Belum di beli':
                total_belanja_unbought += total_price

            tag = 'bought' if status == 'Di beli' else 'not_bought'
            values_to_insert = [item, qty, f"{price:,.2f}", f"{total_price:,.2f}", status]
            self.tree.insert('' , END, values=values_to_insert, tags=(tag,))
        self.total_label.config(text=f"Total Belanjaan: Rp {total_belanja:,.2f}")
        self.total_unbought_label.config(text=f"Total Belanja Belum Dibeli: Rp {total_belanja_unbought:,.2f}")

    def get_data(self):
        # Mengambil data dari Treeview dan mengembalikannya dalam format yang konsisten
        data = []
        for item_id in self.tree.get_children():
            values = self.tree.item(item_id, "values")
            # Pastikan indeks sesuai dengan kolom yang ditampilkan
            item_data = {
                "item": values[0],
                "quantity": int(values[1]),
                "price": float(values[2].replace(",", "")), # Hapus koma untuk konversi float
                "status": values[4]
            }
            data.append(item_data)
        return data

    def show_popup(self, event):
        item_id = self.tree.identify_row(event.y)
        if item_id:
            self.tree.selection_set(item_id)
            self.popup_menu.post(event.x_root, event.y_root)

    def delete_item(self):
        selected_items = self.tree.selection()
        if not selected_items: return
        if messagebox.askyesno("Konfirmasi Hapus", "Apakah Anda yakin ingin menghapus item ini?", parent=self):
            item_name_to_delete = self.tree.item(selected_items[0], "values")[0]
            app_data = self._load_data_from_db()
            app_data['shopping_list'] = [item for item in app_data['shopping_list'] if item['item'] != item_name_to_delete]
            self._save_data_to_db(app_data)
            self._load_data_from_db_and_update_tree() # Refresh UI

    def copy_item(self):
        selected_item_id = self.tree.selection()
        if not selected_item_id: return
        values = self.tree.item(selected_item_id[0], "values")
        copy_text = f"Barang: {values[0]}, Jumlah: {values[1]}, Harga: {values[2]}, Status: {values[4]}"
        self.controller.clipboard_clear()
        self.controller.clipboard_append(copy_text)
        messagebox.showinfo("Disalin", "Data barang telah disalin ke clipboard.", parent=self)

    def update_total(self):
        # Total dihitung ulang di load_items_into_tree
        pass

    def add_item(self):
        item, qty_str, price_str = self.item_entry.get(), self.qty_entry.get(), self.price_entry.get()
        if not all((item, qty_str, price_str)):
            messagebox.showerror("Input Tidak Lengkap", "Semua kolom harus diisi.", parent=self)
            return
        try:
            qty, price = int(qty_str), float(price_str)
            if qty <= 0 or price < 0: raise ValueError
        except ValueError:
            messagebox.showerror("Input Tidak Valid", "Jumlah dan Harga harus angka positif.", parent=self)
            return
        
        app_data = self._load_data_from_db()
        app_data['shopping_list'].append({
            "item": item,
            "quantity": qty,
            "price": price,
            "status": "Belum di beli"
        })
        self._save_data_to_db(app_data)
        self._load_data_from_db_and_update_tree() # Refresh UI

        for entry in (self.item_entry, self.qty_entry, self.price_entry): entry.delete(0, END)
        self.item_entry.focus_set()

    def toggle_status(self, event):
        if self.tree.identify_region(event.x, event.y) != "cell": return
        selected_item_id = self.tree.focus()
        if not selected_item_id: return

        item_name_to_toggle = self.tree.item(selected_item_id, "values")[0]
        app_data = self._load_data_from_db()
        for item in app_data['shopping_list']:
            if item['item'] == item_name_to_toggle:
                item['status'] = "Di beli" if item['status'] == "Belum di beli" else "Belum di beli"
                break
        self._save_data_to_db(app_data)
        self._load_data_from_db_and_update_tree() # Refresh UI


    # Override the default get_data from controller to ensure it saves to DB
    def get_data(self):
        return self._load_data_from_db().get("shopping_list", [])

    # Ensure that when the page is shown, it loads the latest data
    def on_page_show(self):
        self._load_data_from_db_and_update_tree()