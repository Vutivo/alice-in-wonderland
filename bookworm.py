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
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

warnings.filterwarnings("ignore")


# ---------------------------------------------------------------------
#                           Class GutenbergBook
# ---------------------------------------------------------------------

class GutenbergBook:
    
    def GutenbergID(id:int):

        """
        Downloads a Project Gutenberg book by its ID and saves it locally.
        Reuses the cached file if it already exists.
        Cleans the book content using GutenbergBook.CleanFile.

        Args:
            id (int): The Gutenberg book ID (must be > 0).

        Returns:
            str: The local file path of the downloaded book.

        Raises:
            ValueError: If the book ID is negative.
            Exception: If the download fails.
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

        except (urllib.error.URLError, urllib.error.HTTPError) as e:
            if os.path.exists(book_name):
                os.remove(book_name)  
            raise Exception(f"Failed to download catalog: {e}")

    def CleanFile(id:int, file_path):
        """
        Removes the Project Gutenberg header and footer from a book file.
        Keeps only the main text content between the START and END markers.
        Overwrites the original file with the cleaned text.

        Args:
            id (int): The Gutenberg book ID (used for error messages).
            file_path (str): Path to the book file to clean.

        Raises:
            IOError: If the file cannot be read or written.
            Exception: If the Gutenberg markers are missing or an unexpected error occurs.
        """
        try:
            line_file = []
            start_book = None
            end_book = None

            with open(file_path, 'r',encoding='utf-8', errors='ignore') as file:
                for index, line in enumerate(file):
                    if line.startswith("*** START OF THE PROJECT GUTENBERG EBOOK"):
                        start_book = index + 1
                    if line.startswith("*** END OF THE PROJECT GUTENBERG EBOOK"):
                        end_book = index
                    line_file.append(line)

            if start_book is None or end_book is None:
                os.remove(file_path)
                raise Exception(f"Missing Gutenberg markers in {file_path}")

            cleaned_lines = line_file[start_book:end_book]

            with open(file_path, 'w') as file:
                for line in cleaned_lines:
                    file.write(line)
        except IOError as e:
            raise IOError(f"Error reading/writing file {file_path}: {e}")
        except Exception as e:
            raise Exception(f"Unexpected error while cleaning file: {e}")

    def Catalog():
        """
        Downloads the Project Gutenberg catalog CSV if not already cached.
        Saves it to cache/pg_catalog.csv.

        Raises:
            Exception: If the download fails.
        """
        file_path = "cache/pg_catalog.csv"
        os.makedirs("cache", exist_ok=True)
        try:
            if not os.path.exists(file_path):
                urllib.request.urlretrieve("https://www.gutenberg.org/cache/epub/feeds/pg_catalog.csv", file_path)
        except (urllib.error.URLError, urllib.error.HTTPError) as e:
            if os.path.exists(file_path):
                os.remove(file_path)  
            raise Exception(f"Failed to download catalog: {e}")

# ---------------------------------------------------------------------
#                           Class Book
# ---------------------------------------------------------------------
class Book:
    def Summarizer(id:int):
        """
        Generates a summary of Project Gutenberg book from its ID

        Scores each sentence using TF-IDF, then selects the top 4
        while avoiding redundancy (cosine similarity >= 0.7).
        The result is cached at ./cache/summary/summary{id}.txt.

        Args:
            id (int): The Gutenberg book ID.

        Returns:
            str: The 4 most representative sentences joined by a space.
                Returns an empty list if no valid sentences are found.

        Raises:
            FileNotFoundError: If the book file is not found.
            Exception: If the book is empty or an error occurs during processing.

        """
        try:
            summary_path = f"./cache/summary/summary{id}.txt"
            if os.path.exists(summary_path):
                with open(summary_path, 'r', encoding='utf-8') as f:
                    return f.read()

            file_path = f"./cache/book/book{id}.txt"

            if not os.path.exists(file_path):
                GutenbergBook.GutenbergID(args.summarize)

            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()

                if not text.strip():
                    raise Exception(f"Book {id} is empty.")
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
                if 5 < len(words) < 25 and not (sentence.strip().startswith('"') or sentence.strip().startswith("'") or sentence.strip().startswith("“")):
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
            line = 4
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

            result = " ".join(summary)

            os.makedirs("./cache/summary", exist_ok=True)
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(result)

            return result
        
        except FileNotFoundError:
            raise FileNotFoundError(f"Error: Book file not found for ID {id}")
        
        except Exception as e:
            raise Exception(f"Error generating summary: {e}")

    def Similar(id:int):
        """
        Give a five project Gutenberg book with similar from a book id

        Using cosine for create a rank system foreach book in the list: [11,12,16,35,36,55,84,108,113,120,159,164,236,345,834,863,1661,61262,68283,69087,70114]

        The closer the angle is to 1, the more similar the book is to the selected book.

        Args:
            id (int): The Gutenberg book ID.

        Returns:
            list[str]: The 5 most similar book titles, ordered by similarity score.

        Raises:
            FileNotFoundError: If the book file is not found.
            Exception: If the book is empty or an error occurs during processing.


        """
        try:
            list_id = [11,12,16,35,36,55,84,108,113,120,159,164,236,345,834,863,1661,61262,68283,69087,70114]
            list_book = []
            list_titles = []
            file_path = f"./cache/book/"
            df = pd.read_csv("cache/pg_catalog.csv")
            for element in list_id:
                file = f"book{element}.txt"
                final_file = file_path + file
                if not os.path.exists(final_file):
                    GutenbergBook.GutenbergID(element)
                with open(final_file, 'r', encoding='utf-8', errors='ignore') as f:
                    list_book.append(f.read())
                title = df[df["Text#"] == element]["Title"].values[0]
                list_titles.append(title)

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
            raise ValueError(f"Book ID {args.similar} is not in the collection.")
        
        except FileNotFoundError:
            raise FileNotFoundError(f"Error: Book file not found for ID {id}")

    def Lexdiv(id:int):
        """
    Computes lexical diversity metrics for a Project Gutenberg book.

    Args:
        id (int): The Gutenberg book ID.

    Returns:
        dict: A dictionary with the following keys:
            - "tok" (int): Total number of tokens.
            - "typ" (int): Number of unique words.
            - "hap" (int): Number of words appearing only once.
            - "ttr" (float): Type-Token Ratio (unique words / total tokens).
            - "mwl" (float): Mean word length in characters.
            - "mwf" (float): Mean word frequency (total tokens / unique words).

    Raises:
        FileNotFoundError: If the book file is not found.
        Exception: If the book has no words or an error occurs during processing.
        """
        try:
            GutenbergBook.GutenbergID(id)
            with open(f"./cache/book/book{id}.txt", "r", encoding='utf-8', errors='ignore') as f:
                txt = f.read()
            dico = {}
            tokens = word_tokenize(txt)
            tok = [t for t in tokens if t.isalpha()]
            counts = Counter(tok)
            dico["tok"] = len(tok)
            dico["typ"] = len(counts) 
            dico["hap"] = sum(1 for count in counts.values() if count == 1) # Allows you to keep only the words who appears only one time 

            if dico["tok"] == 0:
                raise Exception(f"Book {id} has no words.")
            if dico["typ"] == 0:
                raise Exception(f"Book {id} has no unique words.")
            
            if dico["tok"]>0:
                dico["ttr"] = dico["typ"] / dico["tok"] 
                dico["mwl"] = sum(len(word) for word in tok) / dico["tok"]
            if dico["typ"]>0:
                dico["mwf"] = dico["tok"] / dico["typ"]
            return dico
        except FileNotFoundError:
            raise FileNotFoundError(f"Error: Book file not found for ID {id}")
        except Exception as e:
            raise Exception(f"Error computing lexical diversity: {e}")

    def Topics(id:int):
        """
    Extracts the most frequent words per section of a Project Gutenberg book.

    Splits the book into sections of ~1000 words and returns the top 10
    most frequent words for each section.
    The result is cached at ./cache/topics/topics{id}.json.

    Args:
        id (int): The Gutenberg book ID.

    Returns:
        dict: A dictionary where each key is a section number (int) and
              each value is a list of (word, count) tuples for the top 10 words.

    Raises:
        FileNotFoundError: If the book file is not found.
        Exception: If an error occurs during processing.
        """
        try: 
            cache_path = f"./cache/topics/topics{id}.json"
            if os.path.exists(cache_path):
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)

            GutenbergBook.GutenbergID(id)
            with open(f"./cache/book/book{id}.txt", "r", encoding='utf-8', errors='ignore') as f:
                txt = f.read()

            dico = {}
            mots = [t for t in txt.split() if t.isalpha()]
            nb_sections = max(1, len(mots) // 1000)
            size = len(mots) // nb_sections
            for i in range(nb_sections):
                section = mots[i*size:(i+1)*size]
                counts = Counter(section)
                dico[i+1] = [word for word in counts.most_common(10)]

            result = dico

            os.makedirs("./cache/topics", exist_ok=True)
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(result, f)

            return result

        except FileNotFoundError:
            raise FileNotFoundError(f"Error: Book file not found for ID {id}")
        except Exception as e:
            raise Exception(f"Error extracting topics: {e}")
        
    def Entities(id:int):
        """
    Extracts named entities (characters and locations) from a Project Gutenberg book using spaCy.

    The result is cached at ./cache/entitie/entitie{id}.json.

    Args:
        id (int): The Gutenberg book ID.

    Returns:
        dict: A dictionary with the following keys:
            - "characters" (list[str]): Person names detected in the text.
            - "locations" (list[str]): Place names (GPE, LOC) detected in the text.

    Raises:
        FileNotFoundError: If the book file is not found.
        OSError: If the spaCy model fails to load.
        Exception: If an error occurs during processing.
    """
        try:
            cache_path = f"./cache/entitie/entitie{id}.json"
            if os.path.exists(cache_path):
                with open(cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)

            GutenbergBook.GutenbergID(id)
            with open(f"./cache/book/book{id}.txt", "r", encoding='utf-8', errors='ignore') as f:
                txt = f.read()

            nlp = spacy.load("en_core_web_lg")
            nlp.max_length = 5000000
            doc = nlp(txt)
            dico = {}
            persons = set()
            locations = set()
            
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    persons.add(ent.text)
                elif ent.label_ in ("GPE", "LOC"):
                    locations.add(ent.text)

            dico["characters"] = list(persons)
            dico["locations"] = list(locations)

            result = dico
            os.makedirs("./cache/entitie", exist_ok=True)
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(result, f)

            return result


        except FileNotFoundError:
            raise FileNotFoundError(f"Error: Book file not found for ID {id}")
         
        except OSError as e:
            raise OSError(f"Error loading spaCy model: {e}")
            
        except Exception as e:
            raise Exception(f"Error extracting entities: {e}")

    def Info(id:int):
        """
        Retrieves metadata for a Project Gutenberg book from the local catalog.

        Reads from cache/pg_catalog.csv to extract book information.

        Args:
            id (int): The Gutenberg book ID.

        Returns:
            dict: A dictionary with the following keys:
                - "id" (str): The book ID.
                - "authors" (str): The book's author(s).
                - "bookshelves" (str): The associated bookshelves.

        Raises:
            FileNotFoundError: If cache/pg_catalog.csv is not found.
            Exception: If the ID doesn't exist or an error occurs.
        """
        try:
            df = pd.read_csv("cache/pg_catalog.csv")
            row = df[df["Text#"] == int(id)]
            if row.empty:
                raise Exception(f"Id {id} doesn't exist")
            result = {
            "id": str(id),
            "authors": row["Authors"].values[0],
            "bookshelves": row["Bookshelves"].values[0],
            }
            return result 
        except FileNotFoundError:
            raise FileNotFoundError ("Error: pg_catalog.csv not found")
        
        except Exception as e:
            raise Exception(f"Error retrieving book info: {e}")

    def Card(id:int):
        """
        Aggregates all available analyses for a Project Gutenberg book into a single dictionary.

        Calls Info, Lexdiv, Topics, Entities, Summarizer and Similar for the given ID.
        If a method fails, its value is set to "ERROR" instead of raising an exception.

        Args:
            id (int): The Gutenberg book ID.

        Returns:
            dict: A dictionary with the following keys:
                - "info" (dict): Book metadata.
                -- "lexdiv" (dict): Lexical diversity metrics.
                - "topic" (dict): Top 10 words per section.
                - "entities" (dict): Characters and locations found in the book.
                - "summary" (str): The 4 most representative sentences.
                - "similar" (list[str]): The 5 most similar book titles.
        """
        result = {}
        
        methods = {
            "info": Book.Info,
            "lexdiv": Book.Lexdiv,
            "topic": Book.Topics,
            "entities": Book.Entities,
            "summary": Book.Summarizer,
            "similar": Book.Similar,
        }
        
        for key, func in methods.items():
            try:
                result[key] = func(id)
                print(f"{key} done ") 
            except Exception as e:
                result[key] = "ERROR"
                print(f"{key} ERROR: {e}")
        return result
    
    
    def wordcloud(id):
        try:
            cache_path = f"./cache/wordcloud_{id}.png"

            if os.path.exists(cache_path):
                return cache_path

            GutenbergBook.GutenbergID(id)
            with open(f"./cache/book/book{id}.txt", "r", encoding='utf-8') as f:
                text = f.read()

            wc = WordCloud(width=800, height=400, stopwords=STOPWORDS).generate(text) # We import a set of words to ignore for the wordcloud "STOPWORDS"
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



    def by_author(author_name):
        try:
            df = pd.read_csv("pg_catalog.csv")
            mask = df["Authors"].str.contains(author_name, case=False, na=False) # Allows you to search for an author even if you don't write the name exactly : case = case insensitive, na = False to ignore NaN values
            matches = df[mask]
            if matches.empty:
                print(f"No books found for author: {author_name}")
                return []
            results = []
            for _, row in matches.iterrows(): # iterrows() return 2 things eachj time : the index and the row itself, we use _ for the index because we don't need it (convention in PYTHON)
                book_id = row["Text#"]
                path = GutenbergBook.GutenbergID(book_id)
                results.append({"id": book_id, "title": row["Title"], "path": path})
            return results
        except FileNotFoundError:
            print("Error: pg_catalog.csv not found")
            return []
        except Exception as e:
            print(f"Error searching by author: {e}")
            return []



    def by_category(category_name):
        try:
            
            df = pd.read_csv("pg_catalog.csv")
            mask = df["Bookshelves"].str.contains(category_name, case=False, na=False)
            matches = df[mask]
            if matches.empty:
                print(f"No books found for category: {category_name}")
                return []
            results = []
            for _, row in matches.iterrows():
                book_id = row["Text#"]
                path = GutenbergBook.GutenbergID(book_id)
                results.append({"id": book_id, "title": row["Title"], "path": path})
            return results
        
        except FileNotFoundError:
            print("Error: pg_catalog.csv not found")
            return []
        
        except Exception as e:
            print(f"Error searching by category: {e}")
            return []


    def export_card(id):
        try:

            os.makedirs("./cache/exports", exist_ok=True)
            pdf_path = f"./cache/exports/card_{id}.pdf"
            
            data = Book.card(id)
            doc = SimpleDocTemplate(pdf_path, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []

            story.append(Paragraph(f"Book #{id}", styles["Title"]))
            story.append(Paragraph(f"Author: {data.get('info', {}).get('authors', 'N/A')}", styles["Normal"]))
            story.append(Spacer(1, 12))
            story.append(Paragraph("Summary", styles["Heading2"]))
            story.append(Paragraph(" ".join(data.get("summary", [])), styles["Normal"]))

            doc.build(story)
            return pdf_path
        
        except Exception as e:
            print(f"Error exporting card: {e}")
            return None

        

if __name__ == "__main__":
    GutenbergBook.Catalog()
    parser = argparse.ArgumentParser(description="CLI argumets")

# ---------------------------------------------------------------------
#                               NLP Tasks
# ---------------------------------------------------------------------

    group = parser.add_mutually_exclusive_group(required=True) 
    group.add_argument("--lexdiv", type=int) 
    group.add_argument("--entities", type=int)
    group.add_argument("--summarize", type=int)
    group.add_argument("--topics", type= int)
    group.add_argument("--similar", type=int)
    group.add_argument("--card", type=int)
    group.add_argument("--wordcloud", type=int)
    group.add_argument("--author", type=str)
    group.add_argument("--category", type=str)
    group.add_argument("--export", type=int)

# ---------------------------------------------------------------------
#                           NPL Definitions
# ---------------------------------------------------------------------

    args = parser.parse_args()

    if args.lexdiv:
        result = Book.Lexdiv(args.lexdiv)
        print(result)

    if args.summarize:
        resume = Book.Summarizer(args.summarize)
        print(resume)

    if args.topics:
        result = Book.Topics(args.topics)
        print(result)

    if args.entities:
        result = Book.Entities(args.entities)
        print(result)

    if args.similar:
        result = Book.Similar(args.similar)
        print(result)

    if args.card:
        result = Book.Card(args.card)
        print(result)
    
    if args.wordcloud is not None:
        result = Book.wordcloud(args.wordcloud)
        print(result)
    
    if args.author:
        result = Book.by_author(args.author)
        print(result)

    if args.category:
        result = Book.by_category(args.category)
        print(result)

    if args.export:
        result = Book.export_card(args.export)
        print(result)