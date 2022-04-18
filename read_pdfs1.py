import os
import pdfplumber
import re
import pandas as pd
from collections import namedtuple
#print(pdfplumber.__version__)

Boleta = namedtuple('Boleta', 'numero_boleta fecha nombre rut codigo descripcion  cantidad precio_uni total')
dir_files = os.path.abspath(os.getcwd())
pdfs_dir = '/pdfs/'
file_ext = '.pdf'
pdfs = [os.path.join(dir_files+pdfs_dir, _) for _ in os.listdir(dir_files+pdfs_dir) if _.endswith(file_ext)]


def extract_text_pdf(pdf):
    line_items = []
    page = pdf.pages[0]
    text = page.extract_text()
    # ([A-Z ñ (es) a-z]+\:)([A-Z a-z ñ]+\s)([F\.?\s?[A-Z a-z ó \:]+)(\d{2}-\d{2}-\d{4})
    numero_boleta = re.compile(r'([Nº]+\s)(\d{4})')
    nombre_fecha = re.compile(r'([A-Z ñ (es) a-z]+\:)([A-Z a-z |áÁ|éÉ|íÍ|óÓ|úÚ|ñÑ]+\s)([F\.?\s?[A-Z a-z ó \:]+)(\d{2}-\d{2}-\d{4})')
    rut_fecha = re.compile(r'([A-Z]+\:\s)(\b(\d{1,3}(?:\.\d{1,3}){2}-[\dkK])\b\s)([F\.?\s?[A-Z a-z ó \:]+)(\d{2}-\d{2}-\d{4})')
    productos = re.compile(r'(\d{5}\s)([a-z A-Z]+\d?\.?\d?[a-z A-z]+[\s|\.?])([C\/U\s?]+)(\d{1,}\s?)([CS|cs]+\s?)([0-9]{1,3}.*\s)([0-9]{1,3}.*)')

    for line in text.split('\n'):
        line_n_boleta = numero_boleta.search(line)
        line_nombre_fecha = nombre_fecha.search(line)
        line_rut_fecha = rut_fecha.search(line)
        line_producto_fecha = productos.search(line)

        if line_n_boleta:
            boleta = line_n_boleta.group(2)

        elif line_nombre_fecha:
            nombre = line_nombre_fecha.group(2)
            fecha = line_nombre_fecha.group(4)

        elif line_rut_fecha:
            rut = line_rut_fecha.group(2)
            f_vencimiento = line_rut_fecha.group(5)
        
        elif line_producto_fecha:
            codigo = line_producto_fecha.group(1)
            descripcion = line_producto_fecha.group(2)
            cantidad = line_producto_fecha.group(4)
            precio_uni = line_producto_fecha.group(6)
            total = line_producto_fecha.group(7)
            
            line_items.append(Boleta(boleta,fecha,nombre,rut,codigo,descripcion,cantidad,precio_uni,total))
            
    return line_items


def read_pdfs(list_pdfs):
    data = []
    if list_pdfs:
        print(f'cantidad de pdfs encontrados {len(list_pdfs)}')
        for pdf_file in list_pdfs:
            print('procesando..',pdf_file)
            pdf = pdfplumber.open(pdf_file)
            data.extend(extract_text_pdf(pdf))
    return data

def pdf_text_to_csv(file_name,data):
    df = pd.DataFrame(data)
    df.to_csv(file_name, encoding='utf-8')
    return 'Csv Creado'

if __name__ == "__main__":
        data = read_pdfs(pdfs)
        create_csv = pdf_text_to_csv('boletas.csv',data)
        print(create_csv)
    