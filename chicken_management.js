const API_BASE_URL = '';
let allChickenItemsHistory = []; // Variabel untuk menyimpan riwayat item ayam

document.addEventListener('DOMContentLoaded', () => {
    initChickenManagement();
    showChickenPage('chicken-list-page');
});

function initChickenManagement() {
    const chickenForm = document.getElementById('add-chicken-data-form');
    const itemNameInput = document.getElementById('chicken-item-name');
    const suggestionsContainer = document.getElementById('chicken-item-suggestions');

    if (chickenForm) {
        chickenForm.addEventListener('submit', addChickenData);
    }
    if (itemNameInput) {
        itemNameInput.addEventListener('input', showChickenItemSuggestions);
        itemNameInput.addEventListener('blur', () => {
            // Beri jeda agar event mousedown pada saran bisa berjalan
            setTimeout(() => { suggestionsContainer.innerHTML = ''; }, 200);
        });
    }
    loadChickenData();
}

async function loadChickenData() {
    try {
        const response = await fetch(`${API_BASE_URL}/data`); // Perbaikan: Ambil semua data untuk mendapatkan riwayat
        if (!response.ok) throw new Error('Gagal memuat data.');
        const data = await response.json();
        
        allChickenItemsHistory = Object.values(data.chicken_item_history || {});

        renderChickenDataTable(data.chicken_data || []); // Kirim data yang benar ke fungsi render
    } catch (error) {
        console.error('Error loading chicken data:', error);
        Swal.fire({
            icon: 'error', title: 'Oops...', text: error.message,
            background: '#34495e', color: '#f8f9fa'
        });
    }
}

function renderChickenDataTable(data) {
    const tableBody = document.getElementById('chicken-data-table-body');
    tableBody.innerHTML = ''; // Kosongkan tabel
    let grandTotal = 0;

    if (!data || data.length === 0) {
        tableBody.innerHTML = '<tr><td colspan="7" class="text-center">Belum ada data.</td></tr>';
    } else {
        data.forEach(record => {
            const row = tableBody.insertRow();
            const total = record.quantity * record.price;
            
            const typeClass = record.type === 'Pemasukan' ? 'text-success' : 'text-danger';
            const typeSymbol = record.type === 'Pemasukan' ? '+' : '-';
            grandTotal += (record.type === 'Pemasukan' ? total : -total);

            row.innerHTML = `
                <td class="editable" onclick="makeChickenCellEditable(this, ${record.id}, 'item')">${record.item}</td>
                <td class="${typeClass}" style="font-weight: bold;">${record.type}</td>
                <td class="editable" onclick="makeChickenCellEditable(this, ${record.id}, 'quantity')">${record.quantity}</td>
                <td class="editable" onclick="makeChickenCellEditable(this, ${record.id}, 'price')">Rp ${record.price.toLocaleString('id-ID')}</td>
                <td class="${typeClass}" style="font-weight: bold;">${typeSymbol} Rp ${total.toLocaleString('id-ID')}</td>
                <td>${record.date_added || 'N/A'}</td>
                <td><button class="btn btn-sm btn-danger" onclick="deleteChickenRecord(${record.id}, '${record.item}')"><i class="fas fa-trash"></i></button></td>
            `;
        });
    }
    const totalClass = grandTotal >= 0 ? 'text-success' : 'text-danger';
    document.getElementById('chicken-data-total').innerHTML = `Total Laba/Rugi: <span class="${totalClass}" style="font-weight: bold;">Rp ${grandTotal.toLocaleString('id-ID')}</span>`;
}

async function addChickenData(event) {
    event.preventDefault();
    const itemInput = document.getElementById('chicken-item-name');
    const quantityInput = document.getElementById('chicken-item-quantity');
    const priceInput = document.getElementById('chicken-item-price');
    const type = document.querySelector('input[name="chickenRecordType"]:checked').value;

    const item = itemInput.value;
    const quantity = quantityInput.value;
    const price = priceInput.value;

    if (!item || !quantity || !price || !type) {
        Swal.fire({ icon: 'warning', title: 'Input Tidak Lengkap', text: 'Semua kolom harus diisi.', background: '#34495e', color: '#f8f9fa' });
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/chicken_data/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ item, quantity: parseInt(quantity), price: parseFloat(price), type })
        });
        const result = await response.json();
        if (response.ok) {
            itemInput.value = '';
            quantityInput.value = '';
            priceInput.value = '';
            loadChickenData();
        } else {
            throw new Error(result.error);
        }
    } catch (error) {
        Swal.fire({ icon: 'error', title: 'Gagal Menyimpan', text: error.message, background: '#34495e', color: '#f8f9fa' });
    }
}

