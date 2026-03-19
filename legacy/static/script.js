// Global state variables
const state = {
    fileId: null,
    chapters: [],
    selectedChapter: null,
    scenes: [],
    selectedScenes: [],
    characters: [],
    dialogues: [],
    generatedImages: [],
    selectedImages: [],
    createdPages: []
};

// DOM elements
const uploadForm = document.getElementById('uploadForm');
const uploadStatus = document.getElementById('uploadStatus');
const chapterList = document.getElementById('chapterList');
const sceneList = document.getElementById('sceneList');
const characterList = document.getElementById('characterList');
const dialogueList = document.getElementById('dialogueList');
const generatedImages = document.getElementById('generatedImages');
const imageGenerationStatus = document.getElementById('imageGenerationStatus');
const selectedPanels = document.getElementById('selectedPanels');
const speechBubbleOptions = document.getElementById('speechBubbleOptions');
const mangaPagePreview = document.getElementById('mangaPagePreview');
const mangaPages = document.getElementById('mangaPages');
const exportStatus = document.getElementById('exportStatus');
const downloadLink = document.getElementById('downloadLink');
const progressBar = document.getElementById('progressBar');

// Update progress
function updateProgress(step) {
    const steps = ['upload', 'chapters', 'scenes', 'images', 'layout', 'export'];
    const progress = (steps.indexOf(step) + 1) / steps.length * 100;
    progressBar.style.width = `${progress}%`;
}

// Tab navigation
document.querySelectorAll('.back-btn, .next-btn').forEach(btn => {
    btn.addEventListener('click', function () {
        const targetTab = this.dataset.tab;
        console.log("targetTab: ", targetTab);
        
        // Enable the target tab before clicking it
        document.getElementById(`${targetTab}-tab`).disabled = false;
        
        // Then navigate to it
        document.querySelector(`#workflowTabs button[data-bs-target="#${targetTab}"]`).click();
        updateProgress(targetTab);
    });
});

// File upload
uploadForm.addEventListener('submit', async function (e) {
    e.preventDefault();

    const formData = new FormData();
    const novelFile = document.getElementById('novelFile').files[0];

    if (!novelFile) {
        uploadStatus.innerHTML = '<div class="alert alert-danger">Please select a file</div>';
        return;
    }

    formData.append('novelFile', novelFile);
    uploadStatus.innerHTML = '<div class="alert alert-info">Uploading and processing file...</div>';

    try {
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            uploadStatus.innerHTML = `<div class="alert alert-success">File uploaded successfully! 
                ${data.chapterCount} chapters found.</div>`;

            // Store data and enable next step
            state.fileId = data.fileId;
            state.chapters = data.chapters;

            // Populate chapter list
            populateChapterList();

            // Enable next tab
            document.getElementById('chapters-tab').disabled = false;
            document.getElementById('chapters-tab').click();
            updateProgress('chapters');
        } else {
            uploadStatus.innerHTML = `<div class="alert alert-danger">Error: ${data.error}</div>`;
        }
    } catch (error) {
        uploadStatus.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
    }
});

// Populate chapter list
function populateChapterList() {
    chapterList.innerHTML = '';

    state.chapters.forEach((chapter, index) => {
        const listItem = document.createElement('button');
        listItem.className = 'list-group-item list-group-item-action';
        listItem.textContent = `Chapter ${index + 1}: ${chapter.title}`;
        listItem.addEventListener('click', function () {
            // Highlight selected chapter
            document.querySelectorAll('#chapterList button').forEach(item => {
                item.classList.remove('active');
            });
            this.classList.add('active');

            // Store selected chapter
            state.selectedChapter = index;

            // Enable continue button
            document.querySelector('#chapters .next-btn').disabled = false;

            // Process chapter to get scenes
            processChapter(index);
        });

        chapterList.appendChild(listItem);
    });
}

