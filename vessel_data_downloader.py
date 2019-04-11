import os

from pdf2image import convert_from_path
from PIL import Image
import pytesseract

import requests

# Debug settings
download = True
convert_pdf = True
debug = True

#
# SETTINGS
#
# PDF URL
url = 'https://nrm.dfg.ca.gov/FileHandler.ashx?DocumentID=76424'
# Poppler Binary
poppler_path = os.path.join(os.getcwd(), 'poppler-0.68.0', 'bin')
# Add Poppler to PATH
os.environ['PATH'] = os.environ['PATH']+poppler_path
# PDF File Path
file_path = os.path.join(os.getcwd(), 'vessel.pdf')
# Converted PDF images folder
images_folder = os.path.join(os.getcwd(), 'vessel-images')
if not os.path.exists(images_folder):
    os.mkdir(images_folder)
# Output text file
vessel_text_file = os.path.join(os.getcwd(), 'vessel.txt')
# Image params, where rows start, height of row, distance between rows
y_start = 550
y_height = 32
y_offset = 75
page_end = 2310
# X coordinates to select individual columns
x_coordinates = {
    'id': (75, 170),
    'company': (171, 1000),
    'vessel_name': (1001, 1490),
    'insurance_company': (1491, 1810),
    'insurance_expires': (1811, 2070),
    'cert_number': (2071, 2380),
    'cert_ctrl': (2381, 2515),
    'cert_issue': (2516, 2700),
    'cert_expires': (2701, 2940),
    'imo': (2941, 3150),
}


# Download a file from URL
def download_file(url, local_path):

    if debug:
        print('Requesting %s' % url)
    if debug:
        print('Destination is %s' % local_path)

    try:

        with requests.get(url, stream=True) as r:

            if debug:
                print('Status code is %s, saving...' % r.status_code)

            if r.status_code != 200:
                if debug:
                    print('Falied request, status code %s' % r.status_code)
                return False

            with open(local_path, 'wb') as file:
                file.write(r.content)
                if debug:
                    print('Saved !')

            return True

    except requests.exceptions.ConnectionError as ex:
        print(ex)


# Download PDF file
if download:
    download_file(url, file_path)


# Convert pdf to images
if convert_pdf:
    images = convert_from_path(file_path,
                               dpi=300,
                               thread_count=2,
                               fmt='jpeg',
                               output_file='vessel',
                               output_folder=images_folder,
                               poppler_path=poppler_path
                               )


with open(vessel_text_file, 'w') as f:

    # We need to read from file, I tried to keep all in memory but it uses
    # +4GB
    images = None
    images = os.listdir(images_folder)

    print('Saving to %s' % vessel_text_file)

    # Write Header
    f.write('"Company","Vessel Name","IMO"\n')
    f.flush()

    # Counter
    rows = 1

    # Loop images
    for image_file in images:

        # Load image
        print('Opening %s' % image_file)
        image = Image.open(os.path.join(images_folder, image_file))

        # First row
        y = y_start

        # Loop rows
        while y < page_end:

            # Single row, starts at y, ends at y + row height
            top = y
            bottom = y+y_height

            # Do not go out of image boundaries
            if image.height > bottom:

                print('Row %d, Cropping y=%d' % (rows, top))

                # Crop each of the columns a single row onto images
                img_company = image.crop(
                    (x_coordinates['company'][0], top, x_coordinates['company'][1], bottom))
                img_vessel_name = image.crop(
                    (x_coordinates['vessel_name'][0], top, x_coordinates['vessel_name'][1], bottom))
                img_imo = image.crop(
                    (x_coordinates['imo'][0], top, x_coordinates['imo'][1], bottom))

                # OCR'em and cut spaces and new lines
                company = pytesseract.image_to_string(
                    img_company).strip().replace('\n', '')
                vessel_name = pytesseract.image_to_string(
                    img_vessel_name).strip().replace('\n', '')
                imo = pytesseract.image_to_string(
                    img_imo).strip().replace('\n', '')

                print('OCR returned: Company %s, Vessel %s, IMO %s' %
                      (company, vessel_name, imo))

                # If OCR returned valid data, build CSV row and write
                if len(company) > 0 and len(vessel_name) > 0 and len(imo) > 0:
                    row = '"'+company+'","'+vessel_name+'","'+imo+'"\n'
                    f.write(row)

            # Next row is at top + offset
            y = y+y_offset
            # Counter
            rows = rows + 1

        # Write to disk after the image is processed
        f.flush()
