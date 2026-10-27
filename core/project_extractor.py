import zipfile
import tempfile
from pathlib import Path

def extract_project(archive_path: Path) -> Path:
    """Extract the .aia ZIP archive to a temporary directory."""
    temp_directory = Path(tempfile.mkdtemp(prefix="dr_appinventor_"))
    with zipfile.ZipFile(archive_path, "r") as zip_file:
        zip_file.extractall(temp_directory)
    return temp_directory