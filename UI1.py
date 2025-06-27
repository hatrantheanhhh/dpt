# import tkinter as tk
# from tkinter import filedialog, messagebox
# import os

# # ====== Các hàm xử lý ======
# def import_video():
#     video_paths = filedialog.askopenfilenames(title="Chọn video để thêm vào CSDL", filetypes=[("MP4 files", "*.mp4")])
#     for video_path in video_paths:
#         # TODO: Gọi hàm xử lý thêm video vào CSDL
#         print(f"Đã chọn video: {video_path}")
#     messagebox.showinfo("Thông báo", "Đã thêm video vào CSDL.")

# def upload_image():
#     global query_image_path
#     query_image_path = filedialog.askopenfilename(title="Chọn ảnh truy vấn", filetypes=[("Image files", "*.jpg *.jpeg *.png")])
#     if query_image_path:
#         lbl_image_path.config(text=f"Đã chọn: {os.path.basename(query_image_path)}")

# def search_videos():
#     if not query_image_path:
#         messagebox.showwarning("Thiếu ảnh", "Vui lòng chọn ảnh để tìm kiếm.")
#         return
    
#     # TODO: Gọi hàm tìm kiếm video theo ảnh
#     # Ví dụ: results = search_video_by_image(query_image_path)
#     # Giả lập kết quả
#     results = ["video1.mp4", "video2.mp4", "video3.mp4"]
    
#     result_text.set("\n".join(results))

# # ====== Giao diện chính ======
# root = tk.Tk()
# root.title("Tìm kiếm video động vật")
# root.geometry("400x300")

# query_image_path = ""  # Biến lưu ảnh truy vấn
# result_text = tk.StringVar()

# # --- Các nút chức năng ---
# btn_import = tk.Button(root, text="📥 Thêm video vào CSDL", command=import_video)
# btn_import.pack(pady=10)

# btn_upload = tk.Button(root, text="🖼️ Upload ảnh", command=upload_image)
# btn_upload.pack()

# lbl_image_path = tk.Label(root, text="Chưa chọn ảnh")
# lbl_image_path.pack(pady=5)

# btn_search = tk.Button(root, text="🔍 Tìm kiếm video", command=search_videos)
# btn_search.pack(pady=10)

# tk.Label(root, text="🎬 Kết quả:").pack()
# tk.Label(root, textvariable=result_text, fg="blue").pack()

# root.mainloop()
import tkinter as tk
from tkinter import filedialog, messagebox
import os

from timkiem3 import timkiem, show  # đổi 'your_search_module' thành tên file .py chứa hàm timkiem()
db_path = "new_features.db"  # Đường dẫn đến CSDL của bạn

query_image_path = ""  # Biến toàn cục để lưu ảnh đã chọn

# ================== Các hàm nút ==================
def import_video():
    video_paths = filedialog.askopenfilenames(title="Chọn video để thêm vào CSDL", filetypes=[("MP4 files", "*.mp4")])
    for video_path in video_paths:
        # TODO: Gọi code xử lý thêm video vào CSDL
        print(f"Đã chọn video: {video_path}")
    messagebox.showinfo("Thông báo", "Đã thêm video vào CSDL.")

def upload_image():
    global query_image_path
    query_image_path = filedialog.askopenfilename(
        title="Chọn ảnh truy vấn", filetypes=[("Image files", "*.jpg *.jpeg *.png")]
    )
    if query_image_path:
        lbl_image_path.config(text=f"Ảnh: {os.path.basename(query_image_path)}")

def search_video():
    if not query_image_path:
        messagebox.showwarning("Thiếu ảnh", "Vui lòng chọn ảnh để tìm kiếm.")
        return

    try:
        ket_qua = timkiem(db_path, query_image_path, soluong=3, use_combined=True)
        if len(ket_qua) == 0:
            messagebox.showinfo("Kết quả", "Không tìm thấy kết quả phù hợp.")
        else:
            show(query_image_path, ket_qua)
    except Exception as e:
        messagebox.showerror("Lỗi tìm kiếm", str(e))

# ================== Giao diện chính ==================
root = tk.Tk()
root.title("🔍 Tìm kiếm Video Động Vật")
root.geometry("400x250")

# Nút thêm video
btn_import = tk.Button(root, text="📥 Thêm video vào CSDL", command=import_video)
btn_import.pack(pady=10)

# Nút upload ảnh
btn_upload = tk.Button(root, text="🖼️ Upload ảnh truy vấn", command=upload_image)
btn_upload.pack()

lbl_image_path = tk.Label(root, text="Chưa chọn ảnh")
lbl_image_path.pack(pady=5)

# Nút tìm kiếm
btn_search = tk.Button(root, text="🔎 Tìm kiếm video", command=search_video)
btn_search.pack(pady=10)

# Chạy vòng lặp GUI
root.mainloop()
