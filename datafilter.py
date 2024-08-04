from ftplib import FTP
import os

def gui_file_ftp(hostname, username, password, ten_tep, duong_dan_moi):
    # Kết nối tới máy chủ FTP
    ftp = FTP(hostname)
    ftp.login(username, password)
    
    # Mở tệp tin cần gửi
    with open(ten_tep, 'rb') as file:
        # Đặt thư mục làm việc hiện tại trên máy chủ FTP
        ftp.cwd(duong_dan_moi)
        
        # Gửi dữ liệu tệp tin lên máy chủ FTP
        ftp.storbinary('STOR ' + ten_tep, file)
    
    # Đóng kết nối FTP
    ftp.quit()

# Thông tin kết nối FTP
hostname = 'files.000webhost.com'
username = 'huyhoang02'
password = 'Hoangvip.02'

# Đường dẫn thư mục chứa các tệp tin CSV
duong_dan_folder = 'D:/FTP'

# Lặp qua các tệp tin trong thư mục
for file_name in os.listdir(duong_dan_folder):
    # Kiểm tra nếu là tệp tin CSV
    if file_name.endswith('.csv'):
        # Đường dẫn đầy đủ đến tệp tin
        duong_dan_tep = os.path.join(duong_dan_folder, file_name)
        
        # Gửi tệp tin lên máy chủ FTP
        gui_file_ftp(hostname, username, password, duong_dan_tep, '/data')