// Process chapter
async function processChapter(chapterIndex) {
    try {
        const response = await fetch('/process_chapter', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                fileId: state.fileId,
                chapterId: chapterIndex
            })
        });

        const data = await response.json();

        if (data.success) {
            // Store scene data
            state.scenes = data.scenes;
            state.characters = data.characters;
            state.dialogues = data.dialogues;

            // Enable scenes tab
            document.getElementById('scenes-tab').disabled = false;
        } else {
            alert(`Error processing chapter: ${data.error}`);
        }
    } catch (error) {
        alert(`Error: ${error.message}`);
    }
}

// Generate images (moved to images tab)
document.getElementById('generateImagesBtn').addEventListener('click', async function() {
    // Check which tab we're in and act accordingly
    const activeTab = document.querySelector('.tab-pane.active').id;
    
    if (activeTab === 'scenes') {
        // If in scenes tab, just navigate to images tab
        if (state.selectedScenes.length === 0) {
            alert('Please select at least one scene');
            return;
        }
        
        document.getElementById('images-tab').disabled = false;
        document.querySelector('#workflowTabs button[data-bs-target="#images"]').click();
        updateProgress('images');
        return;
    }
    
    // If in images tab, generate the images
    // Get settings
    const modelProvider = document.getElementById('modelProvider').value;
    const useLocalModel = document.getElementById('useLocalModel').checked;
    const width = parseInt(document.getElementById('imageWidth').value);
    const height = parseInt(document.getElementById('imageHeight').value);

    // Get selected scenes' descriptions
    const descriptions = state.selectedScenes.map(sceneId => {
        return state.scenes.find(scene => scene.id === sceneId).description;
    });

    if (descriptions.length === 0) {
        imageGenerationStatus.innerHTML = '<div class="alert alert-warning">Please select at least one scene</div>';
        return;
    }

    imageGenerationStatus.innerHTML = '<div class="alert alert-info">Generating images. This may take a while...</div>';

    try {
        // Prepare style modifier based on selected style
        const styleModifier = document.getElementById('mangaStyle').value;

        // Send request to backend
        const response = await fetch('/generate_images', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                descriptions: descriptions,
                modelProvider: modelProvider,
                useLocalModel: useLocalModel,
                width: width,
                height: height,
                style: styleModifier
            })
        });

        const data = await response.json();

        if (data.success) {
            // Store generated images
            state.generatedImages = data.images;

            // Display generated images
            displayGeneratedImages(data.images);

            // Update status
            imageGenerationStatus.innerHTML = '<div class="alert alert-success">Images generated successfully!</div>';

            // Enable next step
            document.querySelector('#images .next-btn').disabled = false;
            
            // Enable layout tab
            document.getElementById('layout-tab').disabled = false;
        } else {
            imageGenerationStatus.innerHTML = `<div class="alert alert-danger">Error: ${data.error}</div>`;
        }
    } catch (error) {
        imageGenerationStatus.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
    }
});

// Display generated images
function displayGeneratedImages(images) {
    generatedImages.innerHTML = '';

    images.forEach((image, index) => {
        const col = document.createElement('div');
        col.className = 'col-md-4 mb-3';

        const card = document.createElement('div');
        card.className = 'card h-100';

        const img = document.createElement('img');
        img.src = image.path;
        img.className = 'card-img-top manga-panel';
        img.alt = `Scene ${index + 1}`;
        img.dataset.imageId = image.filename;

        // Add click event to select/deselect image
        img.addEventListener('click', function () {
            this.parentElement.classList.toggle('border-primary');

            if (this.parentElement.classList.contains('border-primary')) {
                // Add to selected images
                state.selectedImages.push(image.filename);
            } else {
                // Remove from selected images
                state.selectedImages = state.selectedImages.filter(filename => filename !== image.filename);
            }

            // Update selected panels preview
            updateSelectedPanels();
        });

        const cardBody = document.createElement('div');
        cardBody.className = 'card-body';

        const cardTitle = document.createElement('h5');
        cardTitle.className = 'card-title';
        cardTitle.textContent = `Scene ${index + 1}`;

        const cardText = document.createElement('p');
        cardText.className = 'card-text small';
        cardText.textContent = image.description.substring(0, 500) + '...';

        cardBody.appendChild(cardTitle);
        cardBody.appendChild(cardText);
        card.appendChild(img);
        card.appendChild(cardBody);
        col.appendChild(card);

        generatedImages.appendChild(col);
    });
    state.selectedImages = images.map(image => image.filename);
}

