#!/usr/bin/python3
import sys
import os
import re
import hashlib


def parse_heading(line):
    """Parse a line and return the corresponding HTML heading tag."""
    level = 0
    while line.startswith("#"):
        level += 1
        line = line[1:]

    if 1 <= level <= 6:
        line = line.strip()
        return f"<h{level}>{line}</h{level}>"
    return None


def parse_list(lines, index, list_type):
    """Parse lines starting from an index to generate an HTML list."""
    html_lines = [f"<{list_type}>"]
    while index < len(lines) and lines[index].startswith(("- ", "* ")):
        item = lines[index][2:].strip()
        html_lines.append(f"<li>{process_text(item)}</li>")
        index += 1
    html_lines.append(f"</{list_type}>")
    return html_lines, index


def parse_paragraphs(lines):
    """Parse lines and convert them into HTML paragraphs with line breaks."""
    html_lines = []
    paragraph = []

    for line in lines:
        stripped_line = line.strip()
        if stripped_line:
            if paragraph:
                paragraph.append(stripped_line)
            else:
                paragraph = [stripped_line]
        else:
            if paragraph:
                html_lines.append('<p>\n' + process_text
                                  ('\n'.join(paragraph)) + '\n</p>')
                paragraph = []

    if paragraph:
        html_lines.append('<p>\n' + process_text
                          ('\n'.join(paragraph)) + '\n</p>')

    return html_lines


def process_text(text):
    """Process text to replace Markdown bold & italic syntax with HTML tag."""
    # Replace **text** with <b>text</b>
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    # Replace __text__ with <em>text</em>
    text = re.sub(r'__(.*?)__', r'<em>\1</em>', text)
    # Convert [[text]] to MD5 hash
    text = re.sub(r'\[\[(.*?)\]\]',
                  lambda m: hashlib.md5(m.group(1).encode()).hexdigest(),
                  text)
    # Remove all 'c' characters from ((text))
    text = re.sub(r'\(\((.*?)\)\)',
                  lambda m: m.group(1).replace('c', '').replace('C', ''),
                  text)
    return text


def convert_markdown_to_html(input_file, output_file):
    """Convert a Markdown file to an HTML file."""
    with open(input_file, 'r') as md_file:
        lines = md_file.readlines()

    with open(output_file, 'w') as html_file:
        index = 0
        while index < len(lines):
            line = lines[index].strip()

            if line.startswith("#"):
                html_line = parse_heading(line)
                if html_line:
                    html_file.write(html_line + '\n')

            elif line.startswith("- "):
                list_lines, index = parse_list(lines, index, "ul")
                html_file.write("\n".join(list_lines) + '\n')
                continue  # Skip the increment as it's already handled

            elif line.startswith("* "):
                list_lines, index = parse_list(lines, index, "ol")
                html_file.write("\n".join(list_lines) + '\n')
                continue  # Skip the increment as it's already handled

            elif line == "":
                index += 1
                continue  # Skip empty lines in the main loop

            else:
                # Collect all remaining lines as paragraphs
                paragraph_lines, index = parse_paragraphs(lines[index:])
                html_file.write("\n".join(paragraph_lines) + '\n')
                break  # End processing as paragraphs should be the last thing

            index += 1


if __name__ == "__main__":
    # Check for the correct number of arguments
    if len(sys.argv) < 3:
        print("Usage: ./markdown2html.py README.md README.html",
              file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Check if the Markdown file exists
    if not os.path.exists(input_file):
        print(f"Missing {input_file}", file=sys.stderr)
        sys.exit(1)

    # Convert Markdown to HTML
    convert_markdown_to_html(input_file, output_file)

    # Exit silently with success
    sys.exit(0)
