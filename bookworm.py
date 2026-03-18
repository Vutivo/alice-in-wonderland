import pandas as pd
import argparse
import os
import urllib.request
import urllib.error
import nltk
from nltk.tokenize import word_tokenize
from collections import Counter
import json

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
            print(f"Book {id} downloaded successfully.")
            print("Cleaned in progress")
            GutenbergBook.CleanFile(id,book_name)
            print("Clean finish")


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


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CLI argumets")

# ---------------------------------------------------------------------
#                               Positional
# ---------------------------------------------------------------------

    # parser.add_argument("Book_id", type=int)

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

        os.makedirs("./cache/token", exist_ok=True)
        token_info = os.path.join("./cache/token", f"book{args.lexdiv}.txt")
        
        if os.path.exists(token_info):
            with open(token_info, 'r') as f:
                dico = json.load(f)
        else:
            with open(f"./cache/book/book{args.lexdiv}.txt", "r", encoding="utf-8") as f:
                txt = f.read()
            
            tokens = word_tokenize(txt)
            tok = [t for t in tokens if t.isalpha()]
            counts = Counter(tok)
            
            dico = {}
            dico["tok"] = len(tok)
            dico["typ"] = len(counts)
            dico["hap"] = sum(1 for count in counts.values() if count == 1)
            
            if dico["tok"] > 0:
                dico["ttr"] = dico["typ"] / dico["tok"]
                dico["mwl"] = sum(len(word) for word in tok) / dico["tok"]
            if dico["typ"] > 0:
                dico["mwf"] = dico["tok"] / dico["typ"]
            
            with open(token_info, 'w') as f:
                json.dump(dico, f)
        
        print(dico)
        
        
       
    