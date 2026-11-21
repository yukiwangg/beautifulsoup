# Milestone-4
A BeautifulSoup object can be used directly in a for loop to visit all
nodes in the parsed document in document order. For example:
from bs4 import BeautifulSoup, Tag

soup = BeautifulSoup("<p><b>Hi</b></p>", "html.parser")
for node in soup:
    print(node.name if isinstance(node, Tag) else str(node))
This prints p, b, and Hi on separate lines.
Implementation
BeautifulSoup.__iter__() returns the existing self.descendants generator.
The generator follows next_element and yields one node at a time. This allows
callers to stop early with break and avoids building a list of all nodes before
iteration starts.
Tests
bs4/tests/test_iterate_soup.py covers empty documents, sibling tags, nested
tags, mixed tags and text, and comments. All five tests passed. The full test
suite reported 842 passed and 7 skipped.