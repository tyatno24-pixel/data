// Shopping List Functions

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

            row.innerHTML = `
                <td>${item.item}</td>
                <td>${item.quantity}</td>
                <td>Rp ${item.price.toLocaleString('id-ID')}</td>
                <td>Rp ${totalHarga.toLocaleString('id-ID')}</td>
                <td class="status-${item.status.toLowerCase().replace(/ /g, '-')}" onclick="toggleShoppingItemStatus('${item.item}')">${item.status}</td>
                <td><button class="btn btn-danger" onclick="deleteShoppingItem('${item.item}')">Hapus</button></td>
            `;
        });
    } else {
        const row = shoppingListTableBody.insertRow();
        const cell = row.insertCell();
        cell.colSpan = 6;
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
            alert(result.message);
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
async function deleteShoppingItem(itemName) {
    if (!confirm(`Apakah Anda yakin ingin menghapus item ${itemName}?`)) {
        return;
    }
    try {
        const response = await fetch(`${API_BASE_URL}/shopping_list/delete/${itemName}`, {
            method: 'DELETE',
        });
        const result = await response.json();
        if (response.ok) {
            alert(result.message);
            fetchAppData(); // Muat ulang data
        } else {
            alert('Gagal menghapus item: ' + (result.error || 'Terjadi kesalahan.'));
        }
    } catch (error) {
        console.error('Error saat menghapus item:', error);
        alert('Terjadi kesalahan jaringan atau server.');
    }
}

// Fungsi untuk mengubah status item
async function toggleShoppingItemStatus(itemName) {
    try {
        const response = await fetch(`${API_BASE_URL}/shopping_list/toggle_status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ item_name: itemName }),
        });
        const result = await response.json();
        if (response.ok) {
            alert(result.message);
            fetchAppData(); // Muat ulang data
        } else {
            alert('Gagal mengubah status item: ' + (result.error || 'Terjadi kesalahan.'));
        }
    } catch (error) {
        console.error('Error saat mengubah status item:', error);
        alert('Terjadi kesalahan jaringan atau server.');
    }
}

function initShoppingList() {
    const shoppingForm = document.getElementById('add-shopping-item-form');
    if (shoppingForm) {
        shoppingForm.addEventListener('submit', addShoppingItem);
    }
    fetchAppData();
}