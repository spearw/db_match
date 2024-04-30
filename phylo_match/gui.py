'''
    Phylo-Match matches a .csv file full of data (species-level data) and
    a nexus file containing a phylogenetic tree
    Copyright (C) William Spear

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

import sys
import datetime

from argparse import ArgumentParser

from PyQt6.QtGui import QIntValidator, QCloseEvent
from PyQt6.uic.properties import QtWidgets
from diskcache import Cache
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, \
    QHBoxLayout, QGridLayout, QLabel, QLineEdit
from phylo_match.definitions.definitions import *
from phylo_match.match.match import *
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *


class LoadingWindow(QMainWindow):
    def __init__(self, parent=None):
        super(LoadingWindow, self).__init__(parent)
        self.setWindowTitle("Loading, please wait...")
        prog_bar = QProgressBar(self)
        prog_bar.setGeometry(50, 100, 250, 30)
        prog_bar.setValue(0)


class MainMenu(QMainWindow):
    # TODO: allow for setting of DB_PATH, TREE_PATH, and before run
    def __init__(self, parent=None):
        super(MainMenu, self).__init__(parent)

        # Create main_layout
        self.main_widget = QWidget()
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QGridLayout(self.main_widget)

        # Set stylesheets
        self.file_selection_stylesheet = "padding: 5px; border-radius: 0px; background-color: white; color: black; border: black 1px;"

        # Add db selection layout
        self.db_selection_layout = QGridLayout()
        self.main_layout.addLayout(self.db_selection_layout, 0, 0)

        # Add nexus selection layout
        self.nexus_selection_layout = QGridLayout()
        self.main_layout.addLayout(self.nexus_selection_layout, 0, 1)

        # Add cache selection layout
        self.cache_selection_layout = QGridLayout()
        self.main_layout.addLayout(self.cache_selection_layout, 0, 3)

        # Add file run button layout
        self.run_button_layout = QGridLayout()
        self.main_layout.addLayout(self.run_button_layout, 1, 3)

        # Add options layout
        self.options_layout = QGridLayout()
        self.main_layout.addLayout(self.options_layout, 1, 0)

        # Add progress layout
        self.progress_layout = QGridLayout()
        self.main_layout.addLayout(self.progress_layout, 2, 0, 1, 4)

        # Add progress bar and label
        self.prog_label = QLabel("")
        self.progress_layout.addWidget(self.prog_label)
        self.prog_bar = QProgressBar(self)
        self.prog_bar.hide()
        self.prog_bar.setValue(0)
        self.progress_layout.addWidget(self.prog_bar)

        # Add db selection button
        self.db_label = QLabel("Database File Selection")
        self.db_label.setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.db_label.setFixedHeight(self.db_label.font().pointSize()*2)

        self.db_path = DB_PATH
        self.db_path_label = QLabel()
        self.db_path_label.setStyleSheet(self.file_selection_stylesheet)
        self.db_path_label.setFixedHeight(self.db_path_label.font().pointSize()*2)

        self.db_file_selection = QPushButton("Change")
        self.db_file_selection.clicked.connect(self.select_db_file)

        self.db_selection_layout.addWidget(self.db_label, 0, 0, 1, 2)
        self.db_selection_layout.addWidget(self.db_path_label, 2, 0, 1, 2)
        self.db_selection_layout.addWidget(self.db_file_selection, 4, 0, 1, 1)

        # Add nexus selection button
        self.nexus_label = QLabel("Nexus File Selection")
        self.nexus_label.setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.nexus_label.setFixedHeight(self.nexus_label.font().pointSize()*2)

        self.nexus_file_selection = QPushButton("Change")
        self.nexus_file_selection.clicked.connect(self.select_nexus_file)

        self.nexus_path = TREE_PATH
        self.nexus_path_label = QLabel()
        self.nexus_path_label.setStyleSheet(self.file_selection_stylesheet)
        self.nexus_path_label.setFixedHeight(self.nexus_path_label.font().pointSize()*2)

        self.nexus_selection_layout.addWidget(self.nexus_label, 0, 0, 1, 2)
        self.nexus_selection_layout.addWidget(self.nexus_path_label, 2, 0, 1, 2)
        self.nexus_selection_layout.addWidget(self.nexus_file_selection, 4, 0, 1, 1)

        # Add cache selection button
        self.cache_label = QLabel("Cache Directory Selection")
        self.cache_label.setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.cache_label.setFixedHeight(self.cache_label.font().pointSize()*2)

        self.homedir = os.getenv("HOME")
        self.cache_path = f"{self.homedir}/phylo-match-cache"
        self.cache_path_label = QLabel(self.cache_path)
        self.cache_path_label.setStyleSheet(self.file_selection_stylesheet)
        self.cache_path_label.setFixedHeight(self.cache_path_label.font().pointSize()*2)

        self.cache_file_selection = QPushButton("Change")
        self.cache_file_selection.clicked.connect(self.select_cache_file)

        self.cache_selection_layout.addWidget(self.cache_label, 0, 0, 1, 2)
        self.cache_selection_layout.addWidget(self.cache_path_label, 2, 0, 1, 2)
        self.cache_selection_layout.addWidget(self.cache_file_selection, 4, 0, 1, 1)

        # Add lookup checkbox
        self.do_lookup = QCheckBox(checked=True)
        self.do_lookup.setText("Lookup Taxa Info")
        self.options_layout.addWidget(self.do_lookup)

        # Add lookup index selector
        self.species_index = 0
        self.lbl_integer = QLabel("Species Index (from 0)")
        self.species_index_textbox = QLineEdit()
        self.species_index_textbox.setPlaceholderText("0")
        self.species_index_textbox.setValidator(QIntValidator(1, 999, self))
        self.options_layout.addWidget(self.lbl_integer)
        self.options_layout.addWidget(self.species_index_textbox)

        # Add run button
        self.run_button_spacer = QLabel()
        self.run_button = QPushButton("Run")
        self.run_button.setEnabled(False)
        self.run_button.clicked.connect(self.start_match)
        self.run_button_layout.addWidget(self.run_button_spacer)
        self.run_button_layout.addWidget(self.run_button)
        self.nexus_file_selected = False
        self.db_file_selected = False


        self.loading_window = LoadingWindow(self)
        self.dialogs = list()

    def select_nexus_file(self):
        self.nexus_path = QFileDialog.getOpenFileName(self, 'Open file',
                                            f'{TREE_PATH}', "Tree files (*.nex)")[0]
        self.nexus_path_label.setText(os.path.basename(self.nexus_path))

        self.nexus_file_selected = True
        if self.nexus_file_selected and self.db_file_selected:
            self.run_button.setEnabled(True)

    def select_db_file(self):
        self.db_path = QFileDialog.getOpenFileName(self, 'Open file',
                                                      f'{DB_PATH}', "DB files ( *.csv)")[0]
        self.db_path_label.setText(os.path.basename(self.db_path))

        self.db_file_selected = True
        if self.nexus_file_selected and self.db_file_selected:
            self.run_button.setEnabled(True)

    def select_cache_file(self):
        self.cache_path = QFileDialog.getExistingDirectory(self, 'Open Directory',
                                                   f'{self.homedir}' "Cache files (*)")[0]
        self.cache_path_label.setText(os.path.basename(self.cache_path))

    def start_match(self):
        # Might include other functionality, such as loading bar
        self.run_match()

    def run_match(self):
        compare_window = Compare(self)

        self.prog_label.setText("Analyzing...")
        self.prog_bar.show()
        self.prog_bar.setValue(0)
        QApplication.processEvents()

        self.dialogs.append(compare_window)

        self.species_index = self.species_index_textbox.text()
        if self.species_index == '':
            self.species_index = 0
        else:
            self.species_index = int(self.species_index_textbox.text())

        dbs, tree = read_files(self.db_path, self.nexus_path, self.species_index)

        dupes = set()
        # Check for duplicate entries in dbs
        for db in dbs:
            db_dupes = set([x for x in db if db.count(x) > 1])
            dupes = dupes.union(db_dupes)

        if len(dupes) > 0:
            msg = QMessageBox()
            # msg.setIcon(QMessageBox.Critical)
            msg.setText("Warning: Duplicate Entries")
            msg.setInformativeText(f"{', '.join(dupes)} appear multiple times")
            msg.setWindowTitle("Duplicate Entries")
            msg.exec()

        taxa_list, compare_window.perfect_matches = match(dbs, tree, "_", 4)

        # If option for online lookup, do lookup
        if self.do_lookup.isChecked():
            # Cached_info may be cached remotely or locally in future versions
            # cached_info = read_wiki_file(INFO_PATH, INFO_FNAME)
            cache = Cache(self.cache_path)

            self.prog_label.setText("Checking Cache...")
            QApplication.processEvents()

            flat_taxa_list = flatten(taxa_list)
            missing_info = list(filter(lambda x: x not in cache, flat_taxa_list))

            self.prog_bar.setRange(0, len(missing_info))
            self.prog_label.setText("Downloading...")
            QApplication.processEvents()

            p = multiprocessing.Pool(multiprocessing.cpu_count())
            wiki_entries = p.map_async(get_wiki_section, missing_info)
            p.close()

            # Loading Bar
            while (True):
                if (wiki_entries.ready()): break
                self.prog_bar.setValue(len(missing_info) - wiki_entries._number_left * wiki_entries._chunksize)

                # Simple animation
                text = self.prog_label.text
                if text == "Downloading...":
                    self.prog_label.setText("Downloading.")
                elif text == "Downloading.":
                    self.prog_label.setText("Downloading..")
                else:
                    self.prog_label.setText("Downloading...")

                QApplication.processEvents()
                time.sleep(0.5)


            self.prog_label.setText("Caching...")
            QApplication.processEvents()

            # Cache items
            for key in missing_info:
                value = get_wiki_section(key)
                cache.set(key, value)

        self.prog_label.setText("Done!")
        QApplication.processEvents()

        compare_window.__init__(self)
        compare_window.setParent(self)
        compare_window.move(self.pos())
        compare_window.species_index = self.species_index
        compare_window.set_db_path(self.db_path)
        compare_window.set_do_lookup(self.do_lookup.isChecked())

        compare_window.set_cache(cache)
        compare_window.compare_mismatch(iter(taxa_list))

        self.hide()
        self.prog_bar.hide()
        self.prog_bar.setValue(0)
        self.prog_label.setText("")


# dialog.close()

#
# start_time = time.time()
# taxa_list = db_match(DB_PATH, TREE_PATH, "_", 4)
#
# compare = Compare(self)
# compare.compare_mismatch(self, iter(taxa_list))


class Compare(QMainWindow):
    def __init__(self, parent=None):
        super(Compare, self).__init__(parent)
        self.setWindowTitle("compare")

        self.db_path = ""
        self.do_lookup = False
        self.cache = None

        # Create main_layout
        self.main_widget = QWidget()
        self.main_widget.setFocus()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QGridLayout(self.main_widget)

        # Create sub-layouts for main_layout and order them
        self.info_layout_style = QWidget()
        self.info_layout_style.setStyleSheet("border-width: 1px; border-style: solid; border-color: black white black black;")
        self.main_layout.addWidget(self.info_layout_style, 0, 0, 3, 1)

        self.info_layout = QVBoxLayout()
        self.main_layout.addLayout(self.info_layout, 0, 0,)

        self.taxa_layout = QVBoxLayout()
        self.taxa_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addLayout(self.taxa_layout, 1, 0)

        self.count_layout = QHBoxLayout()
        self.main_layout.addLayout(self.count_layout, 0, 1)

        self.suggestions_sub_layout = QHBoxLayout()
        self.suggestions_scroll_area = QScrollArea()

        self.suggestions_scrolling_layout = QHBoxLayout()
        self.main_layout.addLayout(self.suggestions_scrolling_layout, 1, 1)

        self.manual_entry_layout = QVBoxLayout()
        self.main_layout.addLayout(self.manual_entry_layout, 2, 1, 1, 2)

        # Add contents to info_layout
        self.taxa_label = QLabel("animals_animals")
        self.taxa_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.taxa_label.setStyleSheet("padding: 30px; border-radius: 0px; background-color: lightgray; color: black;")
        self.info_layout.addWidget(self.taxa_label, 1)

        # Add contents to taxa_layout
        self.removed_suggestions_scroll_area = QScrollArea()
        self.removed_suggestions_scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.removed_suggestions_scroll_area.setContentsMargins(5, 5, 5, 5)
        self.removed_suggestions_count = QLabel()
        self.removed_suggestions_count.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.taxa_layout.addWidget(self.removed_suggestions_count, 1)

        # Add contents to count_layout
        self.options_count_label = QHBoxLayout()
        self.options_count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.similar_entries_count = QPushButton()
        self.options_count_label.addWidget(self.similar_entries_count)
        self.same_species_count = QPushButton()
        self.options_count_label.addWidget(self.same_species_count)
        self.same_genus_count = QPushButton()
        self.options_count_label.addWidget(self.same_genus_count)
        self.count_layout.addLayout(self.options_count_label, 1)

        # Create label for main taxa info, to be attached as needed
        self.taxa_info = QLabel("So many options!")
        self.taxa_info.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add contents to manual_entry_layout
        self.entry_label = QLabel("Manual Entry:")
        self.manual_entry_layout.addWidget(self.entry_label)
        self.line_edit = QLineEdit()
        self.manual_entry_layout.addWidget(self.line_edit)
        self.manual_btn = QPushButton("Enter", self)
        self.manual_btn.setMaximumWidth(150)
        self.manual_entry_layout.addWidget(self.manual_btn)
        self.leave_btn = QPushButton("Leave as is", self)
        self.leave_btn.setMaximumWidth(150)
        self.manual_entry_layout.addWidget(self.leave_btn)
        self.manual_entry_layout.setContentsMargins(10, 10, 10, 10)

        # Init global variables
        self.removed_suggestions = []
        self.taxa_list = []
        self.species_index = 0
        self.force_quit = False

    def closeEvent(self, event, *args, **kwargs):

        if self.force_quit:
            event.accept()
        else:
            ## TODO: Add pop up box with option to save progress
            close = QMessageBox.question(self,
                                         "QUIT",
                                         "Are you sure want to quit? Progress will not be saved",
                                         QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if close == QMessageBox.StandardButton.Yes:
                # Open main menu
                self.parent().show()
                self.parent().move(self.pos())
                event.accept()
            else:
                event.ignore()

    def set_db_path(self, db_path):
        self.db_path = db_path

    def set_do_lookup(self, do_lookup):
        self.do_lookup = do_lookup

    def set_cache(self, cache):
        self.cache = cache

    def compare_mismatch(self, taxa_iter):

        next_taxa = next(taxa_iter, None)
        if next_taxa:
            # Type Str indicates to move on
            if type(next_taxa) == str:
                self.taxa_list.append(next_taxa)
                self.compare_mismatch(taxa_iter)
            else:
                db_taxa = next_taxa[0]

                next_taxa = self.remove_chosen_entries(next_taxa)

                loose_suggestions = next_taxa[4]  # bool indicating whether suggestion has loosened params

                # If suggestions are loose, default to showing them last
                if loose_suggestions:
                    if len(next_taxa[2]) > 0:
                        i = 2
                    elif len(next_taxa[3]) > 0:
                        i = 3
                    else:
                        i = 1
                else:
                    i = 1

                self.show_suggestions(next_taxa, taxa_iter, i)

                self.taxa_label.setText(db_taxa)
                self.show()
        else:
            # End of file, record results
            filepath = write_file(self.taxa_list, self.db_path, self.species_index)

            # Success message
            QMessageBox.information(self,
                                     "Complete!",
                                     f"Selections saved as {filepath}",)

            # Open main menu
            self.parent().show()
            self.parent().move(self.pos())

            # Close window
            self.force_quit = True
            self.close()

    def make_confirm_function(self, suggestion, taxa_iter, compare_window):
        def confirm_suggestion():
            self.taxa_list.append(suggestion)

            self.line_edit.clear()
            self.removed_suggestions.clear()

            self.compare_mismatch(taxa_iter)

        return confirm_suggestion

    def remove_chosen_entries(self, taxa):

        taxa_name = taxa[0]

        for i, taxa_suggestions in enumerate(taxa[0:-1]):
            if type(taxa_suggestions) != str:
                for suggestion in taxa_suggestions:
                    # Remove suggestions that have already been chosen
                    # TODO: do this for entire suggestions list at beginning of new taxa to avoid changing once clicking
                    if suggestion in self.taxa_list or suggestion in self.perfect_matches:
                        self.removed_suggestions.append(suggestion)
                        continue
                taxa[i] = [x for x in taxa_suggestions if x not in self.removed_suggestions]
        return taxa

    def confirm_text(self, suggestion, taxa_iter, compare_window):
        # TODO: close window more intelligently
        self.taxa_list.append(suggestion)

        self.line_edit.clear()
        self.removed_suggestions.clear()

        self.compare_mismatch(taxa_iter)

    def create_wiki_scroll_area(self, taxa):
        # Create text box from wiki
        label = QLabel()
        label.setScaledContents(True)
        try:
            label.setText(get_wiki_section(taxa, cache=self.cache))
        except:
            label.setText("No information found")
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.show()

        # Create scroll area for text box
        scroll = QScrollArea()
        scroll.setWidget(label)
        scroll.setWidgetResizable(True)
        scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setFixedHeight(200)
        scroll.setMaximumWidth(200)

        return scroll

    def create_taxa_layout(self, taxa, taxa_iter):
        # TODO: reimplement count_layout?

        # url_image = get_wiki_image(taxa)
        # Get wiki information, and image if it's available
        # try:
        #     if url_image != 0:
        #         image = QImage()
        #         image.loadFromData(requests.get(url_image).content)
        #
        #         label.setPixmap(QPixmap(image))
        # except:
        #     label.setText("Cannot find " + taxa)

        # Create base main_layout for taxa selection
        taxa_layout = QVBoxLayout()
        taxa_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Create taxa selection button
        btn = QPushButton(taxa, self)
        btn.setStyleSheet("padding: 20px; border-radius: 15px; background-color: gray;")
        # btn.adjustSize()
        f = self.make_confirm_function(taxa, taxa_iter, self)
        btn.clicked.connect(f)
        taxa_layout.addWidget(btn)

        if self.do_lookup:
            scroll = self.create_wiki_scroll_area(taxa)
            taxa_layout.addWidget(scroll)

        taxa_layout.setContentsMargins(10, 5, 10, 5)

        return taxa_layout

    def create_removed_suggestions_scroll_area(self, removed_suggestions_text):
        # Create text box from wiki
        label = QLabel()
        label.setScaledContents(True)
        try:
            label.setText(removed_suggestions_text)
        except:
            label.setText("No entries")
        label.setWordWrap(True)
        label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        label.show()

        # Create scroll area for text box
        scroll = QScrollArea()
        scroll.setWidget(label)
        scroll.setWidgetResizable(True)
        scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setFixedHeight(200)
        scroll.setMaximumWidth(200)

        return scroll

    def create_suggestions_scroll_area(self):
        scroll = QScrollArea()
        widget = QWidget()
        widget.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(self.suggestions_sub_layout)
        scroll.setWidget(widget)
        scroll.setWidgetResizable(True)
        scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        scroll.setFixedHeight(400)
        scroll.setMaximumWidth(800)

        return scroll

    def show_suggestions(self, next_taxa, taxa_iter, match_type):

        # Clear old buttons + count_layout
        for j in reversed(range(self.suggestions_sub_layout.count())):
            layout = self.suggestions_sub_layout.itemAt(j).layout()
            self.suggestions_sub_layout.removeItem(layout)
            for k in reversed(range(layout.count())):
                layout.itemAt(k).widget().setParent(None)

        self.suggestions_scroll_area.setParent(None)
        self.taxa_info.setParent(None)


        self.removed_suggestions_scroll_area.setParent(None)
        self.removed_suggestions_count.setText(f"Removed Suggestions: {len(self.removed_suggestions)}")
        if self.removed_suggestions:
            self.removed_suggestions_scroll_area = self.create_removed_suggestions_scroll_area(", \n".join(self.removed_suggestions))
            self.taxa_layout.addWidget(self.removed_suggestions_scroll_area, 1)

        num_suggestions = [len(next_taxa[1]), len(next_taxa[2]), len(next_taxa[3])]

        category_suggestions = next_taxa[match_type]
        while not category_suggestions:
            match_type += 1
            if match_type > 3:
                break
            category_suggestions = next_taxa[match_type]

        # reset and load taxa, if possible
        self.taxa_info.setParent(None)

        if self.do_lookup:
            self.taxa_info = self.create_wiki_scroll_area(next_taxa[0])
            h_layout = QHBoxLayout()
            h_layout.addWidget(self.taxa_info)
            self.taxa_layout.insertLayout(0, h_layout)

        for suggestion in category_suggestions:

            # Add info and image widget to page
            suggestion_layout = self.create_taxa_layout(suggestion, taxa_iter)
            self.suggestions_sub_layout.addLayout(suggestion_layout)

        self.suggestions_scroll_area = self.create_suggestions_scroll_area()
        self.suggestions_scrolling_layout.addWidget(self.suggestions_scroll_area)


        # TODO: get this logic outside of the category_suggestions, so it's not doing it every time
        # Set button text
        loose_matching = next_taxa[4]
        if loose_matching:
            self.similar_entries_count.setText(f"Similar Entries (Lenient): {num_suggestions[0]}")
        else:
            self.similar_entries_count.setText(f"Similar Entries: {num_suggestions[0]}")
        self.same_species_count.setText(f"Same Species: {num_suggestions[1]}")
        self.same_genus_count.setText(f"Same Genus: {num_suggestions[2]}")

        # Unlink buttons, if needed
        try:
            self.similar_entries_count.clicked.disconnect()
        except Exception:
            pass
        try:
            self.same_species_count.clicked.disconnect()
        except Exception:
            pass
        try:
            self.same_genus_count.clicked.disconnect()
        except Exception:
            pass

        # Link buttons, if category_suggestions exist for those categories
        ## TODO: Refactor to use strings instead of ints for clearer indications of what these numbers mean
        if num_suggestions[0] > 0: self.similar_entries_count.clicked.connect(
            lambda: self.show_suggestions(next_taxa, taxa_iter, 1))
        if num_suggestions[1] > 0: self.same_species_count.clicked.connect(
            lambda: self.show_suggestions(next_taxa, taxa_iter, 2))
        if num_suggestions[2] > 0: self.same_genus_count.clicked.connect(
            lambda: self.show_suggestions(next_taxa, taxa_iter, 3))

        if match_type == 1:
            self.setWindowTitle("Similar Entries")
        elif match_type == 2:
            self.setWindowTitle("Same Species")
        elif match_type == 3:
            self.setWindowTitle("Same Genus")
        else:
            self.setWindowTitle("No Suggestions")

        # Disconnect if already connected
        try:
            self.manual_btn.clicked.disconnect()
        except Exception:
            pass
        try:
            self.leave_btn.clicked.disconnect()
        except Exception:
            pass

        # Chooses the text entry box
        self.manual_btn.setEnabled(False)
        self.line_edit.textChanged.connect(self.disableManualButton)
        self.manual_btn.clicked.connect(lambda: self.confirm_text(self.line_edit.text(), taxa_iter, self))
        # Chooses the text entry box
        self.leave_btn.clicked.connect(lambda: self.confirm_text("", taxa_iter, self))

    def disableManualButton(self):
        if len(self.line_edit.text()) > 0:
            self.manual_btn.setEnabled(True)
        else:
            self.manual_btn.setEnabled(False)

def main():
    app = QApplication(sys.argv)
    main = MainMenu()
    main.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument(
        "--show-c",
        action="store_true",
        help="Show copyright",
    )
    parser.add_argument(
        "--show-w",
        action="store_true",
        help="Show warranty",
    )
    args = parser.parse_args()
    print(f"""
    Phylo-Match  Copyright (C) {datetime.date.today().year}  William Spear
    This program comes with ABSOLUTELY NO WARRANTY; for details type `phylo-match --show-w'.
    This is free software, and you are welcome to redistribute it
    under certain conditions; type `phylo-match --show-c' for details.
    """)

    if args.show_w:
        print("""
        THERE IS NO WARRANTY FOR THE PROGRAM, TO THE EXTENT PERMITTED BY
        APPLICABLE LAW.  EXCEPT WHEN OTHERWISE STATED IN WRITING THE COPYRIGHT
        HOLDERS AND/OR OTHER PARTIES PROVIDE THE PROGRAM "AS IS" WITHOUT WARRANTY
        OF ANY KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT NOT LIMITED TO,
        THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
        PURPOSE.  THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM
        IS WITH YOU.  SHOULD THE PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF
        ALL NECESSARY SERVICING, REPAIR OR CORRECTION.
        """)
    elif args.show_c:
        print("""
        You may convey verbatim copies of the Program's source code as you
        receive it, in any medium, provided that you conspicuously and
        appropriately publish on each copy an appropriate copyright notice;
        keep intact all notices stating that this License and any
        non-permissive terms added in accord with section 7 apply to the code;
        keep intact all notices of the absence of any warranty; and give all
        recipients a copy of this License along with the Program.

          You may charge any price or no price for each copy that you convey,
        and you may offer support or warranty protection for a fee.
        """)
    else:
        main()
