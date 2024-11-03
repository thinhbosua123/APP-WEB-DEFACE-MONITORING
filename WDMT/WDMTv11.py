import hashlib
import smtplib
import ssl
import threading
import time
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from pathlib import Path
from PyQt5 import QtWidgets, QtGui, QtCore
import os
from bs4 import BeautifulSoup
from PyQt5.QtCore import QDateTime
import shutil
import telegram
import asyncio
import requests
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
import re


class MyWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MyWindow, self).__init__()

        self.initUI()

    def initUI(self):
        # Thêm 2 label và 2 line edit để nhập URL và email
        self.url_label = QtWidgets.QLabel(self)
        self.url_label.setText("URL:")
        self.url_label.move(100, 50)
        self.url_input = QtWidgets.QLineEdit(self)
        self.url_input.move(300, 50)
        self.url_input.setFixedWidth(500)
        self.email_label = QtWidgets.QLabel(self)
        self.email_label.setText("Receiver Email:")
        self.email_label.move(100, 100)
        self.email_label.setFixedWidth(200)
        self.email_input = QtWidgets.QLineEdit(self)
        self.email_input.move(300, 100)
        self.email_input.setFixedWidth(500)

        # Thêm 3 nút Store Config, Start, Help
        self.backup_config_button = QtWidgets.QPushButton(self)
        self.backup_config_button.setText("Backup config")
        self.backup_config_button.move(200, 200)
        self.backup_config_button.clicked.connect(self.backup_config)
        self.backup_config_button.resize(150, 50)

        self.start_button = QtWidgets.QPushButton(self)
        self.start_button.setText("Start")
        self.start_button.move(400, 200)
        self.start_button.clicked.connect(self.start_action)
        self.start_button.resize(150, 50)

       

        self.rollback_button = QtWidgets.QPushButton(self)
        self.rollback_button.setText("Rollback")
        self.rollback_button.move(600, 200)
        self.rollback_button.clicked.connect(self.rollback)
        self.rollback_button.resize(150, 50)

        self.about_button = QtWidgets.QPushButton(self)
        self.about_button.setText("About")
        self.about_button.move(800, 200)
        self.about_button.resize(150, 50)
        self.about_button.clicked.connect(self.about)

        # Thêm 1 label và 1 text edit để ghi lịch sử
        self.history_label = QtWidgets.QLabel(self)
        self.history_label.setText("History:")
        self.history_label.move(100, 250)
        self.history_output = QtWidgets.QTextEdit(self)
        self.history_output.move(50, 300)
        self.history_output.setFixedWidth(1100)
        self.history_output.setFixedHeight(1200)
        self.history_output.setReadOnly(True)

        # Kích thước cửa sổ và tọa độ trung tâm
        self.setGeometry(300, 300, 1200, 1200)
        self.setWindowTitle('Web Deface Monitoring Tool')
        self.show()

    def update_info_textbox(self, text):
        current_time = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")
        self.history_output.append(f"[{current_time}] {text}")
    async def send_telegram(self, message, bot_token, chat_id):
        try:
            bot = telegram.Bot(token=bot_token)
            await bot.send_message(chat_id=chat_id, text=message,
                                parse_mode='Markdown')
        except Exception as ex:
          print(ex)
    def invalidURL(self, html):
       urls = []
       soup = BeautifulSoup(html, "html.parser")
       for tag in soup.find_all():
         urls += re.findall(r'https?://[a-zA-Z.]+', str(tag.attrs.values()))

       invalid_urls = []
       for url in urls:
        if not any([url.startswith(domain) for domain in self.KNOWN_DOMAINS]):
            invalid_urls.append(url)
       return invalid_urls
    def backup_config(self):
        url_value = self.url_input.text()
        # store Hash 
        response = requests.get(url_value)
        content = response.content
        soup = BeautifulSoup(content, 'html.parser')
        for tag in soup.find_all(class_='comment'):
            tag.decompose()
        clean_content=str(soup)
        # store Hash html
        hash_object = hashlib.blake2b(clean_content.encode())
        self.previous_hash = hash_object.hexdigest()
        # store Hash Image
        
        img_tags = soup.find_all('img')
        self.img_hashes_previous = []
        for img_tag in img_tags:
          img_url = img_tag.get("src")
          if img_url != None:
            if not img_url.startswith("http"):
               img_url = f"{url_value}/{img_url}"
               img_data = requests.get(img_url).content
               img_hash = hashlib.blake2b(img_data).hexdigest()
               self.img_hashes_previous.append(img_hash)
        # store Hash audio
        audio_tags = soup.find_all('audio')
        self.audio_hashes_previous=[]
        for audio_tag in audio_tags:
            sources = audio_tag.find_all('source')
            for source in sources:
             audio_url = source.get("src")
             if audio_url!=None:
              if not audio_url.startswith("http"):
                audio_url = f"{url_value}/{audio_url}"
                audio_data = requests.get(audio_url).content
                audio_hash = hashlib.blake2b(audio_data).hexdigest()
                self.audio_hashes_previous.append(audio_hash)

        #print(self.previous_hash)
        #print(self.img_hashes_previous)
        #print(self.audio_hashes_previous)

        #Lưu lại dữ liệu
        Folder_current_path = "D:/WDMT/Web/Orginal"
        Backup_path = "D:/WDMT/Web/Backup"
        shutil.copytree(Folder_current_path, Backup_path, dirs_exist_ok=True)
        
        self.KNOWN_DOMAINS = ['https://www.google.com', 'https://www.youtube.com']

        self.update_info_textbox("Đã lưu lại giá trị Hash và nội dung trang web hiện tại") 
        self.update_info_textbox("-----------------------------------------------") 
    def start_action(self):
        url_value = self.url_input.text()
     
        response = requests.get(url_value)
        content = response.content
        soup = BeautifulSoup(content, 'html.parser')
        for tag in soup.find_all(class_='comment'):
            tag.decompose()
        clean_content=str(soup)
        
        # store Hash html
        hash_object = hashlib.blake2b(clean_content.encode())
        current_hash = hash_object.hexdigest()
        # Get Hash Image
        soup = BeautifulSoup(content, 'html.parser')
        img_tags = soup.find_all('img')
        img_hashes_current = []
        for img_tag in img_tags:
          img_url = img_tag.get("src")
          if img_url != None:
            if not img_url.startswith("http"):
               img_url = f"{url_value}/{img_url}"
               img_data = requests.get(img_url).content
               img_hash = hashlib.blake2b(img_data).hexdigest()
               img_hashes_current.append(img_hash)
          
        # Get Hash audio
        audio_tags = soup.find_all('audio')
        audio_hashes_current=[]
        for audio_tag in audio_tags:
            sources = audio_tag.find_all('source')
            for source in sources:
             audio_url = source.get("src")
             if audio_url!=None:
              if not audio_url.startswith("http"):
                audio_url = f"{url_value}/{audio_url}"
                audio_data = requests.get(audio_url).content
                audio_hash = hashlib.blake2b(audio_data).hexdigest()
                audio_hashes_current.append(audio_hash)

        

        # Thông tin tài khoản email
        sender_email = 'thinhbosua123@gmail.com'
        sender_password = 'orzh spoc efyi qglg'
        subject = 'Web change notification'
        # Thiết lập kết nối SMTP server
        smtp_server = 'smtp.gmail.com'
        context = ssl.create_default_context()
        smtp_port = 587
        receiver_email=self.email_input.text()

        # Thông tin Telegram

        bot_token = '6200192705:AAEiGy7e2hhCeF7LNwhO2gtmRil24pgIA8g'
        chat_id = '5840941523'
        
        
      
        # Check Hash HTML
        if  current_hash != self.previous_hash:
             self.update_info_textbox("//Alarm: Nội dung trang web đã thay đổi nội dung text.")
             #print('Nội dung trang web đã thay đổi')
                # Gửi email thông báo
             asyncio.run(self.send_telegram("//Alarm: Nội dung trang web đã bị thay đổi về nội dung text. Admin kiểm tra lại nhé!",bot_token,chat_id))
             body = f'//Alarm: Nội dung trang web {url_value} đã bị thay đổi về nội dung text. Admin kiểm tra lại nhé!'
             message = f'Subject: {subject}\n\n{body}'
             with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls(context=context)
                    server.login(sender_email, sender_password)
                    server.sendmail(sender_email, receiver_email, message.encode('utf-8'))
        else:
             #print('Nội dung trang web không có sự thay đổi')
             self.update_info_textbox("Nội dung trang web không có sự thay đổi về nội dung text.")
        #Check Hash IMAGE
        if img_hashes_current != self.img_hashes_previous:
             self.update_info_textbox("//Alarm: Nội dung trang web về hình ảnh đã thay đổi.")
             #print('Nội dung trang web đã thay đổi')
                # Gửi email thông báo
             asyncio.run(self.send_telegram("Nội dung trang web đã bị thay đổi về nội dung hình ảnh. Admin kiểm tra lại nhé!",bot_token,chat_id))
             body = f'//Alarm: Nội dung trang web {url_value} đã bị thay đổi hình ảnh. Admin kiểm tra lại nhé!'
             message = f'Subject: {subject}\n\n{body}'
             with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls(context=context)
                    server.login(sender_email, sender_password)
                    server.sendmail(sender_email, receiver_email, message.encode('utf-8'))
             
        else:
             #print('Nội dung trang web không có sự thay đổi về hình ảnh')
             self.update_info_textbox("Nội dung trang web không có sự thay đổi về hình ảnh.")
        
        #Check âm thanh
        if audio_hashes_current != self.audio_hashes_previous:
             self.update_info_textbox("//Alarm: Nội dung trang web về âm thanh đã thay đổi.")
             #print('Nội dung trang web đã thay đổi')
                # Gửi email thông báo
             asyncio.run(self.send_telegram("//Alarm: Nội dung trang web đã bị thay đổi về nội dung âm thanh. Admin kiểm tra lại nhé!",bot_token,chat_id))
             body = f'//Alarm: Nội dung trang web {url_value} đã bị thay đổi âm thanh. Admin kiểm tra lại nhé!'
             message = f'Subject: {subject}\n\n{body}'
             with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls(context=context)
                    server.login(sender_email, sender_password)
                    server.sendmail(sender_email, receiver_email, message.encode('utf-8'))
             
        else:
             #print('Nội dung trang web không có sự thay đổi về âm thanh')
             self.update_info_textbox("Nội dung trang web không có sự thay đổi về âm thanh.")
         
        # Check unknow link for redirect
        try:
            url_value = self.url_input.text()

            # Configure Edge WebDriver options
            webdriver_path = 'D:/WebDriver/msedgedriver.exe'  # Update with your actual path
            s = Service(webdriver_path)
            o = Options()
            o.add_argument('headless')
            o.add_experimental_option('excludeSwitches', ['enable-logging']) 
            driver = webdriver.Edge(service=s, options=o)
            driver.get(url_value)
            driver.refresh()

            if not driver.current_url.startswith(url_value):
                self.update_info_textbox(f"//Alarm: Trang web bị chuyển hướng sang {driver.current_url}")
                asyncio.run(self.send_telegram(f"//Alarm: Trang web bị chuyển hướng sang {driver.current_url}. Admin kiểm tra lại nhé!", bot_token, chat_id))
                body = f'//Alarm: Trang web bị chuyển hướng sang trang khác {driver.current_url}. Admin kiểm tra lại nhé!'
                message = f'Subject: {subject}\n\n{body}'
                with smtplib.SMTP(smtp_server, smtp_port) as server:
                    server.starttls(context=context)
                    server.login(sender_email, sender_password)
                    server.sendmail(sender_email, receiver_email, message.encode('utf-8'))
            else:
                invalid_urls = self.invalidURL(driver.page_source)
                if invalid_urls:
                    self.update_info_textbox("//Alarm: Trang web chứa các link lạ.")
                    asyncio.run(self.send_telegram("//Alarm: Trang web chứa các link lạ. Admin kiểm tra lại nhé!", bot_token, chat_id))
                    for invalid_url in invalid_urls:
                        self.update_info_textbox(invalid_url)
                        asyncio.run(self.send_telegram(invalid_url, bot_token, chat_id))
                    body = f'//Alarm: Trang web chứa các link lạ {invalid_urls}. Admin kiểm tra lại nhé!'
                    message = f'Subject: {subject}\n\n{body}'
                    with smtplib.SMTP(smtp_server, smtp_port) as server:
                        server.starttls(context=context)
                        server.login(sender_email, sender_password)
                        server.sendmail(sender_email, receiver_email, message.encode('utf-8'))
        except Exception as e:
            print(f"Exception occurred: {e}")
            self.update_info_textbox(f"Exception occurred: {e}")

        self.update_info_textbox("-----------------------------------------------")
    def rollback(self):
        Folder_current_path = "D:/WDMT/Web/Orginal"
        Backup_path = "D:/WDMT/Web/Backup"
        shutil.copytree(Backup_path, Folder_current_path, dirs_exist_ok=True)
        self.update_info_textbox("Đã rollback lại trang web như trước") 
        self.update_info_textbox("-----------------------------------------------") 
    def about(self):
        win = QtWidgets.QMessageBox(self)
        win.setWindowTitle("About")
        win.setText("WDMT Version 1.0 04.2023\n\nĐề tài môn Bảo mật thông tin\n\nThành viên:\n\n    - Đỗ Hồng Lộc\n    - Nguyễn Nhật Khuong\n    - Nguyễn Dương Huy Hoàng")
        win.exec_()

    

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    win = MyWindow()
    app.exec_()