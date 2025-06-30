""" Scrape_bills:
* This file contains code to create a dataframe called 'clean_dataframe' 
* with data about all the bills introduced to the Ecuadorian national Assembly 
* in the 2009-2014 period. Each observation is a bill across all the possible 
* legislative stages and contains a link to download the corresponding pdf document 
* for each available stage. """

# ============================
# Install and import necessary libraries
# ============================
# !pip install webdriver-manager pandas numpy tqdm beautifulsoup4

import pandas as pd
import time
import os
import numpy as np
from tqdm.auto import tqdm


import selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from bs4 import BeautifulSoup
# =============================


# ============================
# Configure the webdriver
# ============================
options = webdriver.ChromeOptions()
options.add_argument('--no-sandbox')
options.add_argument('--headless')
options.add_argument('--disable-dev-shm-usage')
# =============================


# =============================
# Load URL and data scraping 
# =============================
# URL to scrape
url = 'https://leyes.asambleanacional.gob.ec/'

df = pd.read_csv('/content/pley.csv', sep=';') # Adjust the path to your CSV file
# Create a new dataframe to store the results
df_doc = pd.DataFrame(columns=["Proyecto de Ley", "Informe de Primer Debate de la Comisión",
                               "Informe de Segundo Debate de la Comisión",
                               "Texto aprobado por el Pleno",
                               "Objeción Parcial del Ejecutivo",
                               "Objeción Total del Ejecutivo", "Texto definitivo aprobado por el Pleno",
                               "Registro Oficial"])

driver = webdriver.Chrome(options=options)
driver.get(url)

avanzar_pagina()

merge_df = pd.concat([df, df_doc], axis=1)
merge_df.to_csv('merge_df.csv', index=False)
files.download('merge_df.csv')
df_doc.tail(10)

# -------------------------------

# Funcion para clickear en todas las lupas de una pagina y cerrar ventana emergente despeus de extraer e insertar datos
def click_todas_lupa():
    try:
      lupa_botones = WebDriverWait(driver, 10).until(
          EC.presence_of_all_elements_located((By.XPATH, '//*[contains(concat( " ", @class, " " ), concat( " ", "pi-search", " " ))]'))
      )
      print("Comenzando extraccion de pdfs")
      for i, boton in enumerate(lupa_botones):
        try:
          print("Fila " + str(i + 1) + "/10 ")
          if boton.is_enabled():
            boton.click()

            extraer_pdfs()

            close_buttons = driver.find_elements(By.XPATH, '//*[contains(concat( " ", @class, " " ), concat( " ", "ui-icon-closethick", " " ))]')
            for close_button in close_buttons:
                if close_button.is_displayed() and close_button.is_enabled():
                    try:
                        close_button.click()
                        break
                    except ElementClickInterceptedException:
                        print("Elemento click interceptado. Intentando de nuevo...")
                        time.sleep(1)
                        close_button.click()
            time.sleep(2)
        except (NoSuchElementException, ElementClickInterceptedException) as e:
          print(f"Error interactuando con lupa {i + 1}: {e}")
    except NoSuchElementException as e:
      print(f"Error encontrando lupas: {e}")

# -------------------------------

# Funcion para extraer todos los pdfs
# Inserta datos obtenidos en dataframe
def extraer_pdfs():
  try:
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.ID, 'proyectosDeLeyForm:projectDetail')
    ))
    new_row = {col: None for col in df_doc.columns}

    extraer_proyecto_ley(new_row)
    extraer_1_debate(new_row)
    extraer_2_debate(new_row)
    extraer_texto_apr_pleno(new_row)
    objecion_parcial(new_row)
    objecion_total(new_row)
    texto_definitivo_pleno(new_row)
    registro_oficial(new_row)

    df_doc.loc[len(df_doc)] = new_row

  except (TimeoutException, NoSuchElementException) as e:
    print(f"Error extrayendo la data: {e}")

# -------------------------------

