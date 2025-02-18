import PyPDF2
import sqlite3
import nltk
from nltk.tokenize import sent_tokenize
import re
from tqdm import tqdm  # For progress bars

# Download required NLTK data
nltk.download('punkt')

def create_database():
    """Create the SQLite database and table."""
    conn = sqlite3.connect('embeddings_psy.db')
    cursor = conn.cursor()

    # Create table with id, chapter, and section_text
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS embeddings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chapter TEXT,
            section_text TEXT
        )
    ''')

    conn.commit()
    return conn, cursor

def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file."""
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ''

        # Extract text from each page
        for page in tqdm(pdf_reader.pages, desc="Extracting PDF"):
            text += page.extract_text()

    return text

def preprocess_text(text):
    """Clean and preprocess the extracted text."""
    # Remove extra whitespace and newlines
    text = re.sub(r'\s+', ' ', text)

    # Remove page numbers (assuming they're standalone numbers)
    text = re.sub(r'\s+\d+\s+', ' ', text)

    # Remove header/footer content (customize based on your PDF)
    text = re.sub(r'(Chapter \d+|Page \d+)', '', text)

    # Remove special characters but keep punctuation
    text = re.sub(r'[^a-zA-Z0-9\s\.,!?;:\'\"-]', '', text)

    return text.strip()

def split_into_chapters(text):
    """Split text into chapters based on chapter markers."""
    # Adjust the chapter pattern based on your book's format
    chapter_pattern = r'Chapter\s+\d+|CHAPTER\s+\d+'
    chapters = re.split(chapter_pattern, text)

    # Remove empty chapters and strip whitespace
    chapters = [ch.strip() for ch in chapters if ch.strip()]
    return chapters

def create_chunks(text, max_chunk_size=1000, overlap=100):
    """
    Create overlapping chunks from text, respecting sentence boundaries.
    Args:
        text: The text to chunk
        max_chunk_size: Maximum chunk size in characters
        overlap: Number of characters to overlap between chunks
    """
    sentences = sent_tokenize(text)
    chunks = []
    current_chunk = []
    current_size = 0

    for sentence in sentences:
        sentence_size = len(sentence)

        if current_size + sentence_size > max_chunk_size and current_chunk:
            # Join the current chunk and add it to chunks
            chunks.append(' '.join(current_chunk))

            # Keep last few sentences for overlap
            overlap_size = 0
            overlap_chunk = []
            for s in reversed(current_chunk):
                if overlap_size + len(s) <= overlap:
                    overlap_chunk.insert(0, s)
                    overlap_size += len(s)
                else:
                    break

            current_chunk = overlap_chunk
            current_size = overlap_size

        current_chunk.append(sentence)
        current_size += sentence_size

    # Add the last chunk if it exists
    if current_chunk:
        chunks.append(' '.join(current_chunk))

    return chunks

def process_book(pdf_path):
    """Main function to process the book and store in database."""
    # Create database
    conn, cursor = create_database()

    try:
        # Extract text from PDF
        print("Extracting text from PDF...")
        raw_text = extract_text_from_pdf(pdf_path)

        # Preprocess the text
        print("Preprocessing text...")
        cleaned_text = preprocess_text(raw_text)

        # Split into chapters
        print("Splitting into chapters...")
        chapters = split_into_chapters(cleaned_text)

        # Process each chapter
        for chapter_num, chapter_text in enumerate(chapters, 1):
            print(f"Processing Chapter {chapter_num}...")

            # Create chunks for the chapter
            chunks = create_chunks(chapter_text)

            # Store chunks in database
            for chunk in chunks:
                cursor.execute(
                    'INSERT INTO embeddings (chapter, section_text) VALUES (?, ?)',
                    (f'Chapter {chapter_num}', chunk)
                )

        # Commit changes
        conn.commit()
        print("Processing complete!")

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        conn.rollback()

    finally:
        conn.close()

# Usage
if __name__ == "__main__":
    pdf_path = r"D:\SRM\4th_Year\Internship\Research\psy\psy2_removed1.pdf"
    process_book(pdf_path)