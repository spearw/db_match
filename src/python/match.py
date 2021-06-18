import os
import re
import wikipedia
import requests
import json
from Levenshtein import distance as levenshtein_distance

def match(db_path, tree_path, db_separator ="_", levenshtein_num = 4):


    print("Starting match with parameters:", db_path, tree_path, db_separator, levenshtein_num)
    dbs, tree = read_files(db_path, tree_path)

    output = []
    difference_threshold = int(levenshtein_num)
    for db in dbs:
        for db_name in db:
            suggestions = []
            genus_match = []
            species_match = []
            try:
                genus_name = db_name.split(db_separator,1)[0]
                species_name = db_name.split(db_separator,1)[1]
            except:
                break

            found_match = False
            for tree_name in tree:
                if db_name == tree_name:
                    found_match = True
                    break
                elif levenshtein_distance(db_name, tree_name) < difference_threshold:
                    suggestions.append(tree_name)
                elif re.match(rf".*{species_name}", tree_name):
                    species_match.append(tree_name)
                elif re.match(rf"{genus_name}*", tree_name):
                    genus_match.append(tree_name)

            if found_match:
                output.append(db_name)
            else:
                output.append([db_name, suggestions, species_match, genus_match])

    print(output)
    return output






def read_files(db_path, tree_path):

    dbs = []
    trees = []

    for filename in os.listdir(db_path):
        if not filename.startswith('.'):
            with open(os.path.join(db_path, filename), 'r', encoding="utf-8") as f: # open in readonly mode
                db = []
                for line in f:
                    # Get name for every line
                    name = line.split(",", 1)[0]
                    db.append(name)

                # Remove first line of db (info line)
                db.pop(0)
                dbs.append(db)

    for filename in os.listdir(tree_path):
        if not filename.startswith('.'):
            with open(os.path.join(tree_path, filename), 'r', encoding="utf-8") as f: # open in readonly mode
                fname = os.path.basename(f.name)
                tree = []
                copy = False
                # .nex file read
                if fname.endswith('.nex'):
                    for line in f:
                        if line.strip() == "TAXLABELS":
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

# Takes the completed taxa_list and writes a new file that includes the new taxa names and the rest of the data from db_path
#TODO: handle multiple input dbs, perhaps with search
def write_file(taxa_list, db_path, output_path):
    outf = open(output_path + "/modified.csv", "w", encoding="utf-8")

    fname = os.listdir(db_path)[0]
    inf = open(os.path.join(db_path, fname), "rb")

    data = inf.read()
    data = data.decode()
    lines = data.splitlines()

    print(lines)

    outf.write(lines.pop(0) + "\n")

    i = 0
    for line in lines:
        csv_line = line.split(",")

        # Replace first line with new name, only if not blank
        if taxa_list[i] != "":
            csv_line[0] = taxa_list[i]

        i += 1

        outf.write(",".join(csv_line) + "\n")

    outf.close()
    inf.close()

def get_wiki_image(search_term):
    WIKI_REQUEST = 'http://en.wikipedia.org/w/api.php?action=query&prop=pageimages&format=json&piprop=original&titles='
    try:
        result = wikipedia.search(search_term, results = 1)
        wikipedia.set_lang('en')
        wkpage = wikipedia.WikipediaPage(title = result[0])
        title = wkpage.title
        response  = requests.get(WIKI_REQUEST+title)
        json_data = json.loads(response.text)
        img_link = list(json_data['query']['pages'].values())[0]['original']['source']
        return img_link
    except:
        return 0

def get_wiki_section(topic, n):
    return wikipedia.summary(topic, sentences=n)