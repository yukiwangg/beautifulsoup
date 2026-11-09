import argparse
from pathlib import Path

from bs4 import BeautifulSoup, SoupReplacer


def change_attrs(tag):
    attrs = dict(tag.attrs)

    if tag.name == "p":
        attrs["class"] = ["test"]

    return attrs


parser = argparse.ArgumentParser(
    description='Set class="test" on all p tags during parsing.'
)
parser.add_argument("input_file", help="Input HTML/XML file.")
parser.add_argument("output_file", help="Output file.")
args = parser.parse_args()

input_path = Path(args.input_file)
content = input_path.read_bytes()

if input_path.suffix.lower() == ".xml":
    parser_name = "xml"
else:
    parser_name = "html.parser"

replacer = SoupReplacer(attrs_xformer=change_attrs)

soup = BeautifulSoup(
    content,
    parser_name,
    replacer=replacer,
)

Path(args.output_file).write_text(
    soup.prettify(),
    encoding="utf-8",
)
