// Initialize array to store video players
let players = [];
let resizeTimeout;
// Replace this with your new Base64-encoded API key
const API_KEY_BASE64 = '[API KEY-NO BRACKETS]'; // e.g., 'QUlTUJMKUAS2V5RXhhbXBsZTEyMzQ1Njc4OTA='
const API_KEY = atob(API_KEY_BASE64);

// Ensure script is running
console.log('script.js loaded');

// Function called when YouTube Iframe API is ready
function onYouTubeIframeAPIReady() {
    console.log("YouTube API ready");
    window.addEventListener('resize', debounce(adjustPlayerSizes, 200));
}

// DOMContentLoaded to attach event listeners
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOMContentLoaded event fired');

    // Load saved links from localStorage
    loadSavedLinks();

    // Theme toggle
    const themeToggle = document.querySelector('.theme-toggle');
    if (themeToggle) {
        console.log('Theme toggle found');
        themeToggle.addEventListener('click', () => {
            console.log('Theme toggle clicked');
            document.body.dataset.theme = document.body.dataset.theme === 'light' ? 'dark' : 'light';
            themeToggle.innerHTML = document.body.dataset.theme === 'light' ? '<i class="fas fa-moon"></i>' : '<i class="fas fa-sun"></i>';
        });
    } else {
        console.error('Theme toggle button not found');
    }

    // Textarea event listeners
    const videoUrlsTextarea = document.getElementById('videoUrls');
    if (videoUrlsTextarea) {
        console.log('Textarea #videoUrls found in script.js');
        videoUrlsTextarea.addEventListener('input', () => {
            console.log('Textarea input:', videoUrlsTextarea.value);
        });
        videoUrlsTextarea.addEventListener('keypress', (e) => {
            console.log('Keypress in textarea:', e.key);
            if (e.key === 'Enter') {
                e.preventDefault();
                console.log('Enter key pressed, calling loadVideos');
                loadVideos();
            }
        });
        videoUrlsTextarea.addEventListener('paste', (e) => {
            console.log('Paste event in textarea');
            setTimeout(() => {
                let value = videoUrlsTextarea.value.trim();
                if (value && !value.endsWith('\n')) {
                    videoUrlsTextarea.value = value + '\n';
                }
            }, 0);
        });
    } else {
        console.error('Textarea #videoUrls not found in script.js');
    }

    // Load button event listener (single source of truth)
    const loadBtn = document.getElementById('loadBtn');
    if (loadBtn) {
        console.log('Load button #loadBtn found in script.js');
        let isLoading = false; // Prevent multiple rapid calls
        loadBtn.addEventListener('click', () => {
            if (!isLoading) {
                console.log('Load button clicked (script.js listener)');
                isLoading = true;
                loadVideos();
                setTimeout(() => { isLoading = false; }, 1000); // Reset after 1 second
            } else {
                console.log('Load already in progress, ignoring click');
            }
        });
    } else {
        console.error('Load button #loadBtn not found in script.js');
    }

    // Click listener for saved links
    document.addEventListener('click', (e) => {
        if (e.target.matches('#savedLinks a')) {
            e.preventDefault();
            const url = e.target.dataset.url;
            const newIndex = players.length > 0 ? Math.max(...players.map((p, i) => p ? i : -1), -1) + 1 : 0;
            addVideoPlayer(url, newIndex);
            console.log(`Added video from saved link: ${url} at index ${newIndex}`);
        }
    });

    // Click listener for remove buttons
    document.addEventListener('click', (e) => {
        if (e.target.closest('.remove-btn')) {
            e.preventDefault();
            const outer = e.target.closest('.video-outer');
            const index = parseInt(outer.id.split('-')[1], 10);
            removeVideo(index);
            console.log(`Remove button clicked for index ${index}`);
        }
    });
});

