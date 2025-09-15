const API_BASE_URL = 'http://192.168.1.10:5001'; // GANTI DENGAN ALAMAT IP KOMPUTER ANDA

// Fungsi untuk menampilkan/menyembunyikan halaman
function showPage(pageId) {
    document.getElementById('main-menu-page').classList.add('hidden');
    document.getElementById('shopping-list-page').classList.add('hidden');
    document.getElementById('calculator-page').classList.add('hidden');
    document.getElementById('theme-page').classList.add('hidden');

    document.getElementById(pageId).classList.remove('hidden');

    // Jika halaman daftar belanja ditampilkan, muat datanya
    if (pageId === 'shopping-list-page') {
        initShoppingList();
    } else if (pageId === 'calculator-page') {
        initCalculator();
    }
}