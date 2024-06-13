import re

# Path to the file containing the data
file_path = r'C:/Users/zyd47/Downloads/知轩藏书tree.txt'

# Regular expression to match lines with non-zero file size, book title, and author
pattern = re.compile(r'^\s*(\d+)\s+\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}\s+.*?/《(.*?)》（.*?）作者：(.*?)\/', re.MULTILINE)

# Function to read file and extract data
def extract_books(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = file.read()

    books = []
    max_author_length = 0  # Variable to store the maximum length of author name
    for match in pattern.finditer(data):
        size, title, author = match.groups()
        if int(size) > 0:  # Skip entries with a file size of zero
            size_mb = int(size) / (1024 * 1024)  # Convert size to MB
            author_length = len(author)
            if author_length > max_author_length:
                max_author_length = author_length
            books.append({'Title': title, 'Author': author, 'Length': size_mb})

    return books, max_author_length

# Extracting and displaying the data
books, max_author_length = extract_books(file_path)
for book in books:
    print(f"Title: {book['Title']}, Author: {book['Author']} Length: {book['Length']:.2f} MB")
    with open('output.txt', 'a', encoding='utf-8') as file:
        file.write(f"{book['Title']}, {book['Author']}, {book['Length']:.2f} MB\n")
