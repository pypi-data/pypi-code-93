# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['abnex']

package_data = \
{'': ['*']}

setup_kwargs = {
    'name': 'abnex',
    'version': '1.0.2',
    'description': 'Abnormal expressions (abnex) is an alternative to regular expressions (regex).',
    'long_description': '# Abnormal expressions\nAbnormal expressions (abnex) is an alternative to regular expressions (regex).\nThis is a Python library but the abnex syntax could be ported to other languages.\n\n# Examples\n## Matching an email address\n- Regex\n  - `([\\w\\._-]+)@([\\w\\.]+)`\n- Abnex\n  - `{[w"._-"]1++}"@"{[w"."]1++}`\n- Abnex (spaced)\n  - `{[w "._-"]1++} "@" {[w "."]1++}`\n\n- Abnex (expanded)\n  ```\n  {\n    [w "._-"]1++\n  }\n  "@"\n  {\n    [w "."]1++\n  }\n  ```\n  ## A more advanced pattern:\n  `{{{[a-z \'_\']1++} {[a-z 0-9 \'_-.\']0++}} \'@\' {{[a-z 0-9]1++} \'.\' {[a-z 0-9]1++} {[a-z 0-9 \'-_.\']0++}} {[a-z 0-9]1++}}`.\n\n# Why is Abnex Better?\n- It\'s easier to read, write and understand.\n- You can use spaces inside of the expression, you can also "expand" it, i.e. write it over multiple lines and use indention.\n- You don\'t have to use a backslashes all the time\n- More logical/common symbols like `!` for _not_, `{}` for _groups_, `1++`, `0++`, `0+` for: _one or more_, _zero or more_, _zero or one_.\n- It\'s easier to see if a symbol is an actual symbol you are searching for or if it\'s a regex character, ex:\n  - Regex: `[\\w-]+@[\\w-_]+`\n  - Abnex: `[w "-"]1++ "@" [w "-"]1++`\n\n# Documentation\n### Regex on right after -> is the abnex equivalent\n## Anchors\n- Start of string, or start of line in multi-line pattern\n  - `^` -> `->`\n- End of string, or end of line in multi-line pattern\n  - `$` -> `<-`\n- Start of string\n  - `\\A` -> `s>`\n- End of string\n  - `\\Z` -> `<s`\n- Word boundary\n  - `\\b` -> `:`\n- Not word boundary\n  - `\\B` -> `!:`\n- Start of word\n  - `\\<` -> `w>`\n- End of word\n  - `\\>` -> `<w`\n\n## Character Classes\n- Control character\n  - `\\c` -> `c`\n- White space\n  - `\\s` -> `_`\n- Not white space\n  - `\\S` -> `!_`\n- Digit\n  - `\\d` -> `d`\n- Not digit\n  - `\\D` -> `!d`\n- Word\n  - `\\w` -> `w`\n- Not word\n  - `\\W` -> `!w`\n- Hexade\xadcimal digit\n  - `\\x` -> `x`\n- Octal digit\n  - `\\o` -> `o`\n\n## Quantifiers\n- 0 or more\n  - `*` -> `0++`\n- 1 or more\n  - `+` -> `1++`\n- 0 or 1\n  - `?` -> `0+`\n\n## Groups and Ranges\n- Any character except new line (\\n)\n  - `.` -> `*`\n- a or b\n  - `a|b` -> `"a"|"b"`\n- Group\n  - `(...)` -> `{...}`\n- Passive (non-c\xadapt\xaduring) group\n  - `(?:...)` -> `{#...}`\n- Range (a or b or c)\n  - `[abc]` -> `[\'abc\']` or `["a" "b" "c"]`\n- Not in set\n  - `[^...]` -> `[!...]`\n- Lower case letter from a to Z\n  - `[a-q]` -> `[a-z]`\n- Upper case letter from A to Q\n  - `[A-Q]` -> `[A-Q]`\n- Digit from 0 to 7\n  - `[0-7]` -> `[0-7]`\n\n# Standards\nWhat is the recommended way to write abnexes\n\n- Use spaces between characters in character sets:\n  - Correct: `[w "_-"]`\n  - Incorrect: `[w"_-"]`\n- Put multiple exact characters between the same quotes in character sets:\n  - Correct: `["abc"]`\n  - Incorrect: `["a" "b" "c"]`, especially incorrect: `["a""b""c"]`\n- Put spaces between groups:\n  - Correct: `{w} "." {w}`\n  - Incorrect: `{w}"."{w}`\n\n### Examples:\nMatch for an email address:\n- Regex:\n  - `[\\w-\\._]+@[\\w-\\.]+`\n- Abnex (following standards):\n  - `{[w "-._"]1++} "@" {[w "-."]1++}`\n- Abnex (not following standards):\n  - `{[w"-._"]1++}"@"{[w"-."]1++}`\n  \n# Functions (In Python)\n__Abnex has most functions from the `re` library, but it also has som extra functionality like: `last()` & `contains()`.__\n\n## Common functions between re and abnex\n### Regex on right after -> is the abnex equivalent\n- `match()` -> `match()`\n- `findall()` -> `all()`\n- `split()` -> `split()`\n- `sub()` -> `replace()`\n- `subn()` -> `replace_count()`\n- `search()` -> `first()`\n## Special to abnex\n- `holds()`: whether or not a string matches an expression (bool).\n- `contains()`: wheter or not a string contains a match (bool).\n- `last()`: the last match in a string.\n',
    'author': 'Edvard Busck-Nielsen',
    'author_email': 'me@edvard.dev',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Buscedv/abnormal-expressions',
    'packages': packages,
    'package_data': package_data,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
