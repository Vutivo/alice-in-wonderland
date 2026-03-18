import pandas as pd
import argparse
import os
import urllib.request
import nltk
from nltk.tokenize import word_tokenize
from collections import Counter

urllib.request.urlretrieve("https://www.gutenberg.org/cache/epub/feeds/pg_catalog.csv", "pg_catalog.csv") # Allows you to download a CSV via a link

def main():

    parser = argparse.ArgumentParser(description="CLI argumets")

# ---------------------------------------------------------------------
#                               Positional
# ---------------------------------------------------------------------

    parser.add_argument("Book_id", type=int)

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
        dico = {}
        with open("KenanPart", "r", encoding="utf-8") as f:
            txt = f.read()
        tokens = word_tokenize(txt)
        tok = [t for t in tokens if t.isalpha()]
        dico["tok"] = len(tok)
        dico["typ"] = len(set(tok)) # Set() is same as .unique() in pandas
        dico["hap"] = sum(1 for word in set(tok) if tok.count(word) == 1) # Allows you to keep only the words who appears only one time 
        if dico["tok"]>0:
            dico["ttr"] = dico["typ"] / dico["tok"] 
            dico["mwl"] = sum(len(word) for word in tok) / dico["tok"]
        if dico["typ"]>0:
            dico["mwf"] = dico["tok"] / dico["typ"]     
        print(dico)