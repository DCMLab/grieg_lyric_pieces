![Version](https://img.shields.io/github/v/release/DCMLab/grieg_lyric_pieces?display_name=tag)
[![DOI](https://zenodo.org/badge/383828184.svg)](https://doi.org/10.5281/zenodo.7473578)
![GitHub repo size](https://img.shields.io/github/repo-size/DCMLab/grieg_lyric_pieces)
![License](https://img.shields.io/badge/license-CC%20BY--NC--SA%204.0-9cf)


This is a README file for a data repository originating from the [DCML corpus initiative](https://github.com/DCMLab/dcml_corpora)
and serves as welcome page for both 

* the GitHub repo [https://github.com/DCMLab/grieg_lyric_pieces](https://github.com/DCMLab/grieg_lyric_pieces) and the corresponding
* documentation page [https://dcmlab.github.io/grieg_lyric_pieces](https://dcmlab.github.io/grieg_lyric_pieces)

For information on how to obtain and use the dataset, please refer to [this documentation page](https://dcmlab.github.io/grieg_lyric_pieces/introduction).

# Edvard Grieg – Lyric Pieces (A corpus of annotated scores)


## Getting the data

* download repository as a [ZIP file](https://github.com/DCMLab/grieg_lyric_pieces/archive/main.zip)
* download a [Frictionless Datapackage](https://specs.frictionlessdata.io/data-package/) that includes concatenations
  of the TSV files in the four folders (`measures`, `notes`, `chords`, and `harmonies`) and a JSON descriptor:
  * [grieg_lyric_pieces.zip](https://github.com/DCMLab/grieg_lyric_pieces/releases/latest/download/grieg_lyric_pieces.zip)
  * [grieg_lyric_pieces.datapackage.json](https://github.com/DCMLab/grieg_lyric_pieces/releases/latest/download/grieg_lyric_pieces.datapackage.json)
* clone the repo: `git clone https://github.com/DCMLab/grieg_lyric_pieces.git` 


## Data Formats

Each piece in this corpus is represented by five files with identical name prefixes, each in its own folder. 
For example, the first tale has the following files:

* `MS3/op12n01.mscx`: Uncompressed MuseScore 3.6.2 file including the music and annotation labels.
* `notes/op12n01.notes.tsv`: A table of all note heads contained in the score and their relevant features (not each of them represents an onset, some are tied together)
* `measures/op12n01.measures.tsv`: A table with relevant information about the measures in the score.
* `chords/op12n01.chords.tsv`: A table containing layer-wise unique onset positions with the musical markup (such as dynamics, articulation, lyrics, figured bass, etc.).
* `harmonies/op12n01.harmonies.tsv`: A table of the included harmony labels (including cadences and phrases) with their positions in the score.

Each TSV file comes with its own JSON descriptor that describes the meanings and datatypes of the columns ("fields") it contains,
follows the [Frictionless specification](https://specs.frictionlessdata.io/tabular-data-resource/),
and can be used to validate and correctly load the described file. 

### Opening Scores

After navigating to your local copy, you can open the scores in the folder `MS3` with the free and open source score
editor [MuseScore](https://musescore.org). Please note that the scores have been edited, annotated and tested with
[MuseScore 3.6.2](https://github.com/musescore/MuseScore/releases/tag/v3.6.2). 
MuseScore 4 has since been released which renders them correctly but cannot store them back in the same format.

### Opening TSV files in a spreadsheet

Tab-separated value (TSV) files are like Comma-separated value (CSV) files and can be opened with most modern text
editors. However, for correctly displaying the columns, you might want to use a spreadsheet or an addon for your
favourite text editor. When you use a spreadsheet such as Excel, it might annoy you by interpreting fractions as
dates. This can be circumvented by using `Data --> From Text/CSV` or the free alternative
[LibreOffice Calc](https://www.libreoffice.org/download/download/). Other than that, TSV data can be loaded with
every modern programming language.

### Loading TSV files in Python

Since the TSV files contain null values, lists, fractions, and numbers that are to be treated as strings, you may want
to use this code to load any TSV files related to this repository (provided you're doing it in Python). After a quick
`pip install -U ms3` (requires Python 3.10 or later) you'll be able to load any TSV like this:

```python
import ms3

labels = ms3.load_tsv("harmonies/op12n01.harmonies.tsv")
notes = ms3.load_tsv("notes/op12n01.notes.tsv")
```


## Version history

See the [GitHub releases](https://github.com/DCMLab/grieg_lyric_pieces/releases).

## Questions, Suggestions, Corrections, Bug Reports

Please [create an issue](https://github.com/DCMLab/grieg_lyric_pieces/issues) and/or feel free to fork and submit pull requests.

## Cite as

> Hentschel, J., Rammos, Y., Neuwirth, M., Moss, F. C., & Rohrmeier, M. (2024). An annotated corpus of tonal piano music from the long 19th century. Empirical Musicology Review, 18(1), 84–95. https://doi.org/10.18061/emr.v18i1.8903

## License

Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License ([CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/)).

![cc-by-nc-sa-image](https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png)

## File naming convention


The file names listed in the [Overview](#overview) below refer to the 
[opus numbers](https://en.wikipedia.org/wiki/List_of_compositions_by_Edvard_Grieg) of the 10 books.

## Overview
|file_name|measures|labels|standard|               annotators                | reviewers  |
|---------|-------:|-----:|--------|-----------------------------------------|------------|
|op12n01  |      23|    43|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.30) |Adrian Nagel|
|op12n02  |      79|   125|2.3.0   |Adrian Nagel (2.1.0), John Heilig (2.3.0)|Adrian Nagel|
|op12n03  |      52|   110|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op12n04  |      72|    97|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op12n05  |      40|   109|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op12n06  |      56|   126|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op12n07  |      56|    74|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op12n08  |      32|    78|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op38n01  |      86|   141|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op38n02  |      41|    46|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op38n03  |      48|    87|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op38n04  |      36|    66|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op38n05  |      41|    70|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op38n06  |      47|   104|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op38n07  |      53|    55|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op38n08  |      84|   130|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op43n01  |      42|   102|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op43n02  |      30|    98|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op43n03  |      35|   112|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op43n04  |      36|    52|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op43n05  |      36|   110|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op43n06  |      72|   127|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op47n01  |     184|   159|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op47n02  |     126|   183|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op47n03  |     106|    93|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op47n04  |      38|    21|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op47n05  |      41|   109|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op47n06  |      74|    83|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op47n07  |      97|   134|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op54n01  |      61|   110|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op54n02  |     159|   286|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op54n03  |     194|   267|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op54n04  |      63|    91|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op54n05  |     204|   118|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op54n06  |      90|   171|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op57n01  |     146|   313|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op57n02  |     125|   184|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op57n03  |      67|   186|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op57n04  |      92|   116|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op57n05  |     169|   202|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op57n06  |      95|   156|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op62n01  |      90|    72|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op62n02  |      81|   163|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op62n03  |      65|    95|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op62n04  |      81|    97|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op62n05  |      62|    45|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op62n06  |     150|   173|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op65n01  |     173|   204|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op65n02  |      26|   128|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op65n03  |      58|    87|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op65n04  |      71|   112|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op65n05  |      48|   128|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op65n06  |     179|   224|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op68n01  |      56|   156|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op68n02  |      88|   186|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op68n03  |     114|   134|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op68n04  |      90|    85|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op68n05  |      43|    95|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op68n06  |     202|   200|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op71n01  |      95|   180|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op71n02  |      54|   107|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op71n03  |      79|    72|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op71n04  |      77|    87|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op71n05  |      98|   155|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op71n06  |      32|   133|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|
|op71n07  |      74|    74|2.3.0   |Adrian Nagel (2.1.1), John Heilig (2.3.0)|Adrian Nagel|


*Overview table automatically updated using [ms3](https://ms3.readthedocs.io/).*
