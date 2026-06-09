from datasnap.loaders.detect import load_file, supported_formats
from datasnap.loaders.csv_loader import load_csv
from datasnap.loaders.json_loader import load_json

__all__ = ["load_file", "load_csv", "load_json", "supported_formats"]