// Update selected panels
function updateSelectedPanels() {
    console.log("state: ", state);
    selectedPanels.innerHTML = '';

    // Get selected images
    const images = state.selectedImages.map(imageId => {
        return state.generatedImages.find(img => img.filename === imageId);
    });

    images.forEach((image, index) => {
        const col = document.createElement('div');
        col.className = 'col-md-3 mb-3';

        const card = document.createElement('div');
        card.className = 'card h-100';

        const img = document.createElement('img');
        img.src = image.path;
        img.className = 'card-img-top';
        img.alt = `Panel ${index + 1}`;

        const cardBody = document.createElement('div');
        cardBody.className = 'card-body';

        const cardTitle = document.createElement('h5');
        cardTitle.className = 'card-title';
        cardTitle.textContent = `Panel ${index + 1}`;

        const removeBtn = document.createElement('button');
        removeBtn.className = 'btn btn-sm btn-danger';
        removeBtn.textContent = 'Remove';
        removeBtn.addEventListener('click', function () {
            // Remove from selected images
            state.selectedImages = state.selectedImages.filter(filename => filename !== image.filename);

            // Update selected panels
            updateSelectedPanels();

            // Update original panel selection
            const originalPanel = document.querySelector(`img[data-image-id="${image.filename}"]`);
            if (originalPanel) {
                originalPanel.parentElement.classList.remove('border-primary');
            }
        });

        cardBody.appendChild(cardTitle);
        cardBody.appendChild(removeBtn);
        card.appendChild(img);
        card.appendChild(cardBody);
        col.appendChild(card);

        selectedPanels.appendChild(col);
    });
    
    // Enable/disable the createMangaPageBtn based on selection
    document.getElementById('createMangaPageBtn').disabled = images.length === 0;
}

// Create manga page from selected panels
document.getElementById('createMangaPageBtn').addEventListener('click', function () {
    // Get settings
    const templateName = document.getElementById('templateName').value;
    const pageWidth = parseInt(document.getElementById('pageWidth').value);
    const pageHeight = parseInt(document.getElementById('pageHeight').value);
    const rightToLeft = document.getElementById('rightToLeft').checked;

    if (state.selectedImages.length === 0) {
        mangaPagePreview.innerHTML = '<div class="alert alert-warning">Please select at least one panel</div>';
        return;
    }

    // Create manga page
    createMangaPage(templateName, pageWidth, pageHeight, rightToLeft);
});

// Create manga page
async function createMangaPage(templateName, pageWidth, pageHeight, rightToLeft) {
    try {
        // Get selected images
        const images = state.selectedImages.map(imageId => {
            return state.generatedImages.find(img => img.filename === imageId);
        });

        const response = await fetch('/create_manga_page', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                images: images,
                template: templateName,
                width: pageWidth,
                height: pageHeight,
                rightToLeft: rightToLeft,
                dialogues: state.dialogues.filter(dialogue => {
                    return state.selectedScenes.includes(dialogue.sceneId);
                })
            })
        });

        const data = await response.json();

        if (data.success) {
            // Store created page
            state.createdPages.push(data.pagePath);

            // Display manga page
            displayMangaPage(data.pagePath);

            // Enable next step
            document.querySelector('#layout .next-btn').disabled = false;

            // Update manga pages list
            updateMangaPages();
            
            // Enable export tab
            document.getElementById('export-tab').disabled = false;
        } else {
            mangaPagePreview.innerHTML = `<div class="alert alert-danger">Error: ${data.error}</div>`;
        }
    } catch (error) {
        mangaPagePreview.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
    }
}

