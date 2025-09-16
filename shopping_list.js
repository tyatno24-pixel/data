// Shopping List Functions
let allShoppingItems = []; // Variabel untuk menyimpan semua item belanja untuk fitur saran

async function fetchAppData() {
    try {
        const response = await fetch(`${API_BASE_URL}/data`);
        if (!response.ok) {
            throw new Error(`Kesalahan HTTP! status: ${response.status}`);
        }
        const data = await response.json();
        displayAppData(data);
    } catch (error) {
        console.error('Gagal mengambil data:', error);
        document.getElementById('shopping-list-table-body').innerHTML = `<tr><td colspan="6" class="error">Gagal memuat data. Pastikan aplikasi desktop berjalan dan alamat IP sudah benar.</td></tr>`;
        document.getElementById('shopping-list-total').textContent = 'Total Belanjaan: Rp 0.00';
    }
}

function displayAppData(data) {
    const shoppingListTableBody = document.getElementById('shopping-list-table-body');
    
    // Gabungkan item dari daftar saat ini dan riwayat untuk fitur saran
    const currentItems = data.shopping_list || [];
    const historyItems = Object.values(data.item_history || {});
    const combinedSuggestions = {};
    // Prioritaskan item dari riwayat, lalu timpa dengan item dari daftar saat ini jika ada nama yang sama
    historyItems.forEach(item => {
        combinedSuggestions[item.item.toLowerCase()] = item;
    });
    currentItems.forEach(item => {
        combinedSuggestions[item.item.toLowerCase()] = item;
    });
    allShoppingItems = Object.values(combinedSuggestions);

    shoppingListTableBody.innerHTML = ''; // Bersihkan tabel
    let totalBelanja = 0;
    let totalBelanjaUnbought = 0;

    if (data.shopping_list && data.shopping_list.length > 0) {
        data.shopping_list.forEach(item => {
            const row = shoppingListTableBody.insertRow();
            const totalHarga = item.quantity * item.price;
            totalBelanja += totalHarga;

            if (item.status === 'Belum di beli') {
                totalBelanjaUnbought += totalHarga;
            }

            const deliveryIcon = item.delivery_status === 'Sudah Sampai'
                ? '<i class="fas fa-check-circle" style="color: #28a745;"></i>' // Ceklis hijau
                : '<i class="fas fa-times-circle" style="color: #dc3545;"></i>'; // Silang merah

            row.innerHTML = `
                <td class="editable" onclick="makeEditable(this, ${item.id}, 'item')">${item.item}</td>
                <td class="status-${item.status.toLowerCase().replace(/ /g, '-')}" style="cursor: pointer;" onclick="toggleShoppingItemStatus(${item.id})">${item.status}</td>
                <td style="text-align: center; cursor: pointer;" onclick="toggleDeliveryStatus(${item.id})">${deliveryIcon}</td>
                <td class="editable" onclick="makeEditable(this, ${item.id}, 'quantity')">${item.quantity}</td>
                <td class="editable" onclick="makeEditable(this, ${item.id}, 'price')">Rp ${item.price.toLocaleString('id-ID')}</td>
                <td>Rp ${totalHarga.toLocaleString('id-ID')}</td>
                <td>${item.date_added || 'N/A'}</td>
                <td><button class="btn btn-danger" onclick="deleteShoppingItem(${item.id}, '${item.item}')">Hapus</button></td>
            `;
        });
    } else {
        const row = shoppingListTableBody.insertRow();
        const cell = row.insertCell();
        cell.colSpan = 8;
        cell.textContent = 'Daftar belanja kosong.';
        cell.style.textAlign = 'center';
    }
    document.getElementById('shopping-list-total').textContent = `Total Belanjaan: Rp ${totalBelanja.toLocaleString('id-ID')}`;
    document.getElementById('shopping-list-unbought-total').textContent = `Total Belanja Belum Dibeli: Rp ${totalBelanjaUnbought.toLocaleString('id-ID')}`;
}

