import pandas as pd
import argparse
import os
import urllib.request
import urllib.error
import urllib.parse
import numpy as np
import re
import spacy
import warnings 
import json

from nltk.tokenize import word_tokenize
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from wordcloud import WordCloud, STOPWORDS

warnings.filterwarnings("ignore")


# Télécharge le catalogue au démarrage s'il n'existe pas
try:
    if not os.path.exists("pg_catalog.csv"):
        print("Downloading Project Gutenberg catalog...")
        urllib.request.urlretrieve("https://www.gutenberg.org/cache/epub/feeds/pg_catalog.csv", "pg_catalog.csv")
except urllib.error.URLError as e:
    print(f"Warning: Could not download catalog: {e}")
except Exception as e:
    print(f"Warning: Unexpected error downloading catalog: {e}")



# ---------------------------------------------------------------------
#                           Class GutenbergBook
# ---------------------------------------------------------------------


class GutenbergBook:
    
    def GutenbergID(id:int):
        """
        Download a book from Project Gutenberg by its ID.
        Reuses the file if it already exists.
        Cleans the book using GutenbergBook.CleanFile.
        """
        if int(id) < 0:
            raise ValueError(f"Invalid book ID: {id}")
        url = f"https://www.gutenberg.org/cache/epub/{id}/pg{id}.txt"
        book_name = os.path.join("./cache/book", f"book{id}.txt")
        try:
            if id > 0:
                os.makedirs("./cache/book", exist_ok=True)

                if os.path.exists(book_name):
                    return book_name

                urllib.request.urlretrieve(url, book_name)
                GutenbergBook.CleanFile(id, book_name)
                return book_name

        except urllib.error.URLError as e:
            print(f"Failed to download book: {e}")
            return None
        except urllib.error.HTTPError as e:
            print(f"Failed to download book: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error downloading book: {e}")
            return None
    
    
    
    def CleanFile(id ,file_path):
        """
        Remove the Project Gutenberg header and footer from a book file.
        Keeps only the main text content.
        Overwrites the original file with the cleaned text.
        """
        try:
            line_file = []
            start_book = 0
            end_book = 0
            with open(file_path,'r', encoding='utf-8') as file:
                for index, line in enumerate(file):
                    if line.startswith("*** START OF THE PROJECT GUTENBERG EBOOK"):
                       start_book = index +1
                    if line.startswith("*** END OF THE PROJECT GUTENBERG EBOOK"):
                        end_book = index
                    line_file.append(line)
                cleaned_lines = line_file[start_book:end_book]
            with open(file_path,'w', encoding='utf-8') as file:
               for line in cleaned_lines:
                   file.write(line)
        except IOError as e:
            print(f"Error reading/writing file {file_path}: {e}")
        except Exception as e:
            print(f"Unexpected error while cleaning file: {e}")

