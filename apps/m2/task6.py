import argparse
from bs4 import BeautifulSoup, SoupReplacer
from pathlib import Path
parser = argparse.ArgumentParser(description="Replace all b tags with blockquote tags and save the result.")
parser.add_argument("input_file", help="Path to the input HTML/XML file.")
parser.add_argument("output_file", help="Path to save the prettified output.")
args = parser.parse_args()

input_path = Path(args.input_file)
content = input_path.read_bytes()
if input_path.suffix.lower() == ".xml":
    parser_name = "xml"
else:
    parser_name = "html.parser"
replacer = SoupReplacer("b", "blockquote")

soup = BeautifulSoup(
    content,
    parser_name,
    replacer=replacer
)

output_path = Path(args.output_file)
output_path.write_text(soup.prettify(), encoding="utf-8")
