import urllib.request
import urllib.error

class GutenbergBook:
    def GutenbergURL(id):
        url = f"https://www.gutenberg.org/cache/epub/{id}/pg{id}.txt"
        try:
            book_name =f"book{id}.txt" 
            urllib.request.urlretrieve(url, book_name)
            print(f"Book {id} downloaded successfully.")

            GutenbergBook.CleanFile(id,book_name)


        except urllib.error.URLError as e:
            print(f"Failed to download book: {e}")

        except urllib.error.HTTPError as e:
            print(f"Failed to download book: {e}")


    def CleanFile(id ,file_path):
        line_file = []
        start_book = 0
        end_book = 0
        with open(file_path,'r') as file:
            for index, line in enumerate(file):
                if line.startswith("*** START OF THE PROJECT GUTENBERG EBOOK"):
                   print(f"le livre commence à {index}")
                   start_book = index +1
                if line.startswith("*** END OF THE PROJECT GUTENBERG EBOOK"):
                    print(f"le livre se fini à {index}")
                    end_book = index
                line_file.append(line)
            cleaned_lines = line_file[start_book:end_book]
        with open(file_path,'w') as file:
           for line in cleaned_lines:
               file.write(line)


if __name__ == "__main__":
    ...
  