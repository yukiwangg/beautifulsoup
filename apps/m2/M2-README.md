# Milestone 2

## Environment and setup

Validated with Python 3.10.11 and lxml 5.3.2 on macOS. From the repository root:

```bash
python3.10 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m pip install pytest "lxml==5.3.2" html5lib packaging
```

The unmodified source passed 829 tests, with 7 skipped, after selecting lxml 5.3.2. With lxml 6.1.3, the unmodified source had three failures in TestLXMLTreeBuilder (real XHTML, processing instructions, and out-of-range entities). No original tests were edited to resolve those failures.

## Part 1: selective parsing

The applications retain the argument handling, byte input, and output behavior from Milestone 1. Files ending in `.xml` use the XML parser; other files use `html.parser`.

| Application | Parsing rule | Output query |
| --- | --- | --- |
| `task2.py` | `SoupStrainer("a")` | `find_all("a")` |
| `task3.py` | `SoupStrainer(True)` | `find_all(True)` |
| `task4.py` | `SoupStrainer(attrs={"id": True})` | `find_all(id=True)` |

```bash
python apps/m2/task2.py /path/to/input.html
python apps/m2/task3.py /path/to/input.html
python apps/m2/task4.py /path/to/input.html
```

For each task, M1 and M2 outputs on the same `python.html` file were saved and compared with `diff -u`; all three comparisons showed no differences.

SoupStrainer reduces unwanted tree construction; it does not eliminate reading or processing the input. Accepted tags may retain descendants that do not independently match the rule, so the final queries remain necessary. Task 3 needs every tag and therefore offers no opportunity to discard unwanted tags. The applications still use `read_bytes()`, so the complete input bytes are loaded into memory; they are not streaming applications.

### Timing observations

Both versions were run in the same activated environment with `/usr/bin/time -p`, redirecting standard output to `/dev/null`. Values below are single-run `real` times in seconds, including startup, input reading, parsing, querying, serialization, and output processing. They are preliminary observations, not repeated-run benchmark estimates. Peak memory was not measured.

| Input | Task | M1 | M2 |
| --- | --- | ---: | ---: |
| `pride.html` (852,590 bytes) | 2 | 0.18 | 0.09 |
| `pride.html` | 3 | 0.26 | 0.20 |
| `pride.html` | 4 | 0.12 | 0.09 |
| `wiki_sample_30mb.xml` (31,469,217 bytes) | 2 | 1.34 | 0.50 |
| `wiki_sample_30mb.xml` | 3 | 3.24 | 3.17 |
| `wiki_sample_30mb.xml` | 4 | 1.23 | 0.51 |

The XML sample was extracted from the M1 `wiki_large.xml` file, preserving the root, namespace declarations, site information, and 5,466 complete page elements. Its XML structure was validated. It has no `a` elements or `id` attributes: Tasks 2 and 4 measure the no-match case. XML `<id>` elements are not `id` attributes. These results must not be generalized to all documents or match distributions. Task 3 times are similar, consistent with retaining all tags. The complete 2.4 GB source file was not benchmarked for this milestone.

## Part 2: original API locations

All locations refer to the original commit `9aa1e5ed9b06fdcf64d30448447f38ee4ad62f2f`, before M2 edits. Repeated uses with different search arguments share the same method definition.

| API | Original source | Uses |
| --- | --- | --- |
| `BeautifulSoup(...)`: `BeautifulSoup.__init__` | `bs4/__init__.py:209` | All M1 tasks and M2 Part 1 |
| `Tag.prettify` | `bs4/element.py:2601` | M1 tasks 1, 6, 7, 8 |
| `Tag.find_all` | `bs4/element.py:2715` | M1 tasks 2, 3, 4, 6, 7; M2 tasks 2, 3, 4 |
| `Tag.find` | `bs4/element.py:2684` | M1 tasks 5, 8 |
| `PageElement.find_parent` | `bs4/element.py:992` | M1 task 5 |
| `PageElement.replace_with` | `bs4/element.py:552` | M1 task 8 |
| `Tag.__setitem__` for `tag["class"] = "test"` | `bs4/element.py:2223` | M1 task 7 |
| `SoupStrainer.__init__` | `bs4/filter.py:345` | M2 tasks 2, 3, 4 |

M1 task 6 also assigns `tag.name`: this is a field assignment, not a separate API function. The original `Tag.__init__` assigns `self.name` at `bs4/element.py:1740`. `BeautifulSoup` inherits methods such as `find_all` and `prettify` from `Tag`. Python standard-library APIs (`argparse`, `pathlib`, etc.) are not definitions in this library.

## Part 3: SoupReplacer

```python
from bs4 import BeautifulSoup, SoupReplacer

rule = SoupReplacer("b", "blockquote")
soup = BeautifulSoup(html, "html.parser", replacer=rule)
```

`SoupReplacer` in `bs4/filter.py` stores the original and replacement names and exposes `replace_name(name)`. `bs4/__init__.py` imports it and adds an optional `replacer=None` constructor argument, which is saved on the soup object.

Replacement is integrated into `BeautifulSoup.popTag`: after normal closing-tag matching and stack bookkeeping, the popped tag is renamed. Keeping the original name until closing avoids breaking the matching of input start/end tags, including nested `b` elements. This is an incremental transformation in the parsing/closing path, not a subsequent traversal over a completed tree. Unclosed elements are also popped by the existing end-of-input cleanup. No replacer preserves the existing behavior.

The demonstrated and unit-tested transformation is `b` to `blockquote` with `html.parser`. Arbitrary name changes affecting parser semantics (for example, void or raw-text tags), namespaced inputs, other parser backends, and copying/pickling behavior have not been comprehensively validated. Successful existing tests do not establish support for every such combination.

`apps/m2/task6.py` reuses the M1 application but passes a SoupReplacer to the constructor instead of finding and renaming tags after parsing:

```bash
python apps/m2/task6.py /path/to/input.html /path/to/output.html
```

M1 and M2 task 6 outputs on `html_examples.html` were compared with `diff -u` and were identical.

### New tests and regression checks

`bs4/tests/test_replacer.py` adds two tests:

1. Replace a `b` tag while preserving its attributes and text, and the parent relationship of a following paragraph.
2. Replace nested `b` tags while preserving nesting, text order, and the placement of a following paragraph.

```bash
python -m pytest bs4/tests/test_replacer.py -q
python -m pytest bs4/tests -q
```

Observed results: **2 passed** for the new tests; **831 passed, 7 skipped** for the complete suite.

The HTML/XML input datasets and temporary comparison outputs are external to the repository. Supply your own input paths when reproducing application runs. This README's API locations intentionally refer to the original commit rather than the shifted line numbers after modification.
