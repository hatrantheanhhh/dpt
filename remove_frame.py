import os 
import json
import cv2
import numpy as np
from export_detail import extract_color_histogram, search_by_color, extract_sift
import sqlite3
from tach5 import extract_color_histogram, extract_hog_feature, tach_nen

'''
#đoạn code này làm 3 việc: 
# đưa tất cả removed = 0, 
# tìm các frame giống nhau r lọc = cách cho removed = 1, 
# tìm hog và hist (vector đặc trưng) của các frame dc giữ lại
đang chạy tốt
# '''

db = "new_features.db"
conn = sqlite3.connect(db)
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM traditional_features")
number = cursor.fetchone()[0]


def get_hist(f):
    hist_bytes = f[0]
    try:
        hist = np.frombuffer(hist_bytes, dtype=np.float32)
        return hist
    except Exception as e:
        print(f"lỗi: {e}")
    return

for i in range(1, number):
    cursor.execute("UPDATE traditional_features SET removed = 0 WHERE id="+str(i))
conn.commit()
for i in range(1, number):
    cursor.execute("SELECT color_histogram FROM traditional_features WHERE id = "+str(i))
    f1 = cursor.fetchone()
    # print(type(f1))
    cursor.execute("SELECT color_histogram FROM traditional_features WHERE id = "+str(i+1))
    f2 = cursor.fetchone()
    hist1 = get_hist(f1)
    hist2 = get_hist(f2)
    hist1 = np.array(hist1).flatten()
    hist2 = np.array(hist2).flatten()
    if hist1.size != hist2.size:
        print(f"Histogram size mismatch: {hist1.size} vs {hist2.size}")
        hist2 = np.resize(hist2, hist1.shape)

    # so sánh histogram của cả frame, chưa tách nền, để lọc các frame giống nhau (cùng 1 cảnh quay)
    similarity = 1 - cv2.compareHist(hist1, hist2, cv2.HISTCMP_HELLINGER)
    print(similarity, i, i+1)
    if similarity >0.6:
        cursor.execute("UPDATE traditional_features SET removed = 1 WHERE id="+str(i+1))

for i in range(1, number):
    #nạp hít, hog cho các hàng có removed=0
    cursor.execute("SELECT video_name, frame_name, removed FROM traditional_features WHERE id = ?", (i,))
    result = cursor.fetchone()
    video, frame, removed = result
    if removed: 
        cursor.execute("UPDATE traditional_features SET hist_vector = NULL, hog_vector = NULL WHERE id = ?", (i,))
        continue
    print(video+"\\"+frame)
    # img = tach_nen(str(i)+"\\"+str(i)+"_frame-"+str(i).zfill(3)+".jpg")
    img = tach_nen(video+"\\"+frame)
    # img = tach_nen("img1.jpg")
    hist_vector = extract_color_histogram(img)
    hog_vector = extract_hog_feature(img)

    hist_json = json.dumps(hist_vector.tolist())
    hog_json = json.dumps(hog_vector.tolist())

    cursor.execute("""
    UPDATE traditional_features 
    SET hist_vector = ? 
    WHERE id=?
    """, (hist_json, i))
    cursor.execute("""
    UPDATE traditional_features 
    SET hog_vector = ? 
    WHERE id=?
    """, (hog_json, i))


    #trong file báo cáo nên đề xuất 2 cách: gộp 2
    #vector lại hoặc giữ nguyên 2 vector để tìm khoảng cách, 
    #team mình chọn cách 2
conn.commit()
cursor.close()
conn.close()

print("done")