// Function to load videos from the textarea
function loadVideos() {
    console.log("loadVideos function called");
    const errorMessage = document.getElementById('errorMessage');
    const videoUrlsTextarea = document.getElementById('videoUrls');
    
    if (!errorMessage || !videoUrlsTextarea) {
        console.error('Required DOM elements not found: errorMessage or videoUrls');
        return;
    }

    errorMessage.innerHTML = '';
    let urls = videoUrlsTextarea.value.split('\n').map(url => url.trim()).filter(url => url.length > 0);
    if (urls.length === 0) {
        errorMessage.innerHTML = 'No URLs provided.';
        videoUrlsTextarea.value = ''; // Clear immediately
        return;
    }
    // Remove duplicates
    urls = [...new Set(urls)];
    const maxIndex = players.length > 0 ? Math.max(...players.map((p, i) => p ? i : -1), -1) : -1;
    let nextIndex = maxIndex + 1;
    urls.forEach((url, i) => {
        const videoId = getVideoId(url);
        if (videoId) {
            const currentIndex = nextIndex + i;
            console.log(`Loading video ${currentIndex}: ${videoId}`);
            addVideoPlayer(url, currentIndex);
            saveLink(url, videoId);
            fetchVideoTitle(videoId, currentIndex, url);
        } else {
            errorMessage.innerHTML += `Invalid YouTube URL at line ${i + 1}.<br>`;
        }
    });
    videoUrlsTextarea.value = ''; // Clear after processing
    setTimeout(adjustPlayerSizes, 100);
}

// Function to add a video player to the page
function addVideoPlayer(url, index) {
    console.log(`addVideoPlayer called with url: ${url}, index: ${index}`);
    const videoId = getVideoId(url);
    if (!videoId) {
        console.error(`Invalid video ID for URL: ${url}`);
        return;
    }
    const outerDiv = document.createElement('div');
    outerDiv.className = 'video-outer';
    outerDiv.id = `outer-${index}`;
    const wrapperDiv = document.createElement('div');
    wrapperDiv.className = 'player-wrapper';
    wrapperDiv.id = `wrapper-${index}`;
    const playerDiv = document.createElement('div');
    playerDiv.className = 'player-frame';
    playerDiv.id = `player-${index}`;
    const removeBtn = document.createElement('button');
    removeBtn.className = 'remove-btn';
    removeBtn.innerHTML = '<i class="fas fa-times"></i>';
    wrapperDiv.appendChild(playerDiv);
    outerDiv.appendChild(wrapperDiv);
    outerDiv.appendChild(removeBtn);
    const videoContainer = document.getElementById('videoContainer');
    if (videoContainer) {
        videoContainer.appendChild(outerDiv);
    } else {
        console.error('Video container element not found in the DOM');
        return;
    }
    players[index] = new YT.Player(`player-${index}`, {
        width: '1200',
        videoId: videoId,
        playerVars: {
            'autoplay': 1,
            'playsinline': 1,
            'controls': 1
        },
        events: {
            'onReady': (event) => {
                console.log(`Player ${index} ready`);
                adjustPlayerSizes();
                event.target.mute();
                console.log(`Player ${index} auto-muted`);
            },
            'onError': (e) => {
                console.log(`Player ${index} error: ${e.data}`);
                const errorMessage = document.getElementById('errorMessage');
                if (errorMessage) {
                    errorMessage.innerHTML += `Video ${index + 1} failed to load and was removed.<br>`;
                }
                removeVideo(index);
            }
        }
    });
}

