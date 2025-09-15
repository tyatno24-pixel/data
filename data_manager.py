import json
import os

# Dapatkan direktori tempat file ini (data_manager.py) berada
project_dir = os.path.dirname(os.path.abspath(__file__))

# Buat path absolut ke file database.json di dalam direktori proyek
DB_FILE = os.path.join(project_dir, "database.json")

# Helper for salary data
work_states = ["Libur", "Setengah Hari", "1 Hari Full"]
state_multipliers = {"Libur": 0, "Setengah Hari": 0.5, "1 Hari Full": 1}

def load_app_data():
    if not os.path.exists(DB_FILE):
        return {"theme": "superhero", "shopping_list": [], "salary_data": {"employees": [], "all_time": {}}, "font": "Arial"}
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
            return data
    except (json.JSONDecodeError, FileNotFoundError):
        # Handle corrupted or missing file, return default data
        return {"theme": "superhero", "shopping_list": [], "salary_data": {"employees": [], "all_time": {}}, "font": "Arial"}

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
    app_data['shopping_list'].append({
        "item": item_name,
        "quantity": quantity,
        "price": price,
        "status": "Belum di beli"
    })
    save_app_data(app_data)
    return True, app_data['shopping_list']

def delete_shopping_item_from_data(item_name):
    app_data = load_app_data()
    initial_len = len(app_data['shopping_list'])
    app_data['shopping_list'] = [item for item in app_data['shopping_list'] if item['item'] != item_name]
    
    if len(app_data['shopping_list']) == initial_len:
        return False, "Item tidak ditemukan"

    save_app_data(app_data)
    return True, app_data['shopping_list']

def toggle_shopping_item_status_in_data(item_name):
    app_data = load_app_data()
    found = False
    for item in app_data['shopping_list']:
        if item['item'] == item_name:
            item['status'] = "Di beli" if item['status'] == "Belum di beli" else "Belum di beli"
            found = True
            break
    
    if not found:
        return False, "Item tidak ditemukan"

    save_app_data(app_data)
    return True, app_data['shopping_list']
