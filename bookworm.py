import pandas as pd
import argparse
import os
import urllib.request
import urllib.error
import nltk
import numpy as np
import re
import spacy
import warnings
from nltk.tokenize import word_tokenize
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


warnings.filterwarnings("ignore")


if not os.path.exists("pg_catalog.csv"):
    urllib.request.urlretrieve("https://www.gutenberg.org/cache/epub/feeds/pg_catalog.csv", "pg_catalog.csv") # Allows you to download a CSV via a link

class GutenbergBook:
    def GutenbergID(id:int):
        """
        Download a book from Project Gutenberg by its ID.
        Reuses the file if it already exists.
        Cleans the book using GutenbergBook.CleanFile.
        """
        url = f"https://www.gutenberg.org/cache/epub/{id}/pg{id}.txt"
        try:
            os.makedirs("./cache/book", exist_ok=True)
            book_name = os.path.join("./cache/book", f"book{id}.txt")

            if os.path.exists(book_name):
                return book_name

            urllib.request.urlretrieve(url, book_name)
            GutenbergBook.CleanFile(id,book_name)


        except urllib.error.URLError as e:
            print(f"Failed to download book: {e}")

        except urllib.error.HTTPError as e:
            print(f"Failed to download book: {e}")
    def CleanFile(id ,file_path):
        """
        Remove the Project Gutenberg header and footer from a book file.
        Keeps only the main text content.
        Overwrites the original file with the cleaned text.
        """
        line_file = []
        start_book = 0
        end_book = 0
        with open(file_path,'r') as file:
            for index, line in enumerate(file):
                if line.startswith("*** START OF THE PROJECT GUTENBERG EBOOK"):
                   start_book = index +1
                if line.startswith("*** END OF THE PROJECT GUTENBERG EBOOK"):
                    end_book = index
                line_file.append(line)
            cleaned_lines = line_file[start_book:end_book]
        with open(file_path,'w') as file:
           for line in cleaned_lines:
               file.write(line)

class Book:
    def summarizer(id, n=3):

        file_path = f"./cache/book/book{id}.txt"

        if not os.path.exists(file_path):
            GutenbergBook.GutenbergID(args.summarize)

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

        for idx in ranked_indices:
            if len(selected) >= n:
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
    def similar(id):
        list_id = [11,12,16,35,36,55,84,108,113,120,159,164,236,345,834,863,1661,61262,68283,69087,70114]
        list_book = []
        list_titles = []
        file_path = f"./cache/book/"
        for element in list_id:
            file = f"book{element}.txt"
            final_file = file_path + file
            if not os.path.exists(final_file):
                GutenbergBook.GutenbergID(element)
            
            with open(final_file, 'r') as f:
                list_book.append(f.read())
            
            df = pd.read_csv("pg_catalog.csv")
            title = df[df["Text#"] == element]["Title"].values[0]
            list_titles.append(title)

        

        vectorizer = TfidfVectorizer(stop_words="english")
        X = vectorizer.fit_transform(list_book)

        try:
            target_index = list_id.index(int(args.similar))

            similarities = cosine_similarity(X[target_index], X).flatten()
            ranked = similarities.argsort()[::-1]
            results = []
            for element in ranked:
                if element != target_index:
                    results.append(list_titles[element])
                if len(results) == 5:
                    break
                
            return result
        except ValueError:
            raise ValueError(f"Book ID {args.similar} is not in the collection.")
    def lexdiv(id):
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
    def topics(id):
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
    def entities(id):
        GutenbergBook.GutenbergID(id)
        with open(f"./cache/book/book{id}.txt", "r", encoding="utf-8") as f:
            txt = f.read()

        nlp = spacy.load("en_core_web_trf")
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CLI argumets")

# ---------------------------------------------------------------------
#                               Positional
# ---------------------------------------------------------------------

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

# ---------------------------------------------------------------------
#                           NPL Definitions
# ---------------------------------------------------------------------

    args = parser.parse_args()

    if args.lexdiv:
        result = Book.lexdiv(args.lexdiv)
        print(result)

    if args.summarize:
        resume = Book.summarizer(args.summarize, n=3)
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
