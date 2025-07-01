import pandas as pd
import numpy as np
import re
import unicodedata


# Load the CSV file
csv_file = r"C:\Users\leobi\Downloads\subset_sample_con_ocr.csv"
df = pd.read_csv(csv_file)


df_ocr = df[["id", "texto_2debate_ocr", "texto_aprobado_pleno_ocr", "objecion_parcial_ocr", 
"objecion_total_ocr", "texto_definitivo_pleno_ocr", "registro_oficial_ocr"]].copy()


def normalize_text(text):
    """Normalize text by removing accents"""
    if not isinstance(text, str):
        return "Text not found"
    text = unicodedata.normalize('NFD', text)
    text = ''.join(c for c in text if unicodedata.category(c) != 'Mn')
    return text

# Clean the text from the 'texto_2debate_ocr' column with comments
def clean_text_2debate(text):
    """Clean the text from the 'texto_2debate_ocr' column."""
    if not isinstance(text, str):
        return "Text not found"

    text_norm = normalize_text(text)

    # --- UPPER LIMITS ---
    upper_patterns = [
        r"(CONSIDERANDO[:|,]?[ \t\r\n]+Que[:,]?)",      # CONSIDERANDO (mayúsculas) seguido de Que (primera mayúscula, opcional , o :)
        r"(Considerando[:|,]?[ \t\r\n]+Que[:,]?)",      # Considerando (primera letra mayúscula) seguido de Que (primera mayúscula, opcional , o :)
        r"((?:Que[:,]?[ \t\r\n]+){2,})",                # dos o más "Que" (primera mayúscula, opcional , o :)
        r"(CONSIDERANDOS[:|,]?[ \t\r\n]+Que[:,]?)",      # CONSIDERANDOS (mayúsculas) seguido de Que (primera mayúscula, opcional , o :)
        r"(Considerandos[:|,]?[ \t\r\n]+Que[:,]?)",
    ]
    idx_upper = None
    found_upper = False
    for pat in upper_patterns:
        match = re.search(pat, text_norm)
        if match:
            idx_upper = match.start()
            found_upper = True
            break

    upper_comment = "" if found_upper else "Upper limit not found\n"

    # If it finds the upper limit, it cuts from that point to the end
    if found_upper:
        text = text[idx_upper:]

    # --- LOWER LIMITS ---
    lower_patterns = [
        r"(DISPOSICION(?:ES)?\s+FINAL(?:ES)?[:|,]?)",   # disposition(s) final (mayúsculas)
        r"(Disposicion(?:es)?\s+Final(?:es)?[:|,]?)",   # disposition(s) final (primera letra mayúscula)
        r"(Disposicion(?:es)?\s+final(?:es)?[:|,]?)",
        r"(DISPOSICION(?:ES)?\s+final(?:es)?[:|,]?)"   # disposition(s) final (primera letra mayúscula)

    ]
    idx_lower = None
    found_lower = False
    for pat in lower_patterns:
        match = re.search(pat, text_norm)
        if match:
            idx_lower = match.start()
            found_lower = True
            break

    lower_comment = "" if found_lower else "Lower limit not found\n"

    # If it finds the lower limit, it cuts from that point to the end
    if found_lower:
        text = text[:idx_lower]

    # Remove leading and trailing whitespace
    text = text.strip()
    return f"{upper_comment}{lower_comment}{text}"


# Apply function to clean the 'texto_2debate_ocr' column
df_ocr["texto_2debate_ocr"] = df_ocr["texto_2debate_ocr"].apply(clean_text_2debate)

# Show results
print(df_ocr[["id", "texto_2debate_ocr"]].head(14))