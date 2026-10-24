from bs4 import BeautifulSoup, SoupReplacer


def test_replaces_b_and_preserves_attributes():
    html = '<div><b id="target">Hello</b><p>After</p></div>'

    soup = BeautifulSoup(
        html,
        "html.parser",
        replacer=SoupReplacer("b", "blockquote")
    )

    assert soup.find("b") is None

    replacement = soup.find("blockquote", id="target")
    assert replacement is not None
    assert replacement.get_text() == "Hello"

    assert soup.p.parent is soup.div
    assert soup.p.get_text() == "After"


def test_preserves_nested_structure():
    html = "<div><b>Outer <b>Inner</b> end</b><p>After</p></div>"

    soup = BeautifulSoup(
        html,
        "html.parser",
        replacer=SoupReplacer("b", "blockquote")
    )

    replacements = soup.find_all("blockquote")

    assert soup.find("b") is None
    assert len(replacements) == 2

    outer, inner = replacements

    assert outer.parent is soup.div
    assert inner.parent is outer
    assert inner.get_text() == "Inner"
    assert outer.get_text() == "Outer Inner end"
    assert soup.p.parent is soup.div