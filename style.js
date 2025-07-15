// DOM Elements
const imageInput = document.getElementById('imageInput');
const uploadArea = document.getElementById('uploadArea');
const previewContainer = document.getElementById('previewContainer');
const imagePreview = document.getElementById('imagePreview');
const analyzeBtn = document.getElementById('analyzeBtn');
const resultContainer = document.getElementById('resultContainer');
const emotionResult = document.getElementById('emotionResult');
const historyContainer = document.getElementById('historyContainer');
const profileSection = document.getElementById('profileSection');
const profilePhoto = document.getElementById('profilePhoto');

// User data storage
let userData = {
    name: 'John Doe',
    age: 30,
    id: 'MH-' + new Date().getFullYear() + '-' + String(Math.floor(Math.random() * 999)).padStart(3, '0'),
    emotionHistory: [],
    currentPhoto: null,
    emotionalStability: 95
};

// Handle file input change
imageInput.addEventListener('change', (e) => {
    if (e.target.files.length) {
        handleImageUpload(e.target.files[0]);
    }
});



uploadArea.addEventListener('dragleave', (e) => {
    e.preventDefault();
    if (!uploadArea.contains(e.relatedTarget)) {
        uploadArea.classList.remove('drag-over');
    }
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (files.length) {
        handleImageUpload(files[0]);
    }
});

// Handle image upload
function handleImageUpload(file) {
    // Validate file type
    if (!file.type.startsWith('image/')) {
        showError('Please upload an image file (JPG, PNG, etc.)');
        return;
    }

    // Validate file size (max 5MB)
    if (file.size > 5 * 1024 * 1024) {
        showError('Please upload an image smaller than 5MB');
        return;
}

    const reader = new FileReader();
    reader.onload = (e) => {
        const imageData = e.target.result;
        
        // Validate image dimensions
        const img = new Image();
        img.onload = () => {
            if (img.width < 100 || img.height < 100) {
                showError('Please upload a larger image (minimum 100x100 pixels)');
                return;
            }
            
            // Update UI with valid image
            imagePreview.src = imageData;
            userData.currentPhoto = imageData;
            uploadArea.style.display = 'none';
            previewContainer.style.display = 'block';
            previewContainer.classList.add('active');
            resultContainer.style.display = 'none'; // Hide previous results
        };
        img.src = imageData;
    };
    
    reader.onerror = () => {
        showError('Error reading the image file. Please try again.');
    };
    
    reader.readAsDataURL(file);
}

// Mock emotion analysis (replace with actual API call)
async function analyzeEmotion(imageElement) {
    // Simulating API call delay
    await new Promise(resolve => setTimeout(resolve, 1500));
    
}

// Handle emotion analysis
analyzeBtn.addEventListener('click', async () => {
    analyzeBtn.disabled = true;
    analyzeBtn.innerHTML = '<span class="loading-spinner"></span> Analyzing...';
    
    try {
        const result = await analyzeEmotion(imagePreview);
        
        // Update result container
        resultContainer.style.display = 'block';
        emotionResult.innerHTML = `
            <div class="emotion-icon">${getEmotionIcon(result.emotion)}</div>
            <h4>${result.emotion}</h4>
            <p>We detected that you're feeling ${result.emotion.toLowerCase()} 
               with ${result.confidence}% confidence</p>
        `;
        
        // Add to history
        addToHistory(result);
        
        // Update profile
        updateProfile(result);
        
    } catch (error) {
        console.error('Error analyzing emotion:', error);
        emotionResult.innerHTML = `
            <div class="error">
                <p>Something went wrong while analyzing your emotion.</p>
                <p>Please try again or choose a different photo.</p>
            </div>
        `;
    } finally {
        analyzeBtn.disabled = false;
        analyzeBtn.textContent = 'Analyze Emotion';
    }
});

// Add result to history
function addToHistory(result) {
    const timestamp = new Date().toLocaleString();
    userData.emotionHistory.unshift({
        emotion: result.emotion,
        confidence: result.confidence,
        timestamp,
        photo: userData.currentPhoto
    });
    
    updateHistoryDisplay();
}

// Update history display
function updateHistoryDisplay() {
    historyContainer.innerHTML = userData.emotionHistory
        .map((item, index) => `
            <div class="history-item">
                <div class="history-photo" style="background-image: url('${item.photo}')"></div>
                <h4>${item.emotion}</h4>
                <p>Confidence: ${item.confidence}%</p>
                <small>${item.timestamp}</small>
            </div>
        `)
        .join('');
}

// Update profile display
function updateProfile(result) {
    // Update profile photo
    profilePhoto.src = userData.currentPhoto;
    
    // Update profile information
    document.getElementById('profileName').textContent = userData.name;
    document.getElementById('profileAge').textContent = userData.age;
    document.getElementById('profileId').textContent = userData.id;
    document.getElementById('profileDate').textContent = new Date().toLocaleDateString();
    document.getElementById('profileEmotion').textContent = result.emotion;
    document.getElementById('profileStability').textContent = `${Math.round(userData.emotionalStability)}%`;
    
    // Update emotion history
    document.getElementById('emotionHistory').innerHTML = userData.emotionHistory
        .slice(0, 5)
        .map(item => `
            <div class="emotion-entry">
                <span class="emotion-dot" style="background-color: ${getEmotionColor(item.emotion)}"></span>
                <p>${item.emotion} (${item.timestamp})</p>
            </div>
        `)
        .join('');
    
    // Generate recommendations based on emotion
    const recommendations = getRecommendations(result.emotion);
    document.getElementById('recommendationsList').innerHTML = recommendations
        .map(rec => `<li>${rec}</li>`)
        .join('');
    
    profileSection.style.display = 'block';
}

// Get emotion color
function getEmotionColor(emotion) {
    const colorMap = {
        'Happy': '#FFD700',
        'Sad': '#4169E1',
        'Neutral': '#808080',
        'Excited': '#FF4500',
        'Tired': '#8B4513'
    };
    return colorMap[emotion] || '#000000';
}

// Reset upload area
function resetUpload() {
    // Clear the input
    imageInput.value = '';
    
    // Reset the preview
    imagePreview.src = '';
    userData.currentPhoto = null;
    
    // Show/hide containers
    uploadArea.style.display = 'block';
    previewContainer.style.display = 'none';
    previewContainer.classList.remove('active');
    resultContainer.style.display = 'none';
    
    // Reset the analyze button
    analyzeBtn.disabled = false;
    analyzeBtn.textContent = 'Analyze Emotion';
    
    // Remove any error messages
    const errorMessage = uploadArea.querySelector('.error-message');
    if (errorMessage) {
        errorMessage.remove();
    }
}

// Add styles for loading spinner
const style = document.createElement('style');
style.textContent = `
    .loading-spinner {
        display: inline-block;
        width: 20px;
        height: 20px;
        margin-right: 8px;
        border: 3px solid rgba(255,255,255,0.3);
        border-radius: 50%;
        border-top-color: white;
        animation: spin 1s ease-in-out infinite;
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    .emotion-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        animation: bounceIn 0.6s cubic-bezier(0.68, -0.55, 0.265, 1.55);
    }
    
    @keyframes bounceIn {
        0% { transform: scale(0); }
        50% { transform: scale(1.2); }
        100% { transform: scale(1); }
    }
`;
document.head.appendChild(style);

// Initialize the page
document.addEventListener('DOMContentLoaded', () => {
    updateHistoryDisplay();
});
