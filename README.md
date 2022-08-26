# ASSGrammarCheck

Python tool to check for grammar mistakes in .ass subtitle files.

This tool uses a local LanguageTool server to check each dialogue line in a subtitle file for grammar mistakes. The script is configurable to ignore certain words or specific LanguageTool rule and rule categories.

## Dependencies
- [Python 3.9 or higher](https://www.python.org/downloads/)
- [Python ass](https://pypi.org/project/ass/)
- [language-tool-python](https://pypi.org/project/language-tool-python/)

## Usage
```console
$ assgrammarcheck --help
usage: assGrammarCheck [-h] -i INPUT [-uw] [-ii] [-is] [-iw IGNORE_WORDS [IGNORE_WORDS ...]]
                       [-ir IGNORE_RULES [IGNORE_RULES ...]] [-ic IGNORE_CATEGORIES [IGNORE_CATEGORIES ...]]

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Folder or file input
  -uw, --unknown-words  Alternative mode: retrieve list of unkown/misspelled words
  -ii, --ignore-informal
                        Don't flag informal language as grammar mistakes
  -is, --ignore-spelling
                        Ignore spelling mistakes (e.g. in case you already spell-checked with Aegisub)
  -iw IGNORE_WORDS [IGNORE_WORDS ...], --ignore-words IGNORE_WORDS [IGNORE_WORDS ...]
                        List of words to exclude from any spell checks
  -ir IGNORE_RULES [IGNORE_RULES ...], --ignore-rules IGNORE_RULES [IGNORE_RULES ...]
                        List of rules to ignore (https://community.languagetool.org/rule/list?lang=en)
  -ic IGNORE_CATEGORIES [IGNORE_CATEGORIES ...], --ignore-categories IGNORE_CATEGORIES [IGNORE_CATEGORIES ...]
                        List of rule categories to ignore
                        (https://languagetool.org/development/api/org/languagetool/rules/Categories.html)
```

## Roadmap
- Better support for sentences split over multiple lines
