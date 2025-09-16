import json
import os
from datetime import datetime

# Dapatkan direktori tempat file ini (data_manager.py) berada
project_dir = os.path.dirname(os.path.abspath(__file__))

# Buat path absolut ke file database.json di dalam direktori proyek
DB_FILE = os.path.join(project_dir, "database.json")

# Helper for salary data
work_states = ["Libur", "Setengah Hari", "1 Hari Full"]
state_multipliers = {"Libur": 0, "Setengah Hari": 0.5, "1 Hari Full": 1}

def load_app_data():
    if not os.path.exists(DB_FILE):
        return {"theme": "superhero", "shopping_list": [], "salary_data": {"employees": [], "all_time": {}}, "chicken_data": [], "mushroom_data": [], "font": "Arial"}
    try:
        with open(DB_FILE, 'r') as f:
            data = json.load(f)
            # Ensure salary_data structure exists
            if "salary_data" not in data:
                data["salary_data"] = {"employees": [], "all_time": {}}
            if "employees" not in data["salary_data"]:
                data["salary_data"]["employees"] = []
            if "all_time" not in data["salary_data"]:
                data["salary_data"]["all_time"] = {}
            if "chicken_data" not in data:
                data["chicken_data"] = []
            if "mushroom_data" not in data:
                data["mushroom_data"] = []
            return data
    except (json.JSONDecodeError, FileNotFoundError):
        # Handle corrupted or missing file, return default data
        return {"theme": "superhero", "shopping_list": [], "salary_data": {"employees": [], "all_time": {}}, "chicken_data": [], "mushroom_data": [], "font": "Arial"}

