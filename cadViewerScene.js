class CADViewerScene {
    constructor(renderer, container) {
        this.renderer = renderer;
        this.container = container;
        this.scene = null;
        this.camera = null;
        this.controls = null;
        this.model = null;
        this.backgroundMesh = null;
        this.isActive = false;
        
        this.init();
    }
    
    async init() {
        console.log('Initializing CAD Viewer Scene...');
        
        // Create scene
        this.scene = new THREE.Scene();
        
        // Create camera
        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
        this.camera.position.set(5, 5, 5);
        
        // Create orbit controls
        this.controls = new THREE.OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        this.controls.screenSpacePanning = false;
        this.controls.minDistance = 1;
        this.controls.maxDistance = 50;
        this.controls.maxPolarAngle = Math.PI;
        
        // Load background
        await this.loadBackground();
        
        // Add lighting
        this.setupLighting();
        
        // Load the pipe_Demo.gltf model
        await this.loadGLTFModel('models/pipe_Demo.obj');
        
        console.log('CAD Viewer Scene initialized');
    }
    
    async loadBackground() {
        return new Promise((resolve, reject) => {
            const textureLoader = new THREE.TextureLoader();
            textureLoader.load('Renders/Background.png', (texture) => {
                console.log('Background texture loaded for CAD scene');
                
                // Calculate aspect ratio
                const aspectRatio = texture.image.width / texture.image.height;
                
                // Create background plane
                const geometry = new THREE.PlaneGeometry(20 * aspectRatio, 20);
                const material = new THREE.MeshBasicMaterial({ 
                    map: texture,
                    transparent: false
                });
                
                this.backgroundMesh = new THREE.Mesh(geometry, material);
                this.backgroundMesh.position.z = -10;
                this.scene.add(this.backgroundMesh);
                
                resolve();
            }, undefined, (error) => {
                console.error('Error loading background for CAD scene:', error);
                // Create fallback background
                const geometry = new THREE.PlaneGeometry(20, 20);
                const material = new THREE.MeshBasicMaterial({ color: 0x444444 });
                this.backgroundMesh = new THREE.Mesh(geometry, material);
                this.backgroundMesh.position.z = -10;
                this.scene.add(this.backgroundMesh);
                resolve();
            });
        });
    }
    
    setupLighting() {
        // Ambient light
        const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
        this.scene.add(ambientLight);
        
        // Directional light
        const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
        directionalLight.position.set(10, 10, 5);
        directionalLight.castShadow = true;
        this.scene.add(directionalLight);
        
        // Point light
        const pointLight = new THREE.PointLight(0xffffff, 0.5);
        pointLight.position.set(-10, -10, -5);
        this.scene.add(pointLight);
    }
    
    // This method is now used to load the actual pipe_Demo.gltf model
    
    async show() {
        console.log('Showing CAD Viewer Scene');
        this.isActive = true;
        
        // Update camera aspect ratio
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
        
        // Enable controls
        this.controls.enabled = true;
        
        // Ensure model is visible and properly positioned
        if (this.model) {
            this.model.visible = true;
            
            // Center the model in view
            const box = new THREE.Box3().setFromObject(this.model);
            const center = box.getCenter(new THREE.Vector3());
            const size = box.getSize(new THREE.Vector3());
            
            // Adjust camera to fit model
            const maxDim = Math.max(size.x, size.y, size.z);
            const fov = this.camera.fov * (Math.PI / 180);
            let cameraZ = Math.abs(maxDim / 2 / Math.tan(fov / 2));
            
            // Add some padding
            cameraZ *= 1.5;
            
            this.camera.position.set(cameraZ, cameraZ, cameraZ);
            this.camera.lookAt(center);
            this.controls.target.copy(center);
            this.controls.update();
        }
        
        // Force a render
        this.renderer.render(this.scene, this.camera);
    }
    
    hide() {
        console.log('Hiding CAD Viewer Scene');
        this.isActive = false;
        
        // Disable controls
        this.controls.enabled = false;
    }
    
    animate() {
        if (!this.isActive) return;
        
        // Update controls
        this.controls.update();
        
        // Animate model (optional - rotate slowly)
        if (this.model) {
            this.model.rotation.y += 0.005;
        }
        
        // Render
        this.renderer.render(this.scene, this.camera);
    }
    
    onWindowResize() {
        if (!this.isActive) return;
        
        this.camera.aspect = window.innerWidth / window.innerHeight;
        this.camera.updateProjectionMatrix();
    }
    
    // Method to load actual GLTF models (for future use)
    async loadGLTFModel(url) {
        try {
            const loader = new THREE.GLTFLoader();
            const gltf = await new Promise((resolve, reject) => {
                loader.load(url, resolve, undefined, reject);
            });
            
            // Remove existing model
            if (this.model) {
                this.scene.remove(this.model);
            }
            
            this.model = gltf.scene;
            this.scene.add(this.model);
            
            // Center and scale model
            const box = new THREE.Box3().setFromObject(this.model);
            const center = box.getCenter(new THREE.Vector3());
            const size = box.getSize(new THREE.Vector3());
            
            this.model.position.sub(center);
            
            // Scale to fit in view
            const maxDim = Math.max(size.x, size.y, size.z);
            const scale = 5 / maxDim;
            this.model.scale.setScalar(scale);
            
            console.log('GLTF model loaded successfully');
            
        } catch (error) {
            console.error('Error loading GLTF model:', error);
        }
    }
}
