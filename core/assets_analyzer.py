from pathlib import Path
from utils.helpers import get_image_extensions, get_audio_extensions, get_video_extensions

def analyse_assets(project_directory: Path) -> dict:
    """Analyse multimedia files inside the project's assets/ folder."""
    result = {
        "total_assets": 0,
        "image_assets": 0,
        "audio_assets": 0,
        "video_assets": 0,
        "other_assets": 0,
        "asset_file_names": [],
        "image_filenames": [],
        "audio_filenames": [],
        "video_filenames": [],
    }
    assets_dir = project_directory / "assets"
    if not assets_dir.exists() or not assets_dir.is_dir():
        return result

    for file_path in assets_dir.iterdir():
        if not file_path.is_file():
            continue
        ext = file_path.suffix.lower()
        result["total_assets"] += 1
        result["asset_file_names"].append(file_path.name)

        if ext in get_image_extensions():
            result["image_assets"] += 1
            result["image_filenames"].append(file_path.name)
        elif ext in get_audio_extensions():
            result["audio_assets"] += 1
            result["audio_filenames"].append(file_path.name)
        elif ext in get_video_extensions():
            result["video_assets"] += 1
            result["video_filenames"].append(file_path.name)
        else:
            result["other_assets"] += 1

    return result