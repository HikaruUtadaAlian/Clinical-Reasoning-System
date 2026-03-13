import json
from pathlib import Path
from typing import List, Dict, Any


def load_jsonl(filepath: str) -> List[Dict[str, Any]]:
    """Load a JSONL file and return a list of dicts."""
    records = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def load_json(filepath: str) -> Any:
    """Load a JSON file and return the parsed object."""
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)
