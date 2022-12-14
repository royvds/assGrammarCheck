"""
The command-line interface for assGrammarChecker
"""

import os
import sys
import argparse
from glob import glob

from tabulate import tabulate
from .assgrammarcheck import AssGrammarChecker


def startup(args):
    """ Set up the grammar checker """
    print("Setting up GrammarChecker and LanguageTool server...")
    checker = AssGrammarChecker(args.ignore_rules, args.ignore_spelling,
                                            args.ignore_words, args.ignore_informal,
                                            args.ignore_categories, args.language)
    print("Done!")
    return checker


def check(subtitle, checker):
    """ Check subtitle for grammar mistakes using AssGrammarChecker """
    mistakes = checker.get_subtitle_mistakes(subtitle)
    # Format the data into something tabulate can properly show in console
    output_table = [[mistake[0], match.message, # Limit to max 10 replacements to limit clutter
                    checker.color_mistake_text(match), '; '.join(match.replacements[:10])]
                    for mistake in mistakes for match in mistake[1]]


    if len(output_table) > 0:
        t_width = os.get_terminal_size().columns
        print()
        print()
        print(os.path.basename(subtitle))
        # Slightly less than 100% of t_width in case of rounding errors
        print(tabulate(output_table, maxcolwidths=[None, round(0.36 * t_width),
                                                round(0.36 * t_width), round(0.15 * t_width)],
                    headers=["Line", "Language Error", "Line text", "Suggestions"]))


def main():
    """ Main Function """

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', required=True,
            help="Folder or file input")
    parser.add_argument('-uw', '--unknown-words', default=False, action="store_true",
                        help="Alternative mode: retrieve list of unkown/misspelled words")
    parser.add_argument('-l', '--language',
            help="Set language of subtitle. Default: en-US")
    parser.add_argument('-ii', '--ignore-informal', default=False, action="store_true",
            help="Don't flag informal language as grammar mistakes")
    parser.add_argument('-is', '--ignore-spelling', default=False, action="store_true",
            help="Ignore spelling mistakes (e.g. in case you already spell-checked with Aegisub)")
    parser.add_argument('-iw', '--ignore-words', nargs='+', default=[],
            help="List of words to exclude from any spell checks")
    parser.add_argument('-ir', '--ignore-rules', nargs='+', default=[],
            help="List of rules to ignore \
                (https://community.languagetool.org/rule/list?lang=en)")
    parser.add_argument('-ic', '--ignore-categories', nargs='+', default=[],
            help="List of rule categories to ignore \
                (https://languagetool.org/development/api/org/languagetool/rules/Categories.html)")
    args = parser.parse_args()

    if os.path.isfile(args.input):
        grammar_checker = startup(args)
        if args.unknown_words:
            print('"' + '" "'.join(grammar_checker.get_unknown_words(args.input)) + '"')
        else:
            check(args.input, grammar_checker)
        grammar_checker.close()
    elif os.path.isdir(args.input):
        subtitle_files = glob(f"{args.input}{os.path.sep}*.ass")
        grammar_checker = startup(args)
        if args.unknown_words:
            unknown_words = set()
            for subtitle in subtitle_files:
                unknown_words.update(grammar_checker.get_unknown_words(subtitle))
            print('"' + '" "'.join(unknown_words) + '"')
        else:
            for subtitle in subtitle_files:
                check(subtitle, grammar_checker)
        grammar_checker.close()
    else:
        sys.exit("Given input is not an existing file or folder")


if __name__ == "__main__":
    main()