# Funciones para extraer PDFs por tipo de documento con error  handling
from posixpath import normcase
def extraer_proyecto_ley(row):
  try:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'proyectosDeLeyForm:j_idt77'))
        )
        celda_1debate = driver.find_elements(By.ID, 'proyectosDeLeyForm:j_idt77')
        for celda in celda_1debate:
            try:
                nombre_documento = celda.find_element(By.XPATH, './/div[@class="ui-g-12 ui-md-8 dvDialog"]/label').text
                enlace_pdf = celda.find_element(By.XPATH, './/div[@class="ui-g-12 ui-md-4 dvDialog"]/a').get_attribute("href")
                if nombre_documento in df_doc.columns:
                    row[nombre_documento] = enlace_pdf
                else:
                    print(f"Document name '{nombre_documento}' not found in df_doc columns.")
            except NoSuchElementException:
                print(f"No PDF link found for '{nombre_documento}' in this cell.")
                row[nombre_documento] = None
  except TimeoutException:
      print("Timeout waiting for element with ID 'proyectosDeLeyForm:j_idt77'")
  except NoSuchElementException:
      print("Element with ID 'proyectosDeLeyForm:j_idt77' not found")


def extraer_1_debate(row):
    try:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'proyectosDeLeyForm:j_idt105'))
        )
        celda_1debate = driver.find_elements(By.ID, 'proyectosDeLeyForm:j_idt105')
        for celda in celda_1debate:
            try:
                nombre_documento = celda.find_element(By.XPATH, './/div[@class="ui-g-12 ui-md-8 dvDialog"]/label').text
                enlace_pdf = celda.find_element(By.XPATH, './/div[@class="ui-g-12 ui-md-4 dvDialog"]/a').get_attribute("href")
                if nombre_documento in df_doc.columns:
                    row[nombre_documento] = enlace_pdf
                else:
                    print(f"Document name '{nombre_documento}' not found in df_doc columns.")
            except NoSuchElementException:
                print(f"No PDF link found for '{nombre_documento}' in this cell.")
                row[nombre_documento] = None

    except TimeoutException:
        print("Timeout waiting for element with ID 'proyectosDeLeyForm:j_idt105'")
    except NoSuchElementException:
        print("Element with ID 'proyectosDeLeyForm:j_idt105' not found")


def extraer_2_debate(row):
    try:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'proyectosDeLeyForm:j_idt112'))
        )
        celda_2debate = driver.find_elements(By.ID, 'proyectosDeLeyForm:j_idt112')
        for celda in celda_2debate:
          try:
            nombre_documento = celda.find_element(By.XPATH, './/div[@class="ui-g-12 ui-md-8 dvDialog"]/label').text
            enlace_pdf = celda.find_element(By.XPATH, './/div[@class="ui-g-12 ui-md-4 dvDialog"]/a').get_attribute("href")
            if nombre_documento in df_doc.columns:
              row[nombre_documento] = enlace_pdf
            else:
              print(f"Document name '{nombre_documento}' not found in df_doc columns.")
          except NoSuchElementException:
            print(f"No PDF link found for '{nombre_documento}' in this cell.")
            row[nombre_documento] = None

    except TimeoutException:
        print("Timeout waiting for element with ID 'proyectosDeLeyForm:j_idt112'")
    except NoSuchElementException:
        print("Element with ID 'proyectosDeLeyForm:j_idt112' not found")


def extraer_texto_apr_pleno(row):
    try:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'proyectosDeLeyForm:j_idt119'))
            )
        celda_aprobado_pleno = driver.find_elements(By.ID, 'proyectosDeLeyForm:j_idt119')
        for celda in celda_aprobado_pleno:
          try:
            nombre_documento = celda.find_element(By.XPATH, './/div[@class="ui-g-12 ui-md-8 dvDialog"]/label').text
            enlace_pdf = celda.find_element(By.XPATH, './/div[@class="ui-g-12 ui-md-4 dvDialog"]/a').get_attribute("href")
            if nombre_documento in df_doc.columns:
              row[nombre_documento] = enlace_pdf
            else:
              print(f"Document name '{nombre_documento}' not found in df_doc columns.")
          except NoSuchElementException:
            print(f"No PDF link found for '{nombre_documento}' in this cell.")
            row[nombre_documento] = None

    except TimeoutException:
        print("Timeout waiting for element with ID 'proyectosDeLeyForm:j_idt119'")
    except NoSuchElementException:
        print("Element with ID 'proyectosDeLeyForm:j_idt119' not found")


