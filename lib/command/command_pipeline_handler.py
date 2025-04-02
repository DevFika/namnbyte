import shlex
from .rename_functions import *
from ..signal import Signal, InformationSignal
import datetime

commands = {
    "replace": {"args": [{"name": "old_text", "required": True}, {"name": "new_text", "required": False, "default": ""}]},
    "replace-separator": {"args": [{"name": "new_separator", "required": True}]},
    "replace-ext": {"args": [{"name": "old_ext", "required": True}, {"name": "new_ext", "required": True}]},
    "replace-regex": {"args": [{"name": "pattern", "required": True}, {"name": "replacement", "required": True}]},
    "replace-index": {"args": [{"name": "separator", "required": True}, {"name": "index", "required": True}, {"name": "new_text", "required": True}]},
    "swap": {"args": [{"name": "word1", "required": True}, {"name": "word2", "required": True}]},
    "remove": {"args": [{"name": "text", "required": True, "variadic": True}]},
    "remove-repeating-connected": {"args": [{"name": "text", "required": True, "variadic": True}]},
    "remove-numbers": {"args": []},
    "remove-non-ascii": {"args": []},
    "remove-leading": {"args": [{"name": "text", "required": True}]},
    "remove-trailing": {"args": [{"name": "text", "required": True}]},
    "case": {"args": [{"name": "style", "required": True}]},
    "zeros": {"args": [{"name": "add/remove", "required": True}, {"name": "num_zeros", "required": False, "default": 2}]},
    "prefix": {"args": [{"name": "text_", "required": True}]},
    "suffix": {"args": [{"name": "_text", "required": True}]},
    "clean": {"args": []},
    "reverse": {"args": []},
    "add-separators": {"args": [{"name": "separator", "required": False, "default": "_"}]},
    "add-timestamp": {"args": [{"name": "granularity", "required": False, "default": "day"}, {"name": "separator", "required": False, "default": "_"}]},
    "resolution-add": {"args": [{"name": "type", "required": False, "default": "tag"}]},
    "resolution-remove": {"args": [{"name": "type", "required": False, "default": "tag"}]},
    "img-info-add": {"args": []},
    "reset": {"args": []},
    "normalize": {"args": []},
    "remove-repeating-words": {"args": []},
    "limit-length": {"args": [{"name": "max", "required": True}]},
}

