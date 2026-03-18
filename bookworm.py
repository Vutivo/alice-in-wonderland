import pandas as pd
import argparse
import os
import urllib.request

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
        