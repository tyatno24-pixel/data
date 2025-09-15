// Salary Tracker Functions
const workStates = ["Libur", "Setengah Hari", "1 Hari Full"];
const stateMultipliers = {"Libur": 0, "Setengah Hari": 0.5, "1 Hari Full": 1};

async function loadSalaryData(onlyOverall = false) {
    try {
        const response = await fetch(`${API_BASE_URL}/salary_data`);
        const data = await response.json();
        if (!onlyOverall) {
            renderEmployeeTable(data.employees);
            updateGrandTotalWeeklySalary(data.employees);
        }
        renderOverallSalaryReport(data.all_time);
    } catch (error) {
        console.error('Error loading salary data:', error);
        alert('Gagal memuat data gaji.');
    }
}

function renderEmployeeTable(employees) {
    const tableBody = document.getElementById('employeeTableBody');
    tableBody.innerHTML = ''; // Bersihkan baris yang ada

    if (employees.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="11" class="text-center">Belum ada karyawan terdaftar.</td></tr>';
        return;
    }

    employees.forEach(employee => {
        const row = tableBody.insertRow();
        row.insertCell().textContent = employee.name;
        row.insertCell().textContent = parseFloat(employee.daily_salary).toLocaleString('id-ID', { style: 'currency', currency: 'IDR' });

        const workStates = ["Libur", "Setengah Hari", "1 Hari Full"];

        employee.days.forEach((dayStatus, index) => {
            const cell = row.insertCell();
            const select = document.createElement('select');
            select.className = 'form-select form-select-sm day-select';
            workStates.forEach(state => {
                const option = document.createElement('option');
                option.value = state;
                option.textContent = state;
                if (state === dayStatus) {
                    option.selected = true;
                }
                select.appendChild(option);
            });
            select.addEventListener('change', (event) => updateEmployeeDay(employee.name, index, event.target.value));
            cell.appendChild(select);
        });

        const weeklyTotalCell = row.insertCell();
        weeklyTotalCell.className = 'total-salary';
        weeklyTotalCell.textContent = parseFloat(employee.weekly_total).toLocaleString('id-ID', { style: 'currency', currency: 'IDR' });

        const actionsCell = row.insertCell();
        const deleteButton = document.createElement('button');
        deleteButton.className = 'btn btn-danger btn-sm';
        deleteButton.textContent = 'Hapus';
        deleteButton.addEventListener('click', () => deleteEmployee(employee.name));
        actionsCell.appendChild(deleteButton);
    });
}

function updateGrandTotalWeeklySalary(employees) {
    const grandTotalDiv = document.getElementById('grandTotalWeeklySalary');
    let total = 0;
    employees.forEach(employee => {
        total += employee.weekly_total;
    });
    grandTotalDiv.textContent = `Total Gaji Mingguan: ${total.toLocaleString('id-ID', { style: 'currency', currency: 'IDR' })}`;
}

function renderOverallSalaryReport(allTimeData) {
    const overallSalaryTableBody = document.getElementById('overallSalaryTableBody');
    overallSalaryTableBody.innerHTML = ''; // Clear existing rows

    if (Object.keys(allTimeData).length === 0) {
        overallSalaryTableBody.innerHTML = '<tr><td colspan="2" class="text-center">Belum ada data gaji keseluruhan.</td></tr>';
        return;
    }

    for (const name in allTimeData) {
        const row = overallSalaryTableBody.insertRow();
        row.insertCell().textContent = name;
        row.insertCell().textContent = parseFloat(allTimeData[name]).toLocaleString('id-ID', { style: 'currency', currency: 'IDR' });
    }
}

async function addEmployee(event) {
    event.preventDefault();
    const name = document.getElementById('employeeName').value;
    const dailySalary = document.getElementById('dailySalary').value;

    try {
        const response = await fetch(`${API_BASE_URL}/salary_data/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, daily_salary: parseFloat(dailySalary) })
        });
        const result = await response.json();
        if (response.ok) {
            alert(result.message);
            document.getElementById('addEmployeeForm').reset();
            loadSalaryData(); // Muat ulang data untuk memperbarui tabel
        } else {
            alert(`Error: ${result.error}`);
        }
    } catch (error) {
        console.error('Error saat menambahkan karyawan:', error);
        alert('Gagal menambahkan karyawan.');
    }
}

async function updateEmployeeDay(name, dayIndex, newStatus) {
    try {
        const response = await fetch(`${API_BASE_URL}/salary_data/update_day`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, day_index: dayIndex, new_status: newStatus })
        });
        const result = await response.json();
        if (response.ok) {
            loadSalaryData(); // Muat ulang data untuk memperbarui tabel dan total mingguan
        } else {
            alert(`Error: ${result.error}`);
        }
    } catch (error) {
        console.error('Error saat memperbarui hari karyawan:', error);
        alert('Gagal memperbarui status hari karyawan.');
    }
}

async function submitWeeklySalary() {
    if (!confirm('Apakah Anda yakin ingin mengirim gaji mingguan dan mereset status hari kerja?')) {
        return;
    }
    try {
        const response = await fetch(`${API_BASE_URL}/salary_data/submit_weekly`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        const result = await response.json();
        if (response.ok) {
            alert(result.message);
            loadSalaryData(); // Muat ulang data untuk memperbarui tabel dan total keseluruhan
        } else {
            alert(`Error: ${result.error}`);
        }
    } catch (error) {
        console.error('Error saat mengirim gaji mingguan:', error);
        alert('Gagal mengirim gaji mingguan.');
    }
}

async function deleteEmployee(name) {
    if (!confirm(`Apakah Anda yakin ingin menghapus karyawan ${name}?`)) {
        return;
    }
    try {
        const response = await fetch(`${API_BASE_URL}/salary_data/delete/${name}`, {
            method: 'DELETE'
        });
        const result = await response.json();
        if (response.ok) {
            alert(result.message);
            loadSalaryData(); // Muat ulang data untuk memperbarui tabel
        } else {
            alert(`Error: ${result.error}`);
        }
    } catch (error) {
        console.error('Error saat menghapus karyawan:', error);
        alert('Gagal menghapus karyawan.');
    }
}

function initSalaryTracker() {
    document.getElementById('addEmployeeForm').addEventListener('submit', addEmployee);
    document.getElementById('submitWeeklySalary').addEventListener('click', submitWeeklySalary);
    document.getElementById('showOverallSalaryReport').addEventListener('click', () => {
        loadSalaryData(true);
    });
    loadSalaryData();
}