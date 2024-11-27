
# Passport Photo Maker Studio

**Passport Photo Maker Studio** is a desktop application designed to simplify the creation of professional-quality passport, visa, and ID photos. With advanced features like automatic face detection, background removal, and resizing options, this tool is ideal for anyone who needs standardized photos for official purposes.

---

## Features
- **Automatic Face Detection**: Detects and crops the face to focus on the subject.
- **Background Removal**: Removes the background and replaces it with a solid color.
- **Custom Resizing Options**:
  - Passport size (413x531 px)
  - Application sizes (200x200 px, 300x300 px)
- **Image Enhancement**:
  - Grain removal
  - Upscaling with customizable levels
- **User-Friendly Interface**: An intuitive GUI built with Tkinter for seamless interaction.

---

## Screenshots
![ScreenShot](https://github.com/nayem121/Passport-Photo/blob/main/test.png?raw=true)

## Installation

### Prerequisites
- Python 3.7 or higher
- `pip` (Python package installer)

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/nayem121/passport-photo.git
   cd passport-photo-maker
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Download the `haarcascade_frontalface_default.xml` file (included in the repository). This is required for face detection.

4. Run the application:
   ```bash
   python Passport.py
   ```

---

## Usage
1. **Upload an Image**:
   - Click "Choose Image" to select your input photo.
2. **Set Options**:
   - Choose the upscale level, enable grain removal, and select the desired output size.
3. **Process Image**:
   - Click "Process" to detect the face, remove the background, and resize the image.
4. **Save Image**:
   - After processing, click "Save Image" to export your final photo.

---

## Building as an Executable
To distribute the application as a standalone executable, use **PyInstaller**:
1. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

2. Run the following command to build:
   ```bash
   pyinstaller --onefile --add-data "haarcascade_frontalface_default.xml;." PassportPhoto.py
   ```

3. The executable will be available in the `dist` directory.

---

## Dependencies
The project uses the following Python libraries:
- `opencv-python` (Image processing and face detection)
- `numpy` (Image array manipulation)
- `Pillow` (Image handling for GUI)
- `rembg` (Background removal)
- `tk` and `ttkbootstrap` (GUI components and styling)

Install them with:
```bash
pip install -r requirements.txt
```

---

## Contributing
Contributions are welcome! If you have suggestions or improvements, feel free to fork the repository and submit a pull request.

---

## License
This project is licensed under the MIT License. See the **[license](https://github.com/nayem121/Passport-Photo?tab=MIT-1-ov-file)** file for details.

---

## Author
Created by **[Nayem Uddin Chowdhury](https://github.com/nayem121)**  
For any inquiries, visit [My Facebook](https://facebook.com/nayem121).