def save_app_data(data):
    with open(DB_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def find_employee_index(employees, name):
    for i, emp in enumerate(employees):
        if emp['name'] == name:
            return i
    return -1

def calculate_weekly_total(daily_salary, days):
    total_multiplier = sum(state_multipliers.get(state, 0) for state in days)
    return daily_salary * total_multiplier

def get_salary_data():
    app_data = load_app_data()
    return app_data.get('salary_data', {"employees": [], "all_time": {}})

def add_employee_to_data(name, daily_salary):
    app_data = load_app_data()
    employees = app_data['salary_data']['employees']
    if find_employee_index(employees, name) != -1:
        return False, "Karyawan dengan nama tersebut sudah ada"

    new_employee = {
        "name": name,
        "daily_salary": daily_salary,
        "days": ["Libur"] * 7,
        "weekly_total": 0.0
    }
    employees.append(new_employee)
    save_app_data(app_data)
    return True, new_employee

def update_employee_day_in_data(name, day_index, new_status):
    app_data = load_app_data()
    employees = app_data['salary_data']['employees']
    emp_idx = find_employee_index(employees, name)

    if emp_idx == -1:
        return False, "Karyawan tidak ditemukan"

    employee = employees[emp_idx]
    employee['days'][day_index] = new_status
    employee['weekly_total'] = calculate_weekly_total(employee['daily_salary'], employee['days'])
    save_app_data(app_data)
    return True, employee

def submit_weekly_salary_to_data():
    app_data = load_app_data()
    employees = app_data['salary_data']['employees']
    all_time_salary = app_data['salary_data']['all_time']

    for employee in employees:
        name = employee['name']
        weekly_total = employee['weekly_total']
        all_time_salary[name] = all_time_salary.get(name, 0) + weekly_total
        # Reset for next week
        employee['days'] = ["Libur"] * 7
        employee['weekly_total'] = 0.0
    
    save_app_data(app_data)
    return True, app_data['salary_data']

def delete_employee_from_data(employee_name):
    app_data = load_app_data()
    employees = app_data['salary_data']['employees']
    initial_len = len(employees)
    app_data['salary_data']['employees'] = [emp for emp in employees if emp['name'] != employee_name]

    if len(app_data['salary_data']['employees']) == initial_len:
        return False, "Karyawan tidak ditemukan"

    if employee_name in app_data['salary_data']['all_time']:
        del app_data['salary_data']['all_time'][employee_name]

    save_app_data(app_data)
    return True, app_data['salary_data']

# Shopping list functions (moved from web_api.py for consistency)
def add_shopping_item_to_data(item_name, quantity, price):
    app_data = load_app_data()
    # Gunakan insert(0, ...) untuk menambahkan item ke paling atas daftar
    app_data['shopping_list'].insert(0, {
        "id": datetime.now().timestamp(), # Tambahkan ID unik berbasis timestamp
        "item": item_name,
        "quantity": quantity,
        "price": price,
        "status": "Belum di beli",
        "date_added": datetime.now().strftime('%Y-%m-%d'),
        "delivery_status": "Belum Sampai" # Tambahkan status barang sampai
    })
    save_app_data(app_data)
    return True, app_data['shopping_list']

def delete_shopping_item_from_data(item_id):
    app_data = load_app_data()
    initial_len = len(app_data['shopping_list'])
    # Hapus item berdasarkan ID unik, bukan nama
    app_data['shopping_list'] = [item for item in app_data['shopping_list'] if item.get('id') != item_id]
    
    if len(app_data['shopping_list']) == initial_len:
        return False, "Item tidak ditemukan"

    save_app_data(app_data)
    return True, app_data['shopping_list']

def toggle_shopping_item_status_in_data(item_id):
    app_data = load_app_data()
    found = False
    for item in app_data['shopping_list']:
        # Perbaikan: Gunakan ID unik untuk menghindari bug pada item dengan nama sama
        if item.get('id') == item_id:
            item['status'] = "Di beli" if item['status'] == "Belum di beli" else "Belum di beli"
            found = True
            break
    
    if not found:
        return False, "Item tidak ditemukan"

    save_app_data(app_data)
    return True, app_data['shopping_list']

def toggle_delivery_status_in_data(item_id):
    app_data = load_app_data()
    found = False
    for item in app_data['shopping_list']:
        if item.get('id') == item_id:
            # Toggle status barang sampai
            current_status = item.get('delivery_status', 'Belum Sampai')
            item['delivery_status'] = "Sudah Sampai" if current_status == "Belum Sampai" else "Belum Sampai"
            found = True
            break
    if not found:
        return False, "Item tidak ditemukan"
    
    save_app_data(app_data)
    return True, app_data['shopping_list']

def update_shopping_item_in_data(item_id, update_data):
    app_data = load_app_data()
    found = False
    for item in app_data['shopping_list']:
        if item.get('id') == item_id:
            # Perbarui field jika ada di data pembaruan
            if 'item' in update_data:
                item['item'] = str(update_data['item'])
            if 'quantity' in update_data:
                item['quantity'] = int(update_data['quantity'])
            if 'price' in update_data:
                item['price'] = float(update_data['price'])
            found = True
            break
    if not found:
        return False, "Item tidak ditemukan"
    save_app_data(app_data)
    return True, app_data['shopping_list']

def archive_shopping_list_data():
    app_data = load_app_data()
    shopping_list = app_data.get('shopping_list', [])
    
    # Pisahkan item yang akan diarsipkan (sudah sampai) dan yang akan disimpan
    items_to_archive = [item for item in shopping_list if item.get('delivery_status') == 'Sudah Sampai']
    items_to_keep = [item for item in shopping_list if item.get('delivery_status') != 'Sudah Sampai']
    
    if not items_to_archive:
        return False, "Tidak ada item yang berstatus 'Sudah Sampai' untuk diarsipkan."
    
    # Inisialisasi rekap bulanan jika belum ada
    if 'monthly_recap' not in app_data:
        app_data['monthly_recap'] = {}
    
    # Inisialisasi riwayat item untuk fitur saran/pencarian
    if 'item_history' not in app_data:
        app_data['item_history'] = {}

    # Kelompokkan item berdasarkan bulan (YYYY-MM)
    items_by_month = {}
    for item in items_to_archive:
        month_key = datetime.strptime(item['date_added'], '%Y-%m-%d').strftime('%Y-%m')
        if month_key not in items_by_month:
            items_by_month[month_key] = []
        items_by_month[month_key].append(item)

        # Simpan item ke riwayat untuk fitur saran, timpa dengan data terbaru jika nama sama
        app_data['item_history'][item['item'].lower()] = item

    # Masukkan data yang dikelompokkan ke dalam rekap
    for month, items in items_by_month.items():
        if month not in app_data['monthly_recap']:
            app_data['monthly_recap'][month] = {'total': 0, 'items': []}
        app_data['monthly_recap'][month]['items'].extend(items)
        app_data['monthly_recap'][month]['total'] += sum(it['quantity'] * it['price'] for it in items)

    # Ganti daftar belanja saat ini dengan item yang belum sampai
    app_data['shopping_list'] = items_to_keep
    save_app_data(app_data)
    return True, "Data berhasil diarsipkan."

# Chicken Management Functions
def get_chicken_data():
    app_data = load_app_data()
    # Urutkan data berdasarkan ID (timestamp), yang terbaru di atas
    return sorted(app_data.get('chicken_data', []), key=lambda x: x.get('id', 0), reverse=True)

def add_chicken_record(item_name, quantity, price, record_type):
    app_data = load_app_data()
    new_record = {
        "id": datetime.now().timestamp(),
        "item": item_name,
        "quantity": quantity,
        "price": price,
        "type": record_type,
        "date_added": datetime.now().strftime('%Y-%m-%d')
    }
    # Simpan ke riwayat untuk fitur saran
    if 'chicken_item_history' not in app_data:
        app_data['chicken_item_history'] = {}
    app_data['chicken_item_history'][item_name.lower()] = new_record

    app_data['chicken_data'].insert(0, new_record)
    save_app_data(app_data)
    return True, get_chicken_data()

def delete_chicken_record(record_id):
    app_data = load_app_data()
    app_data['chicken_data'] = [record for record in app_data['chicken_data'] if record.get('id') != record_id]
    save_app_data(app_data)
    return True, get_chicken_data()

def update_chicken_record(record_id, update_data):
    app_data = load_app_data()
    found = False
    for record in app_data['chicken_data']:
        if record.get('id') == record_id:
            if 'item' in update_data:
                record['item'] = str(update_data['item'])
            if 'quantity' in update_data:
                record['quantity'] = int(update_data['quantity'])
            if 'price' in update_data:
                record['price'] = float(update_data['price'])
            if 'type' in update_data:
                record['type'] = str(update_data['type'])
            found = True
            break
    if not found:
        return False, "Data tidak ditemukan"
    save_app_data(app_data)
    return True, get_chicken_data()

def archive_chicken_data():
    app_data = load_app_data()
    chicken_data_list = app_data.get('chicken_data', [])

    if not chicken_data_list:
        return False, "Tidak ada data untuk diarsipkan."

    # Inisialisasi rekap bulanan jika belum ada
    if 'chicken_monthly_recap' not in app_data:
        app_data['chicken_monthly_recap'] = {}

    # Kelompokkan item berdasarkan bulan (YYYY-MM)
    items_by_month = {}
    for item in chicken_data_list:
        month_key = datetime.strptime(item['date_added'], '%Y-%m-%d').strftime('%Y-%m')
        if month_key not in items_by_month:
            items_by_month[month_key] = []
        items_by_month[month_key].append(item)

    # Masukkan data yang dikelompokkan ke dalam rekap
    for month, items in items_by_month.items():
        if month not in app_data['chicken_monthly_recap']:
            app_data['chicken_monthly_recap'][month] = {'total_pemasukan': 0, 'total_pengeluaran': 0, 'laba_rugi': 0, 'items': []}
        
        pemasukan = sum(it['quantity'] * it['price'] for it in items if it['type'] == 'Pemasukan')
        pengeluaran = sum(it['quantity'] * it['price'] for it in items if it['type'] == 'Pengeluaran')
        
        app_data['chicken_monthly_recap'][month]['items'].extend(items)
        app_data['chicken_monthly_recap'][month]['total_pemasukan'] += pemasukan
        app_data['chicken_monthly_recap'][month]['total_pengeluaran'] += pengeluaran
        app_data['chicken_monthly_recap'][month]['laba_rugi'] += (pemasukan - pengeluaran)

    # Kosongkan daftar data ayam saat ini setelah diarsipkan
    app_data['chicken_data'] = []
    save_app_data(app_data)
    return True, "Data manajemen ayam berhasil diarsipkan."

def delete_archived_chicken_record(month_key, record_id):
    app_data = load_app_data()
    if 'chicken_monthly_recap' not in app_data or month_key not in app_data['chicken_monthly_recap']:
        return False, "Bulan rekap tidak ditemukan."

    month_recap = app_data['chicken_monthly_recap'][month_key]
    initial_len = len(month_recap['items'])
    
    # Hapus item dari daftar
    item_to_delete = next((item for item in month_recap['items'] if item.get('id') == record_id), None)
    if not item_to_delete:
        return False, "Item arsip tidak ditemukan."

    month_recap['items'] = [item for item in month_recap['items'] if item.get('id') != record_id]

    # Hitung ulang total untuk bulan tersebut
    pemasukan = sum(it['quantity'] * it['price'] for it in month_recap['items'] if it['type'] == 'Pemasukan')
    pengeluaran = sum(it['quantity'] * it['price'] for it in month_recap['items'] if it['type'] == 'Pengeluaran')
    month_recap['total_pemasukan'] = pemasukan
    month_recap['total_pengeluaran'] = pengeluaran
    month_recap['laba_rugi'] = pemasukan - pengeluaran

    save_app_data(app_data)
    return True, "Item dari arsip berhasil dihapus."

# Mushroom Management Functions
def get_mushroom_data():
    app_data = load_app_data()
    # Urutkan data berdasarkan ID (timestamp), yang terbaru di atas
    return sorted(app_data.get('mushroom_data', []), key=lambda x: x.get('id', 0), reverse=True)

def add_mushroom_record(item_name, quantity, price, record_type):
    app_data = load_app_data()
    new_record = {
        "id": datetime.now().timestamp(),
        "item": item_name,
        "quantity": quantity,
        "price": price,
        "type": record_type,
        "date_added": datetime.now().strftime('%Y-%m-%d')
    }
    # Simpan ke riwayat untuk fitur saran
    if 'mushroom_item_history' not in app_data:
        app_data['mushroom_item_history'] = {}
    app_data['mushroom_item_history'][item_name.lower()] = new_record

    app_data['mushroom_data'].insert(0, new_record)
    save_app_data(app_data)
    return True, get_mushroom_data()

def delete_mushroom_record(record_id):
    app_data = load_app_data()
    app_data['mushroom_data'] = [record for record in app_data['mushroom_data'] if record.get('id') != record_id]
    save_app_data(app_data)
    return True, get_mushroom_data()

def update_mushroom_record(record_id, update_data):
    app_data = load_app_data()
    found = False
    for record in app_data['mushroom_data']:
        if record.get('id') == record_id:
            if 'item' in update_data:
                record['item'] = str(update_data['item'])
            if 'quantity' in update_data:
                record['quantity'] = int(update_data['quantity'])
            if 'price' in update_data:
                record['price'] = float(update_data['price'])
            if 'type' in update_data:
                record['type'] = str(update_data['type'])
            found = True
            break
    if not found:
        return False, "Data tidak ditemukan"
    save_app_data(app_data)
    return True, get_mushroom_data()

def archive_mushroom_data():
    app_data = load_app_data()
    mushroom_data_list = app_data.get('mushroom_data', [])

    if not mushroom_data_list:
        return False, "Tidak ada data untuk diarsipkan."

    if 'mushroom_monthly_recap' not in app_data:
        app_data['mushroom_monthly_recap'] = {}

    items_by_month = {}
    for item in mushroom_data_list:
        month_key = datetime.strptime(item['date_added'], '%Y-%m-%d').strftime('%Y-%m')
        if month_key not in items_by_month:
            items_by_month[month_key] = []
        items_by_month[month_key].append(item)

    for month, items in items_by_month.items():
        if month not in app_data['mushroom_monthly_recap']:
            app_data['mushroom_monthly_recap'][month] = {'total_pemasukan': 0, 'total_pengeluaran': 0, 'laba_rugi': 0, 'items': []}
        
        pemasukan = sum(it['quantity'] * it['price'] for it in items if it['type'] == 'Pemasukan')
        pengeluaran = sum(it['quantity'] * it['price'] for it in items if it['type'] == 'Pengeluaran')
        
        app_data['mushroom_monthly_recap'][month]['items'].extend(items)
        app_data['mushroom_monthly_recap'][month]['total_pemasukan'] += pemasukan
        app_data['mushroom_monthly_recap'][month]['total_pengeluaran'] += pengeluaran
        app_data['mushroom_monthly_recap'][month]['laba_rugi'] += (pemasukan - pengeluaran)

    app_data['mushroom_data'] = []
    save_app_data(app_data)
    return True, "Data manajemen jamur berhasil diarsipkan."

def delete_archived_mushroom_record(month_key, record_id):
    app_data = load_app_data()
    if 'mushroom_monthly_recap' not in app_data or month_key not in app_data['mushroom_monthly_recap']:
        return False, "Bulan rekap tidak ditemukan."

    month_recap = app_data['mushroom_monthly_recap'][month_key]
    month_recap['items'] = [item for item in month_recap['items'] if item.get('id') != record_id]

    pemasukan = sum(it['quantity'] * it['price'] for it in month_recap['items'] if it['type'] == 'Pemasukan')
    pengeluaran = sum(it['quantity'] * it['price'] for it in month_recap['items'] if it['type'] == 'Pengeluaran')
    month_recap['total_pemasukan'] = pemasukan
    month_recap['total_pengeluaran'] = pengeluaran
    month_recap['laba_rugi'] = pemasukan - pengeluaran

    save_app_data(app_data)
    return True, "Item dari arsip berhasil dihapus."
