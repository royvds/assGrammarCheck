"""
    Grammar checker for .ass subtitles
    Uses LanguageTool for the grammar check.

    Useful links:
    https://languagetool.org/development/api/org/languagetool/rules/Categories.html
    https://community.languagetool.org/rule/list?lang=en
"""

import re

import ass
import language_tool_python
from language_tool_python import Match


class TerminalColors:
    """ Color codes for terminal colors """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class AssGrammarChecker:
    """ Class to check grammar mistakes in a .ass subtitle file """

    def __init__(self, ignore_rules: list[str] = None, ignore_spelling: bool = False,
                 ignore_words: list[str] = None, ignore_informal: bool = False,
                 ignore_categories: list[str] = None):
        self.tool = language_tool_python.LanguageTool('en-US')
        self.ignore_rules = [rule.upper() for rule in ignore_rules] or []
        self.ignore_words = [word.lower() for word in ignore_words] or []
        self.ignore_spelling = ignore_spelling
        self.ignore_informal = ignore_informal
        self.ignore_categories = [category.lower() for category in ignore_categories] or []

    def set_ignore_words(self, ignore_words: list[str]):
        """ Setter for ignore_words """
        self.ignore_words = ignore_words

    def set_ignore_spelling(self, boolean: bool):
        """ Setter for ignoring spelling mistakes """
        self.ignore_spelling = boolean

    def __is_dialogue_event(self, event):
        """ Check if a subtitle event is a dialogue event """
        return event.text and \
            not event.dump_with_type().startswith("Comment: ") and \
            re.match('^Dialogue|^main|^Default', event.style)

    def __clean_event_text(self, text: str) -> str:
        """ Extract the actual text from a subtitle event; removes non-visible text. """
        output = re.sub('{.*?}', "", text)
        # Most greedy to least greedy replacement of \n with spaces around
        output = output.replace(" \\N ", " ")
        output = output.replace("\\N ", " ")
        output = output.replace(" \\N", " ")
        output = output.replace("\\N", " ")
        return output

    def __remove_false_positives(self, matches: list[type(Match)]) -> list[type(Match)]:
        """ Remove all error matches that are not supposed to be errors """
        output = []
        for match in matches:
            if match.ruleId in self.ignore_rules:
                continue
            if self.ignore_informal and "informal" in match.message:
                continue
            if match.ruleIssueType in self.ignore_categories:
                continue
            if match.ruleId == "MORFOLOGIK_RULE_EN_US" and \
                    (self.ignore_spelling or
                     (match.matchedText.lower() in self.ignore_words)):
                continue
            output.append(match)
        return output

    def __sort_subtitle_events(self, events: list):
        return sorted(events, key=lambda e: e.start)

    def get_unknown_words(self, subtitle_file: str) -> set:
        """ Retrieve a set of words that get flagged as misspelled,
            useful for creating a list of names to ignore. """
        with open(subtitle_file, encoding='utf_8_sig') as sub_file:
            subs = ass.parse(sub_file)

        word_list = set()
        for event in subs.events:
            if not self.__is_dialogue_event(event):
                continue

            mistakes_list = self.tool.check(
                self.__clean_event_text(event.text))
            for match in mistakes_list:
                if match.ruleId == "MORFOLOGIK_RULE_EN_US":
                    word_list.add(match.matchedText)

        return word_list

    def color_mistake_text(self, match):
        """ Apply terminal color to the text that should be changed """
        # In case of repitition of text we should not use a simple
        # replace, but use the index manually instead
        return match.context[0:match.offsetInContext] + \
            TerminalColors.FAIL + TerminalColors.BOLD + \
            match.context[match.offsetInContext:match.offsetInContext+match.errorLength] + \
            TerminalColors.ENDC + \
            match.context[match.offsetInContext +
                          match.errorLength:len(match.context)]

    def __save_subtitle(self, subtitle, subtitle_filepath):
        with open(subtitle_filepath, "w", encoding='utf_8_sig') as file:
            subtitle.dump_file(file)

    def get_subtitle_mistakes(self, subtitle_file: str) -> list[tuple]:
        """ Check for grammar mistakes in a .ass subtitle file """
        with open(subtitle_file, encoding='utf_8_sig') as sub_file:
            subtitle = ass.parse(sub_file)

        # Sort and save subtitle so that all line indexes will correspond correctly
        subtitle.events = self.__sort_subtitle_events(subtitle.events)
        self.__save_subtitle(subtitle, subtitle_file)

        subtitle_mistakes = []
        for index, event in enumerate(subtitle.events):
            if not self.__is_dialogue_event(event):
                continue

            mistakes_list = self.tool.check(
                self.__clean_event_text(event.text))
            mistakes_list = self.__remove_false_positives(mistakes_list)

            # We check in a loop for the previous dialogue line, since the
            # previous subtitle event might be a sign or something else instead.
            index_offset = 2
            prev_event = subtitle.events[index-1]
            while not self.__is_dialogue_event(prev_event):
                prev_event = subtitle.events[index+index_offset]
                index_offset += 1
                if index-index_offset < 0:
                    # In case the mistake was early on and we
                    # end up going into negative event indexes
                    prev_event = None
                    break

            # We ignore capitalisation errors in case the
            # sentence actually started on the previous line
            if prev_event and (prev_event.text[-1] not in ('.', '?', '!') or
                               prev_event.text.endswith('...')):
                mistakes_list = [x for x in mistakes_list if not
                                 x.ruleId == "UPPERCASE_SENTENCE_START"]

            if len(mistakes_list) > 0:
                subtitle_mistakes.append((index+1, mistakes_list))

        return subtitle_mistakes

    def close(self):
        """ Function to close the LanguageTools server """
        self.tool.close()
