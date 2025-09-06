document.addEventListener('DOMContentLoaded', function() {
    // Get references to UI elements
    const canvas = document.getElementById('viewer');
    const loadingOverlay = document.getElementById('loadingOverlay');
    const loadingText = document.getElementById('loadingText');
    const statusBar = document.getElementById('statusBar');
    const modelStatus = document.getElementById('modelStatus');
    const scaleSlider = document.getElementById('scaleSlider');
    const scaleValue = document.getElementById('scaleValue');
    
    
    // Set up Three.js scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a1a2e);
    
    // Set up camera
    const camera = new THREE.PerspectiveCamera(75, canvas.clientWidth / canvas.clientHeight, 0.1, 1000);
    camera.position.set(5, 5, 5);
    
    // Set up renderer
    const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
    renderer.setSize(canvas.clientWidth, canvas.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    
    // Add lights
    const ambientLight = new THREE.AmbientLight(0x404040, 0.6);
    scene.add(ambientLight);
    
    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(10, 10, 5);
    scene.add(directionalLight);
    
    // Add grid and axes helpers
    const gridHelper = new THREE.GridHelper(20, 20, 0x888888, 0x444444);
    gridHelper.position.y = 0;
    scene.add(gridHelper);
    
    const axesHelper = new THREE.AxesHelper(5);
    scene.add(axesHelper);
    
    // Set up orbit controls
    const controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.minDistance = 2;
    controls.maxDistance = 50;
    
    // Store references to loaded assets
    let currentModel = null;
    let originalScale = 1;
    
    
    
    // Function to dispose of model resources
    function disposeModel(model) {
        model.traverse(function(child) {
            if (child.isMesh) {
                if (child.geometry) {
                    child.geometry.dispose();
                }
                if (child.material) {
                    if (Array.isArray(child.material)) {
                        child.material.forEach(material => material.dispose());
                    } else {
                        child.material.dispose();
                    }
                }
            }
        });
    }
    
    
    // Center and scale model in the scene
    function centerAndScaleModel(model) {
        // First, get the bounding box of the original model
        const box = new THREE.Box3().setFromObject(model);
        const center = box.getCenter(new THREE.Vector3());
        const size = box.getSize(new THREE.Vector3());
        
        // Calculate appropriate scale to fit in view
        const maxDim = Math.max(size.x, size.y, size.z);
        const targetSize = 5; // Target size in units
        originalScale = targetSize / maxDim;
        
        // Apply initial scale
        model.scale.set(originalScale, originalScale, originalScale);
        
        // Move the model so its center is at the world origin (0,0,0)
        model.position.x = -center.x * originalScale;
        model.position.y = -center.y * originalScale;
        model.position.z = -center.z * originalScale;
        
        // Reset scale slider to 100%
        scaleSlider.value = 100;
        scaleValue.textContent = '100%';
        
        console.log('Model centered at origin:', model.position);
    }
    
    // Update camera and controls to focus on the model
    function updateCameraForModel() {
        if (currentModel) {
            console.log('Updating camera for model...');
            console.log('Model position:', currentModel.position);
            
            // Get the bounding box of the model
            const box = new THREE.Box3().setFromObject(currentModel);
            const size = box.getSize(new THREE.Vector3());
            const maxDim = Math.max(size.x, size.y, size.z);
            
            console.log('Model bounding box size:', size);
            console.log('Max dimension:', maxDim);
            
            // Calculate appropriate camera distance
            const fov = camera.fov * (Math.PI / 180);
            let cameraDistance = Math.abs(maxDim / Math.sin(fov / 2));
            
            // Add some padding
            cameraDistance *= 1.5;
            
            console.log('Calculated camera distance:', cameraDistance);
            
            // Position camera at a good viewing angle
            camera.position.set(cameraDistance, cameraDistance, cameraDistance);
            
            // Set controls target to the model's center (which should be at origin)
            controls.target.set(0, 0, 0);
            
            // Reset controls to ensure proper alignment
            controls.reset();
            
            // Force controls update
            controls.update();
            
            console.log('Camera positioned at:', camera.position);
            console.log('Controls target:', controls.target);
            console.log('Model should now be centered at origin');
        }
    }
    
    // Scale the model based on slider value
    function scaleModel(scalePercent) {
        if (currentModel) {
            const scale = originalScale * (scalePercent / 100);
            currentModel.scale.set(scale, scale, scale);
            
            // After scaling, we need to reposition to keep center at origin
            const box = new THREE.Box3().setFromObject(currentModel);
            const center = box.getCenter(new THREE.Vector3());
            
            currentModel.position.x = -center.x;
            currentModel.position.y = -center.y;
            currentModel.position.z = -center.z;
            
            // Update gizmo positions
            translateGizmo.position.copy(currentModel.position);
            rotateGizmo.position.copy(currentModel.position);
            scaleGizmo.position.copy(currentModel.position);
        }
    }
    
    // Set camera to specific views
    function setView(view) {
        switch(view) {
            case 'front':
                camera.position.set(0, 0, 10);
                controls.target.set(0, 0, 0);
                updateStatus('Front view');
                break;
            case 'top':
                camera.position.set(0, 10, 0);
                controls.target.set(0, 0, 0);
                updateStatus('Top view');
                break;
            case 'right':
                camera.position.set(10, 0, 0);
                controls.target.set(0, 0, 0);
                updateStatus('Right view');
                break;
            case 'perspective':
                camera.position.set(5, 5, 5);
                controls.target.set(0, 0, 0);
                updateStatus('Perspective view');
                break;
        }
        controls.update();
    }
    
    // UI control functions
    function resetView() {
        camera.position.set(5, 5, 5);
        controls.reset();
        
        // Reset scale to 100%
        scaleSlider.value = 100;
        scaleValue.textContent = '100%';
        scaleModel(100);
        
        // Reset model position to origin if it exists
        if (currentModel) {
            currentModel.position.set(0, 0, 0);
            currentModel.rotation.set(0, 0, 0);
            currentModel.scale.set(originalScale, originalScale, originalScale);
        }
        
        updateStatus('View and model reset to origin');
    }
    
    function changeColor() {
        if (currentModel) {
            const colors = [
                0x667eea, // Blue
                0xff6b6b, // Red
                0x4ecdc4, // Teal
                0xf9a826, // Yellow
                0xa055ff  // Purple
            ];
            
            const randomColor = colors[Math.floor(Math.random() * colors.length)];
            
            currentModel.traverse(function(child) {
                if (child.isMesh && child.material) {
                    child.material.color.setHex(randomColor);
                }
            });
            
            updateStatus('Model color changed');
        }
    }
    
    function toggleAxes() {
        axesHelper.visible = !axesHelper.visible;
        updateStatus('Axes helper ' + (axesHelper.visible ? 'enabled' : 'disabled'));
    }
    
    function toggleGrid() {
        gridHelper.visible = !gridHelper.visible;
        updateStatus('Grid ' + (gridHelper.visible ? 'enabled' : 'disabled'));
    }
    
    
    function showLoading(show, message = 'Loading...') {
        loadingOverlay.style.display = show ? 'flex' : 'none';
        loadingText.textContent = message;
    }
    
    function updateStatus(message) {
        statusBar.textContent = message;
    }
    
    // Set up event listeners for UI controls
    document.getElementById('resetView').addEventListener('click', resetView);
    document.getElementById('changeColor').addEventListener('click', changeColor);
    document.getElementById('toggleAxes').addEventListener('click', toggleAxes);
    document.getElementById('toggleGrid').addEventListener('click', toggleGrid);
    
    // View buttons
    document.getElementById('frontView').addEventListener('click', () => setView('front'));
    document.getElementById('topView').addEventListener('click', () => setView('top'));
    document.getElementById('rightView').addEventListener('click', () => setView('right'));
    document.getElementById('perspectiveView').addEventListener('click', () => setView('perspective'));
    
    
    // Scale slider event listener
    scaleSlider.addEventListener('input', function() {
        const scalePercent = parseInt(this.value);
        scaleValue.textContent = scalePercent + '%';
        scaleModel(scalePercent);
    });
    
    // Auto-load the default model
    function autoLoadDefaultModel() {
        showLoading(true, 'Loading pipe_Demo.obj...');
        updateModelStatus('Loading pipe_Demo.obj...');
        
        // Try to load the OBJ model
        const objLoader = new THREE.OBJLoader();
        objLoader.load(
            './models/pipe_Demo.obj',
            function(object) {
                // Apply a material to all meshes in the object
                object.traverse(function(child) {
                    if (child.isMesh) {
                        child.material = new THREE.MeshPhongMaterial({
                            color: 0x667eea,
                            specular: 0x111111,
                            shininess: 50
                        });
                    }
                });
                
                currentModel = object;
                centerAndScaleModel(currentModel);
                scene.add(currentModel);
                
                showLoading(false);
                updateModelStatus('✅ pipe_Demo.obj loaded successfully');
                updateStatus('Model loaded successfully');
                console.log('✅ pipe_Demo.obj loaded successfully');
                
                // Update camera and controls after model is fully loaded and rendered
                // Use requestAnimationFrame to ensure it happens after the next render
                requestAnimationFrame(() => {
                    updateCameraForModel();
                });
            },
            function(progress) {
                console.log('Loading progress:', progress);
            },
            function(error) {
                console.error('❌ Error loading pipe_Demo.obj:', error);
                showLoading(false);
                updateModelStatus('❌ Failed to load pipe_Demo.obj');
                updateStatus('Error loading model: ' + error.message);
            }
        );
    }
    
    function updateModelStatus(message) {
        if (modelStatus) {
            modelStatus.textContent = message;
        }
    }
    
    // Handle window resize
    window.addEventListener('resize', function() {
        const width = canvas.clientWidth;
        const height = canvas.clientHeight;
        
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
        
        renderer.setSize(width, height);
    });
    
    // Animation loop
    function animate() {
        requestAnimationFrame(animate);
        
        controls.update();
        renderer.render(scene, camera);
    }
    
    // Start animation
    animate();
    
    // Initial status
    updateStatus('Ready to load 3D model');
    
    // Auto-load the default model after a short delay to ensure everything is initialized
    setTimeout(() => {
        autoLoadDefaultModel();
    }, 500);
});