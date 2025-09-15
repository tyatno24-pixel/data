from flask import Flask, jsonify, send_from_directory, request
import threading
import time
from data_manager import (
    load_app_data, save_app_data,
    get_salary_data, add_employee_to_data, update_employee_day_in_data,
    submit_weekly_salary_to_data, delete_employee_from_data,
    add_shopping_item_to_data, delete_shopping_item_from_data, toggle_shopping_item_status_in_data,
    work_states # Keep work_states for validation in API
)

app = Flask(__name__)

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
    else:
        return jsonify({"error": result}), 500 # Should not happen with current logic

@app.route('/shopping_list/delete/<string:item_name>', methods=['DELETE'])
def delete_shopping_item(item_name):
    success, result = delete_shopping_item_from_data(item_name)
    if success:
        return jsonify({"message": "Item berhasil dihapus", "shopping_list": result}), 200
    else:
        return jsonify({"error": result}), 404

@app.route('/shopping_list/toggle_status/<string:item_name>', methods=['PUT'])
def toggle_shopping_item_status(item_name):
    success, result = toggle_shopping_item_status_in_data(item_name)
    if success:
        return jsonify({"message": "Status item berhasil diubah", "shopping_list": result}), 200
    else:
        return jsonify({"error": result}), 404

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
    else:
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
    else:
        return jsonify({"error": result}), 404

@app.route('/salary_data/submit_weekly', methods=['POST'])
def submit_weekly_salary_data_api():
    success, result = submit_weekly_salary_to_data()
    if success:
        return jsonify({"message": "Data gaji mingguan berhasil dimasukan dan direset.", "salary_data": result}), 200
    else:
        return jsonify({"error": result}), 500 # Should not happen with current logic

@app.route('/salary_data/delete/<string:employee_name>', methods=['DELETE'])
def delete_employee_api(employee_name):
    success, result = delete_employee_from_data(employee_name)
    if success:
        return jsonify({"message": "Karyawan berhasil dihapus", "salary_data": result}), 200
    else:
        return jsonify({"error": result}), 404

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/index.html')
def serve_index_html():
    return send_from_directory('.', 'index.html')

@app.route('/salary_tracker_web')
def serve_salary_tracker_web():
    return send_from_directory('.', 'salary_tracker_web.html')

def run_flask_app():
    app.run(host='0.0.0.0', port=5001, debug=False) 

if __name__ == '__main__':
    run_flask_app()