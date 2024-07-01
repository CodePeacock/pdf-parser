# sudo apt-get update && sudo apt install libglu1-mesa-dev poppler-utils tesseract-ocr
python3 -m venv venv
source venv/bin/activate
pip install -U -r requirements.txt
python3 main.py
# gunicorn -w 2 -b 0.0.0.0:10000 --reload main:app # increase workers to 4 or 6 in production