command_info = {
    "replace": {
        "description": "Replaces occurrences of `old_text` with `new_text`.",
        "usage": "replace old_text new_text",
        "example": "replace apple banana  →  file_apple.txt → file_banana.txt",
    },
    "replace-separator": {
        "description": "Replaces the current separator with a new one.",
        "usage": "replace-separator new_separator",
        "example": "replace-separator -  →  file_name.txt → file-name.txt",
    },
    "replace-ext": {
        "description": "Replaces the old extension with a new extension.",
        "usage": "replace-ext old_ext new_ext",
        "example": "replace-ext txt pdf  →  file.txt → file.pdf",
    },
    "replace-regex": {
        "description": "Replaces occurrences of a pattern with a replacement using regex.",
        "usage": "replace-regex pattern replacement",
        "example": "replace-regex '\d' X  →  123_file.txt → XXX_file.txt",
    },
    "replace-index": {
        "description": "Replaces the text at a specific index, separated by a given separator.",
        "usage": "replace-index separator index new_text",
        "example": "replace-index _ 2 new_text  →  file_part1_part2.txt → file_part1_new_text.txt",
    },
    "swap": {
        "description": "Swaps the occurrences of two words in filenames.",
        "usage": "swap word1 word2",
        "example": "swap apple banana  →  apple_banana.txt → banana_apple.txt",
    },
    "remove": {
        "description": "Removes the given text from filenames.",
        "usage": "remove text1 text2 ...",
        "example": "remove temp_  →  temp_report.txt → report.txt",
    },
    "remove-repeating-connected": {
        "description": "Removes repeating connected words from filenames.",
        "usage": "remove-repeating-connected text1 text2 ...",
        "example": "remove-repeating-connected test  →  testtest.txt → test.txt",
    },
    "remove-numbers": {
        "description": "Removes all numbers from filenames.",
        "usage": "remove-numbers",
        "example": "remove-numbers  →  file123.txt → file.txt",
    },
    "remove-non-ascii": {
        "description": "Removes non-ASCII characters from filenames.",
        "usage": "remove-non-ascii",
        "example": "remove-non-ascii  →  file_éxample.txt → file_example.txt",
    },
    "remove-leading": {
        "description": "Removes leading text from filenames.",
        "usage": "remove-leading text",
        "example": "remove-leading draft_  →  draft_report.txt → report.txt",
    },
    "remove-trailing": {
        "description": "Removes trailing text from filenames.",
        "usage": "remove-trailing text",
        "example": "remove-trailing _draft  →  report_draft.txt → report.txt",
    },
    "case": {
    "description": "Changes the case of the text in filenames. You can choose from various styles.",
    "usage": "case style",
    "example": "case upper  →  file.txt → FILE.TXT",
    "options": [
        "upper: Converts text to uppercase.",
        "lower: Converts text to lowercase.",
        "snake: Converts text to snake_case.",
        "camel: Converts text to camelCase.",
        "pascal: Converts text to PascalCase.",
        "kebab: Converts text to kebab-case.",
        "title: Converts text to title case.",
        "flip: Flips the case of each letter.",
        "capitalize: Capitalizes the first letter of each word.",
        "dot: Converts text to dot.case.",
        "title-snake: Converts text to Title_Snake_Case."
        ]
    },
    "zeros": {
        "description": "Adds or removes leading zeros in filenames.",
        "usage": "zeros add/remove num_zeros",
        "example": "zeros add 3  →  file1.txt → file001.txt",
    },
    "prefix": {
        "description": "Adds a prefix to the filenames.",
        "usage": "prefix text_",
        "example": "prefix new_  →  file.txt → new_file.txt",
    },
    "suffix": {
        "description": "Adds a suffix to the filenames.",
        "usage": "suffix _text",
        "example": "suffix _new  →  file.txt → file_new.txt",
    },
    "clean": {
        "description": "Cleans the filenames by removing unnecessary characters.",
        "usage": "clean",
        "example": "clean  →  file_ name.txt → file_name.txt",
    },
    "reverse": {
        "description": "Reverses the order of characters in filenames.",
        "usage": "reverse",
        "example": "reverse  →  file.txt → elif.txt",
    },
    "add-separators": {
        "description": "Adds separators to the filenames.",
        "usage": "add-separators separator",
        "example": "add-separators _  →  fileText.txt → file_Text.txt",
    },
    "add-timestamp": {
        "description": "Adds a timestamp to the filenames with a specified granularity and separator. You can choose from predefined granularities or use a custom format for the timestamp.",
        "usage": "add-timestamp granularity separator",
        "example": "add-timestamp day _  →  file.txt → file_2025-03-28.txt",
        "options": [
            "year: Adds the year (e.g., 2025)",
            "month: Adds the year and month (e.g., 202503)",
            "day: Adds the full date (e.g., 20250328)",
            "hour: Adds the date and hour (e.g., 20250328_15)",
            "minute: Adds the date and minute (e.g., 20250328_1530)",
            "second: Adds the full date and time with seconds (e.g., 20250328_153045)",
            "custom: A custom format using the strftime syntax (e.g., '%Y%m%d_%H%M')"
        ]
    },
    "resolution-add": {
        "description": "Adds a resolution tag to the filenames.",
        "usage": "resolution-add type",
        "example": "resolution-add tag  →  file.png → file_2k.png",
    },
    "resolution-remove": {
        "description": "Removes a resolution tag from the filenames.",
        "usage": "resolution-remove type",
        "example": "resolution-remove exact  →  file_600x100.png → file.png",
    },
    "img-info-add": {
        "description": "Adds image metadata to the filenames.",
        "usage": "img-info-add",
        "example": "img-info-add  →  file.txt → file_imginfo.txt",
    },
    "reset": {
        "description": "Resets the filenames to their original state.",
        "usage": "reset",
        "example": "reset  →  file.txt → file_original.txt",
    },
    "normalize": {
        "description": "Normalize filenames by collapsing repeated spaces, underscores, dashes, and dots.",
        "usage": "normalize",
        "example": "normalize  →  file__test.txt → file_test.txt",
    },
    "remove-repeating-words": {
        "description": "Removes repeating words in filenames.",
        "usage": "remove-repeating-words",
        "example": "remove-repeating-words  →  file_report_report.txt → file_report.txt",
    },
    "limit-length": {
        "description": "Limits the length of the filenames to a maximum number of characters.",
        "usage": "limit-length max",
        "example": "limit-length 10  →  this_is_a_long_filename.txt → this_is.txt",
    },
}




