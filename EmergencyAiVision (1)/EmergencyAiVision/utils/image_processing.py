import cv2
import numpy as np
from PIL import Image
import io
import base64

def preprocess_image(image, target_size=(512, 512)):
    """
    Preprocess the image for analysis
    
    Args:
        image (PIL.Image): Input image
        target_size (tuple): Target size for resizing
        
    Returns:
        PIL.Image: Preprocessed image
    """
    if image is None:
        raise ValueError("No image provided")
    
    # Ensure image is in RGB mode
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Convert PIL image to numpy array
    img_array = np.array(image)
    
    # Resize image while maintaining aspect ratio
    h, w = img_array.shape[:2]
    aspect = float(w) / float(h)  # Ensure float division
    
    if aspect > 1:  # width > height
        new_w = min(int(target_size[0]), w)  # Don't upscale
        new_h = int(new_w / aspect)
    else:  # height >= width
        new_h = min(int(target_size[1]), h)  # Don't upscale
        new_w = int(new_h * aspect)
    
    resized = cv2.resize(img_array, (new_w, new_h), interpolation=cv2.INTER_AREA)
    
    # Create a blank canvas with target size
    canvas = np.ones((target_size[1], target_size[0], 3), dtype=np.uint8) * 255
    
    # Calculate the position to paste the resized image
    y_offset = (target_size[1] - new_h) // 2
    x_offset = (target_size[0] - new_w) // 2
    
    # Paste the resized image
    canvas[y_offset:y_offset+new_h, x_offset:x_offset+new_w] = resized
    
    # Apply light normalization
    normalized = cv2.normalize(canvas, None, 0, 255, cv2.NORM_MINMAX)
    
    # Convert back to PIL image
    preprocessed_img = Image.fromarray(normalized)
    
    return preprocessed_img

def image_to_base64(image):
    """
    Convert PIL image to base64 encoded string
    
    Args:
        image (PIL.Image): Input image
        
    Returns:
        str: Base64 encoded string
    """
    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    img_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return img_str

def enhance_image_quality(image):
    """
    Enhance image quality for better analysis
    
    Args:
        image (PIL.Image): Input image
        
    Returns:
        PIL.Image: Enhanced image
    """
    img_array = np.array(image)
    
    # Convert to LAB color space
    lab = cv2.cvtColor(img_array, cv2.COLOR_RGB2LAB)
    
    # Split the LAB image into L, A, and B channels
    l, a, b = cv2.split(lab)
    
    # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization) to L channel
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    cl = clahe.apply(l)
    
    # Merge enhanced L channel with original A and B channels
    limg = cv2.merge((cl, a, b))
    
    # Convert back to RGB color space
    enhanced_img = cv2.cvtColor(limg, cv2.COLOR_LAB2RGB)
    
    return Image.fromarray(enhanced_img)
