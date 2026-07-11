# Photo Preparation Pipeline (`prep_photo.py`)

When you run `prep_photo.py` on a source image, it goes through a multi-step image processing pipeline designed specifically to optimize a standard portrait for high-quality, monochrome ASCII conversion. 

Here is exactly what happens to the image under the hood:

### 1. AI Background Removal
The script uses the `rembg` library (powered by ONNX deep learning models like U^2-Net) to identify the subject and strip away the background.
- **Why:** In ASCII art, a busy background creates visual noise that competes with the subject. Removing the background isolates the subject cleanly.

### 2. Grayscale Conversion
The image is stripped of all color information (`cv2.cvtColor`).
- **Why:** The final ASCII portrait is monochrome (a single "ink" color). We only care about luminosity (lightness and darkness), not hue.

### 3. Local Contrast Enhancement (CLAHE)
The script applies Contrast Limited Adaptive Histogram Equalization (CLAHE). Instead of adjusting contrast across the entire image at once, it breaks the image into small tiles (8x8) and boosts contrast locally within each tile.
- **Why:** A flatly-lit face often turns into a featureless blob in ASCII. CLAHE forces shadows to get darker and highlights to get brighter *relative to their immediate surroundings*, which exaggerates facial features like the nose, eyes, and cheekbones, making the face recognizable.

### 4. Global Brightness Lift
A slight global brightness shift is applied (`alpha=1.05, beta=18`).
- **Why:** This pushes the midtones of the face slightly brighter. In the ASCII mapping, lighter pixels map to sparse characters (like `.` or spaces), meaning the face itself won't be filled with dense, dark, unreadable text.

### 5. Compositing onto Pure White
Finally, using the alpha mask generated in step 1, the script pastes the newly contrasted subject onto a pure white background. The mask is feathered slightly to avoid harsh jagged halos.
- **Why:** The ASCII script (`make_ascii_svg.py`) is instructed to map pure white to empty spaces. By forcing the background to pure white, we guarantee that the area around the subject will be completely blank and clean in the final SVG.

### Output
The result is saved as `source-prepped.png`, which serves as the direct input for the `make_ascii_svg.py` script.