# ---------------------------------------------------------------------
#                           Class Book
# ---------------------------------------------------------------------
class Book:
    
    def lexdiv(id):
        try:
            GutenbergBook.GutenbergID(id)
            with open(f"./cache/book/book{id}.txt", "r", encoding="utf-8") as f:
                txt = f.read()
            dico = {}
            tokens = word_tokenize(txt)
            tok = [t for t in tokens if t.isalpha()]
            counts = Counter(tok)
            dico["tok"] = len(tok)
            dico["typ"] = len(counts) 
            dico["hap"] = sum(1 for count in counts.values() if count == 1) # Allows you to keep only the words who appears only one time 
            if dico["tok"]>0:
                dico["ttr"] = dico["typ"] / dico["tok"] 
                dico["mwl"] = sum(len(word) for word in tok) / dico["tok"]
            if dico["typ"]>0:
                dico["mwf"] = dico["tok"] / dico["typ"]
            return dico
        except FileNotFoundError:
            print(f"Error: Book file not found for ID {id}")
            return {}
        except Exception as e:
            print(f"Error computing lexical diversity: {e}")
            return {}
    
    
    
    def topics(id):
        try:
            GutenbergBook.GutenbergID(id)
            with open(f"./cache/book/book{id}.txt", "r", encoding="utf-8") as f:
                txt = f.read()
            dico={}
            mots = [t for t in txt.split() if t.isalpha()]
            nb_sections = max(1, len(mots) // 1000)

            size = len(mots) // nb_sections
            for i in range(nb_sections):
                section = mots[i*size:(i+1)*size]
                counts = Counter(section)
                dico[i+1] = [word for word in counts.most_common(10)]
            return dico
        except FileNotFoundError:
            print(f"Error: Book file not found for ID {id}")
            return {}
        except Exception as e:
            print(f"Error extracting topics: {e}")
            return {}
   
   
   
    def entities(id):
        try:
            GutenbergBook.GutenbergID(id)
            with open(f"./cache/book/book{id}.txt", "r", encoding="utf-8") as f:
                txt = f.read()

            nlp = spacy.load("en_core_web_trf")
            nlp.max_length = 5000000
            doc = nlp(txt)
            dico = {}
            persons = []
            locations = []
            
            for ent in doc.ents:
                if ent.label_ == "PERSON" and ent.text not in persons:
                    persons.append(ent.text)
                elif ent.label_ in ("GPE", "LOC") and ent.text not in locations:
                    locations.append(ent.text)

            dico["characters"] = persons
            dico["locations"] = locations
            return dico
        except FileNotFoundError:
            print(f"Error: Book file not found for ID {id}")
            return {"characters": [], "locations": []}
        except OSError as e:
            print(f"Error loading spaCy model: {e}")
            return {"characters": [], "locations": []}
        except Exception as e:
            print(f"Error extracting entities: {e}")
            return {"characters": [], "locations": []}
   
   
   
    def info(id):
        try:
            df = pd.read_csv("pg_catalog.csv")
            row = df[df["Text#"] == int(id)]
            if row.empty:
                print(f"Error: Book ID {id} not found in catalog")
                return {}
            result = {
            "id": str(id),
            "authors": row["Authors"].values[0],
            "bookshelves": row["Bookshelves"].values[0],
            }
            return result
        except FileNotFoundError:
            print("Error: pg_catalog.csv not found")
            return {}
        except (KeyError, IndexError) as e:
            print(f"Error: Missing data for book ID {id}: {e}")
            return {}
        except Exception as e:
            print(f"Error retrieving book info: {e}")
            return {} 
   


    def summarizer(id):
        try:
            file_path = f"./cache/book/book{id}.txt"

            if not os.path.exists(file_path):
                GutenbergBook.GutenbergID(id)

            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()

            sentences = re.split(r'(?<=[.!?])\s+|\.{3}\s*', text)

            cleaned_sentences = []

            for sentence in sentences:
                sentence = sentence.replace("[Illustration]", "").strip()
                if not sentence:
                    continue
                if not re.search(r'[.!?]$', sentence):
                    continue
                cleaned_sentences.append(sentence)

            filtered_sentences = []

            for sentence in cleaned_sentences:
                words = sentence.split()
                if 5 < len(words) < 25 and not (sentence.strip().startswith('"') or sentence.strip().startswith("'") or sentence.strip().startswith('"')):
                    filtered_sentences.append(sentence)

            if len(filtered_sentences) == 0:
                return []

            vectorizer = TfidfVectorizer(stop_words="english")
            X = vectorizer.fit_transform(filtered_sentences)

            scores = []
            for i in range(X.shape[0]):
                score = X[i].mean()
                scores.append(score)
            scores = np.array(scores).flatten()

            sim_matrix = cosine_similarity(X)

            selected = []
            ranked_indices = scores.argsort()[::-1]  
            line = 3
            for idx in ranked_indices:
                if len(selected) >= line:
                    break

                too_similar = False
                for i in selected:
                    if sim_matrix[idx][i] >= 0.7:
                        too_similar = True
                        break

                if not too_similar:
                    selected.append(idx)

            selected.sort()

            summary = []
            for i in selected:
                summary.append(filtered_sentences[i])

            return summary
        except FileNotFoundError:
            print(f"Error: Book file not found for ID {id}")
            return []
        except Exception as e:
            print(f"Error generating summary: {e}")
            return []
    
    
    
    def similar(id):
        try:
            list_id = [11,12,16,35,36,55,84,108,113,120,159,164,236,345,834,863,1661,61262,68283,69087,70114]
            list_book = []
            list_titles = []
            file_path = f"./cache/book/"
            
            df = pd.read_csv("pg_catalog.csv")
            
            for element in list_id:
                try:
                    file = f"book{element}.txt"
                    final_file = file_path + file
                    if not os.path.exists(final_file):
                        GutenbergBook.GutenbergID(element)
                    
                    with open(final_file, 'r', encoding='utf-8') as f:
                        list_book.append(f.read())
                    
                    title = df[df["Text#"] == element]["Title"].values[0]
                    list_titles.append(title)
                except Exception as e:
                    print(f"Warning: Could not load book {element}: {e}")
                    continue

            if len(list_book) == 0:
                print("Error: No books could be loaded for comparison")
                return []

            vectorizer = TfidfVectorizer(stop_words="english")
            X = vectorizer.fit_transform(list_book)

            target_index = list_id.index(int(id))

            similarities = cosine_similarity(X[target_index], X).flatten()
            ranked = similarities.argsort()[::-1]
            results = []
            for element in ranked:
                if element != target_index:
                    results.append(list_titles[element])
                if len(results) == 5:
                    break
                
            return results
        except ValueError:
            print(f"Book ID {id} is not in the collection.")
            return []
        except FileNotFoundError:
            print("Error: pg_catalog.csv not found")
            return []
        except Exception as e:
            print(f"Error finding similar books: {e}")
            return []
    
    
    
    def wordcloud(id):
        try:
            cache_path = f"./cache/wordcloud_{id}.png"

            if os.path.exists(cache_path):
                return cache_path

            GutenbergBook.GutenbergID(id)
            with open(f"./cache/book/book{id}.txt", "r", encoding='utf-8') as f:
                text = f.read()

            wc = WordCloud(width=800, height=400, stopwords=STOPWORDS).generate(text) # on import un jeu de mots à ignorer pour le wordcloud "STOPWORDS"
            wc.to_file(cache_path)
            return cache_path
        except FileNotFoundError:
            print(f"Error: Book file not found for ID {id}")
            return None
        except ValueError as e:
            print(f"Error generating wordcloud: {e}")
            return None
        except Exception as e:
            print(f"Error creating wordcloud: {e}")
            return None



    def cover(id):
        try:
            cache_path = f"./cache/cover_{id}.jpg"
            if os.path.exists(cache_path):
                return cache_path
            
            df = pd.read_csv("pg_catalog.csv")
            row = df[df["Text#"] == int(id)]
            if row.empty:
                print(f"Error: Book ID {id} not found in catalog")
                return None
                
            title = row["Title"].values[0]
            query = urllib.parse.quote_plus(title)
            url = f"https://openlibrary.org/search.json?q={query}&limit=1"
            
            try:
                with urllib.request.urlopen(url) as response:
                    data = json.loads(response.read().decode())
            except urllib.error.URLError as e:
                print(f"Error fetching cover data: {e}")
                return None
            
            docs = data.get("docs", [])
            if docs and "cover_i" in docs[0]:
                cover_id = docs[0]["cover_i"]
                img_url = f"https://covers.openlibrary.org/b/id/{cover_id}-M.jpg"
                try:
                    urllib.request.urlretrieve(img_url, cache_path)
                    return cache_path
                except urllib.error.URLError as e:
                    print(f"Error downloading cover image: {e}")
                    return None
            
            return None  # pas de couverture trouvée
        except FileNotFoundError:
            print("Error: pg_catalog.csv not found")
            return None
        except Exception as e:
            print(f"Error retrieving cover: {e}")
            return None



    def card(id):
        try:
            result = {
            "info": Book.info(id),
            "lexdiv": Book.lexdiv(id),
            "topics": Book.topics(id),
            "entities": Book.entities(id),
            "summary": Book.summarizer(id),
            "similar": Book.similar(id),
            "wordcloud": Book.wordcloud(id),
        }
            return result
        except Exception as e:
            print(f"Error creating book card: {e}")
            return {}
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CLI argumets")

# ---------------------------------------------------------------------
#                               NLP Tasks
# ---------------------------------------------------------------------

    group = parser.add_mutually_exclusive_group(required=True) # Avoids to put 2 flags in same time 
    group.add_argument("--lexdiv", type=int) 
    group.add_argument("--entities", type=int)
    group.add_argument("--summarize", type=int)
    group.add_argument("--topics", type= int)
    group.add_argument("--similar", type=int)
    group.add_argument("--card", type=int)
    group.add_argument("--info", type=int)
    group.add_argument("--wordcloud", type=int)

# ---------------------------------------------------------------------
#                           NPL Definitions
# ---------------------------------------------------------------------

    args = parser.parse_args()

    if args.lexdiv:
        result = Book.lexdiv(args.lexdiv)
        print(result)

    if args.summarize:
        resume = Book.summarizer(args.summarize)
        for sentence in resume:
            print(sentence)

    if args.topics:
        result = Book.topics(args.topics)
        print(result)

    if args.entities:
        result = Book.entities(args.entities)
        print(result)

    if args.similar:
        result = Book.similar(args.similar)
        print(result)

    if args.card:
        result = Book.card(args.card)
        print(result)
    
    if args.info:   
        result = Book.info(args.info)
        print(result)
    
    if args.wordcloud is not None:
        result = Book.wordcloud(args.wordcloud)
        print(result)