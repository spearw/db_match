from argparse import ArgumentParser

import os

from definitions import DB_PATH
from definitions import TREE_PATH
from definitions import OUTPUT_PATH
from src.python.match import match

import time

from PyQt5.QtWidgets import QApplication, QLabel

if __name__ == "__main__":
    parser = ArgumentParser()

    parser.add_argument(
        "-d",
        "--db-path",
        default=DB_PATH,
        help="path to db",
    )
    parser.add_argument(
        "-t",
        "--tree-path",
        default=TREE_PATH,
        help="path to tree",
    )
    parser.add_argument(
        "-o",
        "--output-directory",
        default=OUTPUT_PATH,
        help="the directory containing all output files",
    )
    parser.add_argument(
        "-ts",
        "--tree-separator",
        default="_",
        help="The genus species separator for the tree input",
    )
    parser.add_argument(
        "-ds",
        "--db-separator",
        default="_",
        help="The genus species separator for the db input",
    )
    parser.add_argument(
        "-l",
        "--levenshtein-distance",
        default="4",
        help="levenshtein distance amount",
    )

    options = parser.parse_args()
    if not os.path.exists(options.output_directory):
        os.mkdir(options.output_directory)

    app = QApplication([])
    app.setStyle('Fusion')

    start_time = time.time()
    taxa_list = match(options.db_path, options.tree_path, options.db_separator, options.tree_separator, options.levenshtein_distance)
    print("--- %s seconds ---" % (time.time() - start_time))

    label = QLabel(taxa_list[0][0])
    label.show()
    app.exec()

