import os
import cv2
import pickle
import numpy as np
from export_detail import extract_color_histogram, search_by_color, extract_sift
import sqlite3
db = "new_features.db"
# Connect to database
conn = sqlite3.connect(db)
cursor = conn.cursor()

# def search_by_color(query_hist, top_k=3):
#     conn = sqlite3.connect(db)
#     cursor = conn.cursor()
    
#     results = []
#     for row in cursor.execute("SELECT id, video_name, frame_name, color_histogram FROM traditional_features LIMIT 100"):
#         id, video_name, frame_name, color_hist_bytes = row
        
#         if color_hist_bytes:
#             db_hist = np.frombuffer(color_hist_bytes, dtype=np.float32)
            
#             # Calculate chi-square distance (suitable for histogram)
#             distance = cv2.compareHist(query_hist, db_hist, cv2.HISTCMP_CHISQR)
#             results.append((id, video_name, frame_name, distance))

# def search_by_color(query_hist, top_k=5):
#     results = []
#     for row in cursor.execute("SELECT id, video_name, frame_name, color_histogram FROM traditional_features"):
#         id, video_name, frame_name, color_hist_bytes = row
        
#         if color_hist_bytes:
#             try:
#                 db_hist = np.frombuffer(color_hist_bytes, dtype=np.float32)

#                 # Đảm bảo histogram có cùng kích thước
#                 if query_hist.size == db_hist.size:
#                     distance = cv2.compareHist(query_hist, db_hist, cv2.HISTCMP_CHISQR)
#                     results.append((id, video_name, frame_name, distance))
#                 else:
#                     print(f"Histogram size mismatch: Query {query_hist.size} vs DB {db_hist.size}")
            
#             except Exception as e:
#                 print(f"Error processing row {id}: {e}")


    
#     # Sort by distance in ascending order
#     results.sort(key=lambda x: x[3])
#     conn.close()
    
#     return results[:top_k]
def filtered_result(results):
    unique_videos = set()
    filtered_results = []

    for video, frame, distance in results:
        if video not in unique_videos:
            filtered_results.append((video, frame, distance))
            unique_videos.add(video)

        if len(filtered_results) >= 5:
            break

    return filtered_results
def search_by_color(query_hist, top_k=5):
    results = []
    for row in cursor.execute("SELECT id, video_name, frame_name, color_histogram FROM traditional_features"):
        id, video_name, frame_name, color_hist_bytes = row
        
        if color_hist_bytes:
            try:
                db_hist = np.frombuffer(color_hist_bytes, dtype=np.float32)

                # Kiểm tra kích thước của query_hist và db_hist
                if query_hist.size == db_hist.size:
                    # print(type(db_hist))
                    # print(type(query_hist))
                    # distance = cv2.compareHist(query_hist.flatten(), db_hist, cv2.HISTCMP_CORREL)
                    distance = cv2.compareHist(query_hist.flatten(), db_hist, cv2.HISTCMP_HELLINGER)
                    results.append((video_name, frame_name, distance))
                else:
                    print(f"Histogram size mismatch: Query {query_hist.size} vs DB {db_hist.size}")
            
            except Exception as e:
                print(f"Error processing row {id}: {e}")

    # Sort by distance in ascending order
    results.sort(key=lambda x: x[2])
    conn.close()


    return filtered_result(results)


def search_by_sift(query_image, top_k=5):
    """Search for similar images based on SIFT features"""
    # Extract SIFT from query image
    query_keypoints, query_descriptors = extract_sift(query_image)
    
    if len(query_descriptors) == 0:
        return []
    
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    
    results = []
    for row in cursor.execute("SELECT id, video_name, frame_name, sift_descriptors FROM traditional_features LIMIT 10"):
        id, video_name, frame_name, sift_bytes = row
        
        if sift_bytes:
            # Convert from bytes to array
            db_descriptors = np.frombuffer(sift_bytes, dtype=np.float32)
            
            # Check size
            if db_descriptors.size == 0:
                continue
                
            # Reshape array
            descriptor_size = 128  # SIFT default has 128 dimensions
            db_descriptors = db_descriptors.reshape(-1, descriptor_size)
            
            # Create matcher
            bf = cv2.BFMatcher()
            matches = bf.knnMatch(query_descriptors, db_descriptors, k=2)
            
            # Apply Lowe's ratio test
            good_matches = []
            for m, n in matches:
                if m.distance < 0.75 * n.distance:
                    good_matches.append(m)
            
            # Number of good matches is the similarity measure
            similarity = len(good_matches)
            results.append((id, video_name, frame_name, similarity))
    
    # Sort by number of matches in descending order
    results.sort(key=lambda x: x[3], reverse=True)
    conn.close()
    
    return filtered_result(results[:top_k])

