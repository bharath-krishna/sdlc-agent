import pathlib

_SKILLS_DIR = pathlib.Path(__file__).parent.parent.parent / "skills"


def list_skills() -> dict:
    """List all available skill names (filenames in the skills directory)."""
    try:
        files = [f.name for f in _SKILLS_DIR.iterdir() if f.is_file()]
        return {"skills": sorted(files)}
    except Exception as e:
        return {"error": str(e)}


def get_skill(filename: str) -> dict:
    """
    Return the content of a skill file by filename.

    Args:
        filename: The skill filename (e.g. "sdlc_cycle.md")

    Returns:
        Dictionary with the skill content, or an error if not found.
    """
    skill_path = (_SKILLS_DIR / filename).resolve()
    if skill_path.parent != _SKILLS_DIR.resolve():
        return {"error": "Invalid filename"}
    try:
        return {"skill": skill_path.read_text()}
    except FileNotFoundError:
        available = [f.name for f in _SKILLS_DIR.iterdir() if f.is_file()]
        return {"error": f"Skill '{filename}' not found. Available: {available}"}
    except Exception as e:
        return {"error": str(e)}