// Fungsi untuk menambahkan item ke daftar belanja
async function addShoppingItem(event) {
    event.preventDefault(); // Mencegah form submit secara default

    const itemInput = document.getElementById('shopping-item-name');
    const quantityInput = document.getElementById('shopping-item-quantity');
    const priceInput = document.getElementById('shopping-item-price');

    const itemName = itemInput.value;
    const quantity = parseInt(quantityInput.value); // Pastikan kuantitas adalah angka
    const price = parseFloat(priceInput.value); // Pastikan harga adalah angka

    if (!itemName || isNaN(quantity) || quantity <= 0 || isNaN(price) || price < 0) {
        alert('Nama item, kuantitas (angka positif), dan harga (angka non-negatif) diperlukan!');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/shopping_list/add`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ item: itemName, quantity: quantity, price: price }),
        });

        const result = await response.json();

        if (response.ok) {
            // alert(result.message); // Pop-up notifikasi dinonaktifkan untuk alur kerja yang lebih cepat
            itemInput.value = ''; // Bersihkan input
            quantityInput.value = ''; // Bersihkan input
            priceInput.value = ''; // Bersihkan input
            fetchAppData(); // Muat ulang data untuk menampilkan daftar yang diperbarui
        } else {
            alert('Gagal menambahkan item: ' + (result.error || 'Terjadi kesalahan.'));
        }
    } catch (error) {
        console.error('Error saat menambahkan item:', error);
        alert('Terjadi kesalahan jaringan atau server.');
    }
}

// Fungsi untuk menghapus item dari daftar belanja
async function deleteShoppingItem(itemId, itemName, skipConfirm = false) {
    if (!skipConfirm) {
        const result = await Swal.fire({
            title: 'Anda yakin?',
            text: `Hapus item "${itemName}"?`,
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'Ya, hapus!',
            cancelButtonText: 'Batal',
            background: '#34495e', color: '#f8f9fa'
        });
        if (!result.isConfirmed) return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/shopping_list/delete/${itemId}`, {
            method: 'DELETE',
        });
        if (response.ok) {
            fetchAppData(); // Muat ulang data
        } else {
            const errorResult = await response.json();
            throw new Error(errorResult.error || 'Gagal menghapus item.');
        }
    } catch (error) {
        console.error('Error saat menghapus item:', error);
        Swal.fire({ icon: 'error', title: 'Gagal Menghapus', text: error.message, background: '#34495e', color: '#f8f9fa' });
    }
}

// Fungsi untuk mengubah status item
async function toggleShoppingItemStatus(itemId) {
    try {
        // Perbaikan: Kirim nama item di URL, sesuai dengan endpoint API
        const response = await fetch(`${API_BASE_URL}/shopping_list/toggle_status/${itemId}`, {
            method: 'PUT',
        });
        if (response.ok) {
            fetchAppData(); // Langsung muat ulang data tanpa alert untuk pengalaman yang lebih baik
        } else {
            alert('Gagal mengubah status item: ' + (result.error || 'Terjadi kesalahan.'));
        }
    } catch (error) {
        console.error('Error saat mengubah status item:', error);
        alert('Terjadi kesalahan jaringan atau server.');
    }
}

