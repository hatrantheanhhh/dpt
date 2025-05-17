import cv2 #lấy
import numpy as np
import matplotlib.pyplot as plt
from skimage import feature

'''
file code này để tách nền ảnh, được file remove_frame import rồi nên k cần chạy file này
có 2 hàm extract_hog_feature, extract_color_histogram dùng AI nên nó dùng các hàm có sẵn, 
nếu có tgian thì mn có thể bung nó ra (thành code trâu) để hiểu thuật toán hơn

'''
def tach_nen(path):
    image = cv2.imread(path)
    height, width = image.shape[:2]
    vien = np.concatenate([
        image[0, :, :],      
        image[height-1, :, :],
        image[:, 0, :],     
        image[:, width-1, :]
    ], axis=0)

    vien_hsv = cv2.cvtColor(vien.reshape(-1, 1, 3), cv2.COLOR_BGR2HSV).reshape(-1, 3)

    trung_binh = np.mean(vien_hsv, axis=0) #tính trung bình các màu trên 4 cạnh cảu ảnh-để tách nền cơ bản
    bien_do = np.std(vien_hsv, axis=0) #tính độ lệch chuẩn của 4 cạnh của ảnh

    print("tb=", trung_binh)
    print("range=", bien_do)

    HUE_range = 30  #để lọc các pixel cạnh nhau có màu (sắc độ) lệch nhau dưới 30 đơn vị
    lower_bound = np.array([max(0, trung_binh[0]-HUE_range), max(0, trung_binh[1]-bien_do[1]), max(0, trung_binh[2]-bien_do[2])  
    ])
    upper_bound = np.array([
        min(179, trung_binh[0]+HUE_range),  min(255, trung_binh[1]+bien_do[1]),  min(255, trung_binh[2]+bien_do[2]) 
    ])
    #lọc nền và trả về kq
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_image, lower_bound, upper_bound)
    mask_lat_nguoc = cv2.bitwise_not(mask)
    result = cv2.bitwise_and(image, image, mask=mask_lat_nguoc)
    return result



def extract_hog_feature(image, resize=(128, 128)):
    """
    Extract HOG (Histogram of Oriented Gradients) feature vector from an image.

    Parameters:
        image (numpy.ndarray): Input image (RGB or grayscale).
        resize (tuple): Optional. Resize image to (width, height) before extraction.
                        Default is (128, 128).

    Returns:
        numpy.ndarray: HOG feature vector.
    """
    # Convert to grayscale if image is RGB
    if len(image.shape) == 3:
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray_image = image

    # Resize image if specified
    if resize:
        gray_image = cv2.resize(gray_image, resize)

    # Extract HOG features
    hog_features, _ = feature.hog(
        gray_image, 
        orientations=9, 
        pixels_per_cell=(8, 8), 
        cells_per_block=(2, 2), 
        transform_sqrt=True, 
        block_norm="L2",
        visualize=True
    )
    print("hog feature vector shape:", np.array(hog_features).shape)
    return np.array(hog_features)

def extract_color_histogram(image, bins=(8, 8, 8), resize=None):
    """
    Extract color histogram feature vector from an image.

    Parameters:
        image (numpy.ndarray): Input image (RGB).
        bins (tuple): Number of bins for each color channel (H, S, V).
        resize (tuple): Optional. Resize image to (width, height) before extraction.

    Returns:
        numpy.ndarray: Color histogram feature vector.
    """
    # Resize image if specified
    if resize:
        image = cv2.resize(image, resize)

    # Convert to HSV color space
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Calculate histogram and normalize
    hist = cv2.calcHist([hsv_image], [0, 1, 2], None, bins, [0, 180, 0, 256, 0, 256])
    hist = cv2.normalize(hist, hist).flatten()
    print("hist ", hist.shape)
    return hist


def khoang_cach(x, y):
    return np.sqrt(np.sum((x-y) ** 2))



