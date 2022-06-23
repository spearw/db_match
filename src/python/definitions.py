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


import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(ROOT_DIR, '../../dat/db')
TREE_PATH = os.path.join(ROOT_DIR, '../../dat/tree')
INFO_PATH = os.path.join(ROOT_DIR, '../../dat/info')
INFO_PATH = "./cache.json"