def objecion_parcial(row):
    try:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'proyectosDeLeyForm:j_idt133'))
            )
        celda_objecion_parcial = driver.find_elements(By.ID, 'proyectosDeLeyForm:j_idt133')
        for celda in celda_objecion_parcial:
            try:
                nombre_documento = celda.find_element(By.XPATH, './/div[@class="ui-g-12 ui-md-8 dvDialog"]/label').text
                enlace_pdf = celda.find_element(By.XPATH, './/div[@class="ui-g-12 ui-md-4 dvDialog"]/a').get_attribute("href")
                if nombre_documento in df_doc.columns:
                  row[nombre_documento] = enlace_pdf
                else:
                  print(f"Document name '{nombre_documento}' not found in df_doc columns.")
            except NoSuchElementException:
                print(f"No PDF link found for '{nombre_documento}' in this cell.")
                row[nombre_documento] = None

    except TimeoutException:
        print("Timeout waiting for element with ID 'proyectosDeLeyForm:j_idt133'")
    except NoSuchElementException:
        print("Element with ID 'proyectosDeLeyForm:j_idt133' not found")


def objecion_total(row):
    try:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'proyectosDeLeyForm:j_idt126'))
            )
        celda_objecion_parcial = driver.find_elements(By.ID, 'proyectosDeLeyForm:j_idt126')
        for celda in celda_objecion_parcial:
            try:
                nombre_documento = celda.find_element(By.XPATH, './/div[@class="ui-g-12 ui-md-8 dvDialog"]/label').text
                enlace_pdf = celda.find_element(By.XPATH, './/div[@class="ui-g-12 ui-md-4 dvDialog"]/a').get_attribute("href")
                if nombre_documento in df_doc.columns:
                  row[nombre_documento] = enlace_pdf
                else:
                  print(f"Document name '{nombre_documento}' not found in df_doc columns.")
            except NoSuchElementException:
                print(f"No PDF link found for '{nombre_documento}' in this cell.")
                row[nombre_documento] = None

    except TimeoutException:
        print("Timeout waiting for element with ID 'proyectosDeLeyForm:j_idt126'")
    except NoSuchElementException:
        print("Element with ID 'proyectosDeLeyForm:j_idt126' not found")


def texto_definitivo_pleno(row):
    try:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'proyectosDeLeyForm:j_idt147'))
            )
        celda_objecion_parcial = driver.find_elements(By.ID, 'proyectosDeLeyForm:j_idt147')
        for celda in celda_objecion_parcial:
            try:
                nombre_documento = celda.find_element(By.XPATH, './/div[@class="ui-g-12 ui-md-8 dvDialog"]/label').text
                enlace_pdf = celda.find_element(By.XPATH, './/div[@class="ui-g-12 ui-md-4 dvDialog"]/a').get_attribute("href")
                if nombre_documento in df_doc.columns:
                  row[nombre_documento] = enlace_pdf
                else:
                  print(f"Document name '{nombre_documento}' not found in df_doc columns.")
            except NoSuchElementException:
                print(f"No PDF link found for '{nombre_documento}' in this cell.")
                row[nombre_documento] = None

    except TimeoutException:
        print("Timeout waiting for element with ID 'proyectosDeLeyForm:j_idt147'")
    except NoSuchElementException:
        print("Element with ID 'proyectosDeLeyForm:j_idt147' not found")


def registro_oficial(row):
    try:
        WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'proyectosDeLeyForm:j_idt154'))
            )
        celda_objecion_parcial = driver.find_elements(By.ID, 'proyectosDeLeyForm:j_idt154')
        for celda in celda_objecion_parcial:
            try:
                nombre_documento = celda.find_element(By.XPATH, './/div[@class="ui-g-12 ui-md-8 dvDialog"]/label').text
                enlace_pdf = celda.find_element(By.XPATH, './/div[@class="ui-g-12 ui-md-4 dvDialog"]/a').get_attribute("href")
                if nombre_documento in df_doc.columns:
                  row[nombre_documento] = enlace_pdf
                else:
                  print(f"Document name '{nombre_documento}' not found in df_doc columns.")
            except NoSuchElementException:
                print(f"No PDF link found for '{nombre_documento}' in this cell.")
                row[nombre_documento] = None

    except TimeoutException:
        print("Timeout waiting for element with ID 'proyectosDeLeyForm:j_idt154'")
    except NoSuchElementException:
        print("Element with ID 'proyectosDeLeyForm:j_idt154' not found")
