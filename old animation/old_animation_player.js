class EnhancedAnimationPlayer {
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
        
        // Available animation sequences
        this.sequences = {
            'restTop': { path: 'Renders/Rest_Top/', frames: 72, suffix: '.png' },
            'restRight': { path: 'Renders/Rest_Right/', frames: 72, suffix: '.png' },
            'restFront': { path: 'Renders/Rest_front/', frames: 73, suffix: '.png' },
            'topFront': { path: 'Renders/top_front/', frames: 97, startFrame: 1, padded: false, suffix: '.png' },
            'topFrontReverse': { path: 'Renders/top_front_reverse/', frames: 73, suffix: '.png' },
            'restTopFront': { path: 'Renders/Rest_top_front/', frames: 144, suffix: '.png' },
            'frontRight': { path: 'Renders/front_right/', frames: 73, startFrame: 1, padded: false, suffix: '.png' },
            'topRight': { path: 'Renders/top_right/', frames: 72, startFrame: 1, padded: false, suffix: '.png' },
            'play': { path: 'Renders/Play/', frames: 232, startFrame: 1, padded: true, suffix: '.png' },
            'restRightReverse': { path: 'Renders/Rest_Right_reverse/', frames: 72, suffix: '.png' }
        };
        
        this.init();
    }
    
    async init() {
        try {
            this.showLoading(true, 'Initialiserer animasjonsspiller...');
            await this.initThreeJS();
            await this.preloadCriticalSequences();
            this.setupEventListeners();
            this.startPerformanceMonitoring();
            this.showNotification('Animasjonsspiller klar', 'success');
            this.showLoading(false);
        } catch (error) {
            console.error('Initialization error:', error);
            this.showNotification('Feil under initialisering', 'error');
            this.showLoading(false);
        }
    }
    
    async initThreeJS() {
        // Create scene
        this.scene = new THREE.Scene();
        
        // Create camera
        this.camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.1, 1000);
        this.camera.position.z = 1;
        
        // Create renderer with better settings
        this.renderer = new THREE.WebGLRenderer({ 
            canvas: document.getElementById('canvas'),
            alpha: false,
            antialias: true,
            powerPreference: "high-performance"
        });
        
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setClearColor(0x000000, 1);
        this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        
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
        const geometry = new THREE.PlaneGeometry(2, 2);
        const material = new THREE.MeshBasicMaterial({ 
            transparent: true,
            alphaTest: 0.1
        });
        
        this.animationMesh = new THREE.Mesh(geometry, material);
        this.animationMesh.visible = false;
        this.scene.add(this.animationMesh);
    }
    
    async loadBackground() {
        return new Promise((resolve) => {
            const textureLoader = new THREE.TextureLoader();
            textureLoader.load('Renders/Background.png', (texture) => {
                this.backgroundTexture = texture;
                this.backgroundTexture.minFilter = THREE.LinearFilter;
                this.backgroundTexture.magFilter = THREE.LinearFilter;
                
                const aspectRatio = texture.image.width / texture.image.height;
                this.updateCameraAspect(aspectRatio);
                
                const geometry = new THREE.PlaneGeometry(2 * aspectRatio, 2);
                const material = new THREE.MeshBasicMaterial({ 
                    map: this.backgroundTexture,
                    transparent: false
                });
                
                this.backgroundMesh = new THREE.Mesh(geometry, material);
                this.backgroundMesh.position.z = -0.1;
                this.scene.add(this.backgroundMesh);
                
                resolve();
            }, undefined, () => {
                // Fallback background
                const geometry = new THREE.PlaneGeometry(2, 2);
                const material = new THREE.MeshBasicMaterial({ color: 0x222222 });
                this.backgroundMesh = new THREE.Mesh(geometry, material);
                this.backgroundMesh.position.z = -0.1;
                this.scene.add(this.backgroundMesh);
                resolve();
            });
        });
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
    
    async preloadCriticalSequences() {
        // Preload the most common sequences for better performance
        const criticalSequences = ['restTop', 'restFront', 'restRight', 'play'];
        
        for (const seqName of criticalSequences) {
            try {
                await this.preloadSequence(seqName);
                this.preloadedSequences.add(seqName);
            } catch (error) {
                console.warn(`Could not preload sequence ${seqName}:`, error);
            }
        }
    }
    
    async preloadSequence(sequenceName) {
        const sequence = this.sequences[sequenceName];
        if (!sequence) return;
        
        // Preload first frame only for quick startup
        const startFrame = sequence.startFrame || 1;
        const firstFrameNum = sequence.padded === false ? 
            startFrame.toString() : 
            startFrame.toString().padStart(4, '0');
        const firstFramePath = `${sequence.path}${firstFrameNum}${sequence.suffix}`;
        
        // Only preload if not already cached
        if (!this.textureCache.has(firstFramePath)) {
            await new Promise((resolve) => {
                new THREE.TextureLoader().load(firstFramePath, (texture) => {
                    texture.minFilter = THREE.LinearFilter;
                    texture.magFilter = THREE.LinearFilter;
                    this.textureCache.set(firstFramePath, texture);
                    resolve();
                }, undefined, resolve);
            });
        }
    }
    
    async goToState(targetState) {
        if (this.isPlaying) {
            this.showNotification('Vent til animasjonen er ferdig', 'warning');
            return;
        }
        
        this.updateStatus(`Går til ${targetState}...`);
        
        if (targetState === 'reset') {
            const transition = this.getTransitionPath(this.currentState, 'reset');
            if (transition) {
                this.animationMesh.visible = true;
                await this.executeTransition(transition);
                this.currentState = 'reset';
                this.animationMesh.visible = false;
                this.updateStatus('I hvileposisjon');
            }
            return;
        }
        
        const transition = this.getTransitionPath(this.currentState, targetState);
        if (transition) {
            await this.executeTransition(transition);
            this.currentState = targetState;
            this.showNotification(`Nå i ${targetState} posisjon`, 'success');
        }
    }
    
    getTransitionPath(fromState, toState) {
        const transitions = {
            'reset': {
                'front': { type: 'direct', sequence: 'restFront', reverse: false },
                'top': { type: 'direct', sequence: 'restTop', reverse: false },
                'right': { type: 'direct', sequence: 'restRight', reverse: false }
            },
            'front': {
                'reset': { type: 'direct', sequence: 'restFront', reverse: true },
                'top': { type: 'direct', sequence: 'topFrontReverse', reverse: false },
                'right': { type: 'direct', sequence: 'frontRight', reverse: false }
            },
            'top': {
                'reset': { type: 'direct', sequence: 'restTop', reverse: true },
                'front': { type: 'direct', sequence: 'topFront', reverse: false },
                'right': { type: 'direct', sequence: 'topRight', reverse: false }
            },
            'right': {
                'reset': { type: 'direct', sequence: 'restRight', reverse: true },
                'front': { type: 'direct', sequence: 'frontRight', reverse: true },
                'top': { type: 'direct', sequence: 'topRight', reverse: true }
            }
        };
        
        return transitions[fromState]?.[toState] || null;
    }
    
    async executeTransition(transition) {
        if (transition.type === 'direct') {
            await this.playDirectSequence(transition.sequence, transition.reverse);
        }
    }
    
    async playDirectSequence(sequenceName, reverse) {
        const sequence = this.sequences[sequenceName];
        if (!sequence) {
            this.showNotification(`Ukjent sekvens: ${sequenceName}`, 'error');
            return;
        }
        
        this.currentSequence = sequenceName;
        this.updateStatus(`Spiller ${sequenceName} ${reverse ? 'baklengs' : 'fremover'}`);
        
        try {
            // Load first frame
            const startFrame = sequence.startFrame || 1;
            const firstFrameNum = sequence.padded === false ? 
                startFrame.toString() : 
                startFrame.toString().padStart(4, '0');
            const firstFramePath = `${sequence.path}${firstFrameNum}${sequence.suffix}`;
            
            let texture;
            if (this.textureCache.has(firstFramePath)) {
                texture = this.textureCache.get(firstFramePath);
            } else {
                texture = await new Promise((resolve) => {
                    new THREE.TextureLoader().load(firstFramePath, resolve, undefined, () => {
                        resolve(null);
                    });
                });
                
                if (texture) {
                    texture.minFilter = THREE.LinearFilter;
                    texture.magFilter = THREE.LinearFilter;
                    this.textureCache.set(firstFramePath, texture);
                }
            }
            
            if (!texture) {
                throw new Error('Kunne ikke laste tekstur');
            }
            
            // Update animation plane
            const aspectRatio = texture.image.width / texture.image.height;
            this.animationMesh.geometry.dispose();
            this.animationMesh.geometry = new THREE.PlaneGeometry(2 * aspectRatio, 2);
            
            this.animationMesh.material.map = texture;
            this.animationMesh.material.needsUpdate = true;
            this.animationMesh.visible = true;
            
            this.totalFrames = sequence.frames;
            this.currentFrame = reverse ? this.totalFrames - 1 : 0;
            this.isPlaying = true;
            this.isReversed = reverse;
            
            this.updateProgress();
            this.updateFrameInfo();
            
            // Wait for animation to complete
            await new Promise((resolve) => {
                this.animationCompleteCallback = resolve;
            });
            
        } catch (error) {
            console.error('Error playing sequence:', error);
            this.showNotification('Feil under avspilling', 'error');
            this.isPlaying = false;
        }
    }
    
    async playFullSequence() {
        if (this.isPlaying) return;
        
        this.updateStatus('Spiller full sekvens...');
        this.showNotification('Starter full sekvens', 'info');
        
        try {
            await this.playDirectSequence('play', false);
            await this.playDirectSequence('restRightReverse', false);
            
            this.animationMesh.visible = false;
            this.currentState = 'reset';
            this.showNotification('Full sekvens fullført', 'success');
            
        } catch (error) {
            console.error('Error playing full sequence:', error);
            this.showNotification('Feil under full sekvens', 'error');
        }
    }
    
    async loadFrame(frameNumber) {
        if (!this.currentSequence) return null;
        
        const sequence = this.sequences[this.currentSequence];
        const startFrame = sequence.startFrame || 1;
        
        // Calculate actual frame number
        let actualFrameNumber;
        if (this.isReversed) {
            actualFrameNumber = startFrame + (this.totalFrames - frameNumber);
        } else {
            actualFrameNumber = startFrame + frameNumber - 1;
        }
        
        // Ensure frame is within valid range
        actualFrameNumber = Math.max(startFrame, Math.min(actualFrameNumber, startFrame + this.totalFrames - 1));
        
        const paddedFrame = sequence.padded === false ? 
            actualFrameNumber.toString() : 
            actualFrameNumber.toString().padStart(4, '0');
        const framePath = `${sequence.path}${paddedFrame}${sequence.suffix}`;
        
        // Check cache first
        if (this.textureCache.has(framePath)) {
            return this.textureCache.get(framePath);
        }
        
        // Load new texture
        try {
            const texture = await new Promise((resolve) => {
                new THREE.TextureLoader().load(framePath, (texture) => {
                    if (texture) {
                        texture.minFilter = THREE.LinearFilter;
                        texture.magFilter = THREE.LinearFilter;
                        this.textureCache.set(framePath, texture);
                    }
                    resolve(texture);
                }, undefined, () => resolve(null));
            });
            
            return texture;
        } catch (error) {
            console.error('Error loading frame:', error);
            return null;
        }
    }
    
    animate() {
        requestAnimationFrame(() => this.animate());
        
        // Calculate FPS
        const now = performance.now();
        this.frameCount++;
        
        if (now >= this.lastFpsUpdate + 1000) {
            this.fps = Math.round((this.frameCount * 1000) / (now - this.lastFpsUpdate));
            this.lastFpsUpdate = now;
            this.frameCount = 0;
            this.updateFpsCounter();
        }
        
        // Handle animation frames
        const currentTime = performance.now();
        const deltaTime = currentTime - this.lastFrameTime;
        
        if (this.isPlaying && this.currentSequence && deltaTime >= (1000 / this.frameRate)) {
            this.lastFrameTime = currentTime;
            
            if (this.isReversed) {
                this.currentFrame--;
                if (this.currentFrame < 0) {
                    this.stopAnimation();
                }
            } else {
                this.currentFrame++;
                if (this.currentFrame >= this.totalFrames) {
                    this.stopAnimation();
                }
            }
            
            // Load and display the current frame
            this.loadFrame(this.currentFrame + 1).then(texture => {
                if (texture && this.animationMesh) {
                    this.animationMesh.material.map = texture;
                    this.animationMesh.material.needsUpdate = true;
                }
            });
            
            this.updateProgress();
            this.updateFrameInfo();
        }
        
        // Always render
        this.renderer.render(this.scene, this.camera);
    }
    
    stopAnimation() {
        this.isPlaying = false;
        if (this.animationCompleteCallback) {
            this.animationCompleteCallback();
            this.animationCompleteCallback = null;
        }
    }
    
    onWindowResize() {
        const aspectRatio = this.backgroundTexture ? 
            this.backgroundTexture.image.width / this.backgroundTexture.image.height : 
            1488 / 1052;
        
        this.updateCameraAspect(aspectRatio);
        this.renderer.setSize(window.innerWidth, window.innerHeight);
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
        
        // Show performance warning if FPS is low
        const perfWarning = document.getElementById('perf-warning');
        if (this.fps < 20 && this.isPlaying) {
            perfWarning.style.display = 'block';
        } else {
            perfWarning.style.display = 'none';
        }
    }
    
    updateStatus(message) {
        document.getElementById('status').textContent = message;
    }
    
    showLoading(show, message = 'Laster...') {
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
    
    startPerformanceMonitoring() {
        // Monitor memory usage and performance
        setInterval(() => {
            // Clean up texture cache if it gets too large
            if (this.textureCache.size > 50) {
                const keys = Array.from(this.textureCache.keys());
                for (let i = 0; i < 10; i++) {
                    if (keys[i]) {
                        const texture = this.textureCache.get(keys[i]);
                        if (texture) texture.dispose();
                        this.textureCache.delete(keys[i]);
                    }
                }
            }
        }, 10000);
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
    window.animationPlayer = new EnhancedAnimationPlayer();
});