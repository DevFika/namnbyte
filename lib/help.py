from textual.widgets import Markdown
from .command import generate_flag_markdown, generate_command_markdown, generate_command_markdown_table
from .command import generate_flag_markdown_table


def generate_general_info():
    """General information about the program."""
    return """\
# Namnbyte

This is a command-line tool for batch renaming files/folders with powerful features like regex, case transformation, prefix/suffix additions, and more.

Built using **Python** and the **Textual** library, this tool offers a flexible and interactive way to manage and rename files/folders.

## Features
- Multiple Renaming Methods: Supports replace, regex-based, index-based renaming, and more.
- Batch Processing: Rename multiple files and folders at once.
- Preview & Apply: Changes are applied in a preview, allowing modifications and confirmation before finalizing.
- Lazy Loading: Dynamically loads files and folders as needed, improving efficiency when handling large directories.

## Disclaimer
Please note that both the program and the documentation are still a work in progress and may contain incomplete or inaccurate information.

---
"""

def generate_general_info_readme():
    """General information about the program."""
    return """\
# Namnbyte
![Batch Renaming Demo](./images/demo.gif)
This is a command-line tool for batch renaming files/folders with powerful features like regex, case transformation, prefix/suffix additions, and more.

Built using **Python** and the **Textual** library, this tool offers a flexible and interactive way to manage and rename files/folders.

## Features
- Multiple Renaming Methods: Supports replace, regex-based, index-based renaming, and more.
- Batch Processing: Rename multiple files and folders at once.
- Preview & Apply: Changes are applied in a preview, allowing modifications and confirmation before finalizing.
- Lazy Loading: Dynamically loads files and folders as needed, improving efficiency when handling large directories.

## Disclaimer
Please note that both the program and the documentation are still a work in progress and may contain incomplete or inaccurate information.

---
"""



def generate_markdown():
    """Compiles the full markdown document."""
    md = generate_general_info()
    md += generate_command_markdown()
    md += generate_flag_markdown()
    return md

def generate_readme_markdown():
    """Compiles the full markdown document."""
    md = generate_general_info_readme()
    md += add_installation()
    md += generate_command_markdown_table()
    md += generate_flag_markdown_table()
    md += add_keybindings()
    md += add_license()
    return md

def add_installation():
    md = """
## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/DevFika/namnbyte.git
   cd namnbyte

2. **Install Dependencies**:
    ```bash
    pip install -r requirements.txt

3. **Usage**:
    ```bash
    python main.py path/to/your/folder

"""
    return md

def add_keybindings():
    """Generates keybindings documentation in markdown format, including command line bindings."""
    md = """
## Keybindings

### General Bindings:
- **1**: Focus on Tree View
- **f1**: Focus on Tree View
- **2**: Focus on File Table
- **f2**: Focus on File Table
- **3**: Focus on Folder Table
- **f3**: Focus on Folder Table
- **4**: Focus on Input Field
- **f4**: Focus on Input Field
- **ctrl+z**: Undo Action
- **ctrl+y**: Redo Action
- **ctrl+q**: Quit

### Table Actions:
- **↻ (Reset)**: Reset the current folder/file name.
- **⏎ (Apply)**: Apply the new folder/file name (confirm change).
- **✓ (Enabled)**: Toggle the folder/file's enabled status.
- **Click on New Name**: Click on the folder/file name to manually edit it.

### Tree Bindings:
- **a**: Expand all
- **c**: Collapse all
- **x**: Disable all
- **e**: Enable all
- **f**: Toggle folder
- **right**: Expand selected
- **left**: Collapse selected
- **ctrl+right**: Expand selected + children
- **ctrl+left**: Collapse selected + children
- **ctrl+down**: Disable selected + children
- **ctrl+up**: Enable selected + children

### Edit Name Screen Bindings:
- **Enter**: Submit current input
- **escape**: Exit

### Command Line Bindings:
- **Enter**: Submit current command/input
- **Up**: Previous command (navigate command history)
- **Down**: Next command (navigate command history)

### Panel Resizing:
- **Click and Drag Separators**: Resize the panels by clicking and dragging the separator between them. This allows you to adjust the layout ratio according to your preferences.

    """
    return md



def add_license():
    md = """
## Contributing
Contributions are welcome! Please open an issue or submit a pull request.

## License
This project is licensed under the MIT License - see the LICENSE file for details.
"""
    return md

def save_markdown_to_file():
    """Generates the markdown and saves it to a README.md file."""
    markdown_content = generate_readme_markdown()  # Generates the markdown content
    with open("README.md", "w", encoding="utf-8") as file:  # Opens the README.md file in write mode
        file.write(markdown_content)  # Writes the markdown content to the file
    print("README.md has been updated!")

if __name__ == "__main__":
    save_markdown_to_file()

EXAMPLE_MARKDOWN = """\
# Markdown Viewer

This is an example of Textual's `MarkdownViewer` widget.


## Features

Markdown syntax and extensions are supported.

- Typography *emphasis*, **strong**, `inline code` etc.
- Headers
- Lists (bullet and ordered)
- Syntax highlighted code blocks
- Tables!

## Tables

Tables are displayed in a DataTable widget.

| Name            | Type   | Default | Description                        |
| --------------- | ------ | ------- | ---------------------------------- |
| `show_header`   | `bool` | `True`  | Show the table header              |
| `fixed_rows`    | `int`  | `0`     | Number of fixed rows               |
| `fixed_columns` | `int`  | `0`     | Number of fixed columns            |
| `zebra_stripes` | `bool` | `False` | Display alternating colors on rows |
| `header_height` | `int`  | `1`     | Height of header row               |
| `show_cursor`   | `bool` | `True`  | Show a cell cursor                 |


## Code Blocks

Code blocks are syntax highlighted, with guidelines.

```python
class ListViewExample(App):
    def compose(self) -> ComposeResult:
        yield ListView(
            ListItem(Label("One")),
            ListItem(Label("Two")),
            ListItem(Label("Three")),
        )
        yield Footer()
```
"""