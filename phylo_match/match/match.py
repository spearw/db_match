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
import re
import wikipedia
import requests
import json
from pathlib import Path
import time
import multiprocessing
from Levenshtein import distance as levenshtein_distance
from functools import lru_cache


def match(dbs, tree, db_separator="_", levenshtein_num=4):

    output = []
    perfect_matches = []
    difference_threshold = int(levenshtein_num)
    for db in dbs:
        for db_name in db:
            suggestions = []
            loose_suggestions = []
            genus_match = []
            species_match = []
            genus_name = db_name.split(db_separator, 1)[0]
            try:
                species_name = db_name.split(db_separator, 1)[1]
            except:
                species_name = ""
                print(f"WARNING: entry [{db_name}] possibly malformed. Check database.")

            found_match = False
            for tree_name in tree:

                loose_suggestion = False

                tree_genus_name = tree_name.split(db_separator, 1)[0]
                try:
                    tree_species_name = tree_name.split(db_separator, 1)[1]
                except:
                    tree_species_name = ""
                    print(f"WARNING: tree entry [{tree_name}] possibly malformed. Check tree.")

                if db_name == tree_name:
                    found_match = True
                    break
                # Match by similarity
                elif levenshtein_distance(db_name, tree_name) < difference_threshold:
                    suggestions.append(tree_name)
                # Match by genus
                elif genus_name == tree_genus_name:
                    genus_match.append(tree_name)
                # Match by similarity (genus only)
                elif levenshtein_distance(genus_name, tree_genus_name) < (difference_threshold - 1):
                    loose_suggestions.append(tree_name)
                # Match by species
                elif species_name == tree_species_name:
                    species_match.append(tree_name)
                # Match by similarity (species only)
                elif levenshtein_distance(species_name, tree_species_name) < (difference_threshold - 1):
                    loose_suggestions.append(tree_name)

            # If suggestions is empty, add loose suggestions (levenshtein applied to genus and species independently)
            if len(suggestions) == 0 and len(loose_suggestions) > 0:
                suggestions = suggestions + loose_suggestions
                loose_suggestion = True
            if found_match:
                output.append(db_name)
                perfect_matches.append(db_name)
            else:
                output.append([db_name, suggestions, species_match, genus_match, loose_suggestion])

    return output, perfect_matches


def read_files(db_path, tree_path, species_name_index):
    dbs = []
    trees = []
    filenames = []
    if os.path.isdir(db_path):
        filenames = os.listdir(db_path)
    else:
        filenames.append(os.path.basename(db_path))
        db_path = os.path.dirname(db_path)

    for filename in filenames:
        if not filename.startswith('.'):
            with open(os.path.join(db_path, filename), 'r', encoding="utf-8") as f:  # open in readonly mode
                db = []
                for line in f:
                    # Get name for every line
                    name = line.split(",")[species_name_index]
                    db.append(name.strip())

                # Remove first line of db (info line)
                db.pop(0)
                dbs.append(db)

    filenames = []
    if os.path.isdir(tree_path):
        filenames = os.listdir(tree_path)
    else:
        filenames.append(os.path.basename(tree_path))
        tree_path = os.path.dirname(tree_path)

    for filename in filenames:
        if not filename.startswith('.'):
            with open(os.path.join(tree_path, filename), 'r', encoding="utf-8") as f:  # open in readonly mode
                fname = os.path.basename(f.name)
                tree = []
                copy = False
                # .nex file read
                if fname.endswith('.nex'):
                    for line in f:
                        if line.strip().upper() == "TAXLABELS":
                            copy = True
                            continue
                        elif line.strip() == ";":
                            break
                        elif copy:
                            tree.append(line.strip())
                # .csv (truth db) file read
                elif fname.endswith('.csv'):
                    for line in f:
                        # Get name for every line
                        name = line.split(",", 1)[0]
                        tree.append(name)
                    # Remove first line of tree (info line)
                    tree.pop(0)
                trees.append(tree)

    return dbs, tree

