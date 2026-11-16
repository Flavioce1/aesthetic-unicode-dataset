# Aesthetic Unicode Dataset

An open dataset of **2,038 Unicode characters, sequences and Japanese kaomoji**, each with a
human-readable name, its code points, and the collections it belongs to. JSON and CSV, no
dependencies, no API key. Data under CC BY 4.0, build script under MIT.

It exists because every "copy and paste symbols" site keeps its list locked inside its own HTML.
This one is a file you can `curl`.

```
2,038  unique characters and sequences
2,727  entries across 24 collections
  927  single code points, all carrying their official Unicode name
   47  entries (1.7%) with no usable name (see Limitations)
```

## Quick start

```bash
curl -O https://raw.githubusercontent.com/Flavioce1/aesthetic-unicode-dataset/main/data/characters.json
```

```python
import json, urllib.request
URL = "https://raw.githubusercontent.com/Flavioce1/aesthetic-unicode-dataset/main/data/entries.json"
entries = json.load(urllib.request.urlopen(URL))

hearts = [e for e in entries if e["category"] == "hearts"]
print(hearts[0]["character"], hearts[0]["name"])   # ♥ Black Heart Suit
```

```js
const entries = await fetch(
  "https://raw.githubusercontent.com/Flavioce1/aesthetic-unicode-dataset/main/data/entries.json"
).then(r => r.json());

const stars = entries.filter(e => e.category === "stars");
```

## Files

| File | What it is |
|---|---|
| `data/entries.json` | Every entry, one per character **per collection**. A symbol that belongs to two collections appears twice. 2,727 rows. |
| `data/entries.csv` | Same data, CSV. |
| `data/characters.json` | Deduplicated: one row per character, with a `collections` array. 2,038 rows. |
| `data/by-category/*.json` | One file per collection, same schema as `entries.json`. |
| `build.py` | The script that produced all of the above. Run it yourself. |

## Schema

```json
{
  "character": "★",
  "name": "Black Star",
  "named": true,
  "collection": "symbols",
  "category": "stars",
  "codepoints": "U+2605",
  "char_length": 1,
  "unicode_name": "BLACK STAR",
  "unicode_category": "So",
  "source": "https://copy-aesthetic.com/symbols-stars"
}
```

| Field | Notes |
|---|---|
| `character` | The character or sequence itself. |
| `name` | Human-readable label. See Provenance for where each one comes from. |
| `named` | `false` when no usable name exists and `name` falls back to the character itself. Filter on this if you need labelled data only. |
| `collection` / `category` | `symbols`, `kaomoji` or `text`, then the specific collection. |
| `codepoints` | Space-separated `U+XXXX`, useful for debugging rendering issues. |
| `char_length` | Number of code units. `1` means a single code point. |
| `unicode_name` / `unicode_category` | Straight from the Unicode Character Database, empty for multi-code-point sequences. |
| `source` | The page the entry was curated on. |

## Collections

**Symbols:** stars, hearts, arrows, music, weather, math, brackets, checks, currency, zodiac, general
**Kaomoji:** all, happy, sad, cat, angry, love, bear
**Text:** dividers, bullets, bio-combos, decorators, small-text, glitch

## Provenance

Names come from three places, in this order:

1. **Human curation**: most entries, especially kaomoji, where a code point name would be
   meaningless. `(╯°□°）╯︵ ┻━┻` is "Table Flip", not a list of 12 code points.
2. **The Unicode Character Database**, via Python's `unicodedata`, for single code points that had
   no curated name. This filled 73 entries.
3. **The character itself**, when neither applies (flagged with `named: false`).

The curated names and the collection groupings come from
[copy-aesthetic.com](https://copy-aesthetic.com), a free copy-paste tool for these characters.
`build.py` extracts them from that site's `ItemList` structured data, so the dataset and the site
cannot drift apart.

## Limitations: read these before relying on it

- **47 entries (1.7%) have no real name.** All of them are multi-character kaomoji whose source
  entry carried the character itself as its label. They are marked `named: false` rather than
  given an invented label.
- **This is not a Unicode mirror.** It is a curated *aesthetic* subset: the characters people
  actually paste into bios and usernames. For the full standard, use the
  [UCD](https://www.unicode.org/Public/UCD/latest/).
- **No rendering guarantees.** Whether `⛧` shows up on your user's Android build is not encoded
  here. Some sequences use variation selectors (`U+FE0E`) that platforms treat differently.
- **Categories overlap by design.** `♡` is in both `hearts` and `bullets`. Use
  `characters.json` if you want one row per character.
- **Kaomoji are not Unicode-standard objects.** They are conventional sequences; there is no
  authority defining them and no canonical spelling.

## Licence

- **Data:** [CC BY 4.0](LICENSE). Use it commercially, modify it, just credit the source.
- **`build.py`:** MIT, do what you like.
- Character names taken from the Unicode Character Database remain subject to the
  [Unicode Terms of Use](https://www.unicode.org/copyright.html). Unicode® is a registered
  trademark of Unicode, Inc.

## Contributing

Missing names, wrong categories and better kaomoji labels are all welcome, especially for the 47
unnamed entries. Open an issue or a PR against `data/`, and mention which collection you are
touching.