# Example usage of color search
def find_similar_by_color(query_image_path):
    # Read query image
    query_image = cv2.imread(query_image_path)
    query_hist = extract_color_histogram(query_image)
    

    ##duke
    for row in cursor.execute("SELECT id, video_name, frame_name, color_histogram FROM traditional_features LIMIT 10"):
        id, video_name, frame_name, col = row

    # Search
    results = search_by_color(query_hist, top_k=5)
    
    print(f"Search results for {query_image_path}:")
    for id, video, frame, distance in results:
        print(f"- Video: {video}, Frame: {frame}, Distance: {distance:.2f}")



# def find_similar_by_hist(query_image_path):
#     # Read query image
#     query_image = cv2.imread(query_image_path)
#     query_hist = extract_color_histogram(query_image)
    

#     ##duke
#     for row in cursor.execute("SELECT id, video_name, frame_name, color_histogram FROM traditional_features LIMIT 10"):
#         id, video_name, frame_name, db_hist = row
#         print(type(db_hist), type(query_hist))

def compare_histogram(query_image_path, top_k=5):
    # Read query image
    query_image = cv2.imread(query_image_path)
    if query_image is None:
        print(f"Cannot read image from {query_image_path}")
        return []

    # Extract histogram of query image
    query_hist = extract_color_histogram(query_image)

    # Connect to database
    conn = sqlite3.connect(db)
    cursor = conn.cursor()

    results = []

    for row in cursor.execute("SELECT id, video_name, frame_name, color_histogram FROM traditional_features"):
        id, video_name, frame_name, color_hist_bytes = row
        # print(type(color_hist_bytes))
        if color_hist_bytes:
            try:
                db_hist = np.frombuffer(color_hist_bytes, dtype=np.float32).flatten()

                # print(query_hist.shape, db_hist.shape)
                if query_hist.shape == db_hist.shape or 1:
                    # print(1)
                    distance = cv2.compareHist(query_hist.flatten(), db_hist, cv2.HISTCMP_CHISQR)
                    results.append((video_name, frame_name, distance))

            except Exception as e:
                print(f"Error processing row {id}: {e}")

    conn.close()

    results.sort(key=lambda x: x[2])

    # Chỉ lấy frame từ tối đa 5 video khác nhau
    unique_videos = set()
    filtered_results = []

    for video, frame, distance in results:
        if video not in unique_videos:
            filtered_results.append((video, frame, distance))
            unique_videos.add(video)

        if len(filtered_results) >= top_k:
            break
    for video, frame, distance in filtered_results:
        print(f"- Video: {video}, Frame: {frame}, Similarity: {1/(1+distance):.4f}")
    return filtered_results
        