flags = {
    "ext": {"args": [{"name": "type", "required": True}]},
    "regex": {"args": [{"name": "pattern", "required": True}]},
    "prefix": {"args": [{"name": "prefix", "required": True}]},
    "size": {"args": [{"name": "min_size", "required": False}, {"name": "max_size", "required": False}]},
    "date": {"args": [{"name": "min_date", "required": False}, {"name": "max_date", "required": False}]},
    "ignore-extension": {"args": []},
    "preserve-caps": {"args": []},
    "split-numbers": {"args": []},
    "apply": {"args": []},
    "apply-all": {"args": []},
    "enable-pattern": {"args": [{"name": "*_pattern*", "required": True}]},
    "disable-pattern": {"args": [{"name": "*_pattern*", "required": True}]},
    "enable-regex": {"args": [{"name": "regex", "required": True}]},
    "disable-regex": {"args": [{"name": "regex", "required": True}]},
    "enable-ext": {"args": [{"name": "ext", "required": True}]},
    "disable-ext": {"args": [{"name": "ext", "required": True}]},
    "enable-all": {"args": []},
    "disable-all": {"args": []},
    "reset-all": {"args": []},
}

flags_info = {
    "ext": {
        "description": "",
        "usage": "",
        "example": "",
    },
    "regex": {
        "description": "",
        "usage": "",
        "example": "",
    },
    "prefix": {
        "description": "",
        "usage": "",
        "example": "",
    },
    "size": {
        "description": "",
        "usage": "",
        "example": "",
    },
    "date": {
        "description": "",
        "usage": "",
        "example": "",
    },
    "ignore-extension": {
        "description": "",
        "usage": "",
        "example": "",
    },
    "preserve-caps": {
        "description": "",
        "usage": "",
        "example": "",
    },
    "split-numbers": {
        "description": "",
        "usage": "",
        "example": "",
    },
    "apply": {
        "description": "",
        "usage": "",
        "example": "",
    },
    "apply-all": {
        "description": "",
        "usage": "",
        "example": "",
    },
    "enable-pattern": {
        "description": "",
        "usage": "",
        "example": "",
    },
    "disable-pattern": {
        "description": "",
        "usage": "",
       "example": "",
    },
    "enable-regex": {
        "description": "",
        "usage": "",
        "example": "",
    },
    "disable-regex": {
        "description": "",
        "usage": "",
        "example": "",
    },
    "enable-ext": {
        "description": "",
        "usage": "",
        "example": "",
    },
    "disable-ext": {
        "description": "",
        "usage": "",
        "example": "",
    },
    "enable-all": {
        "description": "",
        "usage": "",
        "example": "",
    },
    "disable-all": {
        "description": "",
        "usage": "",
        "example": "",
    },
    "reset-all": {
        "description": "",
        "usage": "",
        "example": "",
    },
}


def generate_command_markdown():
    """Generates markdown documentation for commands in a structured, compact format, sorted alphabetically."""
    md = "## Command Reference\n\n"
    
    for cmd in sorted(commands.keys()):  # Sorts commands alphabetically
        info = command_info.get(cmd, {})
        description = info.get("description", "No description available.")
        usage = info.get("usage", "No usage info")
        example = info.get("example", "No example provided")
        options = info.get("options", None)

        # Replace line breaks in description and example if needed
        description = description.replace("\n", " ")  # Single line for description
        example = example.replace("\n", " ")  # Single line for example

        md += f"""
### **-{cmd}**

{description}

**Usage:** `{usage}`

**Example:** `{example}`

"""
        
        # If options are available, display them
        if options:
            md += "\n**Available Options:**\n"
            for option in options:
                md += f"- {option}\n"
        
        # Add a divider between each command
        md += "\n---\n"

    return md