// Async function to fetch the video title using the YouTube API
async function fetchVideoTitle(videoId, index, url) {
    console.log(`Fetching title for video ${index}, ID: ${videoId}, URL: ${url}`);
    try {
        const response = await fetch(`https://www.googleapis.com/youtube/v3/videos?part=snippet&id=${videoId}&key=${API_KEY}`);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}, StatusText: ${response.statusText}`);
        }
        const data = await response.json();
        console.log(`API response for video ${index}:`, data);
        if (data.items && data.items.length > 0) {
            const title = data.items[0].snippet.title;
            console.log(`Title fetched for video ${index}: ${title}`);
            updateSavedLink(url, title);
        } else {
            console.warn(`No title found for video ${index}, ID: ${videoId}, Response:`, data);
            updateSavedLink(url, `Video ${index + 1} (Title unavailable)`);
        }
    } catch (error) {
        console.error(`Failed to fetch title for video ${index}, ID: ${videoId}, Error: ${error.message}`);
        updateSavedLink(url, `Video ${index + 1} (Title fetch failed: ${error.message})`);
    }
}

// Function to save a video link to localStorage
function saveLink(url, videoId) {
    console.log(`Saving link: ${url}`);
    let savedLinks = JSON.parse(localStorage.getItem('savedVideoLinks') || '[]');
    if (!savedLinks.some(link => link.url === url)) {
        savedLinks.push({ url, title: `Video ${videoId} (Loading...)` });
        localStorage.setItem('savedVideoLinks', JSON.stringify(savedLinks));
        loadSavedLinks();
    }
}

// Function to update a saved link’s title in localStorage
function updateSavedLink(url, title) {
    console.log(`Updating saved link title for URL ${url}: ${title}`);
    let savedLinks = JSON.parse(localStorage.getItem('savedVideoLinks') || '[]');
    const linkIndex = savedLinks.findIndex(link => link.url === url);
    if (linkIndex !== -1) {
        savedLinks[linkIndex].title = title;
        localStorage.setItem('savedVideoLinks', JSON.stringify(savedLinks));
        loadSavedLinks();
    }
}

// Function to load and display saved links from localStorage
function loadSavedLinks() {
    console.log('Loading saved links');
    const savedLinks = JSON.parse(localStorage.getItem('savedVideoLinks') || '[]');
    const savedLinksDiv = document.getElementById('savedLinks');
    if (savedLinksDiv) {
        savedLinksDiv.innerHTML = '';
        savedLinks.forEach(link => {
            const a = document.createElement('a');
            a.href = '#';
            a.dataset.url = link.url;
            a.textContent = link.title;
            savedLinksDiv.appendChild(a);
            savedLinksDiv.appendChild(document.createTextNode('\n')); // Preserve line breaks
        });
        addDeleteButtons();
        // Force reflow to ensure scrollbar appears
        const height = savedLinksDiv.scrollHeight;
        console.log(`#savedLinks height: ${height}px, links count: ${savedLinks.length}`);
        savedLinksDiv.style.display = 'none';
        savedLinksDiv.offsetHeight; // Trigger reflow
        savedLinksDiv.style.display = '';
    } else {
        console.error('Saved links div not found in the DOM');
    }
}

// Function to add delete buttons to saved links
function addDeleteButtons() {
    console.log('Adding delete buttons to saved links');
    const savedLinks = document.getElementById('savedLinks');
    if (savedLinks) {
        const links = savedLinks.getElementsByTagName('a');
        for (let link of links) {
            if (!link.querySelector('.delete-link')) {
                const deleteBtn = document.createElement('span');
                deleteBtn.className = 'delete-link';
                deleteBtn.innerHTML = '✕';
                deleteBtn.onclick = (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    link.remove();
                    updateLocalStorage();
                };
                link.appendChild(deleteBtn);
            }
        }
    } else {
        console.error('Saved links element not found when adding delete buttons');
    }
}

// Function to update localStorage after removing a link
function updateLocalStorage() {
    console.log('Updating localStorage after removing a link');
    const savedLinks = document.getElementById('savedLinks');
    if (savedLinks) {
        const links = savedLinks.getElementsByTagName('a');
        const updatedLinks = Array.from(links).map(link => ({
            url: link.dataset.url,
            title: link.textContent.replace(' ✕', '')
        }));
        localStorage.setItem('savedVideoLinks', JSON.stringify(updatedLinks));
    } else {
        console.error('Saved links element not found when updating localStorage');
    }
}

// Function to clear all saved links from localStorage
function clearSavedLinks() {
    console.log("Clearing saved links...");
    localStorage.removeItem('savedVideoLinks');
    const savedLinksDiv = document.getElementById('savedLinks');
    if (savedLinksDiv) {
        savedLinksDiv.innerHTML = '';
    } else {
        console.error('Saved links div not found when clearing links');
    }
}

