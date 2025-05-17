Mn clone về máy và chạy file timkiem.py nhé

Bước 1: Thêm 3 cột mới vào csdl: hog_vector, hist_vector, removed
Mà tải luôn file db mới nè, link Drive: https://drive.google.com/file/d/100CoNxpVwJOu5jZXJrDZhqLFKwkd2F-W/view?usp=sharing
Database này mới chỉ chứa vector đặc trưng của 10 video đầu, chỉ cần các cột id, video_name, frame_name, hog_feature, hist_feature, removed, các cột còn lại mình không sử dụng.

Bước 2: clone 3 file code về cùng 1 thư mục với db và các folder chứa frame, chạy file timkiem.py

Code đang bị lỗi không xử lý dc ảnh đen sì nên mn thêm video vào db thì cắt đầu đuôi nó ra nhé (nếu có hình bị đen)
Các frame bị đen có thể xử lý bằng cách: xóa frame đó đi, nhân bản frame lân cận có chứa nội dung (không bị đen sì), lưu với tên cũ của frame bị xóa
VD: có ảnh 1_frame-004.jpg bình thường, ảnh 1_frame-005.jpg bị đen, hãy xóa ảnh 005 đi và copy ảnh 004 rồi đổi tên bản copy thành 1_frame-005.jpg

Đảm báo cấu trúc project bao gồm folder chứa các frame với cấu trúc: (sttvideo)\(sttvideo_frame-xxx.jpg) ví dụ "1\1_frame-005.jpg" là frame thứ 5 trong video 1, mỗi folder chứa các frame của chỉ 1 video

