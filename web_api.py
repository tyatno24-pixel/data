from flask import Flask, jsonify, send_from_directory, request
import threading
import time
import os
import random
import json
from data_manager import (
    DB_FILE,
    load_app_data, save_app_data, get_chicken_data, add_chicken_record, delete_chicken_record, update_chicken_record, archive_chicken_data, delete_archived_chicken_record, get_mushroom_data, add_mushroom_record, delete_mushroom_record, update_mushroom_record, archive_mushroom_data, delete_archived_mushroom_record, backup_database,
    get_salary_data, add_employee_to_data, update_employee_day_in_data, toggle_delivery_status_in_data, update_shopping_item_in_data, archive_shopping_list_data,
    submit_weekly_salary_to_data, delete_employee_from_data,
    add_shopping_item_to_data, delete_shopping_item_from_data, toggle_shopping_item_status_in_data,
    work_states # Keep work_states for validation in API
)

# Dapatkan path absolut ke direktori proyek
project_dir = os.path.dirname(os.path.abspath(__file__))

# Konfigurasi Flask untuk menggunakan direktori proyek sebagai folder statis
app = Flask(__name__, static_folder=project_dir, static_url_path='')

# Pastikan file database ada saat aplikasi pertama kali dijalankan
if not os.path.exists(DB_FILE):
    print("File database.json tidak ditemukan, membuat file baru...")
    initial_data = {"theme": "superhero", "font": "Arial", "shopping_list": [], "salary_data": {"employees": [], "all_time": {}}, "chicken_data": [], "mushroom_data": []}
    save_app_data(initial_data)


@app.route('/data', methods=['GET'])
def get_data():
    app_data = load_app_data()
    return jsonify(app_data)

@app.route('/shopping_list/add', methods=['POST'])
def add_shopping_item():
    data = request.get_json()
    item_name = data.get('item')
    quantity = data.get('quantity')
    price = data.get('price')

    if not item_name or not quantity or price is None:
        return jsonify({"error": "Item, quantity, dan price diperlukan"}), 400

    success, result = add_shopping_item_to_data(item_name, quantity, price)
    if success:
        return jsonify({"message": "Item berhasil ditambahkan", "shopping_list": result}), 201
    return jsonify({"error": result}), 500

@app.route('/shopping_list/delete/<float:item_id>', methods=['DELETE'])
def delete_shopping_item(item_id):
    success, result = delete_shopping_item_from_data(item_id)
    if success:
        return jsonify({"message": "Item berhasil dihapus", "shopping_list": result}), 200
    return jsonify({"error": result}), 404

@app.route('/shopping_list/toggle_status/<float:item_id>', methods=['PUT'])
def toggle_shopping_item_status(item_id):
    success, result = toggle_shopping_item_status_in_data(item_id)
    if success:
        return jsonify({"message": "Status item berhasil diubah", "shopping_list": result}), 200
    return jsonify({"error": result}), 404

@app.route('/shopping_list/toggle_delivery/<float:item_id>', methods=['PUT'])
def toggle_delivery_status(item_id):
    success, result = toggle_delivery_status_in_data(item_id)
    if success:
        return jsonify({"message": "Status pengiriman berhasil diubah", "shopping_list": result}), 200
    return jsonify({"error": result}), 404

@app.route('/shopping_list/update/<float:item_id>', methods=['PUT'])
def update_shopping_item(item_id):
    data = request.get_json()
    success, result = update_shopping_item_in_data(item_id, data)
    if success:
        return jsonify({"message": "Item berhasil diperbarui", "shopping_list": result}), 200
    return jsonify({"error": result}), 404

@app.route('/shopping_list/archive', methods=['POST'])
def archive_shopping_list():
    success, message = archive_shopping_list_data()
    if success:
        return jsonify({"message": message}), 200
    return jsonify({"error": message}), 400

@app.route('/backup', methods=['POST'])
def backup_data_api():
    success, message = backup_database()
    if success:
        return jsonify({"message": message}), 200
    return jsonify({"error": message}), 500

# Chicken Management Endpoints
@app.route('/chicken_data', methods=['GET'])
def get_chicken_data_api():
    data = get_chicken_data()
    return jsonify(data)