// Function to save the video playlist to a file with options
function saveToFile() {
    console.log("Saving to file...");
    try {
        const savedLinks = JSON.parse(localStorage.getItem('savedVideoLinks') || '[]');
        console.log('Saved links before export:', savedLinks); // Debug log
        const errorMessage = document.getElementById('errorMessage');
        if (!errorMessage) {
            console.error('Error message element not found in the DOM');
            return;
        }

        if (savedLinks.length === 0) {
            errorMessage.innerHTML = 'No saved links to export.';
            return;
        }

        const choice = confirm("Save URLs as a .txt file? Click OK for .txt, Cancel for .html playlist.");
        
        if (choice) {
            const urlsText = savedLinks.map(link => link.url).join('\n');
            const blob = new Blob([urlsText], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'saved_urls.txt';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            console.log("URLs saved as text file successfully");
        } else {
            const videoUrls = JSON.stringify(savedLinks.map(link => link.url)); // Generate valid JSON array
            const scriptContent = `
                document.addEventListener('DOMContentLoaded', function() {
                    console.log('DOM fully loaded in saved_playlist.html');
                    const themeToggle = document.querySelector('.theme-toggle');
                    if (themeToggle) {
                        themeToggle.addEventListener('click', function() {
                            document.body.dataset.theme = document.body.dataset.theme === 'light' ? 'dark' : 'light';
                            themeToggle.innerHTML = document.body.dataset.theme === 'light' ? '<i class="fas fa-moon"></i>' : '<i class="fas fa-sun"></i>';
                            console.log('Theme switched to:', document.body.dataset.theme);
                        });
                    } else {
                        console.error('Theme toggle not found in saved_playlist.html');
                    }
                });

                let players = [];
                let resizeTimeout;
                const videoUrls = ${videoUrls};

                function getVideoId(url) {
                    const regExp = /.*(?:youtu.be\\/|v\\/|u\\/\\w\\/|embed\\/|watch\\?v=|&v=)([^#\\&\\?]*).*/;
                    const match = url.match(regExp);
                    return (match && match[1].length === 11) ? match[1] : null;
                }

                function onYouTubeIframeAPIReady() {
                    console.log('onYouTubeIframeAPIReady called, videoUrls:', videoUrls);
                    window.addEventListener('resize', debounce(adjustPlayerSizes, 200));
                    const videoContainer = document.getElementById('videoContainer');
                    if (videoContainer && videoUrls && Array.isArray(videoUrls)) {
                        videoUrls.forEach(function(url, index) {
                            const videoId = getVideoId(url);
                            if (videoId) {
                                console.log('Creating player for URL: ' + url + ', ID: ' + videoId);
                                const outerDiv = document.createElement('div');
                                outerDiv.className = 'video-outer';
                                outerDiv.id = 'outer-' + index;
                                const wrapperDiv = document.createElement('div');
                                wrapperDiv.className = 'player-wrapper';
                                wrapperDiv.id = 'wrapper-' + index;
                                const playerDiv = document.createElement('div');
                                playerDiv.className = 'player-frame';
                                playerDiv.id = 'player-' + index;
                                wrapperDiv.appendChild(playerDiv);
                                outerDiv.appendChild(wrapperDiv);
                                videoContainer.appendChild(outerDiv);
                                players[index] = new YT.Player('player-' + index, {
                                    videoId: videoId,
                                    playerVars: { 'autoplay': 1, 'playsinline': 1, 'controls': 1 },
                                    events: {
                                        'onReady': function(event) {
                                            console.log('Player ' + index + ' ready');
                                            adjustPlayerSizes();
                                            event.target.mute();
                                            console.log('Player ' + index + ' auto-muted');
                                        },
                                        'onError': function(e) {
                                            console.log('Player ' + index + ' error: ' + e.data);
                                        }
                                    }
                                });
                            } else {
                                console.error('Invalid video ID for URL:', url);
                            }
                        });
                    } else {
                        console.error('videoContainer or videoUrls is invalid:', { videoContainer, videoUrls });
                    }
                }

                function adjustPlayerSizes() {
                    console.log('Adjusting player sizes...');
                    const container = document.getElementById('videoContainer');
                    if (container) {
                        const outers = container.querySelectorAll('.video-outer');
                        console.log('Found outers:', outers.length);
                        if (outers.length === 0) {
                            console.warn('No .video-outer elements found');
                            return;
                        }
                        container.style.display = 'none';
                        container.offsetHeight;
                        container.style.display = '';
                        const containerWidth = container.clientWidth;
                        const minWidth = 280;
                        const maxWidth = 920;
                        const gap = 10;
                        const totalMaxWidthNeeded = outers.length * maxWidth + (outers.length - 1) * gap;
                        const optimalWidth = (containerWidth >= totalMaxWidthNeeded)
                            ? maxWidth
                            : Math.max(minWidth, Math.min(maxWidth, (containerWidth - (outers.length - 1) * gap) / Math.ceil(outers.length / 2)));
                        console.log('Container width: ' + containerWidth + ', Optimal width: ' + optimalWidth + ', Outers: ' + outers.length);
                        outers.forEach(function(outer) {
                            const index = parseInt(outer.id.split('-')[1], 10);
                            const player = players[index];
                            if (player) {
                                outer.style.width = optimalWidth + 'px';
                                const height = optimalWidth * (9 / 16);
                                player.setSize(optimalWidth, height);
                            }
                        });
                    } else {
                        console.error('videoContainer not found in adjustPlayerSizes');
                    }
                }

                function debounce(func, wait) {
                    return function() {
                        clearTimeout(resizeTimeout);
                        resizeTimeout = setTimeout(func, wait);
                    };
                }
            `;
            const htmlContent = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Saved Video Playlist</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH" crossorigin="anonymous">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css" rel="stylesheet" integrity="sha512-SnH5WK+bZxgPHs44uWIX+LLJAJ9/2PkPKZ5QiAj6Ta86w+fsb2TkcmfRyVX3pBnMFcV7oQPJkl9QevSCWr3W6A==" crossorigin="anonymous">
    <script src="https://www.youtube.com/iframe_api"></script>
    <style>
        :root {
            --primary-bg: #1a1a1a;
            --secondary-bg: #2c2c2c;
            --accent-color: #00aaff;
            --text-color: #e0e0e0;
            --shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
            --transition: all 0.3s ease;
            --error-color: #ff5555;
            --success-color: #55ff55;
            --button-bg: #555;
            --button-hover-bg: #777;
        }

        [data-theme="light"] {
            --primary-bg: #f0f0f0;
            --secondary-bg: #ffffff;
            --text-color: #333333;
            --shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            --button-bg: #cccccc;
            --button-hover-bg: #aaaaaa;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            background: linear-gradient(135deg, var(--primary-bg) 0%, var(--secondary-bg) 100%);
            color: var(--text-color);
            font-family: 'Segoe UI', system-ui, sans-serif;
            display: flex;
            flex-direction: column;
            min-height: 100vh;
            margin: 0;
            transition: background var(--transition);
            data-theme="dark";
        }

        .header-row {
            grid-area: header;
            background: var(--secondary-bg);
            padding: 1rem;
            text-align: center;
            box-shadow: var(--shadow);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .header-row h1 {
            font-size: 1.75rem;
            font-weight: 700;
            letter-spacing: 1px;
            text-transform: uppercase;
            color: var(--text-color);
            margin: 0;
        }

        .theme-toggle {
            background: none;
            border: none;
            color: var(--text-color);
            font-size: 1.5rem;
            cursor: pointer;
            transition: var(--transition);
        }

        .theme-toggle:hover {
            color: var(--accent-color);
            transform: scale(1.1);
        }

        .video-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            column-gap: 10px;
            row-gap: 10px;
            flex-grow: 0;
            padding: 10px;
            background: rgba(0, 0, 0, 0.5);
            border-radius: 10px;
            box-shadow: var(--shadow);
            margin: 20px 10px;
        }

        .video-outer {
            position: relative;
            width: calc(50% - 5px);
            max-width: 920px;
            transition: width var(--transition);
            background: #333;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
        }

        .player-wrapper {
            width: 100%;
            aspect-ratio: 16 / 9;
        }

        .player-frame {
            width: 100%;
            height: 100%;
            background: #222;
        }

        .footer-row {
            grid-area: footer;
            background: var(--secondary-bg);
            padding: 1rem;
            text-align: center;
            box-shadow: var(--shadow);
        }

        .footer-row p {
            font-size: 0.9rem;
            opacity: 0.8;
            margin: 0;
        }

        @media (max-width: 768px) {
            .video-outer {
                width: 100%;
            }
        }
    </style>
    <body>
        <div class="header-row">
            <h1>Saved Video Playlist</h1>
            <button class="theme-toggle" aria-label="Toggle theme">
                <i class="fas fa-moon"></i>
            </button>
        </div>
        <div id="videoContainer" class="video-container"></div>
        <div class="footer-row">
            <p>Powered by xAI | @SilentJim1980 | © 2025</p>
        </div>
        <script>${scriptContent}</script>
    </body>
</html>
            `.trim();
            console.log('HTML content before blob:', htmlContent); // Debug log
            const blob = new Blob([htmlContent], { type: 'text/html' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'saved_playlist.html';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            console.log("HTML playlist saved successfully");
        }
    } catch (error) {
        console.error('Error in saveToFile:', error);
    }
}

// Function to refresh all videos
function refreshAll() {
    console.log("Refreshing all videos...");
    players.forEach(player => {
        if (player && player.seekTo) {
            player.seekTo(0);
            player.playVideo();
        }
    });
}

// Function to adjust the sizes of video players responsively
function adjustPlayerSizes() {
    console.log("Adjusting player sizes...");
    const container = document.getElementById('videoContainer');
    const outers = container.querySelectorAll('.video-outer');
    if (outers.length === 0) return;
    container.style.display = 'none';
    container.offsetHeight;
    container.style.display = '';
    const containerWidth = container.clientWidth;
    const minWidth = 280;
    const maxWidth = 920;
    const gap = 10;
    const totalMaxWidthNeeded = outers.length * maxWidth + (outers.length - 1) * gap;
    const optimalWidth = (containerWidth >= totalMaxWidthNeeded)
        ? maxWidth
        : Math.max(minWidth, Math.min(maxWidth, (containerWidth - (outers.length - 1) * gap) / Math.ceil(outers.length / 2)));
    console.log(`Container width: ${containerWidth}, Optimal width: ${optimalWidth}, Outers: ${outers.length}`);
    outers.forEach(outer => {
        const index = parseInt(outer.id.split('-')[1], 10);
        const player = players[index];
        if (player) {
            outer.style.width = `${optimalWidth}px`;
            const height = optimalWidth * (9 / 16);
            player.setSize(optimalWidth, height);
        }
    });
}

// Function to remove a video from the page
function removeVideo(index) {
    console.log(`Removing video ${index}`);
    const outer = document.getElementById(`outer-${index}`);
    if (outer) {
        if (players[index] && players[index].destroy) {
            players[index].destroy();
            console.log(`Player ${index} destroyed`);
        }
        outer.remove();
        console.log(`Outer div ${index} removed`);
        players[index] = null;
        setTimeout(adjustPlayerSizes, 100);
        setTimeout(() => {
            const remainingOuters = document.getElementById('videoContainer').querySelectorAll('.video-outer');
            console.log(`Remaining video-outer elements: ${remainingOuters.length}, active players: ${players.filter(p => p !== null).length}, total players array length: ${players.length}`);
        }, 150);
    } else {
        console.log(`Video ${index} not found in DOM, cleaning up array`);
        players[index] = null;
        setTimeout(adjustPlayerSizes, 100);
    }
}

// Function to extract video ID from a YouTube URL
function getVideoId(url) {
    const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|\&v=)([^#\&\?]*).*/;
    const match = url.match(regExp);
    return (match && match[2].length === 11) ? match[2] : null;
}

// Function to play all videos
function playAll() {
    console.log("Playing all");
    players.forEach(player => {
        if (player && player.playVideo) {
            player.playVideo();
        }
    });
}

// Function to pause all videos
function pauseAll() {
    console.log("Pausing all");
    players.forEach(player => {
        if (player && player.pauseVideo) {
            player.pauseVideo();
        }
    });
}

// Function to mute all videos
function muteAll() {
    console.log("Muting all");
    document.getElementById('videoContainer').querySelectorAll('.video-outer').forEach(outer => {
        const index = parseInt(outer.id.split('-')[1], 10);
        const player = players[index];
        if (player && typeof player.mute === 'function') {
            player.mute();
            console.log(`Muted player ${index}`);
        }
    });
}

// Function to unmute all videos
function unmuteAll() {
    console.log("Unmuting all");
    document.getElementById('videoContainer').querySelectorAll('.video-outer').forEach(outer => {
        const index = parseInt(outer.id.split('-')[1], 10);
        const player = players[index];
        if (player && typeof player.unMute === 'function') {
            player.unMute();
            console.log(`Unmuted player ${index}`);
        }
    });
}

// Function to debounce resize events
function debounce(func, wait) {
    return function() {
        clearTimeout(resizeTimeout);
        resizeTimeout = setTimeout(func, wait);
    };
}

console.log('script.js fully parsed'); // Debugging to confirm script completion