function makeEditable(cell, itemId, field) {
    // Hindari membuat input jika sudah ada
    if (cell.querySelector('input')) {
        return;
    }

    const originalValue = cell.textContent.replace('Rp ', '').replace(/\./g, '');
    cell.innerHTML = `<input type="text" value="${originalValue}" class="form-control form-control-sm">`;
    
    const input = cell.querySelector('input');
    input.focus();
    input.select();

    const saveChanges = async () => {
        const newValue = input.value;

        // Jika tidak ada perubahan, kembalikan ke teks asli
        if (newValue === originalValue) {
            fetchAppData(); // Cukup refresh
            return;
        }

        // Kirim pembaruan ke server
        try {
            const payload = {};
            payload[field] = newValue;

            const response = await fetch(`${API_BASE_URL}/shopping_list/update/${itemId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!response.ok) {
                const errorResult = await response.json();
                throw new Error(errorResult.error || 'Gagal memperbarui item.');
            }

            // Jika berhasil, refresh seluruh data
            fetchAppData();

        } catch (error) {
            console.error('Error updating item:', error);
            alert(error.message);
            fetchAppData(); // Kembalikan ke state semula jika gagal
        }
    };

    // Simpan saat kehilangan fokus (blur)
    input.addEventListener('blur', saveChanges);

    // Simpan saat menekan tombol Enter
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            input.blur(); // Panggil event blur untuk menyimpan
        }
    });
}

async function toggleDeliveryStatus(itemId) {
    try {
        const response = await fetch(`${API_BASE_URL}/shopping_list/toggle_delivery/${itemId}`, {
            method: 'PUT',
        });
        const result = await response.json();
        if (response.ok) {
            fetchAppData(); // Langsung muat ulang data tanpa alert
        } else {
            alert('Gagal mengubah status pengiriman: ' + (result.error || 'Terjadi kesalahan.'));
        }
    } catch (error) {
        console.error('Error saat mengubah status pengiriman:', error);
        alert('Terjadi kesalahan jaringan atau server.');
    }
}

function showItemSuggestions() {
    const input = document.getElementById('shopping-item-name');
    const suggestionsContainer = document.getElementById('item-suggestions');
    const term = input.value.toLowerCase();
    suggestionsContainer.innerHTML = '';

    if (term.length === 0) {
        return;
    }

    const uniqueItems = {};
    allShoppingItems.forEach(item => {
        // Simpan item terbaru dengan nama yang sama
        uniqueItems[item.item.toLowerCase()] = item;
    });

    const filteredItems = Object.values(uniqueItems).filter(item => 
        item.item.toLowerCase().includes(term)
    );

    filteredItems.forEach(item => {
        const div = document.createElement('div');
        div.className = 'suggestion-item';

        // Buat elemen untuk teks dan tombol hapus
        const textSpan = document.createElement('span');
        textSpan.textContent = `${item.item} (Qty: ${item.quantity}, Harga: Rp ${item.price.toLocaleString('id-ID')})`;

        const deleteBtn = document.createElement('button');
        deleteBtn.className = 'delete-suggestion-btn';
        deleteBtn.innerHTML = '<i class="fas fa-trash-alt"></i>';
        
        // Event untuk menghapus item
        deleteBtn.onmousedown = (event) => {
            event.stopPropagation(); // Hentikan event agar tidak mengisi form
            deleteShoppingItem(item.id, item.item); // Panggil fungsi hapus dengan ID
        };

        // Gunakan mousedown karena dieksekusi sebelum 'blur' pada input
        textSpan.onmousedown = () => {
            document.getElementById('shopping-item-name').value = item.item;
            document.getElementById('shopping-item-quantity').value = item.quantity;
            document.getElementById('shopping-item-price').value = item.price;
            suggestionsContainer.innerHTML = ''; // Sembunyikan saran setelah dipilih
        };
        div.appendChild(textSpan);
        div.appendChild(deleteBtn);
        suggestionsContainer.appendChild(div);
    });
}

function initShoppingList() {
    const shoppingForm = document.getElementById('add-shopping-item-form');
    const itemNameInput = document.getElementById('shopping-item-name');
    const suggestionsContainer = document.getElementById('item-suggestions');

    if (shoppingForm) {
        shoppingForm.addEventListener('submit', addShoppingItem);
    }

    if (itemNameInput) {
        itemNameInput.addEventListener('input', showItemSuggestions);
        // Sembunyikan saran saat input kehilangan fokus
        itemNameInput.addEventListener('blur', () => {
            // Beri sedikit jeda agar event mousedown pada saran bisa berjalan
            setTimeout(() => { suggestionsContainer.innerHTML = ''; }, 200);
        });
    }

    fetchAppData();
}

async function displayMonthlyRecap() {
    try {
        const response = await fetch(`${API_BASE_URL}/data`);
        if (!response.ok) throw new Error('Gagal mengambil data rekap.');
        const data = await response.json();
        const recapData = data.monthly_recap || {};
        const recapContainer = document.getElementById('recap-container');
        recapContainer.innerHTML = '';
        let grandTotal = 0;

        const sortedMonths = Object.keys(recapData).sort().reverse();

        if (sortedMonths.length === 0) {
            recapContainer.innerHTML = '<p class="text-center">Belum ada data yang diarsipkan.</p>';
            return;
        }

        // Hitung grand total dari semua bulan
        sortedMonths.forEach(month => {
            grandTotal += recapData[month].total;
        });
        if (grandTotal > 0) {
            recapContainer.innerHTML += `<h4 class="total-display" style="text-align: center; margin-bottom: 20px;">Total Keseluruhan: Rp ${grandTotal.toLocaleString('id-ID')}</h4>`;
        }

        sortedMonths.forEach(month => {
            const monthData = recapData[month];
            const monthDiv = document.createElement('div');
            
            const header = document.createElement('div');
            header.className = 'recap-month-header';
            header.innerHTML = `
                <span>${month}</span>
                <span>Total: Rp ${monthData.total.toLocaleString('id-ID')}</span>
            `;
            
            const tableContainer = document.createElement('div');
            tableContainer.className = 'hidden'; // Sembunyikan detail secara default
            let tableHTML = `
                <table class="table table-sm mt-2">
                    <thead><tr><th>Barang</th><th>Jumlah</th><th>Harga</th><th>Tanggal</th></tr></thead>
                    <tbody>
            `;
            monthData.items.forEach(item => {
                tableHTML += `<tr><td>${item.item}</td><td>${item.quantity}</td><td>Rp ${item.price.toLocaleString('id-ID')}</td><td>${item.date_added}</td></tr>`;
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
        alert(error.message);
    }
}

async function archiveData() {
    if (!confirm('Anda yakin ingin mengarsipkan semua data di daftar belanja saat ini? Daftar belanja akan dikosongkan.')) return;
    try {
        const response = await fetch(`${API_BASE_URL}/shopping_list/archive`, { method: 'POST' });
        const result = await response.json();
        alert(result.message || result.error);
        displayMonthlyRecap(); // Refresh tampilan rekap
    } catch (error) {
        console.error('Error archiving data:', error);
        alert('Gagal mengarsipkan data.');
    }
}