def generate_command_markdown_table():
    """Generates a compact table markdown documentation for commands, sorted alphabetically, including options."""
    md = "## Command Reference\n\n"
    md += "| Command | Description | Usage | Example | Options |\n"
    md += "| ------- | ----------- | ----- | ------- | ------- |\n"
    
    for cmd in sorted(commands.keys()):  # Sorts commands alphabetically
        info = command_info.get(cmd, {})
        description = info.get("description", "No description available.")
        usage = info.get("usage", "No usage info")
        example = info.get("example", "No example provided")
        options = info.get("options", None)

        # Ensure single-line descriptions and examples
        description = description.replace("\n", " ")
        example = example.replace("\n", " ")

        # Format options if available
        options_str = ", ".join(options) if options else ""

        # Add each command, description, usage, example, and options to the table
        md += f"| **-{cmd}** | {description} | `{usage}` | `{example}` | {options_str} |\n"
        
    return md





def generate_flag_markdown():
    """Generates markdown documentation for flags in a structured, compact format, sorted alphabetically."""
    md = "## Flag Reference\n\n"
    
    for flag in sorted(flags.keys()):  # Sorts flags alphabetically
        info = flags_info.get(flag, {})
        description = info.get("description", "No description available.")
        usage = info.get("usage", "No usage info")

        # Replace line breaks in description if needed
        description = description.replace("\n", " ")  # Single line for description

        md += f"""
### **--{flag}**

{description}

**Usage:** `{usage}`

---
"""
    return md


def generate_flag_markdown_table():
    """Generates a compact table markdown documentation for flags, sorted alphabetically."""
    md = "## Flag Reference\n\n"
    md += "| Flag        | Description               | Usage               |\n"
    md += "| ----------- | ------------------------- | ------------------- |\n"
    
    for flag in sorted(flags.keys()):  # Sorts flags alphabetically
        info = flags_info.get(flag, {})
        description = info.get("description", "No description available.")
        usage = info.get("usage", "No usage info")

        # Replace line breaks in description if needed
        description = description.replace("\n", " ")  # Single line for description

        # Add each flag, description, and usage in the table
        md += f"| **--{flag}** | {description} | `{usage}` |\n"
        
    return md