@app.route('/chicken_data/add', methods=['POST'])
def add_chicken_record_api():
    data = request.get_json()
    success, result = add_chicken_record(data.get('item'), data.get('quantity'), data.get('price'), data.get('type'))
    if success:
        return jsonify({"message": "Data berhasil ditambahkan", "data": result}), 201
    return jsonify({"error": "Gagal menyimpan data"}), 500

@app.route('/chicken_data/delete/<float:record_id>', methods=['DELETE'])
def delete_chicken_record_api(record_id):
    success, result = delete_chicken_record(record_id)
    if success:
        return jsonify({"message": "Data berhasil dihapus", "data": result}), 200
    return jsonify({"error": "Gagal menghapus data"}), 500

@app.route('/chicken_data/update/<float:record_id>', methods=['PUT'])
def update_chicken_record_api(record_id):
    data = request.get_json()
    success, result = update_chicken_record(record_id, data)
    if success:
        return jsonify({"message": "Data berhasil diperbarui", "data": result}), 200
    return jsonify({"error": "Gagal memperbarui data"}), 404

@app.route('/chicken_data/archive', methods=['POST'])
def archive_chicken_data_api():
    success, message = archive_chicken_data()
    if success:
        return jsonify({"message": message}), 200
    return jsonify({"error": message}), 400

@app.route('/chicken_data/archive/delete/<string:month_key>/<float:record_id>', methods=['DELETE'])
def delete_archived_chicken_record_api(month_key, record_id):
    success, message = delete_archived_chicken_record(month_key, record_id)
    if success:
        return jsonify({"message": message}), 200
    return jsonify({"error": message}), 404

# Salary Tracker Endpoints
@app.route('/salary_data', methods=['GET'])
def get_salary_data_api():
    salary_data = get_salary_data()
    return jsonify(salary_data)

@app.route('/salary_data/add', methods=['POST'])
def add_employee_api():
    data = request.get_json()
    name = data.get('name')
    daily_salary = data.get('daily_salary')

    if not name or daily_salary is None:
        return jsonify({"error": "Nama dan Gaji per Hari diperlukan"}), 400
    try:
        daily_salary = float(daily_salary)
        if daily_salary < 0: raise ValueError
    except ValueError:
        return jsonify({"error": "Gaji per Hari harus berupa angka positif"}), 400

    success, result = add_employee_to_data(name, daily_salary)
    if success:
        return jsonify({"message": "Karyawan berhasil ditambahkan", "employee": result}), 201
    return jsonify({"error": result}), 409

@app.route('/salary_data/update_day', methods=['PUT'])
def update_employee_day_api():
    data = request.get_json()
    name = data.get('name')
    day_index = data.get('day_index')
    new_status = data.get('new_status')

    if not all([name, day_index is not None, new_status]):
        return jsonify({"error": "Nama, indeks hari, dan status baru diperlukan"}), 400
    if not (0 <= day_index < 7) or new_status not in work_states:
        return jsonify({"error": "Indeks hari atau status tidak valid"}), 400

    success, result = update_employee_day_in_data(name, day_index, new_status)
    if success:
        return jsonify({"message": "Status hari karyawan berhasil diperbarui", "employee": result}), 200
    return jsonify({"error": result}), 404

@app.route('/salary_data/submit_weekly', methods=['POST'])
def submit_weekly_salary_data_api():
    success, result = submit_weekly_salary_to_data()
    if success:
        return jsonify({"message": "Data gaji mingguan berhasil dimasukan dan direset.", "salary_data": result}), 200
    return jsonify({"error": result}), 500

@app.route('/salary_data/delete/<string:employee_name>', methods=['DELETE'])
def delete_employee_api(employee_name):
    success, result = delete_employee_from_data(employee_name)
    if success:
        return jsonify({"message": "Karyawan berhasil dihapus", "salary_data": result}), 200
    return jsonify({"error": result}), 404

@app.route('/')
def serve_index():
    return app.send_static_file('index.html')

@app.route('/index.html')
def serve_index_html():
    return app.send_static_file('index.html')

@app.route('/shopping_list')
def serve_shopping_list():
    return app.send_static_file('shopping_list.html')

@app.route('/chicken_management')
def serve_chicken_management():
    return app.send_static_file('chicken_management.html')

@app.route('/mushroom_management')
def serve_mushroom_management():
    return app.send_static_file('mushroom_management.html')

@app.route('/salary_tracker_web')
def serve_salary_tracker_web():
    return app.send_static_file('salary_tracker_web.html')