# def show_frame_from_db(video_name, frame_name):
#     frame_path = "vd"+str(video_name)+"\\"+str(video_name)+"\\"+frame_name
#     frame_img = cv2.imread(frame_path)
#     cv2.imshow(f"Video: {video_name} - Frame: {frame_name}", frame_img)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()
def show_frame_from_db(query_image_path, results):
    # Đọc ảnh đầu vào
    query_image = cv2.imread(query_image_path)
    if query_image is None:
        print("Không thể đọc ảnh đầu vào.")
        return

    # Đọc 5 ảnh kết quả
    images = [query_image]  # Ảnh đầu vào là ảnh đầu tiên
    for video_name, frame_name, _ in results:
        frame_path = "vd" + str(video_name) + "\\" + str(video_name) + "\\" + frame_name
        frame_img = cv2.imread(frame_path)
        if frame_img is not None:
            images.append(frame_img)

    # Đảm bảo có đủ 6 ảnh (1 ảnh input + 5 kết quả)
    if len(images) < 6:
        print("Không đủ ảnh kết quả.")
        return

    # Định kích thước ảnh để dễ dàng ghép
    image_height = 300  # Chiều cao cố định cho tất cả ảnh
    image_width = 300   # Chiều rộng cố định cho tất cả ảnh

    resized_images = [cv2.resize(img, (image_width, image_height)) for img in images]

    # Ghép ảnh thành 1 cửa sổ
    top_row = np.hstack(resized_images[:3])   # 3 ảnh hàng trên
    bottom_row = np.hstack(resized_images[3:]) # 3 ảnh hàng dưới
    final_image = np.vstack([top_row, bottom_row])

    # Hiển thị ảnh kết quả
    cv2.imshow("Query and Top 5 Results", final_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def test_search_by_color(query_image_path):
    """
    Test function for color search
    """
    # Path to query image
    # query_image_path = input("Nhập đường dẫn đến ảnh truy vấn (mặc định: test.jpg): ") or "test.jpg"
    # query_image_path = "img1.jpg"
    
    # Check if file exists
    if not os.path.exists(query_image_path):
        print(f"File does not exist: {query_image_path}")
        return
        
    # Read query image
    query_image = cv2.imread(query_image_path)
    if query_image is None:
        print(f"Cannot read image from {query_image_path}")
        return
        
    # Extract color histogram
    query_hist = extract_color_histogram(query_image)
    
    # Search for similar images
    results = search_by_color(query_hist, top_k=5)
    
    # Display results
    print(f"Top 5 results similar to {os.path.basename(query_image_path)}:")
    for video, frame, distance in results:
        print(f"- Video: {video}, Frame: {frame}, Similarity: {1/(1+distance):.4f}")
        
        # Optional: display result image
        frame_path = os.path.join("Frames", video, frame)
        if os.path.exists(frame_path):
            result_img = cv2.imread(frame_path)
            if result_img is not None:
                cv2.imshow(f"Result {id}", result_img)
    
    if cv2.waitKey(0):
        cv2.destroyAllWindows()
    return results

if __name__ == "__main__":
    # test_search_by_color()
    show_frame_from_db("vd3\\3\\3_frame-002.jpg", test_search_by_color("vd3\\3\\3_frame-002.jpg"))
    # find_similar_by_hist("img1.png")

    # query_image_path = "img1.jpg"  
    # # results = compare_histogram(query_image_path, top_k=5)

    # # print("Top 5 similar frames:")
    # # for video, frame, distance in results:
    # #     print(f"Video: {video}, Frame: {frame}, Distance: {distance:.4f}")
    # show_frame_from_db("vd1\\1\\1_frame-002.jpg", compare_histogram("img1.jpg", top_k=5))





    # #thử đổi BLOB sang vector
    # for x in cursor.execute("SELECT id, video_name, frame_name, color_histogram FROM traditional_features LIMIT 1"):
    #     _, _, _, hist = x
    #     print(hist, pickle.loads(hist))

    # cursor.execute("SELECT id, video_name, frame_name, color_histogram FROM traditional_features LIMIT 1")
    # x = cursor.fetchone()
    # _, _, _, hist = x
    # print(hist, pickle.loads(hist))

    # cursor.execute("SELECT id, video_name, frame_name, color_histogram FROM traditional_features LIMIT 1")
    # x = cursor.fetchone()  # Lấy một dòng từ kết quả

    # if x:  # Kiểm tra nếu có dữ liệu trả về
    #     _, _, _, hist = x  # Tách giá trị từ tuple
    #     print(f"BLOB: {hist}")  # In ra giá trị BLOB (nhị phân)
    #     print(f"Vector Histogram: {pickle.loads(hist)}")  # Giải mã BLOB thành vector histogram
    # else:
    #     print("Không có dữ liệu.")



'''
hướng: 1 video có khoảng 100-200 frames, sau đó tính tương quan histogram 2 frame cạnh nhau, nếu chúng giống nhau 99% thì bỏ bớt 1 cái
để lọc các frame trong cùng 1 cảnh quay, mỗi cảnh quay giữ lại dc ít nhất 1 frame là đủ dùng -> tối ưu tốc độ, nhma chưa biết làm :)
phải sửa csdl, thêm 1 cột similarity_with_previous_frame để đánh dấu là tương đồng hoặc xóa mẹ frame đó luôn
có 2 hàm tìm theo histogram là compare_histogram() và search_by_color(), ra kết quả giống nhau nhưng thuật toán của search_by_color oke hơn
t giải nén các folder chứa frame ra và đổi tên thành vd1, vd2, vd3, 1 đường dẫn cụ thể vào 1 frame là vd1\1\1_frame-002.jpg

'''
