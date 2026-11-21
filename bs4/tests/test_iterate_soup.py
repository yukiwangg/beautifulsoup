from bs4 import BeautifulSoup, Comment, NavigableString, Tag


def test_empty_document_has_no_nodes():
    soup = BeautifulSoup("", "html.parser")
    assert list(soup) == []


def test_iterates_over_sibling_tags():
    soup = BeautifulSoup("<p></p><div></div>", "html.parser")
    assert [node.name for node in soup] == ["p", "div"]


def test_iterates_over_nested_tags_in_document_order():
    soup = BeautifulSoup("<div><p><b></b></p></div><hr>", "html.parser")
    assert [node.name for node in soup] == ["div", "p", "b", "hr"]


def test_iterates_over_tags_and_text():
    soup = BeautifulSoup("<p>Hello <b>world</b>!</p>", "html.parser")
    paragraph, first_text, bold, second_text, punctuation = soup

    assert isinstance(paragraph, Tag) and paragraph.name == "p"
    assert isinstance(bold, Tag) and bold.name == "b"
    assert isinstance(first_text, NavigableString) and first_text == "Hello "
    assert isinstance(second_text, NavigableString) and second_text == "world"
    assert isinstance(punctuation, NavigableString) and punctuation == "!"


def test_iterates_over_comments():
    soup = BeautifulSoup("<!--note--><p></p>", "html.parser")
    comment, paragraph = soup

    assert isinstance(comment, Comment) and comment == "note"
    assert isinstance(paragraph, Tag) and paragraph.name == "p"