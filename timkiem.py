import sqlite3
import json
import cv2
import numpy as np
from tach5 import extract_color_histogram, extract_hog_feature

"""
tìm kiếm các ảnh tương đồng trong CSDL dựa trên vector đặc trưng
"""
def timkiem(db_path, input_image_path, soluong=5, use_combined=True):

    image = cv2.imread(input_image_path)
    hist_vector = extract_color_histogram(image, resize=(128, 128))
    hog_vector = extract_hog_feature(image, resize=(128, 128))

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    #lấy các vector từ db (bỏ qua những hàng có removed = 1 hoặc vector NULL)
    cursor.execute("""
        SELECT id, video_name, frame_name, hog_vector, hist_vector 
        FROM traditional_features 
        WHERE removed = 0 AND hog_vector IS NOT NULL AND hist_vector IS NOT NULL
    """)

    results = []
    for row in cursor.fetchall():
        id, video_name, frame_name, hog_json, hist_json = row
        db_hog_vector = np.array(json.loads(hog_json))
        db_hist_vector = np.array(json.loads(hist_json))

        #tính khoảng cách giữa vector đặc trưng của input với các vct của các ảnh trong db
        if use_combined:
            combined_input = np.concatenate((hog_vector, hist_vector))
            combined_db = np.concatenate((db_hog_vector, db_hist_vector))
            distance = np.linalg.norm(combined_input - combined_db)
            # distance = np.linalg.norm(hog_vector - db_hog_vector)
        else:
            distance = np.linalg.norm(hog_vector - db_hog_vector)

        results.append((id, video_name, frame_name, distance))


    results.sort(key=lambda x: x[3])

    s = set()
    kq_cuoi_cung = []

    for res in results:
        if res[1] not in s:
            kq_cuoi_cung.append(res)
            s.add(res[1])
        if len(kq_cuoi_cung) == soluong:
            break

    conn.close()
    return kq_cuoi_cung

def show(input_image_path, results):
    """
    Cái này k biết vẽ nên nhờ AI vẽ hộ, trông hơi lỏ
    Hiển thị ảnh đầu vào và 5 kết quả tìm kiếm trên cùng một cửa sổ.

    Parameters:
        input_image_path (str): Đường dẫn đến ảnh đầu vào.
        results (list): Danh sách kết quả tìm được.
    """
    # Đọc và hiển thị ảnh đầu vào
    input_image = cv2.imread(input_image_path)
    input_image = cv2.resize(input_image, (200, 200))

    # Tạo danh sách ảnh hiển thị (bắt đầu với ảnh đầu vào)
    display_images = [input_image]
    labels = ["Query"]

    # Đọc ảnh từ kết quả tìm được
    for res in results:
        _, video_name, frame_name, _ = res
        image_path = f"{video_name}/{frame_name}"
        img = cv2.imread(image_path)
        if img is not None:
            img = cv2.resize(img, (200, 200))
            display_images.append(img)
            labels.append(f"{video_name}\n{frame_name}")

    # Tạo cửa sổ hiển thị kết quả
    combined_image = np.hstack(display_images)
    cv2.imshow("Kết quả tìm kiếm", combined_image)
    print("\n".join(labels))
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Ví dụ sử dụng:
if __name__ == "__main__":
    db_path = "new_features.db"
    input_image = "img2.jpg"  # Đường dẫn đến ảnh cần tìm kiếm
    
    ket_qua = timkiem(db_path, input_image, soluong=5, use_combined=True)
    show(input_image, ket_qua)
