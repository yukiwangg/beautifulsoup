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


def test_name_transformer():
    html = "<div><b>Hello</b><i>World</i></div>"

    replacer = SoupReplacer(
        name_xformer=lambda tag:
            "blockquote" if tag.name == "b" else tag.name
    )

    soup = BeautifulSoup(html, "html.parser", replacer=replacer)

    assert soup.find("b") is None
    assert soup.blockquote.get_text() == "Hello"
    assert soup.i.get_text() == "World"


def test_attrs_transformer_adds_and_replaces_class():
    html = (
        '<div><p id="first">One</p>'
        '<p class="old">Two</p><span>Other</span></div>'
    )

    def change_attrs(tag):
        attrs = dict(tag.attrs)

        if tag.name == "p":
            attrs["class"] = ["test"]

        return attrs

    soup = BeautifulSoup(
        html,
        "html.parser",
        replacer=SoupReplacer(attrs_xformer=change_attrs),
    )

    paragraphs = soup.find_all("p")

    assert len(paragraphs) == 2
    assert all(tag["class"] == ["test"] for tag in paragraphs)
    assert paragraphs[0]["id"] == "first"
    assert not soup.span.has_attr("class")


def test_xformer_modifies_tag_and_ignores_return_value():
    html = '<div class="outer"><p class="old">Hello</p></div>'

    def remove_class(tag):
        if "class" in tag.attrs:
            del tag.attrs["class"]

        return "This return value should be ignored"

    soup = BeautifulSoup(
        html,
        "html.parser",
        replacer=SoupReplacer(xformer=remove_class),
    )

    assert not soup.div.has_attr("class")
    assert not soup.p.has_attr("class")
    assert soup.p.get_text() == "Hello"


def test_transformer_execution_order():
    events = []

    def rename(tag):
        events.append(("name", tag.name))
        return "section"

    def change_attrs(tag):
        events.append(("attrs", tag.name))
        return {"data-name": tag.name}

    def modify(tag):
        events.append(("xformer", tag.name))
        tag["data-final"] = tag["data-name"] + "-done"

    soup = BeautifulSoup(
        "<p>Hello</p>",
        "html.parser",
        replacer=SoupReplacer(
            name_xformer=rename,
            attrs_xformer=change_attrs,
            xformer=modify,
        ),
    )

    assert events == [
        ("name", "p"),
        ("attrs", "section"),
        ("xformer", "section"),
    ]
    assert soup.section["data-name"] == "section"
    assert soup.section["data-final"] == "section-done"


def test_nested_tags_transform_once_during_parsing():
    visited = []

    def rename(tag):
        visited.append(tag.name)

        if tag.name == "b":
            return "blockquote"

        return tag.name

    soup = BeautifulSoup(
        "<div><b>Outer <b>Inner</b></b><p>After</p></div>",
        "html.parser",
        replacer=SoupReplacer(name_xformer=rename),
    )

    assert visited == ["b", "b", "p", "div"]

    outer, inner = soup.find_all("blockquote")

    assert outer.parent is soup.div
    assert inner.parent is outer
    assert outer.get_text() == "Outer Inner"
    assert soup.p.parent is soup.div


def test_no_transformers_preserves_document():
    html = '<div id="root"><p class="old">Hello</p></div>'

    normal = BeautifulSoup(html, "html.parser")

    with_replacer = BeautifulSoup(
        html,
        "html.parser",
        replacer=SoupReplacer(),
    )

    assert str(with_replacer) == str(normal)