# =============================


# ============================
# Edit and format the dataframe
# ============================
df1 = pd.read_csv('/content/drive/MyDrive/Colab Notebooks/merge_df.csv')
df_copy = df1.rename(columns={ # Cambiar nombre de columnas
    'Fecha de Presentación': 'fecha_presentacion',
    'Proyecto': 'proyecto_ley',
    'Código': 'id',
    'Proponente(s)': 'proponente',
    'Estado': 'estado',
    'Cargo': 'cargo',
    'Comisión': 'comision',
    'Proyecto de Ley': 'texto_proyecto_ley',
    'Informe de Primer Debate de la Comisión': 'texto_1debate',
    'Informe de Segundo Debate de la Comisión': 'texto_2debate',
    'Texto aprobado por el Pleno': 'texto_aprobado_pleno',
    'Objeción Parcial del Ejecutivo': 'objecion_parcial',
    'Objeción Total del Ejecutivo': 'objecion_total',
    'Texto definitivo aprobado por el Pleno': 'texto_definitivo_pleno',
    'Registro Oficial': 'registro_oficial'
})
print(df_copy.columns)
df_copy['id'] = df_copy['id'].str.extract(r'(AN-\d{4}-\d{3,4})') # Formatear id

columns_to_check = ['texto_proyecto_ley', 'texto_1debate', 'texto_2debate', 'texto_aprobado_pleno', 'objecion_parcial', 'objecion_total', 'texto_definitivo_pleno', 'registro_oficial']

for column in columns_to_check: # Insertar '1' y '0' según precencia de pdf
    new_column_name = column + '_pdf_presente'
    df_copy[new_column_name] = df_copy[column].apply(lambda x: 1 if pd.notna(x) else 0)

    # Index de columna
    original_column_index = df_copy.columns.get_loc(column)

    # insertar nueva columna al al lado de original
    df_copy.insert(original_column_index, new_column_name, df_copy.pop(new_column_name))

df_copy.to_csv('/content/drive/MyDrive/Colab Notebooks/merge_df.csv', index=False)

df_copy.tail()
# ============================


# ============================
# Edit and clean 'cargo' column
# ============================
# Dataframe clean and completed without 'cargo' edited
df_1 = pd.read_csv('/content/drive/MyDrive/Colab Notebooks/cleaned_merge_df (1).csv')
df_1copy = df_1.copy()

df_1copy = df_1copy.fillna("NA")
df_1copy['comision'] = df_1copy['comision'].replace("No Asignada", "NA")
df_1copy['cargo'] = df_1copy['cargo'].str.upper()
df_1copy['cargo'] = df_1copy['cargo'].str.replace('  ', ' ')

variaciones_asambleista = ['ASAMBLEISTA  / ASAMBLEA NACIONAL', 'ASAMBLEISTA / ASAMBLEA NACIONAL',
                            'ASAMBLEISTA / ASAMBLEA NACIONALL', 'ASAMBLEISYA / ASAMBLEA NACIONAL',
                            'ASAMBLEITA / ASAMBLEA NACIONAL', 'ASAMBLESITA / AAMBLEA NACIONAL',
                            'ASAMBLESITA / ASAMBLEA ANCIONAL', 'ASAMBLESITA / ASAMBLEA NACIONAL',
                            'ASAMBLESITA / ASAMBLEAQ NACIONAL', 'ASAMBLESITAS / ASAMBLEA NACINAL',
                            'ASAMBLESITAS / ASAMBLEA NACIONAL', 'ASAMBLESTA / ASAMBLEA NACIONAL',
                            'ASAMBLEUSTA / ASAMBLEA NACIONAL', 'ASAMBLEÌSTA / ASAMBLEA NACIONAL',
                            'ASAMBLEÍSTA / ASAMBLEA NACIONAL', 'ASAMBLEÍSTAS / ASAMBLEA NACIONAL',
                            'ASMBLEÍSTA / ASAMBLEA NACIONAL']
