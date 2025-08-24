class SceneManager {
    constructor() {
        this.scenes = [];
        this.currentSceneIndex = 0;
        this.renderer = null;
        this.container = null;
        
        this.init();
    }
    
    init() {
        console.log('Initializing Scene Manager...');
        this.container = document.getElementById('container');
        this.setupRenderer();
        this.setupScenes();
        this.setupSceneSwitcher();
        this.switchToScene(0);
    }
    
    setupRenderer() {
        // Create a single renderer that will be shared across scenes
        this.renderer = new THREE.WebGLRenderer({ 
            canvas: document.getElementById('canvas'),
            alpha: false,
            antialias: true
        });
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.renderer.setClearColor(0x000000, 1);
        this.renderer.setPixelRatio(window.devicePixelRatio);
    }
    
    setupScenes() {
        // Initialize all available scenes
        this.scenes = [
            new AnimationPlayerScene(this.renderer, this.container),
            new CADViewerScene(this.renderer, this.container)
        ];
        
        console.log(`Initialized ${this.scenes.length} scenes`);
    }
    
    setupSceneSwitcher() {
        // Create scene navigation buttons
        const sceneSwitcher = document.createElement('div');
        sceneSwitcher.id = 'scene-switcher';
        sceneSwitcher.innerHTML = `
            <button id="prevScene" class="scene-nav-btn">← Previous</button>
            <span id="sceneIndicator">Scene 1/2</span>
            <button id="nextScene" class="scene-nav-btn">Next →</button>
        `;
        
        // Insert after the controls
        const controls = document.getElementById('controls');
        controls.parentNode.insertBefore(sceneSwitcher, controls.nextSibling);
        
        // Add event listeners
        document.getElementById('prevScene').addEventListener('click', () => {
            this.previousScene();
        });
        
        document.getElementById('nextScene').addEventListener('click', () => {
            this.nextScene();
        });
        
        // Add keyboard navigation
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft') this.previousScene();
            if (e.key === 'ArrowRight') this.nextScene();
        });
    }
    
    async switchToScene(index) {
        if (index < 0 || index >= this.scenes.length) {
            console.error('Invalid scene index:', index);
            return;
        }
        
        console.log(`Switching to scene ${index + 1}`);
        
        // Hide current scene
        if (this.scenes[this.currentSceneIndex]) {
            this.scenes[this.currentSceneIndex].hide();
        }
        
        // Show new scene
        this.currentSceneIndex = index;
        await this.scenes[this.currentSceneIndex].show();
        
        // Update UI
        this.updateSceneIndicator();
        this.updateNavigationButtons();
    }
    
    previousScene() {
        const newIndex = (this.currentSceneIndex - 1 + this.scenes.length) % this.scenes.length;
        this.switchToScene(newIndex);
    }
    
    nextScene() {
        const newIndex = (this.currentSceneIndex + 1) % this.scenes.length;
        this.switchToScene(newIndex);
    }
    
    updateSceneIndicator() {
        const indicator = document.getElementById('sceneIndicator');
        const sceneNames = ['Animation Player', 'CAD Viewer'];
        indicator.textContent = `${sceneNames[this.currentSceneIndex]} (${this.currentSceneIndex + 1}/${this.scenes.length})`;
    }
    
    updateNavigationButtons() {
        const prevBtn = document.getElementById('prevScene');
        const nextBtn = document.getElementById('nextScene');
        
        // Update button states
        prevBtn.disabled = this.currentSceneIndex === 0;
        nextBtn.disabled = this.currentSceneIndex === this.scenes.length - 1;
    }
    
    onWindowResize() {
        this.renderer.setSize(window.innerWidth, window.innerHeight);
        this.scenes.forEach(scene => {
            if (scene.onWindowResize) {
                scene.onWindowResize();
            }
        });
    }
    
    animate() {
        requestAnimationFrame(() => this.animate());
        
        // Render current scene
        if (this.scenes[this.currentSceneIndex] && this.scenes[this.currentSceneIndex].animate) {
            this.scenes[this.currentSceneIndex].animate();
        }
    }
}