async function deleteChickenRecord(recordId, itemName) {
    const result = await Swal.fire({
        title: 'Anda yakin?', text: `Hapus data "${itemName}"?`, icon: 'warning',
        showCancelButton: true, confirmButtonColor: '#d33', cancelButtonColor: '#3085d6',
        confirmButtonText: 'Ya, hapus!', cancelButtonText: 'Batal',
        background: '#34495e', color: '#f8f9fa'
    });
    if (!result.isConfirmed) return;

    try {
        const response = await fetch(`${API_BASE_URL}/chicken_data/delete/${recordId}`, { method: 'DELETE' });
        if (response.ok) {
            loadChickenData();
        } else {
            const errorData = await response.json();
            throw new Error(errorData.error);
        }
    } catch (error) {
        Swal.fire({ icon: 'error', title: 'Gagal Menghapus', text: error.message, background: '#34495e', color: '#f8f9fa' });
    }
}

function makeChickenCellEditable(cell, recordId, field) {
    if (cell.querySelector('input')) return;

    const originalValue = cell.textContent.replace('Rp ', '').replace(/\./g, '').replace(/,/g, '.');
    cell.innerHTML = `<input type="text" value="${originalValue}" class="form-control form-control-sm">`;
    
    const input = cell.querySelector('input');
    input.focus();
    input.select();

    const saveChanges = async () => {
        const newValue = input.value;
        if (newValue === originalValue) {
            loadChickenData();
            return;
        }

        try {
            const payload = { [field]: newValue };
            const response = await fetch(`${API_BASE_URL}/chicken_data/update/${recordId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (!response.ok) {
                const errorResult = await response.json();
                throw new Error(errorResult.error || 'Gagal memperbarui data.');
            }
            loadChickenData();
        } catch (error) {
            Swal.fire({ icon: 'error', title: 'Gagal Memperbarui', text: error.message, background: '#34495e', color: '#f8f9fa' });
            loadChickenData();
        }
    };

    input.addEventListener('blur', saveChanges);
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') input.blur();
    });
}

async function displayChickenMonthlyRecap() {
    try {
        const response = await fetch(`${API_BASE_URL}/data`);
        if (!response.ok) throw new Error('Gagal mengambil data rekap.');
        const data = await response.json();
        const recapData = data.chicken_monthly_recap || {};
        const recapContainer = document.getElementById('chicken-recap-container');
        recapContainer.innerHTML = '';

        const sortedMonths = Object.keys(recapData).sort().reverse();

        if (sortedMonths.length === 0) {
            recapContainer.innerHTML = '<p class="text-center">Belum ada data yang diarsipkan.</p>';
            return;
        }

        let grandTotalLabaRugi = 0;
        sortedMonths.forEach(month => {
            grandTotalLabaRugi += recapData[month].laba_rugi;
        });
        const grandTotalClass = grandTotalLabaRugi >= 0 ? 'text-success' : 'text-danger';
        recapContainer.innerHTML += `<h4 class="total-display" style="text-align: center; margin-bottom: 20px;">Total Laba/Rugi Keseluruhan: <span class="${grandTotalClass}">Rp ${grandTotalLabaRugi.toLocaleString('id-ID')}</span></h4>`;

        sortedMonths.forEach(month => {
            const monthData = recapData[month];
            const monthDiv = document.createElement('div');
            const labaRugiClass = monthData.laba_rugi >= 0 ? 'text-success' : 'text-danger';
            
            const header = document.createElement('div');
            header.className = 'recap-month-header';
            header.innerHTML = `
                <span>${month}</span>
                <span class="${labaRugiClass}" style="font-weight:bold;">Laba/Rugi: Rp ${monthData.laba_rugi.toLocaleString('id-ID')}</span>
            `;
            
            const tableContainer = document.createElement('div');
            tableContainer.className = 'hidden'; // Sembunyikan detail secara default

            // Buat tabel detail untuk setiap bulan
            let tableHTML = `
                <div class="p-2 mt-1" style="background-color: #4a6280; border-radius: 4px;">
                    <p class="mb-1">
                        <strong>Total Pemasukan:</strong> 
                        <span class="text-success">Rp ${monthData.total_pemasukan.toLocaleString('id-ID')}</span>
                    </p>
                    <p class="mb-0">
                        <strong>Total Pengeluaran:</strong> 
                        <span class="text-danger">Rp ${monthData.total_pengeluaran.toLocaleString('id-ID')}</span>
                    </p>
                </div>
                <table class="table table-sm table-dark mt-2">
                    <thead><tr><th>Item</th><th>Jenis</th><th>Jumlah</th><th>Harga</th><th>Total</th><th>Tanggal</th><th>Aksi</th></tr></thead>
                    <tbody>
            `;
            monthData.items.forEach(item => {
                const typeClass = item.type === 'Pemasukan' ? 'text-success' : 'text-danger';
                tableHTML += `
                    <tr>
                        <td>${item.item}</td>
                        <td class="${typeClass}">${item.type}</td>
                        <td>${item.quantity}</td>
                        <td>Rp ${item.price.toLocaleString('id-ID')}</td>
                        <td>${item.date_added}</td>
                        <td><button class="btn btn-sm btn-danger py-0 px-1" onclick="deleteArchivedRecord('${month}', ${item.id}, '${item.item}')"><i class="fas fa-trash"></i></button></td>
                    </tr>`;
            });
            tableHTML += '</tbody></table>';
            tableContainer.innerHTML = tableHTML;
            
            header.onclick = () => tableContainer.classList.toggle('hidden');

            monthDiv.appendChild(header);
            monthDiv.appendChild(tableContainer);
            recapContainer.appendChild(monthDiv);
        });

    } catch (error) {
        console.error('Error displaying recap:', error);
        Swal.fire({ icon: 'error', title: 'Gagal Menampilkan Rekap', text: error.message, background: '#34495e', color: '#f8f9fa' });
    }
}

async function archiveChickenData() {
    const confirmResult = await Swal.fire({ title: 'Anda yakin?', text: 'Ini akan mengarsipkan semua data saat ini dan mengosongkan daftar.', icon: 'warning', showCancelButton: true, confirmButtonText: 'Ya, arsipkan!', cancelButtonText: 'Batal', background: '#34495e', color: '#f8f9fa' });
    if (!confirmResult.isConfirmed) return;
    try {
        const response = await fetch(`${API_BASE_URL}/chicken_data/archive`, { method: 'POST' });
        const result = await response.json();
        Swal.fire({ icon: response.ok ? 'success' : 'error', title: response.ok ? 'Berhasil' : 'Gagal', text: result.message || result.error, background: '#34495e', color: '#f8f9fa' });
        displayChickenMonthlyRecap(); // Refresh tampilan rekap
        loadChickenData(); // Refresh daftar utama (seharusnya sudah kosong)
    } catch (error) {
        console.error('Error archiving data:', error);
        Swal.fire({ icon: 'error', title: 'Gagal Mengarsipkan', text: 'Terjadi kesalahan jaringan.', background: '#34495e', color: '#f8f9fa' });
    }
}

async function deleteArchivedRecord(monthKey, recordId, itemName) {
    const confirmResult = await Swal.fire({
        title: 'Hapus dari Arsip?',
        text: `Anda yakin ingin menghapus item "${itemName}" dari arsip bulan ${monthKey}?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        confirmButtonText: 'Ya, hapus!',
        cancelButtonText: 'Batal',
        background: '#34495e', color: '#f8f9fa'
    });
    if (!confirmResult.isConfirmed) return;

    try {
        const response = await fetch(`${API_BASE_URL}/chicken_data/archive/delete/${monthKey}/${recordId}`, { method: 'DELETE' });
        if (!response.ok) throw new Error('Gagal menghapus item dari arsip.');
        displayChickenMonthlyRecap(); // Refresh tampilan rekap setelah berhasil
    } catch (error) {
        Swal.fire({ icon: 'error', title: 'Gagal', text: error.message, background: '#34495e', color: '#f8f9fa' });
    }
}

function showChickenItemSuggestions() {
    const input = document.getElementById('chicken-item-name');
    const suggestionsContainer = document.getElementById('chicken-item-suggestions');
    const term = input.value.toLowerCase();
    suggestionsContainer.innerHTML = '';

    if (term.length === 0) {
        return;
    }

    const filteredItems = allChickenItemsHistory.filter(item => 
        item.item.toLowerCase().includes(term)
    );

    filteredItems.forEach(item => {
        const div = document.createElement('div');
        div.className = 'suggestion-item';

        const textSpan = document.createElement('span');
        textSpan.textContent = `${item.item} (Qty: ${item.quantity}, Harga: Rp ${item.price.toLocaleString('id-ID')})`;

        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'delete-suggestion-btn';
        deleteBtn.innerHTML = '<i class="fas fa-trash-alt"></i>';
        
        deleteBtn.onmousedown = (event) => {
            event.stopPropagation();
            // Fungsi untuk menghapus dari riwayat bisa ditambahkan di sini jika perlu
            // Untuk saat ini, kita hanya akan menghapus dari daftar utama
            deleteChickenRecord(item.id, item.item);
            suggestionsContainer.innerHTML = '';
        };

        textSpan.onmousedown = () => {
            document.getElementById('chicken-item-name').value = item.item;
            document.getElementById('chicken-item-quantity').value = item.quantity;
            document.getElementById('chicken-item-price').value = item.price;
            // Pilih radio button yang sesuai
            const typeRadio = document.querySelector(`input[name="chickenRecordType"][value="${item.type}"]`);
            if (typeRadio) typeRadio.checked = true;
            suggestionsContainer.innerHTML = '';
        };
        div.appendChild(textSpan);
        // div.appendChild(deleteBtn); // Tombol hapus bisa diaktifkan jika perlu
        suggestionsContainer.appendChild(div);
    });
}