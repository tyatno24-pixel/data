const API_BASE_URL = '';

document.addEventListener('DOMContentLoaded', () => {
    const analyzeButton = document.getElementById('analyze-button');
    if (analyzeButton) {
        analyzeButton.addEventListener('click', startAnalysis);
    }
});

async function startAnalysis() {
    const titleInput = document.getElementById('product-title');
    const priceInput = document.getElementById('product-price');
    const descriptionInput = document.getElementById('product-description');
    const loadingIndicator = document.getElementById('loading-indicator');
    const resultSection = document.getElementById('result-section');

    const productData = {
        title: titleInput.value,
        price: priceInput.value,
        description: descriptionInput.value
    };

    if (!productData.title || !productData.price || !productData.description) {
        Swal.fire({
            icon: 'error', title: 'Data Tidak Lengkap', text: 'Harap isi semua kolom (Judul, Harga, dan Deskripsi).',
            background: '#34495e', color: '#f8f9fa'
        });
        return;
    }

    // Tampilkan loading dan sembunyikan hasil sebelumnya
    loadingIndicator.classList.remove('hidden');
    resultSection.classList.add('hidden');

    try {
        const response = await fetch(`${API_BASE_URL}/analyze_product`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(productData)
        });

        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Gagal menganalisa produk.');
        }

        const analysisResult = await response.json();
        displayResults(analysisResult);

    } catch (error) {
        console.error('Analysis failed:', error);
        Swal.fire({
            icon: 'error', title: 'Analisa Gagal', text: error.message,
            background: '#34495e', color: '#f8f9fa'
        });
    } finally {
        // Sembunyikan loading
        loadingIndicator.classList.add('hidden');
    }
}

function displayResults(result) {
    const resultSection = document.getElementById('result-section');
    const scoreCircle = document.getElementById('score-circle');
    const scoreSummary = document.getElementById('score-summary');
    const recommendationList = document.getElementById('recommendation-list');
    const analysisDetails = document.getElementById('analysis-details');
    // Elemen baru untuk konten yang diperbaiki
    const improvedTitle = document.getElementById('improved-title');
    const improvedDescription = document.getElementById('improved-description');
    const priceSuggestion = document.getElementById('price-suggestion');


    // Tampilkan skor
    scoreCircle.textContent = `${result.effectiveness_score}%`;
    scoreSummary.textContent = result.summary;

    // Tampilkan rekomendasi
    recommendationList.innerHTML = '';
    result.recommendations.forEach(rec => {
        const li = document.createElement('li');
        li.innerHTML = `<strong>${rec.area}:</strong> ${rec.suggestion}`;
        recommendationList.appendChild(li);
    });

    // Tampilkan konten yang sudah diperbaiki
    improvedTitle.value = result.improved_content.title;
    improvedDescription.value = result.improved_content.description;
    priceSuggestion.textContent = result.improved_content.price_suggestion;

    // Tampilkan detail analisis
    analysisDetails.innerHTML = `
        <p><strong>Judul Produk:</strong> ${result.analysis.title_review}</p>
        <p><strong>Deskripsi:</strong> ${result.analysis.description_review}</p>
        <p><strong>Harga:</strong> ${result.analysis.price_review}</p>
        <p><strong>Foto Produk:</strong> ${result.analysis.photo_review}</p>
    `;

    // Tampilkan seluruh bagian hasil
    resultSection.classList.remove('hidden');
}

function copyToClipboard(elementId) {
    const element = document.getElementById(elementId);
    if (!element) return;

    element.select();
    element.setSelectionRange(0, 99999); // Untuk perangkat mobile

    try {
        navigator.clipboard.writeText(element.value);
        Swal.fire({
            toast: true, position: 'top-end', showConfirmButton: false, timer: 2000,
            icon: 'success', title: 'Teks berhasil disalin!',
            background: '#34495e', color: '#f8f9fa'
        });
    } catch (err) {
        console.error('Gagal menyalin teks: ', err);
    }
}