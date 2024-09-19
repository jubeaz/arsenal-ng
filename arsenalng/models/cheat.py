#!/usr/bin/python3
from pathlib import Path

from docutils.parsers import rst
from docutils.utils import new_document
from docutils.frontend import OptionParser
from docutils import nodes

from yaml import load as yml_load, FullLoader
import re


class Cheat:
    name = ""
    str_title = ""
    titles = []
    filename = ""
    tags = ""
    command_tags = {}
    command = ""
    printable_command = ""
    description = ""
    variables = dict()
    command_capture = False
    rate = 0

    def is_done(self):
        return self.name != "" and self.command != "" and not self.command_capture

    def inline_cheat(self):
        return "{}{}{}".format({self.tags}, {self.name}, {self.command})

    def get_rating(self):
        # Rating
        rate = ""
        for i in range(0, 5):
            if self.rate <= i:
                rate += "★"
            else:
                rate += "⭐"
        return rate

    def get_tags(self):
        tags_dict = {"target/local": "Loc",
                     "target/remote": "Rem",
                     "target/serve": "Ser",
                     "plateform/linux": "[L] ",
                     "plateform/windows": "[W] ",
                     "plateform/mac": "[M] ",
                     "plateform/multiple": "[*] "}

        tag_string = ""
        if self.command_tags is not None:
            for tag_key in self.command_tags.keys():
                tag = tag_key + "/" + self.command_tags[tag_key]
                if tag in tags_dict.keys():
                    tag_string += "" + tags_dict[tag]
                elif "cat/" in tag:
                    tag_string += " " + tag.split("cat/")[1].upper().strip()
                # else:
                #     tag_string += "|" + tag.lower().strip()
        return tag_string


class ArsenalRstVisitor(nodes.GenericNodeVisitor):
    def __init__(self, document, cheats):
        self.cheats = cheats
        super().__init__(document)

    def default_visit(self, node):
        # Previous cheat completed ? -> Create a new one
        if self.cheats.current_cheat.is_done():
            self.cheats.end_cheat()
            self.cheats.new_cheat()

    def visit_section(self, node):
        """Cheats and titles"""
        # if no cmd but description use description as the command
        if self.cheats.current_cheat.command == "" and \
                self.cheats.current_cheat.description != "":
            self.cheats.current_cheat.command = self.cheats.current_cheat.description.replace("\n", ";\\\n")
            self.cheats.current_cheat.description = ""
            self.cheats.end_cheat()
            self.cheats.new_cheat()
        # Parsing is based on sections (delimited by titles)
        current = " ".join(node.get("ids"))
        niv = 0
        if isinstance(node.parent, nodes.document):
            self.cheats.firsttitle = current
            self.cheats.titles = [current]
        else:
            parent = " ".join(node.parent.get("ids"))
            niv = self.cheats.titles.index(parent) + 1
            self.cheats.titles = self.cheats.titles[:niv] + [current]
        self.cheats.new_cheat()
        # Set default tag to all titles tree
        self.cheats.current_tags = ", ".join(self.cheats.titles)

    def visit_comment(self, node):
        """Tags"""
        self.cheats.current_tags = node.astext()

    def visit_literal_block(self, node):
        """Commands"""
        self.cheats.current_cheat.command = node.astext().replace("\n", " \\\n")

    def visit_paragraph(self, node):
        """Descriptions, constants and variables"""
        para = node.astext()
        descr = []  # Using mutable objects for string concat
        for line in para.split("\n"):
            # Constants and variables
            if line.startswith("=") or line.startswith("$") and ":" in line:
                varname, varval = [x.strip() for x in line[1:].split(":")]
                if line.startswith("$"):
                    varval = "$({0})".format(varval)
                self.cheats.filevars[varname] = varval
            elif line.endswith(":"):  # Name
                self.cheats.current_cheat.name = line[:-1]
            else:  # Description
                descr += [line]
        # If description list is not empty, convert it to string as description
        # Here we only do this if command has been filled to avoid junk text
        if len(descr) and len(self.cheats.current_cheat.command):
            self.cheats.current_cheat.description = "\n".join(descr)
            # For me descriptions are in paragraphs not title so I use the descr as a name
            self.cheats.current_cheat.name = " ".join(descr)