// Display manga page
function displayMangaPage(pagePath) {
    const mangaPagePreview = document.getElementById('mangaPagePreview');
    mangaPagePreview.innerHTML = ''; // Clear previous content

    const pageContainer = document.createElement('div');
    pageContainer.className = 'page-container';

    const img = document.createElement('img');
    img.src = pagePath; // Use the pagePath to set the image source
    img.style.width = '100%';
    img.style.height = 'auto';
    img.style.objectFit = 'cover';

    pageContainer.appendChild(img);
    mangaPagePreview.appendChild(pageContainer);
}

// Update manga pages list
function updateMangaPages() {
    mangaPages.innerHTML = '';

    state.createdPages.forEach((page, index) => {
        const col = document.createElement('div');
        col.className = 'col-md-4 mb-3';

        const card = document.createElement('div');
        card.className = 'card h-100';

        const img = document.createElement('img');
        img.src = page.thumbnailUrl;
        img.className = 'card-img-top';
        img.alt = `Page ${index + 1}`;

        const cardBody = document.createElement('div');
        cardBody.className = 'card-body';

        const cardTitle = document.createElement('h5');
        cardTitle.className = 'card-title';
        cardTitle.textContent = `Page ${index + 1}`;

        cardBody.appendChild(cardTitle);
        card.appendChild(img);
        card.appendChild(cardBody);
        col.appendChild(card);

        mangaPages.appendChild(col);
    });

    // Enable export tab if we have at least one page
    if (state.createdPages.length > 0) {
        document.getElementById('export-tab').disabled = false;
    }
}

// Export manga
document.getElementById('exportMangaBtn').addEventListener('click', async function () {
    const title = document.getElementById('mangaTitle').value || 'My Manga';
    const format = document.getElementById('exportFormat').value;

    if (state.createdPages.length === 0) {
        exportStatus.innerHTML = '<div class="alert alert-warning">Please create at least one page</div>';
        return;
    }

    exportStatus.innerHTML = '<div class="alert alert-info">Exporting manga...</div>';

    try {
        const response = await fetch('/export_manga', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                title: title,
                format: format,
                pages: state.createdPages
            })
        });

        const data = await response.json();

        if (data.success) {
            exportStatus.innerHTML = '<div class="alert alert-success">Manga exported successfully!</div>';

            // Create download link
            downloadLink.innerHTML = `<a href="${data.downloadUrl}" class="btn btn-success">Download ${title}.${format}</a>`;
        } else {
            exportStatus.innerHTML = `<div class="alert alert-danger">Error: ${data.error}</div>`;
        }
    } catch (error) {
        exportStatus.innerHTML = `<div class="alert alert-danger">Error: ${error.message}</div>`;
    }
});

// Scene selection
document.addEventListener('DOMContentLoaded', function () {
    // Populate scene list when scenes tab is activated
    document.getElementById('scenes-tab').addEventListener('shown.bs.tab', function () {
        populateSceneList();
    });

    // Populate dialogues when images tab is activated
    document.getElementById('images-tab').addEventListener('shown.bs.tab', function () {
        populateDialogueOptions();
    });
    
    // Handle tab activation to properly enable/disable tabs
    const tabLinks = document.querySelectorAll('.nav-tabs .nav-link');
    tabLinks.forEach(tab => {
        tab.addEventListener('shown.bs.tab', function (e) {
            updateProgress(e.target.id.replace('-tab', ''));
        });
    });
});

