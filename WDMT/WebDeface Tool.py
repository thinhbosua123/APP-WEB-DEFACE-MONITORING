from PyQt5 import QtWidgets, QtGui, QtCore
from bs4 import BeautifulSoup
import shutil
from PyQt5.QtCore import QDateTime

class MyApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Web Deface Tool')
        self.setGeometry(100, 100, 1000, 1000)
        self.initUI()

    def initUI(self):
        # Button 1
        btn1 = QtWidgets.QPushButton('Change HTML', self)
        btn1.setGeometry(QtCore.QRect(100, 50, 200, 50))
        btn1.clicked.connect(self.change_html)

        # Button 2
        btn2 = QtWidgets.QPushButton('Change Audio', self)
        btn2.setGeometry(QtCore.QRect(100, 150, 200, 50))
        btn2.clicked.connect(self.copy_audio)

        # Button 3
        btn3 = QtWidgets.QPushButton('Change Image', self)
        btn3.setGeometry(QtCore.QRect(100, 250, 200, 50))
        btn3.clicked.connect(self.copy_image)

        # Thêm 1 label và 1 text edit để ghi lịch sử
        self.history_label = QtWidgets.QLabel(self)
        self.history_label.setText("History:")
        self.history_label.move(10, 350)
        self.history_output = QtWidgets.QTextEdit(self)
        self.history_output.move(5, 400)
        self.history_output.setFixedWidth(990)
        self.history_output.setFixedHeight(1000)
        self.history_output.setReadOnly(True)

        self.show()  # Ensure show() is called after all widgets are initialized

    def update_info_textbox(self, text):
        current_time = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        self.history_output.append(f"[{current_time}] {text}")

    def change_html(self):
        file_path = "D:/WDMT/Web/Orginal/templates/index.html"
        # Read content of HTML file
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            # Parse HTML content
            soup = BeautifulSoup(content, "html.parser")
            # Find h1 tag with class="title" and replace its content
            h1_tag = soup.find("h1", {"class": "title"})
            h1_tag.string.replace_with("Trang thông tin nhóm -----ABC------")
        # Write modified content back to file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(str(soup))
        self.update_info_textbox("Đã thay đổi nội dung text thành công")
        self.update_info_textbox("-----------------------------------------------")

    def copy_audio(self):
        source_file_path = "D:/WDMT/Web/hack/audio2.m4a"
        target_folder_path = "D:/WDMT/Web/Orginal/static/sounds"
        shutil.copy(source_file_path, target_folder_path)
        self.update_info_textbox("Đã thay đổi file audio thành công")
        self.update_info_textbox("-----------------------------------------------")

    def copy_image(self):
        source_file_path = "D:/WDMT/Web/hack/image3.png"
        target_folder_path = "D:/WDMT/Web/Orginal/static/images/"
        shutil.copy(source_file_path, target_folder_path)
        self.update_info_textbox("Đã thay đổi file image thành công")
        self.update_info_textbox("-----------------------------------------------")

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    window = MyApp()
    app.exec_()
