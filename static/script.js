function previewImage(event) {
    const reader = new FileReader();
    reader.onload = function() {
        const preview = document.getElementById('preview');
        preview.src = reader.result;
        preview.style.display = 'block';
    }
    if (event.target.files[0]) {
        reader.readAsDataURL(event.target.files[0]);
    }
}

async function uploadImage() {
    const fileInput = document.getElementById('imageInput');
    const container = document.getElementById('resultsContainer');
    const loading = document.getElementById('loading');

    if (fileInput.files.length === 0) {
        alert('Please select an image first!');
        return;
    }

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    container.innerHTML = '';
    loading.style.display = 'block';

    try {
        const response = await fetch('/process-image', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();
        loading.style.display = 'none';

        if (!response.ok || data.error) {
            container.innerHTML = `<div style="color:red; text-align:center;">${data.error || 'Failed to process image'}</div>`;
            return;
        }

        // Render Card for each Subject
        data.rows.forEach(subject => {
            const cardHTML = `
                <div class="subject-card">
                    <div class="card-header">
                        🏆 Subject: ${subject.Subject}
                    </div>
                    <div class="card-body">
                        <!-- Mid 1 & Mid 2 Top Grid -->
                        <div class="grid-2">
                            <div class="metric-box best">
                                <div class="box-title">Mid Exam 1 Score</div>
                                <div class="box-value">${subject.Mid1_Score}</div>
                                <div class="box-sub">out of 30</div>
                                <span class="badge-best">Best</span>
                            </div>

                            <div class="metric-box">
                                <div class="box-title">Mid Exam 2 Score</div>
                                <div class="box-value">${subject.Mid2_Score}</div>
                                <div class="box-sub">out of 30</div>
                            </div>
                        </div>

                        <!-- Weightage Banner -->
                        <div class="weightage-banner">
                            <div class="w-item">
                                <span class="w-label">Best Mid (80%)</span>
                                <span class="w-val">${subject.Best_Mid_80}</span>
                            </div>
                            <div class="w-item" style="text-align: right;">
                                <span class="w-label">Other Mid (20%)</span>
                                <span class="w-val">${subject.Other_Mid_20}</span>
                            </div>
                        </div>

                        <!-- Bottom Final Summary Grid -->
                        <div class="grid-2">
                            <div class="banner-blue">
                                <div class="banner-title">Final Mid Average</div>
                                <div class="banner-val">${subject.Final_Mid_Average}</div>
                                <div class="banner-sub">out of 30</div>
                            </div>

                            <div class="banner-orange">
                                <div class="banner-title">Required Semester Marks</div>
                                <div class="banner-val">${subject.Required_Sem_Marks}</div>
                                <div class="banner-sub">out of 70</div>
                            </div>
                        </div>

                        <!-- Status Footer Pill -->
                        <div class="status-pill">
                            You need ${subject.Required_Sem_Marks} marks in semester exam to pass.
                        </div>
                    </div>
                </div>
            `;
            container.innerHTML += cardHTML;
        });

    } catch (error) {
        loading.style.display = 'none';
        container.innerHTML = `<div style="color:red; text-align:center;">Error connecting to server.</div>`;
    }
}