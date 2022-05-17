# Phylo-Match

Phylo-Match is a package for correcting misspellings or disparate labelings in phylogenetic trees

## Installation

This project was built with python v3.8. Later versions should be fine, but no guarantees for earlier. Not compatible with python 2.

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install phylo-match.

```bash
pip install phylo-match
```

## Usage

```bash
phylo-match
```
Use the gui to select a database file (.csv), and a taxa tree (.nexus) to match the database to. Click run when you are happy with your selection.

*Phylo-Match does all of its calculations and api requests upfront, so users may have to wait a minute or two after run is clicked, depending on internet speed.*

Information about the DB's taxa will be on the left-hand side. All similar entries in the .nexus file will appear in the middle of the screen. Click on the name you'd like to change the entry to, manually enter a name on the bottom, or click on 'same species', or 'same genus' for additional options, if available.

Once all selections have been made, a new .csv file will be created in the same directory as the original database .csv file.

## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[MIT](https://choosealicense.com/licenses/mit/)