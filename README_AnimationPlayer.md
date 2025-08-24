# Three.js Animation Player

A web-based animation player built with Three.js that displays your render sequences over a background image.

## Features

- **Background Image**: Uses `Renders/Background.png` as the base background
- **Three Animation Sequences**:
  - **Rest Top**: 72 frames (0001.png to 0072.png)
  - **Rest Right**: 72 frames (0001.png to 0072.png)  
  - **Rest Sliced 2**: 144 frames (0001.png to 0144.png)
- **Playback Controls**:
  - Play/Pause
  - Stop
  - Reverse direction
  - Progress bar
  - Status display

## How to Run

1. **Start the server**:
   ```bash
   python3 server.py
   ```

2. **Open your browser** and go to:
   ```
   http://localhost:8000
   ```

## Usage

1. **Load Background**: The background image loads automatically when the page opens
2. **Play Sequences**: Click any of the three sequence buttons to start playing:
   - "Play Rest Top" - Plays the Rest_Top sequence
   - "Play Rest Right" - Plays the Resr_Right sequence
   - "Play Rest Sliced 2" - Plays the Rest_Sliced_2 sequence
3. **Control Playback**:
   - **Reverse**: Toggle between forward and reverse playback
   - **Pause**: Pause/resume the current animation
   - **Stop**: Stop the animation and hide the sequence
4. **Monitor Progress**: Watch the progress bar and status text for current playback information

## Technical Details

- **Frame Rate**: 30 FPS (configurable in the code)
- **Rendering**: Uses Three.js with WebGL for smooth playback
- **Memory Management**: Automatically disposes of old textures to prevent memory leaks
- **Responsive**: Adapts to window resizing
- **Cross-browser**: Works in modern browsers with WebGL support

## File Structure

```
├── index.html          # Main HTML file
├── app.js              # Three.js application logic
├── server.py           # Python HTTP server
├── README_AnimationPlayer.md  # This file
└── Renders/            # Your render sequences
    ├── Background.png
    ├── Rest_Top/
    ├── Resr_Right/
    └── Rest_Sliced_2/
```

## Customization

You can modify the following in `app.js`:

- **Frame Rate**: Change `this.frameRate = 30` to your desired FPS
- **Sequences**: Add or modify sequences in the `this.sequences` object
- **UI**: Modify the HTML and CSS in `index.html` for different styling

## Troubleshooting

- **Images not loading**: Make sure the server is running and the file paths are correct
- **Performance issues**: Try reducing the frame rate or image resolution
- **Browser compatibility**: Ensure your browser supports WebGL

## Notes

- The app loads images dynamically as needed to conserve memory
- Each sequence loops continuously until stopped
- The background image remains visible while sequences play over it
- All animations use transparent overlays so the background shows through 