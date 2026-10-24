import argparse
from bs4 import BeautifulSoup, SoupStrainer
from pathlib import Path

parser = argparse.ArgumentParser(
    description="Read an HTML/XML file and print all tags with an id attribute."
)
parser.add_argument("input_file", help="Path to the input HTML/XML file.")
args = parser.parse_args()

input_path = Path(args.input_file)
html = input_path.read_bytes()

if input_path.suffix.lower() == ".xml":
    parser_name = "xml"
else:
    parser_name = "html.parser"

only_ids = SoupStrainer(attrs={"id": True})

soup = BeautifulSoup(html, parser_name, parse_only=only_ids)

tags = soup.find_all(id=True)

for tag in tags:
    print(tag)