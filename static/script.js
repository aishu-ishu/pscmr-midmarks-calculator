// let startTime;
// let timerInterval;

// function startTimer() {
//     startTime = Date.now();
//     const loading = document.getElementById('loading');
//     loading.style.display = 'inline-block';
//     loading.style.color = 'var(--primary)';
//     timerInterval = setInterval(() => {
//         const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
//         loading.innerText = `Processing... (${elapsed}s)`;
//     }, 100);
// }

// function stopTimer() {
//     clearInterval(timerInterval);
//     const elapsedSeconds = Math.floor((Date.now() - startTime) / 1000);
//     const mins = Math.floor(elapsedSeconds / 60);
//     const secs = elapsedSeconds % 60;
//     const loading = document.getElementById('loading');
//     loading.style.display = 'inline-block';
//     loading.style.color = '#16a34a';
//     loading.innerText = `Completed in ${mins}m ${secs}s`;
// }

// function previewImage(event) {
//     const reader = new FileReader();
//     reader.onload = function() {
//         const preview = document.getElementById('preview');
//         preview.src = reader.result;
//         preview.style.display = 'block';
//     }
//     if (event.target.files[0]) {
//         reader.readAsDataURL(event.target.files[0]);
//     }
// }

// async function uploadImage() {
//     const fileInput = document.getElementById('imageInput');
//     const container = document.getElementById('resultsContainer');
//     const loading = document.getElementById('loading');
//     if (fileInput.files.length === 0) {
//         alert('Please select an image first!');
//         return;
//     }
//     const formData = new FormData();
//     formData.append('file', fileInput.files[0]);
//     container.innerHTML = '';
//     startTimer();
//     try {
//         const response = await fetch('/process-image', {
//             method: 'POST',
//             body: formData
//         });
//         const data = await response.json();
//         stopTimer();
//         if (!response.ok || data.error) {
//             container.innerHTML = `<div style="color:red; text-align:center;">${data.error || 'Failed to process image'}</div>`;
//             return;
//         }

//         data.rows.forEach(subject => {
//             const mid1IsBest = subject.Mid1_Score >= subject.Mid2_Score;
            
//             const cardHTML = `
//                 <div class="subject-card">
//                     <div class="card-header">
//                          Subject: ${subject.Subject}
//                     </div>
//                     <div class="card-body">
//                         <div class="grid-2">
//                             <div class="metric-box ${mid1IsBest ? 'best' : ''}">
//                                 <div class="box-title">Mid Exam 1 Score</div>
//                                 <div class="box-value">${subject.Mid1_Score}</div>
//                                 <div class="box-sub">out of 30</div>
//                                 ${mid1IsBest ? '<span class="badge-best">Best</span>' : ''}
//                             </div>
//                             <div class="metric-box ${!mid1IsBest ? 'best' : ''}">
//                                 <div class="box-title">Mid Exam 2 Score</div>
//                                 <div class="box-value">${subject.Mid2_Score}</div>
//                                 <div class="box-sub">out of 30</div>
//                                 ${!mid1IsBest ? '<span class="badge-best">Best</span>' : ''}
//                             </div>
//                         </div>
//                         <div class="weightage-banner">
//                             <div class="w-item">
//                                 <span class="w-label">Best Mid (80%)</span>
//                                 <span class="w-val">${subject.Best_Mid_80}</span>
//                             </div>
//                             <div class="w-item" style="text-align: right;">
//                                 <span class="w-label">Other Mid (20%)</span>
//                                 <span class="w-val">${subject.Other_Mid_20}</span>
//                             </div>
//                         </div>
//                         <div class="grid-2">
//                             <div class="banner-blue">
//                                 <div class="banner-title">Final Mid Average</div>
//                                 <div class="banner-val">${subject.Final_Mid_Average}</div>
//                                 <div class="banner-sub">out of 30</div>
//                             </div>
//                             <div class="banner-orange">
//                                 <div class="banner-title">Required Semester Marks</div>
//                                 <div class="banner-val">${subject.Required_Sem_Marks}</div>
//                                 <div class="banner-sub">out of 70</div>
//                             </div>
//                         </div>
//                         <div class="status-pill">
//                             You need ${subject.Required_Sem_Marks} marks in semester exam to pass.
//                         </div>
//                     </div>
//                 </div>
//             `;
//             container.innerHTML += cardHTML;
//         });
//     } catch (error) {
//         stopTimer();
//         loading.style.color = '#dc2626';
//         loading.innerText = 'Failed to connect';
//         container.innerHTML = `<div style="color:red; text-align:center;">Error connecting to server.</div>`;
//     }
// }