def append_id(filename):
    p = Path(filename)
    return "{0}_{2}{1}".format(Path.joinpath(p.parent, p.stem), p.suffix, time.time())

# Takes the completed taxa_list and writes a new file that includes the new taxa names and the rest of the data from db_path
# TODO: handle multiple input dbs, perhaps with search
def write_file(taxa_list, db_path, species_index):

    outfile_path = append_id(db_path)

    with open(outfile_path, "w", encoding="utf-8") as outf:

        with open(db_path, 'r', encoding="utf-8") as f:  # open in readonly mode

            i = 0

            for line in f:

                if i == 0:
                    outf.write(line)
                    i += 1
                else:
                    csv_list = line.strip().split(",")
                    # Replace first line with new name, only if not blank
                    if taxa_list[i - 1] != "":
                        csv_list[species_index] = taxa_list[i - 1]
                    outf.write(f"{','.join(csv_list)}\n")
                    i += 1

    return outfile_path


def get_wiki_image(search_term):
    WIKI_REQUEST = 'http://en.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&piprop=original&titles='
    try:
        result = wikipedia.search(search_term, results=1)
        wikipedia.set_lang('en')
        wikipage = wikipedia.WikipediaPage(title=result[0])
        title = wikipage.title
        response = requests.get(WIKI_REQUEST + title)
        json_data = json.loads(response.text)
        img_link = list(json_data['query']['pages'].values())[0]['original']['source']
        return img_link
    except:
        return 0


@lru_cache(maxsize=None)
def get_wiki_section(topic, cache=None, n=10):
    if cache and topic in cache:
        return cache.get(topic)
    else:
        try:
            summary = wikipedia.summary(topic, sentences=n)
        except:
            summary = "No Info"
        return summary


# Takes list and returns wiki first paragraph for each entry
def get_wiki_info(search_terms):
    p = multiprocessing.Pool(multiprocessing.cpu_count())
    wiki_entries = p.map(get_wiki_section, search_terms)
    return wiki_entries


def write_wiki_file(new_data, path, fname):
    try:
        with open(f"{path}/{fname}", "r") as f:
            current_data = json.load(f)
            full_data = current_data | new_data
        with open(f"{path}/{fname}", "w") as f:
            json.dump(full_data, f, indent=6, sort_keys=True)
    except:
        with open(f"{path}/{fname}", "w") as f:
            json.dump(new_data, f, indent=6, sort_keys=True)


def read_wiki_file(path, fname):
    try:
        with open(f"{path}/{fname}", 'r') as f:
            dict = json.load(f)
        return dict
    except:
        return {}


# checks information in info and ensures it has entries for every possible match
# returns list of all missing species. Empty list is fully complete.
def validate_info(info, suggestions):
    missing_info = []
    for suggestion in suggestions:
        # match found
        if type(suggestion) is str:
            continue
        for sub_suggestion in suggestion:
            # list of suggestions
            if type(sub_suggestion) is list:
                for sub_sub_suggestion in sub_suggestion:
                    if sub_sub_suggestion not in info:
                        missing_info.append(sub_sub_suggestion)
            elif sub_suggestion not in info:
                missing_info.append(sub_suggestion)
    # return set to weed out duplicates
    return set(missing_info)

def flatten(xss):
    flat_list = []
    for xs in xss:
        if not isinstance(xs, str):
            for x in xs:
                if type(x) is list:
                    flat_list.extend(x)
                else:
                    flat_list.append(x)


    return set(flat_list)


if __name__ == '__main__':
    info = read_wiki_file("dat/info", "info.json")
    suggestions = match("dat/db", "dat/tree")
    missing_info = validate_info(info, suggestions)
    wiki_info = get_wiki_info(missing_info)
    write_wiki_file(wiki_info, "dat/info", "info.json")
