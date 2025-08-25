class AnimationPlayer {
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
        this.frameRate = 12; // FPS
        this.lastFrameTime = 0;
        
        // Available animation sequences
        this.sequences = {
            'restTop': {
                path: 'Renders/Rest_Top/',
                frames: 72,
                suffix: '.png'
            },
            'restRight': {
                path: 'Renders/Rest_Right/',
                frames: 72,
                suffix: '.png'
            },
            'restFront': {
                path: 'Renders/Rest_front/',
                frames: 73,
                suffix: '.png'
            },
            'topFront': {
                path: 'Renders/top_front/',
                frames: 97,
                startFrame: 1,
                padded: false,
                suffix: '.png'
            },
            'topFrontReverse': {
                path: 'Renders/top_front_reverse/',
                frames: 73,
                suffix: '.png'
            },
            'restTopFront': {
                path: 'Renders/Rest_top_front/',
                frames: 144,
                suffix: '.png'
            },
            'frontRight': {
                path: 'Renders/front_right/',
                frames: 73,
                startFrame: 1,
                padded: false,
                suffix: '.png'
            },
            'topRight': {
                path: 'Renders/top_right/',
                frames: 72,
                startFrame: 1,
                padded: false,
                suffix: '.png'
            },
            'play': {
                path: 'Renders/Play/',
                frames: 232,
                startFrame: 1,
                padded: true,
                suffix: '.png'
            },
            'restRightReverse': {
                path: 'Renders/Rest_Right_reverse/',
                frames: 72,
                suffix: '.png'
            }
        };
        
        this.init();
        this.setupEventListeners();
    }
    
    init() {
        console.log('Initializing Three.js scene...');
        
        // Create scene
        this.scene = new THREE.Scene();
        
        // Create camera - simple orthographic camera
        this.camera = new THREE.OrthographicCamera(-1, 1, 1, -1, 0.1, 1000);
        this.camera.position.z = 1;
        
        // Create renderer
        this.renderer = new THREE.WebGLRenderer({ 
            canvas: document.getElementById('canvas'),
            alpha: false, // Changed to false for solid background
            antialias: true
        });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setClearColor(0x000000, 1); // Black background
        this.renderer.setPixelRatio(window.devicePixelRatio);
        
        // Create animation plane first
        this.createAnimationPlane();
        
        // Load background image
        this.loadBackground();
        
        // Start render loop
        this.animate();
        
        // Handle window resize
        window.addEventListener('resize', () => this.onWindowResize());
        
        console.log('Initialization complete');
    }
    
    loadBackground() {
        console.log('Loading background image...');
        const textureLoader = new THREE.TextureLoader();
        textureLoader.load('Renders/Background.png', (texture) => {
            console.log('Background texture loaded successfully');
            this.backgroundTexture = texture;
            this.backgroundTexture.minFilter = THREE.LinearFilter;
            this.backgroundTexture.magFilter = THREE.LinearFilter;
            
            // Calculate aspect ratio and adjust camera
            const aspectRatio = texture.image.width / texture.image.height; // 1488/1052 ≈ 1.415
            const windowAspect = window.innerWidth / window.innerHeight;
            
            if (windowAspect > aspectRatio) {
                // Window is wider than image - fit to height
                this.camera.left = -windowAspect;
                this.camera.right = windowAspect;
                this.camera.top = 1;
                this.camera.bottom = -1;
            } else {
                // Window is taller than image - fit to width
                this.camera.left = -1;
                this.camera.right = 1;
                this.camera.top = 1 / windowAspect;
                this.camera.bottom = -1 / windowAspect;
            }
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
        });
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
        console.log('Animation plane created');
    }
    
    async goToState(targetState) {
        console.log(`Going from ${this.currentState} to ${targetState}`);
        
        if (targetState === 'reset') {
            // Going to rest position - need to play appropriate sequence
            const transition = this.getTransitionPath(this.currentState, 'reset');
            if (transition) {
                console.log('Playing reverse animation to rest position...');
                // Keep animation mesh visible during reverse animation
                this.animationMesh.visible = true;
                // Play the reverse animation FIRST, then change state
                await this.executeTransition(transition);
                // Only after animation completes, change to rest state
                this.currentState = 'reset';
                this.animationMesh.visible = false;
                this.updateStatus('At rest position');
            } else {
                this.updateStatus('No path to rest position');
            }
            return;
        }
        
        // Get transition path from combination.txt
        const transition = this.getTransitionPath(this.currentState, targetState);
        
        if (transition) {
            await this.executeTransition(transition);
            this.currentState = targetState;
        } else {
            this.updateStatus('No transition path available');
        }
    }
    
    getTransitionPath(fromState, toState) {
        // Exact transitions from combination.txt
        const transitions = {
            'reset': {
                'front': { type: 'direct', sequence: 'restFront', reverse: false }, // Reset to front: reset_front
                'top': { type: 'direct', sequence: 'restTop', reverse: false }, // Reset to top: Rest_Top
                'right': { type: 'direct', sequence: 'restRight', reverse: false } // Reset to right: Reset_right
            },
            'front': {
                'reset': { type: 'direct', sequence: 'restFront', reverse: true }, // front to Reset: rewind the reset_front
                'top': { type: 'direct', sequence: 'topFrontReverse', reverse: false }, // Front to top: reverse top_front (use reverse sequence)
                'right': { type: 'direct', sequence: 'frontRight', reverse: false } // front to right: front_right
            },
            'top': {
                'reset': { type: 'direct', sequence: 'restTop', reverse: true }, // top to reset: rewind Rest_top
                'front': { type: 'direct', sequence: 'topFront', reverse: false }, // Top to front: top_front
                'right': { type: 'direct', sequence: 'topRight', reverse: false } // top to right: top_right
            },
            'right': {
                'reset': { type: 'direct', sequence: 'restRight', reverse: true }, // Right to reset: rewind Reset_right
                'front': { type: 'direct', sequence: 'frontRight', reverse: true }, // right to front: reverse front_right
                'top': { type: 'direct', sequence: 'topRight', reverse: true } // right to top: rewind top_right
            }
        };
        
        return transitions[fromState]?.[toState] || null;
    }
    
    async executeTransition(transition) {
        if (transition.type === 'direct') {
            await this.playDirectSequence(transition.sequence, transition.reverse);
        } else if (transition.type === 'complex') {
            await this.playComplexSequence(transition.steps, transition.reverse);
        }
    }
    
    async playDirectSequence(sequenceName, reverse) {
        console.log(`Playing ${sequenceName} ${reverse ? 'in reverse' : 'forward'}`);
        
        const sequence = this.sequences[sequenceName];
        if (!sequence) {
            console.error('Unknown sequence:', sequenceName);
            return;
        }
        
        this.currentSequence = sequenceName;
        this.updateStatus(`Playing ${sequenceName} ${reverse ? 'in reverse' : 'forward'}`);
        
        try {
            // Load first frame - handle different frame numbering
            const startFrame = sequence.startFrame || 1;
            const firstFrameNum = sequence.padded === false ? 
                startFrame.toString() : 
                startFrame.toString().padStart(4, '0');
            const firstFramePath = `${sequence.path}${firstFrameNum}${sequence.suffix}`;
            const textureLoader = new THREE.TextureLoader();
            
            const texture = await new Promise((resolve, reject) => {
                textureLoader.load(firstFramePath, resolve, undefined, reject);
            });
            
            texture.minFilter = THREE.LinearFilter;
            texture.magFilter = THREE.LinearFilter;
            
            // Update animation plane with proper aspect ratio
            const aspectRatio = texture.image.width / texture.image.height;
            this.animationMesh.geometry.dispose();
            this.animationMesh.geometry = new THREE.PlaneGeometry(2 * aspectRatio, 2);
            
            // Update animation plane BEFORE making it visible
            this.animationMesh.material.map = texture;
            this.animationMesh.material.needsUpdate = true;
            
            // Only make visible after texture is loaded and applied
            this.animationMesh.visible = true;
            
            this.totalFrames = sequence.frames;
            this.currentFrame = reverse ? this.totalFrames - 1 : 0;
            this.isPlaying = true;
            this.isReversed = reverse;
            
            this.updateProgress(reverse ? 1 : 0);
            
            console.log(`Started ${reverse ? 'reverse' : 'forward'} animation. Total frames: ${this.totalFrames}, Starting frame: ${this.currentFrame}`);
            
            // Immediately load the first frame to prevent flash
            const firstFrameToLoad = reverse ? this.totalFrames : 1;
            console.log(`Immediately loading first frame: ${firstFrameToLoad}`);
            await this.loadFrame(firstFrameToLoad);
            
            // Wait for animation to complete
            await this.waitForAnimationComplete();
            
        } catch (error) {
            console.error('Error loading sequence:', error);
            this.updateStatus('Error loading sequence');
        }
    }
    
    async playComplexSequence(stepSequences, reverseFlags) {
        for (let i = 0; i < stepSequences.length; i++) {
            const sequenceName = stepSequences[i];
            const reverse = reverseFlags[i];
            
            this.updateStatus(`Playing step ${i + 1}/${stepSequences.length}: ${sequenceName}`);
            await this.playDirectSequence(sequenceName, reverse);
        }
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
    
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    async playFullSequence() {
        console.log('Playing PLAY + Rest_Right_reverse sequence');
        this.updateStatus('Spiller PLAY + Rest_Right_reverse sekvens...');
        
        try {
            // First play the Play sequence
            console.log('Playing Play sequence (232 frames)');
            await this.playDirectSequence('play', false);
            
            // Then play the Rest_Right_reverse sequence
            console.log('Playing Rest_Right_reverse sequence (72 frames)');
            await this.playDirectSequence('restRightReverse', false);
            
            this.updateStatus('PLAY + Rest_Right_reverse sekvens fullført!');
            this.animationMesh.visible = false;
            this.currentState = 'reset';
            
        } catch (error) {
            console.error('Error playing complete sequence:', error);
            this.updateStatus('Feil ved spilling av komplett sekvens');
        }
    }
    
    async loadFrame(frameNumber) {
        if (!this.currentSequence) return;
        
        const sequence = this.sequences[this.currentSequence];
        const startFrame = sequence.startFrame || 1;
        const actualFrameNumber = startFrame + frameNumber - 1;
        const paddedFrame = sequence.padded === false ? 
            actualFrameNumber.toString() : 
            actualFrameNumber.toString().padStart(4, '0');
        const framePath = `${sequence.path}${paddedFrame}${sequence.suffix}`;
        
        try {
            const textureLoader = new THREE.TextureLoader();
            const texture = await new Promise((resolve, reject) => {
                textureLoader.load(framePath, resolve, undefined, reject);
            });
            
            texture.minFilter = THREE.LinearFilter;
            texture.magFilter = THREE.LinearFilter;
            
            // Dispose old texture to prevent memory leaks
            if (this.animationTexture) {
                this.animationTexture.dispose();
            }
            
            this.animationTexture = texture;
            this.animationMesh.material.map = this.animationTexture;
            this.animationMesh.material.needsUpdate = true;
            
        } catch (error) {
            console.error('Error loading frame:', frameNumber, error);
        }
    }
    
    animate() {
        requestAnimationFrame(() => this.animate());
        
        const currentTime = performance.now();
        const deltaTime = currentTime - this.lastFrameTime;
        
        if (this.isPlaying && this.currentSequence && deltaTime >= (1000 / this.frameRate)) {
            this.lastFrameTime = currentTime;
            
            if (this.isReversed) {
                this.currentFrame--;
                if (this.currentFrame < 0) {
                    this.currentFrame = 0;
                    this.isPlaying = false;
                    this.updateStatus('Reached first frame');
                }
            } else {
                this.currentFrame++;
                if (this.currentFrame >= this.totalFrames) {
                    this.currentFrame = this.totalFrames - 1;
                    this.isPlaying = false;
                    this.updateStatus('Animation complete');
                }
            }
            
            // Ensure frame number is within valid range (1 to totalFrames)
            const frameToLoad = Math.max(1, Math.min(this.currentFrame + 1, this.totalFrames));
            console.log(`Loading frame ${frameToLoad} (currentFrame: ${this.currentFrame}, totalFrames: ${this.totalFrames})`);
            this.loadFrame(frameToLoad);
            this.updateProgress(this.currentFrame / (this.totalFrames - 1));
        }
        
        // Always render the scene
        this.renderer.render(this.scene, this.camera);
    }
    
    onWindowResize() {
        const windowAspect = window.innerWidth / window.innerHeight;
        const imageAspect = 1488 / 1052; // Fixed aspect ratio for all images
        
        if (windowAspect > imageAspect) {
            // Window is wider than image - fit to height
            this.camera.left = -windowAspect;
            this.camera.right = windowAspect;
            this.camera.top = 1;
            this.camera.bottom = -1;
        } else {
            // Window is taller than image - fit to width
            this.camera.left = -1;
            this.camera.right = 1;
            this.camera.top = 1 / windowAspect;
            this.camera.bottom = -1 / windowAspect;
        }
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(window.innerWidth, window.innerHeight);
    }
    
    updateProgress(progress) {
        const progressBar = document.getElementById('progress-bar');
        progressBar.style.width = `${progress * 100}%`;
    }
    
    updateStatus(message) {
        document.getElementById('status').textContent = message;
        console.log('Status:', message);
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