let startTime;
let timerInterval;

function startTimer() {
    startTime = Date.now();
    const loading = document.getElementById('loading');
    loading.style.display = 'inline-block';
    loading.style.color = 'var(--primary)';
    timerInterval = setInterval(() => {
        const elapsed = ((Date.now() - startTime) / 1000).toFixed(1);
        loading.innerText = `Processing... (${elapsed}s)`;
    }, 100);
}

function stopTimer() {
    clearInterval(timerInterval);
    const elapsedSeconds = Math.floor((Date.now() - startTime) / 1000);
    const mins = Math.floor(elapsedSeconds / 60);
    const secs = elapsedSeconds % 60;
    const loading = document.getElementById('loading');
    loading.style.display = 'inline-block';
    loading.style.color = '#16a34a';
    loading.innerText = `Completed in ${mins}m ${secs}s`;
}

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
    startTimer();
    try {
        const response = await fetch('/process-image', {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        stopTimer();
        if (!response.ok || data.error) {
            container.innerHTML = `<div style="color:red; text-align:center;">${data.error || 'Failed to process image'}</div>`;
            return;
        }

        data.rows.forEach(subject => {
            const mid1IsBest = subject.Mid1_Score >= subject.Mid2_Score;
            
            // Dynamic styling configuration for Required Semester Marks
            const isGreen = subject.Required_Sem_Marks === 24;
            const bannerClass = isGreen ? 'banner-green' : 'banner-red';
            const boxStyle = isGreen 
                ? 'background-color: #dcfce7; border: 2px solid #16a34a; color: #15803d;' 
                : 'background-color: #fee2e2; border: 2px solid #dc2626; color: #b91c1c;';
            const textStyle = 'font-weight: bold;';

            const cardHTML = `
                <div class="subject-card">
                    <div class="card-header">
                         Subject: ${subject.Subject}
                    </div>
                    <div class="card-body">
                        <div class="grid-2">
                            <div class="metric-box ${mid1IsBest ? 'best' : ''}">
                                <div class="box-title">Mid Exam 1 Score</div>
                                <div class="box-value">${subject.Mid1_Score}</div>
                                <div class="box-sub">out of 30</div>
                                ${mid1IsBest ? '<span class="badge-best">Best</span>' : ''}
                            </div>
                            <div class="metric-box ${!mid1IsBest ? 'best' : ''}">
                                <div class="box-title">Mid Exam 2 Score</div>
                                <div class="box-value">${subject.Mid2_Score}</div>
                                <div class="box-sub">out of 30</div>
                                ${!mid1IsBest ? '<span class="badge-best">Best</span>' : ''}
                            </div>
                        </div>
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
                        <div class="grid-2">
                            <div class="banner-blue">
                                <div class="banner-title">Final Mid Average</div>
                                <div class="banner-val">${subject.Final_Mid_Average}</div>
                                <div class="banner-sub">out of 30</div>
                            </div>
                            <div class="${bannerClass}" style="${boxStyle}">
                                <div class="banner-title" style="${textStyle}">Required Semester Marks</div>
                                <div class="banner-val" style="${textStyle}">${subject.Required_Sem_Marks}</div>
                                <div class="banner-sub" style="${textStyle}">out of 70</div>
                            </div>
                        </div>
                        <div class="status-pill">
                            You need ${subject.Required_Sem_Marks} marks in semester exam to pass.
                        </div>
                    </div>
                </div>
            `;
            container.innerHTML += cardHTML;
        });
    } catch (error) {
        stopTimer();
        loading.style.color = '#dc2626';
        loading.innerText = 'Failed to connect';
        container.innerHTML = `<div style="color:red; text-align:center;">Error connecting to server.</div>`;
    }
}
