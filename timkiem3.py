import sqlite3
import json
import os
import cv2
import numpy as np
from tach5 import extract_color_histogram, extract_hog_feature

"""
Module: timkiem.py (GUI = PyQt5 + OpenCV)
----------------------------------------
• Cột trái: **"Hình ảnh yêu cầu"** + ảnh truy vấn phóng lớn.  
• Cột phải: **"Video 1/2/3"** + thumbnail đầu video (nút bấm).  
  ↳ Nhấp thumbnail → phát video bằng OpenCV (`cv2.imshow`).

🔧 **Fix 2025‑06‑27**  
`cv2.destroyWindow` gây lỗi *Null pointer* khi người dùng bấm ✖ trước khi vòng lặp kết thúc.  
→ Bọc `destroyWindow` trong `try/except` (hoặc kiểm tra tồn tại) để tránh crash.

Yêu cầu:
```bash
pip install PyQt5 opencv-python
```
"""

# =============================================================
# 1) Hàm tìm kiếm
# =============================================================

def timkiem(db_path: str, input_image_path: str, soluong: int = 5, use_combined: bool = True):
    """Trả về danh sách (id, video_name, frame_name, distance) gần nhất."""
    q_img = cv2.imread(input_image_path)
    if q_img is None:
        raise FileNotFoundError(f"Không mở được ảnh: {input_image_path}")

    hist_q = extract_color_histogram(q_img, resize=(128, 128))
    hog_q  = extract_hog_feature(q_img,  resize=(128, 128))

    conn = sqlite3.connect(db_path)
    cur  = conn.cursor()
    cur.execute(
        """SELECT id, video_name, frame_name, hog_vector, hist_vector
               FROM traditional_features
               WHERE removed = 0 AND hog_vector IS NOT NULL AND hist_vector IS NOT NULL"""
    )

    res = []
    for id_, vid, frame, hog_js, hist_js in cur.fetchall():
        hog_db  = np.array(json.loads(hog_js))
        hist_db = np.array(json.loads(hist_js))
        dist = np.linalg.norm(
            np.concatenate((hog_q, hist_q)) - np.concatenate((hog_db, hist_db))
        ) if use_combined else np.linalg.norm(hog_q - hog_db)
        res.append((id_, vid, frame, dist))
    conn.close()

    # Sắp xếp & lấy tối đa 1 frame/video
    res.sort(key=lambda x: x[3])
    uniq, out = set(), []
    for r in res:
        if r[1] not in uniq:
            out.append(r)
            uniq.add(r[1])
        if len(out) == soluong:
            break
    return out

# =============================================================
# 2) Hàm hiển thị (PyQt5 + thumbnail + OpenCV player)
# =============================================================

def show(input_image_path: str, results: list, video_dir: str = "Video-collected"):
    from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
    from PyQt5.QtGui import QPixmap, QImage, QIcon
    from PyQt5.QtCore import QSize, Qt
    import sys

    class VideoApp(QWidget):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("Kết quả tìm kiếm video")

            # ---- Cấu hình kích thước cửa sổ ----
            screen = QApplication.primaryScreen().availableGeometry()
            sw, sh = screen.width(), screen.height()
            self.resize(int(sw * 0.6), int(sh * 0.8))

            main = QHBoxLayout(self)

            # ---- Cột trái: ảnh truy vấn ----
            left = QVBoxLayout()
            lbl_title_q = QLabel("Hình ảnh yêu cầu")
            lbl_title_q.setAlignment(Qt.AlignCenter)
            lbl_title_q.setStyleSheet("font-weight:bold; font-size:16px")
            left.addWidget(lbl_title_q)

            lbl_q = QLabel()
            q = cv2.cvtColor(cv2.imread(input_image_path), cv2.COLOR_BGR2RGB)
            side = int(sh * 0.6)
            q = cv2.resize(q, (side, side))
            h, w, c = q.shape
            lbl_q.setPixmap(QPixmap.fromImage(QImage(q.data, w, h, c*w, QImage.Format_RGB888)))
            left.addWidget(lbl_q)
            main.addLayout(left)

            # ---- Cột phải: 3 video ----
            right = QVBoxLayout()
            tsize = QSize(int(sw*0.24), int(sw*0.24*9/16))

            for idx, res in enumerate(results[:3], 1):
                vid = str(res[1])
                vpath = os.path.join(video_dir, f"{vid}.mp4")

                lbl_vid = QLabel(f"Video {idx}")
                lbl_vid.setAlignment(Qt.AlignCenter)
                lbl_vid.setStyleSheet("font-weight:bold")
                right.addWidget(lbl_vid)

                btn = QPushButton()
                btn.setIcon(QIcon(self.make_thumb(vpath, tsize)))
                btn.setIconSize(tsize)
                btn.setFixedSize(tsize.width()+20, tsize.height()+20)
                btn.clicked.connect(lambda _, p=vpath, sw=sw: self.play_video(p, sw))
                right.addWidget(btn)

            main.addLayout(right)

        # ---------- Thumbnail helper ----------
        def make_thumb(self, vpath, size):
            if not os.path.exists(vpath):
                return QPixmap(size)
            cap = cv2.VideoCapture(vpath)
            ok, frame = cap.read(); cap.release()
            if not ok:
                return QPixmap(size)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (size.width(), size.height()))
            return QPixmap.fromImage(QImage(frame.data, size.width(), size.height(), 3*size.width(), QImage.Format_RGB888))

        # ---------- Video player helper ----------
        def play_video(self, vpath, sw):
            cap = cv2.VideoCapture(vpath)
            if not cap.isOpened():
                print(f"[⚠] Không mở {vpath}"); return
            win = os.path.basename(vpath)
            cv2.namedWindow(win, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(win, int(sw*0.5), int(sw*0.5*9/16))
            while True:
                ret, frame = cap.read()
                visible = cv2.getWindowProperty(win, cv2.WND_PROP_VISIBLE) >= 1
                if not ret or not visible:
                    break
                cv2.imshow(win, frame)
                if cv2.waitKey(25) & 0xFF in (27, ord('q')):
                    break
            cap.release()
            try:
                cv2.destroyWindow(win)
            except cv2.error:
                pass  # window already closed

    app = QApplication(sys.argv)
    gui = VideoApp(); gui.show(); app.exec_()

# =============================================================
# 3) Demo test nhanh
# =============================================================
if __name__ == "__main__":
    DB = "new_features.db"; IMG = r"Frames/38/38_frame-002.jpg"; VID_DIR = "Video-collected"
    top = timkiem(DB, IMG, soluong=3)
    show(IMG, top, video_dir=VID_DIR)
