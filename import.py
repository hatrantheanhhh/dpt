import os
import cv2
import matplotlib.pyplot as plt
import json
import sqlite3
from tach5 import tach_nen, extract_color_histogram, extract_hog_feature

#file import, nó đã xong nhiệm vụ, đừng chạy nữa, nổ đấyyyyy
#file import, nó đã xong nhiệm vụ, đừng chạy nữa, nổ đấyyyyy
#file import, nó đã xong nhiệm vụ, đừng chạy nữa, nổ đấyyyyy


db = "new_featuress.db"
conn = sqlite3.connect(db)
cursor = conn.cursor()


def doc_anh_thu_muc(thu_muc, index):
    """
    Đọc và hiển thị lần lượt các ảnh trong thư mục.

    Parameters:
        thu_muc (str): Đường dẫn tới thư mục chứa ảnh.
    """
    # Lấy danh sách file trong thư mục
    danh_sach_file = os.listdir(thu_muc)
    danh_sach_file_anh = [f for f in danh_sach_file if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff'))]
    
    if not danh_sach_file_anh:
        print("Thư mục không chứa ảnh nào.")
        return
    
    for file_anh in danh_sach_file_anh:
        path = os.path.join(thu_muc, file_anh)

        print(thu_muc, file_anh, path)
        img_full = cv2.imread(path)
        img = tach_nen(path)

        hist_vector = extract_color_histogram(img)
        hist_json = json.dumps(hist_vector.tolist())

        hog_vector = extract_hog_feature(img)
        hog_json = json.dumps(hog_vector.tolist())

        hist_full = extract_color_histogram(img_full)
        color_hist_bytes = hist_full.tobytes() if hist_full.size > 0 else None  

        cursor.execute("""
        INSERT INTO traditional_features (
            video_name, frame_name, color_histogram, removed
        ) VALUES (?, ?, ?, ?)
        """, (index, file_anh, color_hist_bytes, 0,))
        # # Hiển thị ảnh
        # plt.imshow(cv2.cvtColor(anh, cv2.COLOR_BGR2RGB))
        # plt.title(file_anh)
        # plt.show()
    conn.commit()



for i in range(1, 121):
    path = "Frames\\"+str(i)
    doc_anh_thu_muc(path, i)
