import urllib.request
import urllib.error
import os

class GutenbergBook:
    def GutenbergID(int:id):  
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
    GutenbergBook.GutenbergID(7)