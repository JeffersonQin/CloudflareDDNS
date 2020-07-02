import json
import requests
import time
import sys
import os
import PyQt5.sip
#从PyQt库导入QtWidget通用窗口类,基本的窗口集在PyQt5.QtWidgets模块里.
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QWidget,QSystemTrayIcon,QAction,QMenu,qApp,QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QFormLayout, QLabel, QLineEdit, QPushButton, QHBoxLayout, QTextEdit, QCheckBox
import threading
from appdata import AppDataPaths

my_ip = ""

X_AUTH_KEY = ""
ZONE_ID = ""
EMAIL = ""
DNS_RECORD_NAME = ""
WEBSITE_URL = ""
AUTO_START = False

headers = {
        "X-Auth-Email": EMAIL,
        "X-Auth-Key": X_AUTH_KEY,
        "Content-Type": "application/json"
}

started_flag = False

paths = AppDataPaths('CloudFlareDDNS')

app_data_dir = paths.app_data_path

if os.path.exists(app_data_dir):
    if os.path.isfile(app_data_dir + "\\config.ini"):
        print(app_data_dir + "\\config.ini")
        with open(app_data_dir + "\\config.ini", 'r') as f:
            file_data = json.load(f)
            X_AUTH_KEY = file_data["X_AUTH_KEY"]
            ZONE_ID = file_data["ZONE_ID"]
            EMAIL = file_data["EMAIL"]
            DNS_RECORD_NAME = file_data["DNS_RECORD_NAME"]
            WEBSITE_URL = file_data["WEBSITE_URL"]
            AUTO_START = bool(file_data["AUTO_START"])
else:
    os.makedirs(app_data_dir)




class update_Thread(QtCore.QThread):

    update_text = QtCore.pyqtSignal(str)
    
    def run(self):
        global X_AUTH_KEY
        global ZONE_ID
        global EMAIL
        global headers
        global started_flag
        global tp
        global DNS_RECORD_NAME
        global WEBSITE_URL
        global AUTO_START
        if started_flag == False:
            X_AUTH_KEY = le1.text()
            ZONE_ID = le2.text()
            EMAIL = le3.text()
            DNS_RECORD_NAME = le4.text()
            WEBSITE_URL = le5.text()

            json_data = {"X_AUTH_KEY": X_AUTH_KEY, "ZONE_ID": ZONE_ID, "EMAIL": EMAIL, "DNS_RECORD_NAME": DNS_RECORD_NAME, "WEBSITE_URL": WEBSITE_URL, "AUTO_START": AUTO_START}
            with open(app_data_dir + "\\config.ini", 'w') as f:
                json.dump(json_data, f)
            
            headers = {
                    "X-Auth-Email": EMAIL,
                    "X-Auth-Key": X_AUTH_KEY,
                    "Content-Type": "application/json"
            }
            started_flag = True
        else:
            tp.showMessage("Error", "DDNS已开启", icon=3)
            return
        global my_ip
        global w
        global text_panel
        tp.showMessage("CloudFlareDDNS", "服务成功启动", icon = 0)

        error_flag = False
        while True:
            try:
                new_ip = requests.get(url='http://ip.42.pl/raw').text
                self.update_text.emit(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + " " + new_ip))
            except:
                tp.showMessage("Error", "IP Update Error", icon=3)
                tp.messageClicked.connect(lambda: w.show())
                self.update_text.emit(str(time.strftime("IP UPDATE ERROR")))
                error_flag = False
                continue


            if new_ip != my_ip or error_flag:
                my_ip = new_ip
                try:
                    response = requests.get(url="https://api.cloudflare.com/client/v4/zones/" + ZONE_ID + "/dns_records", headers=headers)
                    res = json.loads(response.text)
                    result_arr = res["result"]
                    site_id = ""
                    for result in result_arr:
                        print(result)
                        if result["type"] == 'A':
                            if str(result["name"]) == WEBSITE_URL:
                                site_id = result["id"]
                                break
                    response = requests.put(url="https://api.cloudflare.com/client/v4/zones/" + ZONE_ID + "/dns_records/" + str(site_id), 
                                            headers=headers, 
                                            data='{"type":"A","name":"' + DNS_RECORD_NAME + '","content":"' + my_ip + '","ttl":1,"proxied":false}')
                    res = json.loads(response.text)
                    if res["success"]:
                        self.update_text.emit("UPLOAD SUCCESS")
                        error_flag = False
                    else:
                        self.update_text.emit("UPLOAD FAILED")
                        tp.showMessage("Error", "Upload Failed", icon=3)
                        tp.messageClicked.connect(lambda: w.show())
                        error_flag = True
                except:
                    self.update_text.emit("UNKNOWN EXCEPTION")
                    tp.showMessage("Error", "Unknown Exception", icon=3)
                    tp.messageClicked.connect(lambda: w.show())
                    error_flag = True
            time.sleep(60)

        tp.showMessage("CloudFlareDDNS", "服务成功终止", icon = 0)
        started_flag = False





