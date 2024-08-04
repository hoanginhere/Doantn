import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from qt import Ui_MainWindow

class Mainwindow:
    def __init__(self):
        self.main_win = QMainWindow()
        self.uic = Ui_MainWindow()
        self.uic.setupUi(self.main_win)
      #khai báo nút hiện page
        self.uic.button1.clicked.connect(self.showpage1)
        self.uic.button2.clicked.connect(self.showpage2)
        self.uic.button3.clicked.connect(self.showpage3)
      #khai báo nút nhấn show
        self.uic.Button_show.clicked.connect(self.showtext)
    
    def showpage1(self):
        self.uic.stackedWidget.setCurrentWidget(self.uic.page_1)
    def showpage2(self):
        self.uic.stackedWidget.setCurrentWidget(self.uic.page_2)
    def showpage3(self):
        self.uic.stackedWidget.setCurrentWidget(self.uic.page_3)
    def showtext(self):
        self.uic.textEdit.setText("hello cưng")
        


    def show(self):
        self.main_win.show()
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = Mainwindow()
    main_win.show()
    sys.exit(app.exec())