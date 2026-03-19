import pandas as pd
import argparse
import os
import urllib.request
import urllib.error
import nltk
from nltk.tokenize import word_tokenize
from collections import Counter
import re

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
    def summarizer(cleaned_sentences, n=3):
        stop_words = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", "he", "him",
                           "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs", "themselves", "what",
                             "which", "who", "whom", "this", "that", "these", "those", "am", "is", "are", "was", "were", "be", "been", "being", "have", "has",
                               "had", "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if", "or", "because", "as", "until", "while", 
                               "of", "at", "by", "for", "with", "about", "against", "between", "into", "through", "during", "before", "after", "above", "below",
                                 "to", "from", "up", "down", "in", "out", "on", "off", "over", "under", "again", "further", "then", "once", "here", "there", "when", 
                                 "where", "why", "how", "all", "any", "both", "each", "few", "more", "most", "other", "some", "such", "no", "nor", "not", "only", "own", 
                                 "same", "so", "than", "too", "very", "s", "t", "can", "will", "just", "don", "should", "now"]
 
        freq_word = {}
        for sentence in cleaned_sentences:
            for word in sentence.lower().split():
                if word not in stop_words:
                    freq_word[word] = freq_word.get(word, 0) + 1

        sentence_point = {}
        for sentence in cleaned_sentences:
            for word in sentence.lower().split():
                if word in freq_word:
                    sentence_point[sentence] = sentence_point.get(sentence, 0) + freq_word[word]

        sorted_sentences = sorted(sentence_point.items(), key=lambda x: x[1], reverse=True)
        best_sentences = []
        for i in range(n):
            best_sentences.append(sorted_sentences[i][0])

        return best_sentences


        

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
        GutenbergBook.GutenbergID(args.lexdiv)
        with open(f"./cache/book/book{args.lexdiv}.txt", "r", encoding="utf-8") as f:
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
        print(dico)

    if args.summarize:
        file_path = f"./cache/book/book{args.summarize}.txt"
        if not os.path.exists(file_path):
            GutenbergBook.GutenbergID(args.summarize)
        with open (file_path,'r') as f:
            text = f.read()
            sentences = re.split(r'(?<=[.!?])\s+|\.{3}\s+', text)
            
        cleaned_sentences = []
        for element in sentences:
            element.strip()

            element = element.replace("[Illustration]", "").strip()
            

            if re.match(r'^CHAPTER\s+[IVX]+\.$', element):
                continue
            cleaned_sentences.append(element)
        