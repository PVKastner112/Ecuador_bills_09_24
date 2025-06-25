#Downloads PDFs from a DataFrame containing URLs and saves them to a specified directory.
import os
import requests
from tqdm import tqdm
import pandas as pd

csv_path = '/content/drive/MyDrive/Colab Notebooks/cleaned_merge_df.csv' # Adjust the path to your CSV file
# Load the DataFrame from the CSV file
df_clean = pd.read_csv(csv_path)
len(df_clean)
df_clean.columns.tolist()
#From now on we work with the subset of bills approved after 2nd debate
df_subset = df_clean[(df_clean['texto_aprobado_pleno_pdf_presente'] == 1) & ((df_clean['objecion_parcial_pdf_presente'] == 1) | (df_clean['objecion_total_pdf_presente'] == 1))]
len(df_subset)



#Function to download pdfs
def download_pdfs(df, csv_path):
    base_dir = os.path.dirname(os.path.abspath(csv_path))
    dir_path = os.path.join(base_dir, 'pdfs')
    os.makedirs(dir_path, exist_ok=True)

    pdf_columns = [
        'texto_2debate',
        'texto_aprobado_pleno', 'objecion_parcial', 'objecion_total',
        'texto_definitivo_pleno', 'registro_oficial'
    ]


    tasks = []
    for _, row in df.iterrows():
        for column in pdf_columns:
            flag_col = f"{column}_pdf_presente"
            if row.get(flag_col, 0) == 1:
                tasks.append((row, column))


    for row, column in tqdm(tasks, desc="Downloading PDFs"):
        pdf_url   = row[column]
        file_name = f"{row['id']}_{column}.pdf"
        file_path = os.path.join(dir_path, file_name)

        try:

            resp = requests.get(pdf_url, stream=True)
            resp.raise_for_status()
            with open(file_path, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
        except requests.exceptions.RequestException as e:
            tqdm.write(f"Error downloading {file_name}: {e}")

