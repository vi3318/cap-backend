import uuid
import os
from typing import List


def generate_document_id() -> str:
    """Generate a unique document ID"""
    return str(uuid.uuid4())


def validate_file_type(filename: str) -> bool:
    """Validate if file type is supported"""
    allowed_extensions = {'.pdf', '.doc', '.docx', '.txt', '.jpg', '.jpeg', '.png'}
    file_ext = os.path.splitext(filename.lower())[1]
    return file_ext in allowed_extensions


def ensure_directory_exists(directory: str) -> None:
    """Ensure directory exists, create if it doesn't"""
    os.makedirs(directory, exist_ok=True)


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove or replace unsafe characters
    unsafe_chars = '<>:"/\\|?*'
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    return filename


def chunk_text(text: str, chunk_size: int = 1000) -> List[str]:
    """Split text into chunks for processing"""
    words = text.split()
    chunks = []
    current_chunk = []
    current_size = 0
    
    for word in words:
        word_size = len(word) + 1  # +1 for space
        if current_size + word_size > chunk_size and current_chunk:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_size = word_size
        else:
            current_chunk.append(word)
            current_size += word_size
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks 