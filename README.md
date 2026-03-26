# Alice in Wonderland
This project was made for Epitech. The goal is to build a CLI using NLP techniques. 

We work with the Project Gutenberg website to download books and their catalog.


---


## Contents
- `bookworm.py` — main CLI script containing all NLP logic
- `cache/book/` — downloaded and cleaned Gutenberg `.txt` files
- `cache/pg_catalog.csv` — local copy of the Project Gutenberg catalog `.csv`
- `cache/summary/` — cached summaries per book ID `.txt`
- `cache/topics/` — cached topic results per book ID `.json`
- `cache/entitie/` — cached entity results per book ID `.json`
- `requirements.txt` — all Python dependencies

```
projet/

├── datasets/
     └── entities_pipeline.svg
     └── lexdiv_pipeline.svg
     └── topics_pipeline.svg
├── .venv/
├── .gitignore
├── bookworm.py
├── README.md
└── requirements.txt

```
---


## How to use
1. Clone the repository.
```
git clone <repo-url>
```
 
2. Create a virtual environment.
```
python -m venv venv
source venv/bin/activate
```
 
3. Install dependencies.
```
pip install -r requirements.txt
```
 
4. Run a command.
```
python bookworm.py --lexdiv 11
python bookworm.py --entities 11
python bookworm.py --summarize 11
python bookworm.py --topics 11
python bookworm.py --similar 11
python bookworm.py --card 11
```

---


## CLI Reference

 Option | Argument | Description |
|---|---|---|
| `--lexdiv` | `<ID>` | Compute lexical diversity metrics for a book |
| `--entities` | `<ID>` | Extract named characters and locations |
| `--summarize` | `<ID>` | Generate  summary |
| `--topics` | `<ID>` | Extract top keywords per section |
| `--similar` | `<ID>` | Find the 5 most similar books in the corpus |
| `--card` | `<ID>` | Return a full metadata card combining all of the above |


---


## NLP Tasks

### Lexical Diversity
![Pipeline lexdiv](assets/lexdiv_pipeline.svg)

### Topic Modeling
![Pipeline topics](assets/topics_pipeline.svg)

### Named Entity Recognition
![Pipeline entities](assets/entities_pipeline.svg)


---


## Bonuses made

- [x] retrieve information and download all books [co-]written by a given author;
- [x] retrieve information and download all books from a specific category
- [x] fetch book covers to illustrate your book cards
- [x] generate a word cloud of the most frequent words to illustrate your book cards
- [ ] compute additional lexical diversity measurements such as: MSTTR, MATTR, MTLD, Evenness, Rarity, Dispersion, Disparity, Guiraud's Index, Herdan's C, Yule's I, Yule's K, Maas's a², Dugast's U²;
- [ ] compare topic modeling results using LSA and LDA, and choose the best approach
- [ ] export book cards in a cross-platform and user-friendly format
- [ ] cluster books using K-Means or hierarchical clustering to group similar texts
- [ ] build a simple frontend to make your NLP engine interactive


---


## Credits
 
This project was made by [MelioSousLo](https://github.com/MelioSousLo), and [Kenan-LCF](https://github.com/Kenan-LCF).