class CommandPipelineHandler:
    def __init__(self):
        # self.input_command = input_command
        self.command_history = []
        self.history_index = -1
        self.flags = set()
        self.process_steps = []
        self.information_signal = InformationSignal()
        self.task_request_signal = Signal()

    def get_input_command(self, input_command):
        self.input_command = input_command

    def process_input(self, input_command, state):
        # Set the input command
        self.get_input_command(input_command)
        if input_command != "" and (len(self.command_history) == 0 or self.command_history[-1] != input_command):
            self.command_history.append(input_command)
            self.history_index = len(self.command_history)
        self.process_steps = []
        
        # Try parsing and preparing the pipeline, and validate
        try:
            self.parse_and_prepare_pipeline()
        except Exception as e:
            self.information_signal.emit_error(f"Error {e}")
            print(f"Error while parsing or preparing pipeline: {e}")
            return False  # Stop the processing if there's an error

        # If the pipeline preparation was successful, process the file names
        try:
            self.process_file_names(state)
        except Exception as e:
            self.information_signal.emit_error(f"Error while processing file names: {e}")
            print(f"Error while processing file names: {e}")
            print(f"Error while processing file names: {e}")
            print(f"Error while processing file names: {e}")
            return False  # Stop the processing if there's an error

        return True  # If everything succeeds, return True

    def parse_and_prepare_pipeline(self):
        try:
            # Use shlex.split to safely split the command into parts
            parts = shlex.split(self.input_command)
            
            # Process the flags and arguments
            self.flags, cleaned_parts = self._preprocess_flags(parts)
            commands_args = self._parse_commands(cleaned_parts)
            if not commands_args:
                self.information_signal.emit_error(f"No command entered")
                # self.(f"No command entered")
                return None

            for command, args in commands_args:
                command_name = command.lstrip('-')
                
                if command_name not in commands:
                    self.information_signal.emit_error(f"Unknown command: {command_name}")
                    print(f"Unknown command: {command_name}")
                    continue

                expected_args = commands[command_name]["args"]
                filled_args = self._fill_arguments(args, expected_args)

                step = self._create_process_step(command_name, filled_args)
                self.process_steps.append(step)

            if not self.process_steps:
                self.information_signal.emit_error(f"No command entered")

        except ValueError as e:
            self.information_signal.emit_error(f"Error while processing file names: {e}")

    def _preprocess_flags(self, parts):
        flags = {}
        cleaned_parts = []
        i = 0

        while i < len(parts):
            part = parts[i]

            if part.startswith("--"):
                flag_name = part.lstrip("-")
                if flag_name not in flags:
                    flags[flag_name] = []

                flag_spec = self._get_flag_spec(flag_name)

                if flag_spec:
                    for arg_spec in flag_spec.get("args", []):
                        i += 1
                        if i < len(parts):
                            flags[flag_name].append(parts[i])
                        elif arg_spec["required"]:
                            self.information_signal.emit_error(f"Missing required argument for flag: --{flag_name}")
                            raise ValueError(f"Missing required argument for flag: --{flag_name}")

                elif flag_name in flags:  # Simple flag with no args
                    flags[flag_name] = True  # Set simple flags to True for presence
                else:
                    flags[flag_name] = True  # If it's not defined, assume simple flag

            else:
                cleaned_parts.append(part)

            i += 1

        return flags, cleaned_parts


    def _get_flag_spec(self, flag_name):
        return flags.get(flag_name, None)

    def _parse_commands(self, parts):
        commands_args = []
        current_command = None
        current_args = []

        for part in parts:
            if part.startswith("-") and len(part) > 1:  # Detect command
                if current_command:
                    commands_args.append((current_command, current_args))
                current_command = part
                current_args = []
            else:
                current_args.append(part)

        if current_command:
            commands_args.append((current_command, current_args))

        return commands_args

    def _fill_arguments(self, provided_args, expected_args):
        filled_args = []
        index = 0

        for arg_info in expected_args:
            if arg_info.get("variadic", False):  # Handle variadic arguments
                filled_args.append(provided_args[index:])  # Capture remaining args as a list
                break  # Stop processing more args
            elif index < len(provided_args):
                filled_args.append(provided_args[index])
                index += 1
            elif not arg_info["required"]:
                filled_args.append(arg_info.get("default", ""))
            else:
                self.information_signal.emit_error(f"Missing required argument: {arg_info['name']}")
                print(f"Missing required argument: {arg_info['name']}")
                return None

        return filled_args


    def _create_process_step(self, command_name, args):
        def step(filename, path, current_name, state):
            return self._process_filename(filename, command_name, args, path, current_name, state)
        return step

    # TODO: Validate input
    def _process_filename(self, name, command_name, values, path=None, current_name="", state="file"):
        ignore_extension = "ignore-extension" in self.flags
        preserve_caps = "preserve-caps" in self.flags
        split_numbers = "split-numbers" in self.flags

        if state == "folder":
            ignore_extension = True

        if values is None:
            self.information_signal.emit_error(f"Error: Invalid arguments for command '{command_name}'. Skipping file processing.")
            print(f"Error: Invalid arguments for command '{command_name}'. Skipping file processing.")
            return name

        try:
            if command_name == "case":
                style = values[0].lower()
                if style == "upper":
                    return to_uppercase(name, ignore_extension)
                elif style == "lower":
                    return to_lowercase(name, ignore_extension, preserve_caps)
                elif style == "snake":
                    return to_snake_case(name, ignore_extension, preserve_caps, split_numbers=split_numbers)
                elif style == "camel":
                    return to_camel_case(name, ignore_extension, preserve_caps, split_numbers=split_numbers)
                elif style == "pascal":
                    return to_pascal_case(name, ignore_extension, preserve_caps, split_numbers=split_numbers)
                elif style == "kebab":
                    return to_kebab_case(name, ignore_extension, preserve_caps, split_numbers=split_numbers)
                elif style == "title":
                    return to_title_case(name, ignore_extension, preserve_caps, split_numbers=split_numbers)
                elif style == "flip":
                    return flip_case(name, ignore_extension)
                elif style == "capitalize":
                    return to_capitalize(name, ignore_extension, preserve_caps)
                elif style == "dot":
                    return to_dot_case(name, ignore_extension, preserve_caps, split_numbers=split_numbers)
                # elif style == "train":
                #     return to_train_case(name, ignore_extension, preserve_caps)
                elif style == "title-snake":
                    return to_capitalized_snake_case(name, ignore_extension, preserve_caps, split_numbers=split_numbers)

            elif command_name == "zeros":
                style = values[0].lower()
                if style == "add":
                    return add_leading_zeros_to_number(name,values[1], ignore_extension)
                elif style == "remove":
                    return remove_leading_zeros(name, ignore_extension)
                
            elif command_name == "prefix":
                return prefix_add(name, values[0], ignore_extension)
            elif command_name == "suffix":
                return suffix_add(name, values[0], ignore_extension)
            
            elif command_name == "clean":
                return clean_filename(name, ignore_extension)

            elif command_name == "replace":
                old_text, new_text = values
                return replace_in_filename(name, old_text, new_text, ignore_extension)
            elif command_name == "replace-separator":
                new_separator = values[0]
                return replace_separator(name, new_separator, ignore_extension)
            elif command_name == "replace-regex":
                pattern = values[0]
                replacement = values[1]
                return regex_replace_in_filenames(name, pattern, replacement, ignore_extension)
            elif command_name == "replace-ext":
                return regex_replace_in_filenames(name, r'\.' + re.escape(values[0]) + '$', '.' + values[1], True)
            elif command_name == "replace-index":
                return replace_word_by_index(name, values[0], int(values[1]), values[2], ignore_extension)
            elif command_name == "swap":
                return swap_words(name, values[0], values[1], ignore_extension)

            elif command_name == "remove":
                if isinstance(values[0], list):
                    values = values[0]
                return remove_in_filename(name, values, ignore_extension)
            elif command_name == "remove-repeating-connected":
                if isinstance(values[0], list):
                    values = values[0]
                return remove_connected_repeating_input(name, values, ignore_extension)
            elif command_name == "remove-numbers":
                return remove_numbers(name, ignore_extension)
            elif command_name == "remove-special":
                return remove_special_characters(name, ignore_extension)
            elif command_name == "remove-non-ascii":
                return remove_non_ascii(name, ignore_extension)
            elif command_name == "remove-leading":
                return remove_leading(name, values, ignore_extension)
            elif command_name == "remove-trailing":
                return remove_trailing(name, values, ignore_extension)
            elif command_name == "remove-repeating-words":
                return remove_duplicate_words(name, ignore_extension)
            
            elif command_name == "reverse":
                return reverse_string(name, ignore_extension)
            
            elif command_name == "add-timestamp":
                return add_timestamp(name=name, granularity=values[0], separator=values[1], ignore_extension=ignore_extension)
            elif command_name == "add-separators":
                return add_separators(name=name, separator=values[0], ignore_extension=ignore_extension, split_numbers=split_numbers)
            
            elif command_name == "resolution-add":
                return add_resolution(name=name, values=values, ignore_extension=ignore_extension, path=path)
            elif command_name == "resolution-remove":
                return remove_resolution(file_name=name, type=values, ignore_extension=ignore_extension)
            elif command_name == "img-info-add":
                return add_image_info(name=name, values=values, ignore_extension=ignore_extension, path=path)
            
            elif command_name == "reset":
                return current_name
            elif command_name == "normalize":
                return normalize_filename(name=name, ignore_extension=ignore_extension)
            elif command_name == "limit-length":
                return limit_filename_length(name=name, max_length=int(values[0]), ignore_extension=ignore_extension)
            return name
        except Exception as e:
            self.information_signal.emit_error(f"{e}")
            raise

    def process_file_names(self, state):
        filters = self._extract_filters_from_flags()

        # Handle the "enable-all" and "disable-all" directly through flags.
        if "enable-all" in self.flags:
            self.task_request_signal.emit({"type": "enable-all", "state": state})
        elif "disable-all" in self.flags:
            self.task_request_signal.emit({"type": "disable-all", "state": state})

        if "reset-all" in self.flags:
            self.task_request_signal.emit({"type": "reset-all", "state": state})

        # Handle enable/disable based on specific patterns, regex, extensions, etc.
        if "enable-pattern" in self.flags:
            pattern = self.flags["enable-pattern"][0]
            self.task_request_signal.emit({"type": "enable-pattern", "pattern": pattern, "state": state})
        elif "disable-pattern" in self.flags:
            pattern = self.flags["disable-pattern"][0]
            self.task_request_signal.emit({"type": "disable-pattern", "pattern": pattern, "state": state})

        if "enable-regex" in self.flags:
            regex = self.flags["enable-regex"][0]
            self.task_request_signal.emit({"type": "enable-regex", "regex": regex, "state": state})
        elif "disable-regex" in self.flags:
            regex = self.flags["disable-regex"][0]
            self.task_request_signal.emit({"type": "disable-regex", "regex": regex, "state": state})

        if "enable-ext" in self.flags:
            ext = self.flags["enable-ext"][0]
            self.task_request_signal.emit({"type": "enable-ext", "extension": ext, "state": state})
        elif "disable-ext" in self.flags:
            ext = self.flags["disable-ext"][0]
            self.task_request_signal.emit({"type": "disable-ext", "extension": ext, "state": state})

        self.task_request_signal.emit({"type": "process-file-names", "filters": filters, "pipeline": self._pipeline_callable, "state": state})

        if "apply-all" in self.flags:
            self.task_request_signal.emit({"type": "request_apply_names", "scope": "all", "state": state})
        elif "apply" in self.flags:
            self.task_request_signal.emit({"type": "request_apply_names", "scope": "enabled", "state": state})


    def _pipeline_callable(self, new_name, abs_path, current_name, state):
        for step in self.process_steps:
            new_name = step(new_name, abs_path, current_name, state)
        return new_name
    
    def _extract_filters_from_flags(self):
        filters = {}

        # Check for the "ext" flag (can support multiple extensions)
        if "ext" in self.flags:
            extensions = self.flags["ext"]
            filters["ext"] = extensions  # List of extensions

        # Check for the "regex" flag (supporting regex filtering if provided)
        if "regex" in self.flags:
            regex_pattern = self.flags["regex"][0]
            filters["regex"] = regex_pattern

        # Check for the "prefix" flag (can support prefix filtering)
        if "prefix" in self.flags:
            prefix_value = self.flags["prefix"][0]
            filters["prefix"] = prefix_value

        # Check for the "size" flag (supports size filtering as a tuple of (min_size, max_size))
        if "size" in self.flags:
            size_values = self.flags["size"]
            min_size = int(size_values[0]) if size_values[0] else None
            max_size = int(size_values[1]) if size_values[1] else None
            filters["size"] = (min_size, max_size)

        # Check for the "date" flag (supports date filtering)
        if "date" in self.flags:
            date_values = self.flags["date"]
            min_date = datetime.strptime(date_values[0], "%Y-%m-%d") if date_values[0] else None
            max_date = datetime.strptime(date_values[1], "%Y-%m-%d") if date_values[1] else None
            filters["date"] = (min_date, max_date)

        # Add other flag-based filters as needed (e.g., file name patterns, date filters, etc.)
        if "ignore-extension" in self.flags:
            filters["ignore_extension"] = True

        return filters
    
    def get_previous_command(self):
        """Returns the previous command in the history, if any."""
        if self.history_index > 0:
            self.history_index -= 1
            return self.command_history[self.history_index]
        self.history_index = -1
        return ""
        return self.command_history[0]  # If at the start, return the first command

    def get_next_command(self):
        """Returns the next command in the history, if any."""
        if len(self.command_history) == 0:
            return None
        if self.history_index < len(self.command_history) - 1:
            self.history_index += 1
            return self.command_history[self.history_index]
        return self.command_history[-1]  # If at the end, return the last command

    def get_latest_command(self):
        """Returns the most recent command in history."""
        if self.command_history:
            return self.command_history[-1]
        return None  # No commands in history

    def reset_history(self):
        """Reset the history index to the latest command."""
        if self.command_history:
            self.history_index = len(self.command_history) - 1
            return self.command_history[self.history_index]
        return None  # No history to reset

    def clear_history(self):
        """Clear command history."""
        self.command_history = []
        self.history_index = -1