if __name__ == '__main__':

    global tp
    thread_update_text_qt = None

    last_update_time = 'None'
    last_update_ip = 'None'
    last_check_time = 'None'

    def resource_path(relative_path):
        """ Get absolute path to resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)


    

    # pyqt窗口必须在QApplication方法中使用 
    # 每一个PyQt5应用都必须创建一个应用对象.sys.argv参数是来自命令行的参数列表.Python脚本可以从shell里运行.这是我们如何控制我们的脚本运行的一种方法.
    app = QApplication(sys.argv)
    # 关闭所有窗口,也不关闭应用程序
    QApplication.setQuitOnLastWindowClosed(False)
    
    from PyQt5 import QtWidgets
 
    # QWidget窗口是PyQt5中所有用户界口对象的基本类.我们使用了QWidget默认的构造器.默认的构造器没有父类.一个没有父类的窗口被称为一个window.
    w = QWidget()
    # resize()方法调整了窗口的大小.被调整为250像素宽和250像素高.
    w.resize(500,500)
    # move()方法移动了窗口到屏幕坐标x=300, y=300的位置.
    w.move(300,300)
    # 在这里我们设置了窗口的标题.标题会被显示在标题栏上.
    w.setWindowTitle('Cloudflare DDNS by H.Q. _ v0.1(beta)')
    # show()方法将窗口显示在屏幕上.一个窗口是先在内存中被创建,然后显示在屏幕上的.
    w.show()
 
    # 在系统托盘处显示图标
    tp = QSystemTrayIcon(w)
    tp.setIcon(QIcon('dns.png'))
    # 设置系统托盘图标的菜单
    a1 = QAction('&显示(Show)',triggered = w.show)
    
    form = QFormLayout()

    lb1 = QLabel('X_AUTH_KEY')
    le1 = QLineEdit(X_AUTH_KEY)
    le1.setEchoMode(QLineEdit.Password)
    lb2 = QLabel('ZONE_ID')
    le2 = QLineEdit(ZONE_ID)
    le2.setEchoMode(QLineEdit.Password)
    lb3 = QLabel('Email')
    le3 = QLineEdit(EMAIL)
    lb4 = QLabel('DNS_RECORD_NAME')
    le4 = QLineEdit(DNS_RECORD_NAME)
    lb5 = QLabel('WEBSITE_URL')
    le5 = QLineEdit(WEBSITE_URL)

    text_panel = QTextEdit()

    thread_update_text_qt = update_Thread(w)
    thread_update_text_qt.update_text.connect(text_panel.append)
    
    def stop_ddns():
        global thread_update_text_qt
        global started_flag
        thread_update_text_qt.terminate()
        thread_update_text_qt.quit()
        started_flag = False
        tp.showMessage("CloudFlareDDNS", "服务成功终止", icon = 0)

    def start_ddns():
        global thread_update_text_qt, text_panel
        thread_update_text_qt = update_Thread(w)
        thread_update_text_qt.update_text.connect(text_panel.append)
        thread_update_text_qt.start()

    hbox = QHBoxLayout()
    button_start = QPushButton("Start DDNS")
    button_stop = QPushButton("Stop DDNS")

    button_start.clicked.connect(start_ddns)
    button_stop.clicked.connect(stop_ddns)

    hbox.addWidget(button_start)
    hbox.addWidget(button_stop)


    autoStart_checkbox = QCheckBox("Auto Start DDNS when program starts")
    
    if AUTO_START:
        autoStart_checkbox.setChecked(True)
        start_ddns()

    def auto_started_changed():
        print(autoStart_checkbox.isChecked())
        AUTO_START = autoStart_checkbox.isChecked()
        json_data = {"X_AUTH_KEY": X_AUTH_KEY, "ZONE_ID": ZONE_ID, "EMAIL": EMAIL, "DNS_RECORD_NAME": DNS_RECORD_NAME, "WEBSITE_URL": WEBSITE_URL, "AUTO_START": AUTO_START}
        with open(app_data_dir + "\\config.ini", 'w') as f:
            json.dump(json_data, f)

    autoStart_checkbox.stateChanged.connect(auto_started_changed)


    form.addRow(lb1, le1)
    form.addRow(lb2, le2)
    form.addRow(lb3, le3)
    form.addRow(lb4, le4)
    form.addRow(lb5, le5)
    form.addRow(hbox)
    form.addRow(autoStart_checkbox)
    form.addRow(text_panel)

    w.setLayout(form)

    def quitApp():
        w.show() # w.hide() #隐藏
        re = QMessageBox.question(w, "提示", "退出系统", QMessageBox.Yes |   
            QMessageBox.No, QMessageBox.No)
        if re == QMessageBox.Yes:
            # 关闭窗体程序
            QCoreApplication.instance().quit()
            # 在应用程序全部关闭后，TrayIcon其实还不会自动消失，
            # 直到你的鼠标移动到上面去后，才会消失，
            # 这是个问题，（如同你terminate一些带TrayIcon的应用程序时出现的状况），
            # 这种问题的解决我是通过在程序退出前将其setVisible(False)来完成的。 
            tp.setVisible(False)
    a2 = QAction('&退出(Exit)',triggered = quitApp) # 直接退出可以用qApp.quit

    tpMenu = QMenu()
    tpMenu.addAction(a1)
    tpMenu.addAction(a2)
    tp.setContextMenu(tpMenu)
    # 不调用show不会显示系统托盘
    tp.show()
   
    # 信息提示
    # 参数1：标题
    # 参数2：内容
    # 参数3：图标（0没有图标 1信息图标 2警告图标 3错误图标），0还是有一个小图标
    def message():
        w.show()
    tp.messageClicked.connect(message)
    def act(reason):
        # 鼠标点击icon传递的信号会带有一个整形的值，1是表示单击右键，2是双击，3是单击左键，4是用鼠标中键点击
        if reason == 2 or reason == 3:
            w.show()
        # print("系统托盘的图标被点击了")
    tp.activated.connect(act)
    
    # sys为了调用sys.exit(0)退出程序
    # 最后,我们进入应用的主循环.事件处理从这里开始.主循环从窗口系统接收事件,分派它们到应用窗口.如果我们调用了exit()方法或者主窗口被销毁,则主循环结束.sys.exit()方法确保一个完整的退出.环境变量会被通知应用是如何结束的.
    # exec_()方法是有一个下划线的.这是因为exec在Python中是关键字.因此,用exec_()代替.
    sys.exit(app.exec_())