for variacion in variaciones_asambleista:
    df_1copy['cargo'] = df_1copy['cargo'].replace(variacion, 'ASAMBLEÍSTA/S')

variaciones_presidenteECU =['PRESIDENTE CONSTITUCIONAL / PRESIDENCIA DE LA REPUBLICA',
                            'PRESIDENTE CONSTITUCIONAL DE LA  REPÚBLICA. / PRESIDENCIA DE LA REPÚBLICA',
                            'PRESIDENTE CONSTITUCIONAL DE LA REPUBLICA / PRESIDENCIA DE LA REPUBLICA',
                            'PRESIDENTE CONSTITUCIONAL DE LA REPÚBLICA / PRESIDENCIA',
                            'PRESIDENTE CONSTITUCIONAL DE LA REPÚBLICA DEL ECUADOR / PRESIDENCIA DE LA REPÚBLICA',
                            'PRESIDENTE CONSTITUCIONAL DEL ECUADOR / PRESIDENCIA DEL ECUADOR',
                            'PRESIDENTE CONSTITUCIONAL REPUBLICA / PRESIDENCIA DE LA REPUBLICA',
                            'PRESIDENTE / PRESIDENCIA DE LA REPUBLICA',
                            'PRESIDENTE DE LA REPUBLICA / PRESIDENCIA DE LA REPUBLICA',
                            'PRESIDENTE DE LA REPÚBLICA DEL ECUADOR / PRESIDENCIA DE LA REPÚBLICA DEL ECUADOR',
                            'PRESIDENTE CONSTITUCIONAL DEL ECUADOR / PRESIDENCIA DEL ECUADOR',
                            'PRESIDENTE CONSTITUCIONAL REPUBLICA / PRESIDENCIA DE LA REPUBLICA',
                            'PRESIDENTE CONSTITUCIONAL DE LA REPÚBLICA. / PRESIDENCIA DE LA REPÚBLICA'
                            ]
for variacion in variaciones_presidenteECU:
    df_1copy['cargo'] = df_1copy['cargo'].replace(variacion, 'PRESIDENTE DE LA REPÚBLICA DEL ECUADOR')

variaciones_defensor_del_pueblo = ['DEFENSOR DEL PUEBLO / DEFENSORIA DEL PUEBLO',
                                   'DEFENSOR DEL PUEBLO / DEFENSORÍA DEL PUEBLO',
                                   'DEFENSOR DEL PUEBLO, ENCARGADO / DEFENSORÍA DEL PUEBLO']
for variacion in variaciones_defensor_del_pueblo:
    df_1copy['cargo'] = df_1copy['cargo'].replace(variacion, 'DEFENSOR DEL PUEBLO')



df_1copy['cargo'] = df_1copy['cargo'].replace('PRESIDENTE DE LA CORTE NACIONAL DE JUSTICIA DE LA REPÚBLICA DEL ECUADOR / CORTE NACIONAL DE JUSTICIA',
                                              'PRESIDENTE DE LA CORTE NACIONAL DE JUSTICIA')
df_1copy['cargo'] = df_1copy['cargo'].replace('PRESIDENTE / FUNCIÓN DE TRANSPARENCIA Y CONTRO SOCIAL', 'PRESIDENTE DE LA FUNCIÓN DE TRANSPARENCIA Y CONTROL SOCIAL')
df_1copy['cargo'] = df_1copy['cargo'].replace('CIUDADANIA / CIUDADANIA', 'CIUDADANÍA')
df_1copy['cargo'] = df_1copy['cargo'].replace('CIUDADANO / #ACUERDO CONTRA EL CANCER', 'CIUDADANO DEL ACUERDO CONTRA EL CANCER')

