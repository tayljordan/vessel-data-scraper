# vessel-data-scraper
Python 3 script to download and scrape vessel data from the California Department of Fish and Wildlife’s (CDFW) Data Portal.

## Operation
A PDF file is downloaded from the CDFW portal. Each page of the file is converted to JPG using *Poppler*, which is included into the repository.
The included version is *poppler-0.68.0*.

Once converted, image files are processed using *pillow* to crop individual regions. These regions are processed using *Tesseract*, which is not included, and the data is saved onto a txt file.

## Requirements

### Python Packages
* pillow
* pdf2image
* pytesseract
* requests

### Binaries
* poppler (included)
* tesseract, get it from https://github.com/tesseract-ocr/tesseract
