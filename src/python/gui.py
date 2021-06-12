import sys
import time
import requests
from threading import Thread

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox, QProgressDialog, QMainWindow, QVBoxLayout, \
    QHBoxLayout, QGridLayout, QLabel, QSizePolicy, QLineEdit
from PyQt5.QtGui import QImage, QPixmap
from definitions import DB_PATH
from definitions import TREE_PATH
from src.python.match import match, write_file, get_wiki_image


class LoadingWindow(QMainWindow):
    def __init__(self, parent=None):
        super(LoadingWindow, self).__init__(parent)
        self.setWindowTitle("Loading, please wait...")

class MainMenu(QMainWindow):
    def __init__(self, parent=None):
        super(MainMenu, self).__init__(parent)
        self.pushButton = QPushButton("Run")

        self.setCentralWidget(self.pushButton)

        self.pushButton.clicked.connect(self.start_match)

        self.loading_window = LoadingWindow(self)

        self.dialogs = list()

    def start_match(self):
        # Might include other functionality, such as loading bar
        self.run_match()

    def run_match(self):

        compare_window = Compare(self)
        self.dialogs.append(compare_window)

        taxa_list = match(DB_PATH, TREE_PATH, "_", 4)
        compare_window.__init__(self)

        compare_window.compare_mismatch(iter(taxa_list), compare_window)



# dialog.close()

        # print("Starting Match...")
        #
        # start_time = time.time()
        # taxa_list = db_match(DB_PATH, TREE_PATH, "_", 4)
        # print("--- %s seconds ---" % (time.time() - start_time))
        #
        # compare = Compare(self)
        # compare.compare_mismatch(self, iter(taxa_list))


class Compare(QMainWindow):
    def __init__(self, parent=None):
        super(Compare, self).__init__(parent)
        self.setWindowTitle("compare")

        self.main_widget = QWidget()
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
        self.layout = QGridLayout(self.main_widget)

        self.info_layout = QVBoxLayout()
        self.layout.addLayout(self.info_layout, 0, 1)

        self.suggestions_layout = QHBoxLayout()
        self.layout.addLayout(self.suggestions_layout, 1, 1)

        self.images = QHBoxLayout()
        self.layout.addLayout(self.images, 2, 1)

        self.buttons = QHBoxLayout()
        self.layout.addLayout(self.buttons, 3, 1)

        self.suggestion_label = QLabel("Suggestion!")
        self.suggestion_label.setAlignment(Qt.AlignCenter)
        # self.suggestion_label.setStyleSheet(
        #     "border-style: solid; border-width: 1px; border-color: black;"
        # )
        self.info_layout.addWidget(self.suggestion_label, 1)

        self.continue_btn = QPushButton("None of these", self)
        self.buttons.addWidget(self.continue_btn, 1)

        self.line_edit = QLineEdit()
        self.buttons.addWidget(self.line_edit, 1)

        self.skip_btn = QPushButton("Enter", self)
        self.buttons.addWidget(self.skip_btn, 1)

        self.taxa_list = []


    def compare_mismatch(self, taxa_iter, compare_window):

        #TODO: when taxa_iter is done (file is complete) - need to run write_file

        next_taxa = next(taxa_iter)
        print(next_taxa)
        if type(next_taxa) == str:
            self.taxa_list.append(next_taxa)
            self.compare_mismatch(taxa_iter, compare_window)
        else:

            db_taxa = next_taxa[0]

            i = 1
            self.show_suggestions(next_taxa, taxa_iter, i)

            compare_window.setWindowTitle(db_taxa)
            compare_window.setGeometry(100, 100, 600, 400)
            compare_window.show()

    def confirm_suggestion(self, suggestion, taxa_iter, compare_window):
        print("You chose:", suggestion)
        self.taxa_list.append(suggestion)

        self.line_edit.clear()

        self.compare_mismatch(taxa_iter, compare_window)

    def show_suggestions(self, next_taxa, taxa_iter, i):

        # Clear old buttons + images
        for j in reversed(range(self.suggestions_layout.count())):
            self.suggestions_layout.itemAt(j).widget().setParent(None)
        for k in reversed(range(self.images.count())):
            self.images.itemAt(k).widget().setParent(None)

        print(next_taxa)

        if i <= 3:
            suggestions = next_taxa[i]
            while not suggestions:
                i += 1
                if i > 3:
                    break
                suggestions = next_taxa[i]

            if i <= 3:
                for suggestion in suggestions:

                    #TODO: add images from wiki
                    url_image = get_wiki_image(suggestion)
                    image = QImage()
                    image.loadFromData(requests.get(url_image).content)

                    image_label = QLabel()
                    image_label.setScaledContents(True)
                    image_label.setPixmap(QPixmap(image))
                    image_label.setMaximumSize(200, 200)
                    image_label.show()
                    self.images.addWidget(image_label)

                    print(suggestion)
                    self.btn = QPushButton(suggestion, self)
                    self.btn.adjustSize()
                    self.btn.clicked.connect(lambda: self.confirm_suggestion(suggestion, taxa_iter, self))
                    self.suggestions_layout.addWidget(self.btn)

        if i == 1:
            self.suggestion_label.setText("Similar Entries")
        elif i == 2:
            self.suggestion_label.setText("Same Species")
        elif i == 3:
            self.suggestion_label.setText("Same Genus")
        else:
            self.suggestion_label.setText("No More Suggestions. Type manually and click enter, or leave blank to keep old name.")

        # Disconnect if already connected
        try: self.continue_btn.clicked.disconnect()
        except Exception: pass

        if i <= 3:
            self.continue_btn.setText("None of these")
            self.continue_btn.clicked.connect(lambda: self.show_suggestions(next_taxa, taxa_iter, i+1))
        else:
            self.continue_btn.setText("Back")
            self.continue_btn.clicked.connect(lambda: self.show_suggestions(next_taxa, taxa_iter, 1))

        # Disconnect if already connected
        try: self.skip_btn.clicked.disconnect()
        except Exception: pass

        # Chooses the original spelling, unmodified
        self.skip_btn.clicked.connect(lambda: self.confirm_suggestion(self.line_edit.text(), taxa_iter, self))

def main():
    app = QApplication(sys.argv)
    main = MainMenu()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()



