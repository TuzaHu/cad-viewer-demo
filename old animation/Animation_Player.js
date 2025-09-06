class DynamicAnimationPlayer {
    constructor() {
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.backgroundTexture = null;
        this.animationTexture = null;
        this.backgroundMesh = null;
        this.animationMesh = null;
        
        this.currentState = 'reset';
        this.currentSequence = null;
        this.currentFrame = 0;
        this.totalFrames = 0;
        this.isPlaying = false;
        this.isReversed = false;
        this.frameRate = 15;
        this.lastFrameTime = 0;
        this.fps = 0;
        this.lastFpsUpdate = 0;
        this.frameCount = 0;
        
        this.textureCache = new Map();
        this.preloadedSequences = new Set();
        
        // Base folder structure
        this.basePath = 'Renders/';
        
        // Will be populated by scanning folders
        this.sequences = {};
        
        this.init();
    }
    
    async init() {
        try {
            this.showLoading(true, 'Loading animation player...');
            await this.initThreeJS();
            await this.scanForSequences();
            this.setupEventListeners();
            this.startPerformanceMonitoring();
            this.showNotification('Animation player ready', 'success');
            this.showLoading(false);
        } catch (error) {
            console.error('Initialization error:', error);
            console.error('Error details:', error.message, error.stack);
            this.showNotification('Failed to load animation sequences', 'error');
            this.showLoading(false);
        }
    }
    
    async initThreeJS() {
        // Create scene
        this.scene = new THREE.Scene();
        
        // Create camera - will be adjusted when background loads
        this.camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.1, 1000);
        this.camera.position.z = 1;
        
        // Create renderer with better settings
        this.renderer = new THREE.WebGLRenderer({ 
            canvas: document.getElementById('canvas'),
            alpha: false,
            antialias: true,
            powerPreference: "high-performance"
        });
        
        // Set renderer size to match background image aspect ratio
        const backgroundAspectRatio = 1488 / 1052; // Background image dimensions
        const windowAspectRatio = window.innerWidth / window.innerHeight;
        
        let renderWidth, renderHeight;
        if (windowAspectRatio > backgroundAspectRatio) {
            // Window is wider than background - fit to height
            renderHeight = window.innerHeight;
            renderWidth = renderHeight * backgroundAspectRatio;
        } else {
            // Window is taller than background - fit to width
            renderWidth = window.innerWidth;
            renderHeight = renderWidth / backgroundAspectRatio;
        }
        
        this.renderer.setSize(renderWidth, renderHeight);
        this.renderer.setClearColor(0x000000, 1);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        
        // Canvas will be centered by CSS
        
        // Create animation plane
        this.createAnimationPlane();
        
        // Load background
        await this.loadBackground();
        
        // Start render loop
        this.animate();
        
        // Handle window resize
        window.addEventListener('resize', () => this.onWindowResize(), { passive: true });
    }
    
    createAnimationPlane() {
        // Create animation plane to match background image aspect ratio (1488x1052)
        const aspectRatio = 1488 / 1052;
        const geometry = new THREE.PlaneGeometry(2 * aspectRatio, 2);
        const material = new THREE.MeshBasicMaterial({ 
            transparent: true,
            alphaTest: 0.1
        });
        
        this.animationMesh = new THREE.Mesh(geometry, material);
        this.animationMesh.visible = false;
        this.scene.add(this.animationMesh);
    }
    
    async loadBackground() {
        return new Promise((resolve, reject) => {
            console.log('Loading background image...');
            const textureLoader = new THREE.TextureLoader();
            textureLoader.load('/Renders/Background.png', (texture) => {
                console.log('Background texture loaded successfully');
                this.backgroundTexture = texture;
                this.backgroundTexture.minFilter = THREE.LinearFilter;
                this.backgroundTexture.magFilter = THREE.LinearFilter;
                
                // Set camera to match background image dimensions exactly
                const aspectRatio = texture.image.width / texture.image.height; // 1488/1052 ≈ 1.415
                
                // Set camera bounds to match the background image aspect ratio
                this.camera.left = -aspectRatio;
                this.camera.right = aspectRatio;
                this.camera.top = 1;
                this.camera.bottom = -1;
                this.camera.updateProjectionMatrix();
                
                // Create background plane with proper aspect ratio
                const geometry = new THREE.PlaneGeometry(2 * aspectRatio, 2);
                const material = new THREE.MeshBasicMaterial({ 
                    map: this.backgroundTexture,
                    transparent: false
                });
                this.backgroundMesh = new THREE.Mesh(geometry, material);
                this.backgroundMesh.position.z = -0.1;
                this.scene.add(this.backgroundMesh);
                
                this.updateStatus('Background loaded');
                console.log('Background mesh added to scene');
                
                // Force a render
                this.renderer.render(this.scene, this.camera);
                resolve();
                
            }, undefined, (error) => {
                console.error('Error loading background:', error);
                this.updateStatus('Error loading background');
                
                // Create a colored background as fallback
                const geometry = new THREE.PlaneGeometry(2, 2);
                const material = new THREE.MeshBasicMaterial({ color: 0x444444 });
                this.backgroundMesh = new THREE.Mesh(geometry, material);
                this.backgroundMesh.position.z = -0.1;
                this.scene.add(this.backgroundMesh);
                this.renderer.render(this.scene, this.camera);
                reject(error);
            });
        });
    }
    
    async scanForSequences() {
        console.log('scanForSequences called');
        this.showLoading(true, 'Scanning for animation sequences...');
        this.updateStatus('Scanning folders...');
        
        try {
            console.log('Starting real folder scan...');
            // Real implementation: scan actual Renders/ folder
            const detectedSequences = await this.scanRendersFolder();
            console.log('Detected sequences:', detectedSequences);
            
            if (Object.keys(detectedSequences).length > 0) {
                console.log('Using detected sequences');
                this.sequences = detectedSequences;
                this.updateStatus('Ready');
                this.showNotification(`Found ${Object.keys(this.sequences).length} animation sequences`, 'success');
            } else {
                console.log('No sequences detected, throwing error');
                throw new Error('No sequences detected');
            }
        } catch (error) {
            console.warn('Real scanning failed:', error);
            console.warn('Error details:', error.message, error.stack);
            this.showNotification('Failed to scan animation sequences', 'error');
            this.updateStatus('Error loading sequences');
        }
    }
    
    async scanRendersFolder() {
        console.log('Starting real folder scan...');
        
        // Get list of folders in Renders directory
        const folders = await this.getFoldersInRenders();
        const sequences = {};
        
        for (const folder of folders) {
            try {
                const sequenceInfo = await this.analyzeSequenceFolder(folder);
                if (sequenceInfo) {
                    sequences[folder] = sequenceInfo;
                    console.log(`Analyzed ${folder}: ${sequenceInfo.frames} frames, start: ${sequenceInfo.startFrame}, padded: ${sequenceInfo.padded}`);
                }
            } catch (error) {
                console.warn(`Failed to analyze folder ${folder}:`, error);
            }
        }
        
        console.log(`Found ${Object.keys(sequences).length} sequences from Renders/ folder`);
        console.log('Sequences:', Object.keys(sequences));
        
        return sequences;
    }
    
    async getFoldersInRenders() {
        // Since we can't directly list directories from browser, we'll try to detect folders
        // by testing common folder names that might exist
        const possibleFolders = [
            'Rest_Top', 'Rest_Right', 'Rest_front', 'Rest_front_reverse', 'Rest_Right_reverse', 'Rest_Top_reverse',
            'top_front', 'top_front_reverse', 'top_right', 'front_right', 'Play', 'New_Play',
            'Rest_top_front', 'Rest_top_front_reverse', 'newcon', 'newcon_renamed', 'new Rest front'
        ];
        
        const existingFolders = [];
        
        for (const folder of possibleFolders) {
            const testPath = `/Renders/${folder}/`;
            if (await this.folderExists(testPath)) {
                existingFolders.push(folder);
            }
        }
        
        return existingFolders;
    }
    
    async folderExists(folderPath) {
        // Test if folder exists by trying to load a test image
        const testPaths = [
            `${folderPath}0001.png`,
            `${folderPath}0000.png`,
            `${folderPath}1.png`,
            `${folderPath}10.png`
        ];
        
        for (const testPath of testPaths) {
            try {
                const response = await fetch(testPath, { method: 'HEAD' });
                if (response.ok) {
                    return true;
                }
            } catch (error) {
                // Continue to next test path
            }
        }
        
        return false;
    }
    
    async analyzeSequenceFolder(folderName) {
        const folderPath = `/Renders/${folderName}/`;
        
        // Try different patterns to find the actual files
        const patterns = [
            { startFrame: 0, padded: true, padLength: 4 },   // 0000.png, 0001.png, ...
            { startFrame: 1, padded: true, padLength: 4 },   // 0001.png, 0002.png, ...
            { startFrame: 1, padded: false, padLength: 0 },  // 1.png, 2.png, ...
            { startFrame: 10, padded: false, padLength: 0 }  // 10.png, 11.png, ...
        ];
        
        for (const pattern of patterns) {
            const sequenceInfo = await this.testPattern(folderPath, pattern);
            if (sequenceInfo) {
                return {
                    path: folderPath,
                    frames: sequenceInfo.frames,
                    startFrame: pattern.startFrame,
                    padded: pattern.padded,
                    padLength: pattern.padLength,
                    suffix: '.png'
                };
            }
        }
        
        return null;
    }
    
    async testPattern(folderPath, pattern) {
        let frameCount = 0;
        let currentFrame = pattern.startFrame;
        
        // Test up to 500 frames to find the sequence length
        while (frameCount < 500) {
            const frameNumber = currentFrame + frameCount;
            const paddedFrame = pattern.padded ? 
                frameNumber.toString().padStart(pattern.padLength, '0') : 
                frameNumber.toString();
            const framePath = `${folderPath}${paddedFrame}.png`;
            
            try {
                const response = await fetch(framePath, { method: 'HEAD' });
                if (!response.ok) {
                    break; // Frame doesn't exist, we've found the end
                }
                frameCount++;
            } catch (error) {
                break; // Error loading frame, we've found the end
            }
        }
        
        // Only return if we found at least 10 frames (reasonable minimum)
        if (frameCount >= 10) {
            return { frames: frameCount };
        }
        
        return null;
    }
    
    async testImageExists(imagePath) {
        try {
            const response = await fetch(imagePath, { method: 'HEAD' });
            return response.ok;
        } catch (error) {
            console.warn(`Failed to test image ${imagePath}:`, error);
            return false;
        }
    }
    
    startPerformanceMonitoring() {
        // Simple FPS monitoring
        setInterval(() => {
            this.fps = Math.round(1000 / (performance.now() - this.lastFpsUpdate));
            this.lastFpsUpdate = performance.now();
            
            const fpsElement = document.getElementById('fps-counter');
            if (fpsElement) {
                fpsElement.textContent = `${this.fps} FPS`;
            }
        }, 1000);
        
        console.log('Performance monitoring started');
    }
    
    // Add the missing animation functions from app.js
    async goToState(targetState) {
        console.log(`Going from ${this.currentState} to ${targetState}`);
        
        if (targetState === 'reset') {
            const transition = this.getTransitionPath(this.currentState, 'reset');
            if (transition) {
                console.log('Playing reverse animation to rest position...');
                this.animationMesh.visible = true;
                await this.executeTransition(transition);
                this.currentState = 'reset';
                this.animationMesh.visible = false;
                this.updateStatus('At rest position');
                return;
            }
        }
        
        const transition = this.getTransitionPath(this.currentState, targetState);
        
        if (transition) {
            await this.executeTransition(transition);
            this.currentState = targetState;
        } else {
            this.updateStatus('No transition path available');
        }
    }
    
    getTransitionPath(fromState, toState) {
        // Map the detected sequences to the original transition logic
        const transitions = {
            'reset': {
                'front': { type: 'direct', sequence: 'Rest_front', reverse: false },
                'top': { type: 'direct', sequence: 'Rest_Top', reverse: false },
                'right': { type: 'direct', sequence: 'Rest_Right', reverse: false }
            },
            'front': {
                'reset': { type: 'direct', sequence: 'Rest_front', reverse: true },
                'top': { type: 'direct', sequence: 'top_front_reverse', reverse: false },
                'right': { type: 'direct', sequence: 'front_right', reverse: false }
            },
            'top': {
                'reset': { type: 'direct', sequence: 'Rest_Top', reverse: true },
                'front': { type: 'direct', sequence: 'top_front', reverse: false },
                'right': { type: 'direct', sequence: 'top_right', reverse: false }
            },
            'right': {
                'reset': { type: 'direct', sequence: 'Rest_Right', reverse: true },
                'front': { type: 'direct', sequence: 'front_right', reverse: true },
                'top': { type: 'direct', sequence: 'top_right', reverse: true }
            }
        };
        
        const transition = transitions[fromState] && transitions[fromState][toState];
        if (transition && !this.sequences[transition.sequence]) {
            console.error(`Sequence ${transition.sequence} not found in available sequences:`, Object.keys(this.sequences));
            return null;
        }
        return transition;
    }
    
    async executeTransition(transition) {
        if (transition.type === 'direct') {
            await this.playDirectSequence(transition.sequence, transition.reverse);
        }
    }
    
    async playDirectSequence(sequenceName, reverse = false) {
        console.log(`Playing sequence: ${sequenceName}, reverse: ${reverse}`);
        console.log('Available sequences:', Object.keys(this.sequences));
        
        if (!this.sequences[sequenceName]) {
            console.error(`Sequence ${sequenceName} not found in available sequences:`, Object.keys(this.sequences));
            this.updateStatus(`Sequence ${sequenceName} not found`);
            return;
        }
        
        const sequence = this.sequences[sequenceName];
        console.log('Sequence details:', sequence);
        
        this.currentSequence = sequenceName;
        this.currentFrame = reverse ? sequence.frames : 0; // Start at 0, not 1
        this.totalFrames = sequence.frames;
        this.isPlaying = true;
        this.isReversed = reverse;
        this.lastFrameTime = performance.now(); // Reset frame timing
        
        this.animationMesh.visible = true;
        this.updateStatus(`Playing ${sequenceName}...`);
        
        try {
            const firstFrameToLoad = reverse ? this.totalFrames : 1;
            console.log(`Loading first frame: ${firstFrameToLoad} from path: ${sequence.path}`);
            await this.loadFrame(firstFrameToLoad);
            
            await this.waitForAnimationComplete();
            
        } catch (error) {
            console.error('Error loading sequence:', error);
            this.updateStatus(`Error loading sequence: ${error.message}`);
        }
    }
    
    async loadFrame(frameNumber) {
        if (!this.currentSequence) {
            console.error('No current sequence set');
            return;
        }
        
        const sequence = this.sequences[this.currentSequence];
        if (!sequence) {
            console.error(`Sequence ${this.currentSequence} not found`);
            return;
        }
        
        const startFrame = sequence.startFrame || 1;
        const actualFrameNumber = startFrame + frameNumber - 1;
        const paddedFrame = sequence.padded === false ? 
            actualFrameNumber.toString() : 
            actualFrameNumber.toString().padStart(sequence.padLength || 4, '0');
        const framePath = `${sequence.path}${paddedFrame}${sequence.suffix}`;
        
        console.log(`Loading frame: ${framePath}`);
        
        return new Promise((resolve, reject) => {
            const textureLoader = new THREE.TextureLoader();
            textureLoader.load(framePath, (texture) => {
                console.log(`Successfully loaded frame: ${framePath}`);
                texture.minFilter = THREE.LinearFilter;
                texture.magFilter = THREE.LinearFilter;
                this.animationTexture = texture;
                this.animationMesh.material.map = texture;
                this.animationMesh.material.needsUpdate = true;
                resolve();
            }, undefined, (error) => {
                console.error(`Error loading frame ${frameNumber} from ${framePath}:`, error);
                reject(new Error(`Failed to load frame ${frameNumber}: ${error.message || error}`));
            });
        });
    }
    
    loadFrameSync(frameNumber) {
        if (!this.currentSequence) return;
        
        const sequence = this.sequences[this.currentSequence];
        const startFrame = sequence.startFrame || 1;
        const actualFrameNumber = startFrame + frameNumber - 1;
        const paddedFrame = sequence.padded === false ? 
            actualFrameNumber.toString() : 
            actualFrameNumber.toString().padStart(sequence.padLength || 4, '0');
        const framePath = `${sequence.path}${paddedFrame}${sequence.suffix}`;
        
        console.log(`Loading frame: ${framePath} (frameNumber: ${frameNumber}, actualFrameNumber: ${actualFrameNumber})`);
        
        const textureLoader = new THREE.TextureLoader();
        textureLoader.load(framePath, (texture) => {
            console.log(`Successfully loaded frame: ${framePath}`);
            texture.minFilter = THREE.LinearFilter;
            texture.magFilter = THREE.LinearFilter;
            this.animationTexture = texture;
            this.animationMesh.material.map = texture;
            this.animationMesh.material.needsUpdate = true;
        }, undefined, (error) => {
            console.error(`Error loading frame ${frameNumber} from ${framePath}:`, error);
        });
    }
    
    async waitForAnimationComplete() {
        return new Promise((resolve) => {
            const checkComplete = () => {
                if (!this.isPlaying) {
                    resolve();
                } else {
                    setTimeout(checkComplete, 100);
                }
            };
            checkComplete();
        });
    }
    
    async playFullSequence() {
        console.log('Playing PLAY + Rest_Right_reverse sequence');
        this.updateStatus('Playing PLAY + Rest_Right_reverse sequence...');
        
        try {
            console.log('Playing Play sequence (232 frames)');
            await this.playDirectSequence('Play', false);
            
            console.log('Playing Rest_Right_reverse sequence (72 frames)');
            await this.playDirectSequence('Rest_Right_reverse', false);
            
            this.updateStatus('PLAY + Rest_Right_reverse sequence completed!');
            this.animationMesh.visible = false;
            this.currentState = 'reset';
            
        } catch (error) {
            console.error('Error playing complete sequence:', error);
            this.updateStatus('Error playing complete sequence');
        }
    }
    
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    
    async playSequence(sequenceName, reverse = false) {
        const sequence = this.sequences[sequenceName];
        if (!sequence) {
            this.showNotification(`Sequence "${sequenceName}" not found`, 'error');
            return;
        }
        
        this.currentSequence = sequenceName;
        this.updateStatus(`Playing ${sequenceName} ${reverse ? 'in reverse' : ''}`);
        
        // For demo purposes, we'll simulate playing the sequence
        this.totalFrames = sequence.frames;
        this.currentFrame = reverse ? this.totalFrames - 1 : 0;
        this.isPlaying = true;
        this.isReversed = reverse;
        
        this.updateProgress();
        this.updateFrameInfo();
        
        // Simulate animation playback
        const interval = setInterval(() => {
            if (this.isReversed) {
                this.currentFrame--;
                if (this.currentFrame < 0) {
                    clearInterval(interval);
                    this.isPlaying = false;
                    this.updateStatus('Playback completed');
                    this.showNotification('Playback completed', 'success');
                }
            } else {
                this.currentFrame++;
                if (this.currentFrame >= this.totalFrames) {
                    clearInterval(interval);
                    this.isPlaying = false;
                    this.updateStatus('Playback completed');
                    this.showNotification('Playback completed', 'success');
                }
            }
            
            this.updateProgress();
            this.updateFrameInfo();
        }, 1000 / this.frameRate);
    }
    
    updateCameraAspect(aspectRatio) {
        const windowAspect = window.innerWidth / window.innerHeight;
        
        if (windowAspect > aspectRatio) {
            this.camera.left = -windowAspect;
            this.camera.right = windowAspect;
            this.camera.top = 1;
            this.camera.bottom = -1;
        } else {
            this.camera.left = -1;
            this.camera.right = 1;
            this.camera.top = 1 / windowAspect;
            this.camera.bottom = -1 / windowAspect;
        }
        
        this.camera.updateProjectionMatrix();
    }
    
    animate() {
        requestAnimationFrame(() => this.animate());
        
        const currentTime = performance.now();
        const deltaTime = currentTime - this.lastFrameTime;
        
        if (this.isPlaying && this.currentSequence && deltaTime >= (1000 / this.frameRate)) {
            this.lastFrameTime = currentTime;
            
            if (this.isReversed) {
                this.currentFrame--;
                if (this.currentFrame < 1) {
                    this.isPlaying = false;
                    this.updateStatus('Reverse playback completed');
                    return;
                }
            } else {
                this.currentFrame++;
                if (this.currentFrame > this.totalFrames) {
                    this.isPlaying = false;
                    this.updateStatus('Playback completed');
                    return;
                }
            }
            
            const frameToLoad = Math.max(1, Math.min(this.currentFrame, this.totalFrames));
            console.log(`Loading frame ${frameToLoad} (currentFrame: ${this.currentFrame}, totalFrames: ${this.totalFrames})`);
            
            // Load frame synchronously to prevent animation from skipping ahead
            this.loadFrameSync(frameToLoad);
            this.updateProgress((this.currentFrame - 1) / (this.totalFrames - 1));
        }
        
        // Always render the scene
        this.renderer.render(this.scene, this.camera);
    }
    
    onWindowResize() {
        const backgroundAspectRatio = 1488 / 1052; // Background image dimensions
        const windowAspectRatio = window.innerWidth / window.innerHeight;
        
        // Resize renderer to maintain background aspect ratio
        let renderWidth, renderHeight;
        if (windowAspectRatio > backgroundAspectRatio) {
            // Window is wider than background - fit to height
            renderHeight = window.innerHeight;
            renderWidth = renderHeight * backgroundAspectRatio;
        } else {
            // Window is taller than background - fit to width
            renderWidth = window.innerWidth;
            renderHeight = renderWidth / backgroundAspectRatio;
        }
        
        this.renderer.setSize(renderWidth, renderHeight);
        
        // Update camera to match background aspect ratio
        this.camera.left = -backgroundAspectRatio;
        this.camera.right = backgroundAspectRatio;
        this.camera.top = 1;
        this.camera.bottom = -1;
        this.camera.updateProjectionMatrix();
    }
    
    updateProgress() {
        if (this.totalFrames > 0) {
            const progress = this.currentFrame / (this.totalFrames - 1);
            document.getElementById('progress-bar').style.width = `${progress * 100}%`;
        }
    }
    
    updateFrameInfo() {
        document.getElementById('frame-info').textContent = 
            `Frame: ${this.currentFrame + 1}/${this.totalFrames}`;
    }
    
    updateFpsCounter() {
        document.getElementById('fps-counter').textContent = `${this.fps} FPS`;
    }
    
    updateStatus(message) {
        document.getElementById('status').textContent = message;
    }
    
    showLoading(show, message = 'Loading...') {
        const loading = document.getElementById('loading');
        if (loading) {
            loading.style.display = show ? 'flex' : 'none';
            if (message) {
                loading.innerHTML = `<div class="spinner"></div><div>${message}</div>`;
            }
        }
    }
    
    showNotification(message, type = 'info') {
        const notification = document.getElementById('notification');
        if (notification) {
            notification.textContent = message;
            notification.className = 'notification show';
            
            // Style based on type
            if (type === 'error') {
                notification.style.borderLeftColor = '#ff6b6b';
            } else if (type === 'warning') {
                notification.style.borderLeftColor = '#ffc107';
            } else if (type === 'success') {
                notification.style.borderLeftColor = '#00c853';
            } else {
                notification.style.borderLeftColor = '#667eea';
            }
            
            // Auto hide after 3 seconds
            setTimeout(() => {
                notification.className = 'notification';
            }, 3000);
        }
    }
    
    setupEventListeners() {
        document.getElementById('goToTop').addEventListener('click', () => {
            this.goToState('top');
        });
        
        document.getElementById('goToFront').addEventListener('click', () => {
            this.goToState('front');
        });
        
        document.getElementById('goToRight').addEventListener('click', () => {
            this.goToState('right');
        });
        
        document.getElementById('goToReset').addEventListener('click', () => {
            this.goToState('reset');
        });
        
        document.getElementById('playSequence').addEventListener('click', () => {
            this.playFullSequence();
        });
    }
}

// Initialize the application
window.addEventListener('load', () => {
    window.animationPlayer = new DynamicAnimationPlayer();
});