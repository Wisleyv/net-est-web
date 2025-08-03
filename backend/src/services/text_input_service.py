"""Text Input Service for NET-EST System
Handles text preprocessing, file processing, and validation
"""

import base64
import logging
import os
import re
import tempfile
from pathlib import Path


# Document processing libraries
try:
    import docx
    from docx import Document

    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    from odf import teletype
    from odf import text as odf_text
    from odf.opendocument import load

    ODT_AVAILABLE = True
except ImportError:
    ODT_AVAILABLE = False

try:
    import pdfplumber
    import pypdf  # Migrated from PyPDF2 to pypdf

    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

from ..models.text_input import (
    FileType,
    FileUploadInfo,
    InputType,
    ProcessedText,
    TextInputRequest,
    TextInputResponse,
    TextValidationResult,
)


logger = logging.getLogger(__name__)


class TextInputService:
    """Service for processing text inputs and file uploads"""

    # Text processing limits
    MAX_CHARS = 50000
    MAX_PARAGRAPHS = 500
    WARNING_CHARS = 25000
    WARNING_PARAGRAPHS = 250

    # File size limits (bytes)
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    WARNING_FILE_SIZE = 5 * 1024 * 1024  # 5MB

    def __init__(self):
        self.supported_formats = self._check_supported_formats()
        logger.info(
            f"TextInputService initialized with formats: {list(self.supported_formats.keys())}"
        )

    def _check_supported_formats(self) -> dict[str, bool]:
        """Check which file formats are supported based on available libraries"""
        return {
            "txt": True,
            "md": True,
            "docx": DOCX_AVAILABLE,
            "odt": ODT_AVAILABLE,
            "pdf": PDF_AVAILABLE,
        }

    def validate_text_input(self, text: str) -> TextValidationResult:
        """Validate text input and provide recommendations"""
        char_count = len(text)
        word_count = len(text.split())
        paragraph_count = len([p for p in text.split("\n\n") if p.strip()])

        warnings = []
        errors = []
        recommendations = []

        # Character limit validation
        if char_count > self.MAX_CHARS:
            errors.append(f"Text exceeds maximum limit of {self.MAX_CHARS:,} characters")
        elif char_count > self.WARNING_CHARS:
            warnings.append(
                f"Large text detected ({char_count:,} characters). Processing may take longer."
            )

        # Paragraph limit validation
        if paragraph_count > self.MAX_PARAGRAPHS:
            errors.append(
                f"Too many paragraphs ({paragraph_count}). Maximum: {self.MAX_PARAGRAPHS}"
            )
        elif paragraph_count > self.WARNING_PARAGRAPHS:
            warnings.append(
                f"Many paragraphs detected ({paragraph_count}). Consider breaking into smaller sections."
            )

        # Content recommendations
        if char_count < 100:
            recommendations.append(
                "Text is very short. Consider adding more content for better analysis."
            )

        if paragraph_count < 2:
            recommendations.append(
                "Single paragraph detected. Multi-paragraph texts provide richer analysis."
            )

        return TextValidationResult(
            is_valid=len(errors) == 0,
            character_count=char_count,
            word_count=word_count,
            paragraph_count=paragraph_count,
            warnings=warnings,
            errors=errors,
            processing_recommendations=recommendations,
        )

    def clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""

        # Remove excessive whitespace
        text = re.sub(r"\s+", " ", text)

        # Normalize line breaks
        text = re.sub(r"\r\n|\r", "\n", text)

        # Remove excessive line breaks but preserve paragraph structure
        text = re.sub(r"\n{3,}", "\n\n", text)

        # Strip leading/trailing whitespace
        text = text.strip()

        return text

    def segment_paragraphs(self, text: str) -> list[str]:
        """Segment text into paragraphs"""
        if not text:
            return []

        # Split by double line breaks
        paragraphs = text.split("\n\n")

        # Clean and filter empty paragraphs
        paragraphs = [p.strip() for p in paragraphs if p.strip()]

        return paragraphs

    def extract_text_from_file(
        self, file_content: str, file_type: FileType, file_name: str
    ) -> tuple[str, list[str]]:
        """Extract text content from uploaded file"""
        warnings = []

        try:
            # Decode base64 content
            file_data = base64.b64decode(file_content)

            if file_type == FileType.TXT:
                # Try different encodings for text files
                for encoding in ["utf-8", "latin-1", "cp1252"]:
                    try:
                        text = file_data.decode(encoding)
                        break
                    except UnicodeDecodeError:
                        continue
                else:
                    raise ValueError("Could not decode text file with supported encodings")

            elif file_type == FileType.MD:
                text = file_data.decode("utf-8")

            elif file_type == FileType.DOCX:
                if not DOCX_AVAILABLE:
                    raise ValueError("DOCX processing not available. Install python-docx package.")

                tmp_file = None
                try:
                    tmp_file = tempfile.NamedTemporaryFile(suffix=".docx", delete=False)
                    tmp_file.write(file_data)
                    tmp_file.flush()
                    tmp_file.close()  # Close file handle before processing

                    doc = Document(tmp_file.name)
                    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
                    text = "\n\n".join(paragraphs)
                finally:
                    # Robust cleanup with retry mechanism for Windows
                    if tmp_file and hasattr(tmp_file, "name"):
                        import time

                        for attempt in range(3):
                            try:
                                if os.path.exists(tmp_file.name):
                                    os.unlink(tmp_file.name)
                                break
                            except (OSError, PermissionError) as e:
                                if attempt < 2:
                                    time.sleep(0.1)
                                    continue
                                else:
                                    logger.warning(
                                        f"Could not delete temporary DOCX file {tmp_file.name}: {e}"
                                    )

            elif file_type == FileType.ODT:
                if not ODT_AVAILABLE:
                    raise ValueError("ODT processing not available. Install odfpy package.")

                tmp_file = None
                try:
                    tmp_file = tempfile.NamedTemporaryFile(suffix=".odt", delete=False)
                    tmp_file.write(file_data)
                    tmp_file.flush()
                    tmp_file.close()  # Close file handle before processing

                    doc = load(tmp_file.name)
                    paragraphs = []
                    for p in doc.getElementsByType(odf_text.P):
                        paragraph_text = teletype.extractText(p)
                        if paragraph_text.strip():
                            paragraphs.append(paragraph_text)
                    text = "\n\n".join(paragraphs)
                finally:
                    # Robust cleanup with retry mechanism for Windows
                    if tmp_file and hasattr(tmp_file, "name"):
                        import time

                        for attempt in range(3):
                            try:
                                if os.path.exists(tmp_file.name):
                                    os.unlink(tmp_file.name)
                                break
                            except (OSError, PermissionError) as e:
                                if attempt < 2:
                                    time.sleep(0.1)
                                    continue
                                else:
                                    logger.warning(
                                        f"Could not delete temporary ODT file {tmp_file.name}: {e}"
                                    )

            elif file_type == FileType.PDF:
                if not PDF_AVAILABLE:
                    raise ValueError(
                        "PDF processing not available. Install pypdf and pdfplumber packages."
                    )

                import gc
                import uuid

                # Create unique temporary file path
                temp_dir = tempfile.gettempdir()
                temp_filename = f"pdf_extract_{uuid.uuid4().hex}.pdf"
                temp_path = os.path.join(temp_dir, temp_filename)

                try:
                    # Write file data directly to temporary path
                    with open(temp_path, "wb") as temp_file:
                        temp_file.write(file_data)

                    # Try pdfplumber first (better text extraction)
                    text = ""
                    try:
                        import pdfplumber

                        with pdfplumber.open(temp_path) as pdf:
                            pages_text = []
                            for page in pdf.pages:
                                page_text = page.extract_text()
                                if page_text:
                                    pages_text.append(page_text)
                            text = "\n\n".join(pages_text)
                        # Explicitly delete references and force garbage collection
                        del pdf
                        gc.collect()
                    except Exception as e:
                        logger.warning(f"pdfplumber failed: {e}, trying pypdf")
                        # Fallback to pypdf (successor to PyPDF2)
                        try:
                            import pypdf

                            with open(temp_path, "rb") as pdf_file:
                                pdf_reader = pypdf.PdfReader(pdf_file)
                                pages_text = []
                                for page in pdf_reader.pages:
                                    page_text = page.extract_text()
                                    if page_text:
                                        pages_text.append(page_text)
                                text = "\n\n".join(pages_text)
                            # Explicitly delete references and force garbage collection
                            del pdf_reader, pdf_file
                            gc.collect()
                        except Exception as pdf_error:
                            raise Exception(
                                f"Both PDF libraries failed. pdfplumber: {e}, pypdf: {pdf_error}"
                            )

                finally:
                    # Robust cleanup with multiple strategies for Windows
                    if os.path.exists(temp_path):
                        import gc
                        import time

                        # Force garbage collection to release any remaining references
                        gc.collect()

                        # Multiple cleanup attempts with increasing delays
                        for attempt in range(5):  # Increased to 5 attempts
                            try:
                                os.unlink(temp_path)
                                break
                            except (OSError, PermissionError) as e:
                                if attempt < 4:  # Not the last attempt
                                    # Progressively longer delays
                                    delay = 0.1 * (2**attempt)  # 0.1, 0.2, 0.4, 0.8 seconds
                                    time.sleep(delay)
                                    gc.collect()  # Force GC on each retry
                                    continue
                                else:
                                    logger.warning(
                                        f"Could not delete temporary PDF file {temp_path}: {e}"
                                    )
                                    # As last resort, try to schedule deletion on next boot (Windows)
                                    try:
                                        import subprocess

                                        subprocess.run(
                                            [
                                                "schtasks",
                                                "/create",
                                                "/tn",
                                                f"DeleteTempPDF_{uuid.uuid4().hex[:8]}",
                                                "/tr",
                                                f'del "{temp_path}"',
                                                "/sc",
                                                "onstart",
                                                "/ru",
                                                "SYSTEM",
                                            ],
                                            capture_output=True,
                                            check=False,
                                        )
                                    except:
                                        pass  # Silent fail for cleanup scheduling

                if not text.strip():
                    warnings.append(
                        "PDF text extraction resulted in empty content. File may contain images or be password protected."
                    )

            else:
                raise ValueError(f"Unsupported file type: {file_type}")

            return text, warnings

        except Exception as e:
            logger.error(f"Error extracting text from {file_type} file '{file_name}': {str(e)}")
            raise ValueError(f"Failed to process {file_type.upper()} file: {str(e)}")

    def get_file_info(self, file_name: str, file_size: int) -> FileUploadInfo:
        """Get information about uploaded file"""
        file_ext = Path(file_name).suffix.lower().lstrip(".")

        try:
            file_type_enum = FileType(file_ext)
        except ValueError:
            return FileUploadInfo(
                file_name=file_name,
                file_size=file_size,
                file_type=FileType.TXT,  # Default to TXT to avoid type errors
                supported=False,
                warnings=[f"Unsupported file format: {file_ext}"],
            )

        warnings = []
        supported = self.supported_formats.get(file_ext, False)

        if not supported:
            warnings.append(f"File format {file_ext.upper()} is not supported in this installation")

        if file_size > self.MAX_FILE_SIZE:
            warnings.append(
                f"File size ({file_size:,} bytes) exceeds maximum limit ({self.MAX_FILE_SIZE:,} bytes)"
            )
            supported = False
        elif file_size > self.WARNING_FILE_SIZE:
            warnings.append(
                f"Large file detected ({file_size:,} bytes). Processing may take longer."
            )

        # Estimate processing time based on file size and type
        estimated_time = None
        if supported:
            if file_type_enum == FileType.PDF:
                estimated_time = max(
                    2.0, file_size / (1024 * 1024) * 3
                )  # ~3 seconds per MB for PDF
            elif file_type_enum in [FileType.DOCX, FileType.ODT]:
                estimated_time = max(
                    1.0, file_size / (1024 * 1024) * 2
                )  # ~2 seconds per MB for documents
            else:
                estimated_time = max(0.5, file_size / (1024 * 1024))  # ~1 second per MB for text

        return FileUploadInfo(
            file_name=file_name,
            file_size=file_size,
            file_type=file_type_enum,
            supported=supported,
            estimated_processing_time=estimated_time,
            warnings=warnings,
        )

    async def process_text_input(self, request: TextInputRequest) -> TextInputResponse:
        """Process text input request and return cleaned, segmented text"""
        try:
            warnings = []
            source_text = ""
            target_text = ""

            # Handle file input
            if request.input_type == InputType.FILE:
                if not all([request.file_content, request.file_name, request.file_type]):
                    return TextInputResponse(
                        success=False,
                        errors=["File input requires file_content, file_name, and file_type"],
                    )

                # Check if file type is supported
                if request.file_type and not self.supported_formats.get(
                    request.file_type.value, False
                ):
                    return TextInputResponse(
                        success=False,
                        errors=[f"File format {request.file_type.value.upper()} is not supported"],
                    )

                # Extract text from file
                try:
                    if request.file_content and request.file_type and request.file_name:
                        extracted_text, file_warnings = self.extract_text_from_file(
                            request.file_content, request.file_type, request.file_name
                        )
                        warnings.extend(file_warnings)

                        # For file input, use extracted text as source
                        # Target text can be provided separately or be the same
                        source_text = extracted_text
                        target_text = request.target_text or extracted_text

                except Exception as e:
                    return TextInputResponse(
                        success=False, errors=[f"Failed to process file: {str(e)}"]
                    )

            # Handle typed input
            elif request.input_type == InputType.TYPED:
                if not request.source_text:
                    return TextInputResponse(
                        success=False, errors=["Typed input requires source_text"]
                    )

                source_text = request.source_text
                target_text = request.target_text or ""

                if not target_text:
                    warnings.append("No target text provided. Using source text as target.")
                    target_text = source_text

            else:
                return TextInputResponse(
                    success=False, errors=[f"Invalid input type: {request.input_type}"]
                )

            # Validate texts
            source_validation = self.validate_text_input(source_text)
            target_validation = self.validate_text_input(target_text)

            if not source_validation.is_valid:
                return TextInputResponse(
                    success=False,
                    errors=[
                        f"Source text validation failed: {'; '.join(source_validation.errors)}"
                    ],
                )

            if not target_validation.is_valid:
                return TextInputResponse(
                    success=False,
                    errors=[
                        f"Target text validation failed: {'; '.join(target_validation.errors)}"
                    ],
                )

            # Collect validation warnings
            warnings.extend(source_validation.warnings)
            warnings.extend(target_validation.warnings)

            # Clean texts
            clean_source = self.clean_text(source_text)
            clean_target = self.clean_text(target_text)

            # Segment into paragraphs
            source_paragraphs = self.segment_paragraphs(clean_source)
            target_paragraphs = self.segment_paragraphs(clean_target)

            # Create processed text result
            processed_text = ProcessedText(
                source_text=clean_source,
                target_text=clean_target,
                source_paragraphs=source_paragraphs,
                target_paragraphs=target_paragraphs,
                metadata={
                    "source_stats": {
                        "characters": source_validation.character_count,
                        "words": source_validation.word_count,
                        "paragraphs": len(source_paragraphs),
                    },
                    "target_stats": {
                        "characters": target_validation.character_count,
                        "words": target_validation.word_count,
                        "paragraphs": len(target_paragraphs),
                    },
                    "processing": {
                        "input_type": request.input_type.value,
                        "file_type": request.file_type.value if request.file_type else None,
                        "file_name": request.file_name,
                    },
                },
            )

            return TextInputResponse(
                success=True,
                processed_text=processed_text,
                warnings=warnings,
                metadata={
                    "processing_time": "calculated_later",
                    "supported_formats": list(self.supported_formats.keys()),
                },
            )

        except Exception as e:
            logger.error(f"Error processing text input: {str(e)}")
            return TextInputResponse(success=False, errors=[f"Internal processing error: {str(e)}"])
