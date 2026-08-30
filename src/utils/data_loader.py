import pandas as pd

def load_transcripts(file_path: str = "data/transcripts.xlsx") -> pd.DataFrame:
    """
    Load transcripts dataset
    """
    df = pd.read_excel(file_path)
    return df