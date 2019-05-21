from . import csv
import re


class SectionConfigReader:
    def __init__(self, config):
        self.config = list(config)
        sections = {}
        regex = re.compile(r'\[[a-z0-9]+\]', re.IGNORECASE)
        prev_idx = 0
        prev_section = None
        for idx, line in enumerate(self.config):
            if len(line) == 1 and regex.match(line[0]):
                sections[prev_section] = slice(prev_idx + 1 if prev_idx != 0 else 0, idx)
                prev_idx = idx
                prev_section = line[0][1:-1]

        sections[prev_section] = slice(prev_idx + 1, idx + 1)
        self.sections = sections

    def __iter__(self):
        return iter(self.config)

    def __getitem__(self, k):
        return self.config[self.sections[k]]

    def __contains__(self, item):
        return item in self.sections


def reader(file):
    csvreader = csv.reader(file, 'whitespace')
    sectionreader = SectionConfigReader(csvreader)
    return sectionreader
