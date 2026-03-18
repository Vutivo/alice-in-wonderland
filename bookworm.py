import urllib.request
import urllib.error

class GutenbergBook:
    def GutenbergURL(id):
        url = f"https://www.gutenberg.org/cache/epub/{id}/pg{id}.txt"
        try:

            urllib.request.urlretrieve(url, "file.txt")
            print(f"Book {id} downloaded successfully.")


        except urllib.error.URLError as e:
            print(f"Failed to download book: {e}")

        except urllib.error.HTTPError as e:
            print(f"Failed to download book: {e}")