// Populate scene list
function populateSceneList() {
    sceneList.innerHTML = '';
    characterList.innerHTML = '';
    dialogueList.innerHTML = '';

    // Populate scenes
    state.scenes.forEach(scene => {
        const col = document.createElement('div');
        col.className = 'col-md-4 mb-3';

        const card = document.createElement('div');
        card.className = 'card h-100';
        
        // If this scene was previously selected, add the border-primary class
        if (state.selectedScenes.includes(scene.id)) {
            card.classList.add('border-primary');
        }

        const cardBody = document.createElement('div');
        cardBody.className = 'card-body';

        const cardTitle = document.createElement('h5');
        cardTitle.className = 'card-title';
        cardTitle.textContent = `Scene ${scene.id}`;

        const cardText = document.createElement('p');
        cardText.className = 'card-text';
        cardText.textContent = scene.description.substring(0, 500) + '...';

        const selectBtn = document.createElement('button');
        selectBtn.className = 'btn btn-sm btn-primary scene-checkbox';
        selectBtn.textContent = state.selectedScenes.includes(scene.id) ? 'Deselect' : 'Select';
        
        selectBtn.addEventListener('click', function () {
            // Toggle selection
            if (state.selectedScenes.includes(scene.id)) {
                state.selectedScenes = state.selectedScenes.filter(id => id !== scene.id);
                this.textContent = 'Select';
                card.classList.remove('border-primary');
            } else {
                state.selectedScenes.push(scene.id);
                this.textContent = 'Deselect';
                card.classList.add('border-primary');
            }
            
            // Enable/disable Generate Images button based on selection
            document.getElementById('generateImagesBtn').disabled = state.selectedScenes.length === 0;
        });

        cardBody.appendChild(cardTitle);
        cardBody.appendChild(cardText);
        cardBody.appendChild(selectBtn);
        card.appendChild(cardBody);
        col.appendChild(card);

        sceneList.appendChild(col);
    });

    // Populate characters
    state.characters.forEach(character => {
        const badge = document.createElement('span');
        badge.className = 'badge bg-secondary m-1';
        badge.textContent = character.name;

        characterList.appendChild(badge);
    });

    // Populate dialogues
    state.dialogues.forEach(dialogue => {
        const listItem = document.createElement('div');
        listItem.className = 'list-group-item';

        const speaker = document.createElement('strong');
        speaker.textContent = dialogue.speaker + ': ';

        const text = document.createTextNode(dialogue.text);

        listItem.appendChild(speaker);
        listItem.appendChild(text);

        dialogueList.appendChild(listItem);
    });
    
    // Enable/disable Generate Images button based on selection
    document.getElementById('generateImagesBtn').disabled = state.selectedScenes.length === 0;
}

// Select/Deselect all scenes
const selectAllCheckbox = document.getElementById('selectAllScenes');
selectAllCheckbox.addEventListener('change', function () {
    const sceneButtons = document.querySelectorAll('.scene-checkbox');
    const cardElements = document.querySelectorAll('#sceneList .card');
    
    sceneButtons.forEach((button, index) => {
        if (selectAllCheckbox.checked) {
            button.textContent = 'Deselect';
            cardElements[index].classList.add('border-primary');
            if (!state.selectedScenes.includes(state.scenes[index].id)) {
                state.selectedScenes.push(state.scenes[index].id);
            }
        } else {
            button.textContent = 'Select';
            cardElements[index].classList.remove('border-primary');
            state.selectedScenes = [];
        }
    });
    
    // Enable/disable Generate Images button based on selection
    document.getElementById('generateImagesBtn').disabled = state.selectedScenes.length === 0;
});

// Populate dialogue options for speech bubbles
function populateDialogueOptions() {
    speechBubbleOptions.innerHTML = '';

    // Get dialogues for selected scenes
    const relevantDialogues = state.dialogues.filter(dialogue => {
        return state.selectedScenes.includes(dialogue.sceneId);
    });

    relevantDialogues.forEach((dialogue, index) => {
        const listItem = document.createElement('div');
        listItem.className = 'form-check';

        const checkbox = document.createElement('input');
        checkbox.className = 'form-check-input';
        checkbox.type = 'checkbox';
        checkbox.value = dialogue.id;
        checkbox.id = `dialogue-${dialogue.id}`;

        const label = document.createElement('label');
        label.className = 'form-check-label';
        label.htmlFor = `dialogue-${dialogue.id}`;
        label.textContent = `${dialogue.speaker}: ${dialogue.text}`;

        listItem.appendChild(checkbox);
        listItem.appendChild(label);

        speechBubbleOptions.appendChild(listItem);
    });
}