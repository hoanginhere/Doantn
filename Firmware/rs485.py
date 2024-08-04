import os

def convert_csv_to_txt(directory):
    try:
        for filename in os.listdir(directory):
            if filename.endswith(".csv"):
                csv_file_path = os.path.join(directory, filename)
                txt_file_path = os.path.join(directory, filename.replace(".csv", ".txt"))
                os.rename(csv_file_path, txt_file_path)
                print(f"Đã đổi tên {csv_file_path} thành {txt_file_path}")
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")

# Thay đổi đường dẫn thư mục bên dưới thành đường dẫn thư mục của bạn
directory_path = "E:\\Doantn\\Firmware\\data_output"
convert_csv_to_txt(directory_path)
