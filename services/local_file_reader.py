"""Local file reader service implementation."""
import os
from typing import List
from pathlib import Path
import docx
import openpyxl

from interfaces import ILocalFileReader, IVisionAnalyzer
from models.data_models import Document, DocumentType


class LocalFileReader(ILocalFileReader):
    """Service for reading local files and directories."""

    # Supported file extensions
    IMAGE_EXTENSIONS = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg', '.webp'}
    DIAGRAM_EXTENSIONS = {'.drawio'}
    DOCUMENT_EXTENSIONS = {'.docx', '.doc'}
    SPREADSHEET_EXTENSIONS = {'.xlsx', '.xls'}

    def __init__(self, vision_analyzer: IVisionAnalyzer = None):
        """
        Initialize the local file reader.

        Args:
            vision_analyzer: Optional vision analyzer for processing images
        """
        self.vision_analyzer = vision_analyzer

    def read_directory(self, directory_path: str) -> List[Document]:
        """
        Read all supported files from a directory recursively.

        Args:
            directory_path: Path to the directory

        Returns:
            List of Document objects
        """
        documents = []
        directory = Path(directory_path)

        if not directory.exists():
            print(f"Warning: Directory {directory_path} does not exist")
            return documents

        print(f"Scanning directory: {directory_path}")

        # Walk through all files recursively
        for file_path in directory.rglob('*'):
            if file_path.is_file():
                try:
                    document = self.read_file(str(file_path))
                    if document:
                        documents.append(document)
                        print(f"Processed: {file_path.name}")
                except Exception as e:
                    print(f"Error processing {file_path}: {str(e)}")

        print(f"Total files processed: {len(documents)}")
        return documents

    def read_file(self, file_path: str) -> Document:
        """
        Read a single file.

        Args:
            file_path: Path to the file

        Returns:
            Document object or None if file type not supported
        """
        path = Path(file_path)
        extension = path.suffix.lower()

        # Determine file type and process accordingly
        if extension in self.IMAGE_EXTENSIONS:
            return self._process_image(file_path)
        elif extension in self.DIAGRAM_EXTENSIONS:
            return self._process_diagram(file_path)
        elif extension in self.DOCUMENT_EXTENSIONS:
            return self._process_word_document(file_path)
        elif extension in self.SPREADSHEET_EXTENSIONS:
            return self._process_spreadsheet(file_path)
        else:
            # Skip unsupported file types
            return None

    def _process_image(self, file_path: str) -> Document:
        """Process image files using Vision API."""
        if not self.vision_analyzer:
            return Document(
                content=f"Image file: {os.path.basename(file_path)} (Vision API not configured)",
                file_path=file_path,
                repository_url="local",
                document_type=DocumentType.IMAGE,
                metadata={"source": "local_directory", "file_type": "image"}
            )

        # Use Vision API to analyze the image
        summary = self.vision_analyzer.generate_summary(file_path)

        return Document(
            content=summary,
            file_path=file_path,
            repository_url="local",
            document_type=DocumentType.IMAGE,
            metadata={
                "source": "local_directory",
                "file_type": "image",
                "analyzed_by": "google_vision_api"
            }
        )

    def _process_diagram(self, file_path: str) -> Document:
        """Process diagram files (.drawio)."""
        # For .drawio files, try to read as XML text
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # If there's a corresponding .png file, also analyze it
            png_path = file_path + '.png'
            if os.path.exists(png_path) and self.vision_analyzer:
                vision_summary = self.vision_analyzer.generate_summary(png_path)
                content = f"Diagram File: {os.path.basename(file_path)}\n\n--- Visual Analysis ---\n{vision_summary}\n\n--- Source XML ---\n{content}"
            else:
                content = f"Diagram File: {os.path.basename(file_path)}\n\n{content}"

            return Document(
                content=content,
                file_path=file_path,
                repository_url="local",
                document_type=DocumentType.DRAWIO,
                metadata={
                    "source": "local_directory",
                    "file_type": "drawio",
                    "has_png_export": os.path.exists(png_path)
                }
            )
        except Exception as e:
            return Document(
                content=f"Diagram file: {os.path.basename(file_path)} (Error reading: {str(e)})",
                file_path=file_path,
                repository_url="local",
                document_type=DocumentType.DRAWIO,
                metadata={"source": "local_directory", "file_type": "drawio", "error": str(e)}
            )

    def _process_word_document(self, file_path: str) -> Document:
        """Process Word documents (.docx, .doc)."""
        try:
            # Only .docx is supported by python-docx
            if file_path.endswith('.docx'):
                doc = docx.Document(file_path)
                content = []

                # Extract paragraphs
                for paragraph in doc.paragraphs:
                    if paragraph.text.strip():
                        content.append(paragraph.text)

                # Extract tables
                for table in doc.tables:
                    for row in table.rows:
                        row_text = ' | '.join([cell.text for cell in row.cells])
                        if row_text.strip():
                            content.append(row_text)

                full_content = f"Word Document: {os.path.basename(file_path)}\n\n" + "\n".join(content)

                return Document(
                    content=full_content,
                    file_path=file_path,
                    repository_url="local",
                    document_type=DocumentType.WORD_DOCUMENT,
                    metadata={
                        "source": "local_directory",
                        "file_type": "word_document",
                        "paragraph_count": len(doc.paragraphs),
                        "table_count": len(doc.tables)
                    }
                )
            else:
                return Document(
                    content=f"Word document: {os.path.basename(file_path)} (.doc format not supported, only .docx)",
                    file_path=file_path,
                    repository_url="local",
                    document_type=DocumentType.WORD_DOCUMENT,
                    metadata={"source": "local_directory", "file_type": "word_document"}
                )
        except Exception as e:
            return Document(
                content=f"Word document: {os.path.basename(file_path)} (Error reading: {str(e)})",
                file_path=file_path,
                repository_url="local",
                document_type=DocumentType.WORD_DOCUMENT,
                metadata={"source": "local_directory", "file_type": "word_document", "error": str(e)}
            )

    def _process_spreadsheet(self, file_path: str) -> Document:
        """Process spreadsheet files (.xlsx, .xls)."""
        try:
            workbook = openpyxl.load_workbook(file_path, data_only=True)
            content = [f"Spreadsheet: {os.path.basename(file_path)}\n"]

            for sheet_name in workbook.sheetnames:
                sheet = workbook[sheet_name]
                content.append(f"\n--- Sheet: {sheet_name} ---")

                # Read up to 100 rows to avoid too much data
                max_rows = min(sheet.max_row, 100)
                for row_idx, row in enumerate(sheet.iter_rows(max_row=max_rows, values_only=True), 1):
                    row_text = ' | '.join([str(cell) if cell is not None else '' for cell in row])
                    if row_text.strip():
                        content.append(row_text)

                if sheet.max_row > 100:
                    content.append(f"... (Truncated, total rows: {sheet.max_row})")

            full_content = "\n".join(content)

            return Document(
                content=full_content,
                file_path=file_path,
                repository_url="local",
                document_type=DocumentType.SPREADSHEET,
                metadata={
                    "source": "local_directory",
                    "file_type": "spreadsheet",
                    "sheet_count": len(workbook.sheetnames),
                    "sheet_names": workbook.sheetnames
                }
            )
        except Exception as e:
            return Document(
                content=f"Spreadsheet: {os.path.basename(file_path)} (Error reading: {str(e)})",
                file_path=file_path,
                repository_url="local",
                document_type=DocumentType.SPREADSHEET,
                metadata={"source": "local_directory", "file_type": "spreadsheet", "error": str(e)}
            )

