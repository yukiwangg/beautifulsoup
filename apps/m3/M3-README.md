# Milestone 3 — Functional SoupReplacer

## API Comparison and Recommendation

Milestone 2 uses `SoupReplacer("b", "blockquote")` to replace a fixed tag name. This API is simple to understand, but only supports name replacement based on an exact match.

Milestone 3 accepts three optional functions:

- `name_xformer(tag)` returns a replacement tag name.
- `attrs_xformer(tag)` returns replacement attributes.
- `xformer(tag)` modifies the tag directly; its return value is ignored.

The functional API allows decisions based on a tag's name, attributes, or content without adding a new library method for every rule. Its trade-off is that callers must write functions and understand when they run.

I recommend keeping the Milestone 2 form for simple replacements and offering the Milestone 3 functions for more flexible transformations.

## Implementation and Behavior

`SoupReplacer` is implemented in `bs4/filter.py`. Its `apply(tag)` method is called from the existing `BeautifulSoup.popTag()` parsing path in `bs4/__init__.py`, after the original stack bookkeeping.

Transformations run when a tag is popped during parsing, including end-of-input cleanup. The implementation does not traverse the completed tree afterward.

When supplied together, operations run in this order:

1. Milestone 2 name replacement.
2. `name_xformer`.
3. `attrs_xformer`.
4. `xformer`.

Each operation sees the changes made by earlier operations. No transformations are applied when all options are omitted.

Callbacks should preserve valid tag names and attributes. Structural changes such as removing or moving nodes, and behavior across other parser backends, have not been comprehensively validated.

## Application

`apps/m3/task7.py` sets or replaces `class="test"` on every `p` tag during parsing. Other attributes and other tags are preserved.

From the repository root, in the activated project environment:

```bash
python apps/m3/task7.py input.html output.html
```

## Validation

Six new tests cover name transformation, attribute transformation, direct mutation, operation order, nested parsing order, and no-op behavior. The two Milestone 2 tests are retained.

```bash
python -m pytest bs4/tests/test_replacer.py -q
python -m pytest bs4/tests -q
```

Observed results:

- Replacer tests: 8 passed.
- Full suite: 837 passed, 7 skipped.

The application was also checked with paragraphs both with and without an existing class. Both received `class="test"`; an existing paragraph ID and a span's class were preserved.