cargos_quitar_sl = ['AUTORIDADES ISFFA / ISSFA', 'DEFENSOR PUBLICO GENERAL DEL ESTADO / DEFENSORÍA PUBLICA DEL ECUADOR',
                    'DEFENSOR PÚBLICO GENERAL DEL ESTADO, ENCARGADO / DEFENSORÍA PÚBLICA', 'DEFENSORA DEL PUEBLO (SUBROGANTE) / DEFENSORÍA DEL PUEBLO',
                    'DIRECTOR GENERAL DEL ISSPOL / ISSPOL', 'PRESIDENTE CONSEJO DE EDUCACION SUPERIOR / CONSEJO DE EDUCACION SUPERIOR',
                    'PRESIDENTE CONSEJO JUDICATURA / CONSEJO JUDICATURA', 'PRESIDENTE CONSEJO JUDICATURA Y PRESIDENTE CORTE NACIONAL DE JUSTICIA / CONSEJO DE LA JUDICATURA',
                    'PRESIDENTE DE LA CORTE NACIONAL DE JUSTICIA / CORTE NACIONAL DE JUSTICIA',
                    'PRESIDENTE DE LA FUNCIÓN DE TRANSPARENCIA Y CONTROL SOCIAL / FUNCIÓN DE TRANSPARENCIA Y CONTROL SOCIAL',
                    'PRESIDENTE DEL CONSEJO NACIONAL ELECTORAL / CONSEJO NACIONAL ELECTORAL', 'PROCURADOR GENERAL DEL ESTADO / PROCURADURIA GENERAL DEL ESTA',
                    'PROCURADOR GENERLA DEL ESTADO / PROCURADURIA GENERAL DEL ESTADO', 'PRESIDENTA ASAMBLEA NACIONAL / ASAMBLEA NACIONAL',
                    'FISCAL GENERAL DEL ESTADO / FISCALÍA GENERAL DEL ESTADO'
 ]
for var in cargos_quitar_sl:
    df_1copy.loc[df_1copy['cargo'] == var, 'cargo'] = var.split('/')[0].strip()

cargos_mas_del = ['PRESIDENTA / CONSEJO DE PARTICIPACIÓN CIUDADANA Y CONTROL SOCIAL',
                  'PRESIDENTA / UNE' 'PRESIDENTA ASAMBLEA NACIONAL',
                  'PRESIDENTE / CONSEJO DE LA JUDICATURA',
                  'PRESIDENTE / CONSEJO DE PARTICIPACIÓN CIUDADANA',
                  'PRESIDENTE / CONSEJO NACIONAL ELECTORAL',
                  'SECRETARIO GENERAL / CONSEJO NACIONAL ELECTORAL',
                  'DIRECTOR GENERAL DE PATROCINIO / MINISTERIO DE EDUCACIÓN',
                  'MINISTRA / MINISTERIO DEL TRABAJO',
                    ]
for var in cargos_mas_del:
    df_1copy.loc[df_1copy['cargo'] == var, 'cargo'] = var.replace('/', 'DEL')

cargos_mas_dela =['CIUDADANOS / INICIATIVA POPULAR',
                  'PRESIDENTA / UNE',
                  'PRESIDENTE / CORTE NACIONAL DE JUSTICIA', 'PRESIDENTE / FENOCIN',
                  'PRESIDENTE / FUNCIÓN DE TRANSPARENCIA Y CONTROL SOCIAL',
                  'PRIMERA VICEPRESIDENTA / ASAMBLEA NACIONAL','REPREDENTANTE DE LOS COMBATIENTES 1995 / UNCAC',
                  'SUBDIRECTOR DE GESTION DOCUMENTARIA, SUBROGANTE / DEFENSORÍA PÚBLICA DEL ECUADOR'
                  ]
for var in cargos_mas_dela:
    df_1copy.loc[df_1copy['cargo'] == var, 'cargo'] = var.replace('/', 'DE LA')





# df_1copy.to_csv('/content/drive/MyDrive/Colab Notebooks/cleaned_merge_df (1).csv', index=False)

df_1copy.tail()
# ============================


# ============================
# Download PDFs from the DataFrame
# ============================
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

# Call the function to download PDFs
dir_path = '' # Specify the directory path where you want to save the PDFs
download_pdfs(df_subset, dir_path)



