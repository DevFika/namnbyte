import os
import re
from datetime import datetime

# Keep this
from ..image_info import add_image_info, add_resolution, remove_resolution

## Case
def to_uppercase(name, ignore_extension):
    """Convert filename to uppercase."""
    if ignore_extension:
        new_name = name.upper()
    else:
        base_name, ext = os.path.splitext(name)
        new_name = base_name.upper() + ext
    return new_name

def to_lowercase(name, ignore_extension, preserve_caps=False):
    """Convert filename to lowercase, optionally preserving fully uppercase words."""
    if ignore_extension:
        base_name, ext = name, ""
    else:
        base_name, ext = os.path.splitext(name)

    if preserve_caps:
        # Preserve fully uppercase substrings (not split into words)
        new_name = _preserve_caps_transform(base_name, str.lower)
    else:
        new_name = base_name.lower()

    return new_name + ext

def to_train_case(name, ignore_extension, preserve_caps=False, split_numbers=False):
    """Converts to train case: words separated by hyphens, like Pascal case but with hyphens."""
    name, ext = _split_extension(name) if not ignore_extension else (name, "")
    words = _split_into_words(name, split_numbers=split_numbers)

    if not preserve_caps:
        words = [word.lower() for word in words]
    else:
        words = [word if word.isupper() else word.lower() for word in words]

    return '-'.join(words) + ext

def to_capitalized_snake_case(name, ignore_extension, preserve_caps=False, split_numbers=False):
    """Convert to snake_case with each word capitalized (e.g., My_Variable_Name)."""
    name, ext = _split_extension(name) if not ignore_extension else (name, "")
    words = _split_into_words(name, split_numbers=split_numbers)

    if not preserve_caps:
        words = [word.capitalize() for word in words]  # Capitalize each word
    else:
        words = [word if word.isupper() else word.capitalize() for word in words]

    return '_'.join(words) + ext

def to_dot_case(name, ignore_extension, preserve_caps=False, split_numbers=False):
    name, ext = _split_extension(name) if not ignore_extension else (name, "")
    words = _split_into_words(name, split_numbers=split_numbers)

    if not preserve_caps:
        words = [word.lower() for word in words]
    else:
        words = [word if word.isupper() else word.lower() for word in words]

    return '.'.join(words) + ext

def _to_lowercase(name, ignore_extension):
    """Convert filename to lowercase."""
    if ignore_extension:
        new_name = name.lower()
    else:
        base_name, ext = os.path.splitext(name)
        new_name = base_name.lower() + ext
    return new_name

import os

def to_capitalize(name, ignore_extension, preserve_caps=False):
    """
    Capitalize the first letter of each alphanumeric segment, preserving all separators.
    Fully-uppercase words are preserved if preserve_caps=True.
    """
    if ignore_extension:
        base_name, ext = name, ""
    else:
        base_name, ext = os.path.splitext(name)

    result = []
    word = []
    is_new_word = True  # Start with new word logic (first letter capitalization)

    for char in base_name:
        if char.isalnum():  # part of a word
            if is_new_word:
                if preserve_caps and char.isupper() and base_name.isupper():
                    # If whole word is uppercase, preserve it (check later in full word)
                    word.append(char)
                else:
                    word.append(char.upper())
                is_new_word = False
            else:
                word.append(char)
        else:  # separator
            if word:
                full_word = ''.join(word)
                if preserve_caps and full_word.isupper():
                    result.append(full_word)
                else:
                    result.append(full_word.capitalize())
                word = []
            result.append(char)
            is_new_word = True  # Next alphanumeric character starts a new word

    # Add any remaining word at the end
    if word:
        full_word = ''.join(word)
        if preserve_caps and full_word.isupper():
            result.append(full_word)
        else:
            result.append(full_word.capitalize())

    return ''.join(result) + ext

def to_snake_case(name, ignore_extension, preserve_caps=False, split_numbers=False):
    name, ext = _split_extension(name) if not ignore_extension else (name, "")
    words = _split_into_words(name, split_numbers=split_numbers)
    
    if preserve_caps:
        # Only preserve fully uppercase words, others are transformed to lowercase
        words = [word if word.isupper() else word.lower() for word in words]
    else:
        # Convert all words to lowercase when preserve_caps is False
        words = [word.lower() for word in words]
    
    return '_'.join(words) + ext

def to_camel_case(name, ignore_extension, preserve_caps=False, split_numbers=False):
    name, ext = _split_extension(name) if not ignore_extension else (name, "")
    words = _split_into_words(name, split_numbers=split_numbers)

    if not preserve_caps:
        # When not preserving caps, make all words lowercase.
        words = [word.lower() for word in words]
    else:
        # When preserving caps, lowercase only non-uppercase words (preserve fully uppercase words).
        words = [word if word.isupper() else word.lower() for word in words]

    # Start with the first word (lowercased), then capitalize the first letter of all other words.
    camel = words[0].lower() + ''.join(word if word.isupper() else word.capitalize() for word in words[1:])
    
    return camel + ext


def to_pascal_case(name, ignore_extension, preserve_caps=False, split_numbers=False):
    name, ext = _split_extension(name) if not ignore_extension else (name, "")
    words = _split_into_words(name, split_numbers=split_numbers)
    
    if not preserve_caps:
        words = [word.lower() for word in words]
    
    # Capitalize first letter of each word (Pascal case), and keep fully uppercase words as they are
    return ''.join(word[0].upper() + word[1:] if not word.isupper() else word for word in words) + ext


def to_kebab_case(name, ignore_extension, preserve_caps=False, split_numbers=False):
    name, ext = _split_extension(name) if not ignore_extension else (name, "")
    words = _split_into_words(name, split_numbers=split_numbers)
    
    if preserve_caps:
        # Only preserve fully uppercase words, others are transformed to lowercase
        words = [word if word.isupper() else word.lower() for word in words]
    else:
        # Convert all words to lowercase when preserve_caps is False
        words = [word.lower() for word in words]
    
    return '-'.join(words) + ext

def to_title_case(name, ignore_extension, preserve_caps=False, split_numbers=False):
    name, ext = _split_extension(name) if not ignore_extension else (name, "")
    words = _split_into_words(name, split_numbers=split_numbers)
    
    if preserve_caps:
        # Keep fully uppercase words as they are, others capitalized
        words = [word if word.isupper() else word.capitalize() for word in words]
    else:
        # Capitalize all words if preserve_caps is not set
        words = [word.capitalize() for word in words]
    
    return ' '.join(words) + ext

def flip_case(name, ignore_extension):
    """Flip uppercase to lowercase and vice versa in the filename."""
    if ignore_extension:
        return name.swapcase()  # Swap case for the whole filename

    base_name, ext = os.path.splitext(name)
    flipped_base_name = base_name.swapcase()  # Swap case only for the base name
    
    return flipped_base_name + ext


## Numbers
def remove_leading_zeros(name, ignore_extension):
    """Remove leading zeros from all numbers in a filename."""
    
    def strip_zeros(match):
        return str(int(match.group()))  # Convert to int and back to remove leading zeros

    if ignore_extension:
        new_name = re.sub(r'\d+', strip_zeros, name)
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = re.sub(r'\d+', strip_zeros, base_name)
        new_name = new_base_name + ext

    return new_name

def add_leading_zeros_to_number(name, total_digits=2, ignore_extension=False):
    """Add leading zeros to numbers in the filename to ensure consistent digit length."""
    try:
        total_digits = int(total_digits)
    except ValueError:
        return name  # Return early if the conversion fails
    
    if ignore_extension:
        new_name = re.sub(r'(\d+)', lambda match: match.group(0).zfill(total_digits), name)
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = re.sub(r'(\d+)', lambda match: match.group(0).zfill(total_digits), base_name)
        new_name = new_base_name + ext
    return new_name


## Prefix Suffix
def prefix_add(name, prefix, ignore_extension):
    """Add a prefix to filenames."""
    if ignore_extension:
        new_name = prefix + name
    else:
        base_name, ext = os.path.splitext(name)
        new_name = prefix + base_name + ext
    return new_name

def suffix_add(name, suffix, ignore_extension):
    """Add a suffix to filenames before the extension."""
    if ignore_extension:
        new_name = name + suffix
    else:
        base_name, ext = os.path.splitext(name)
        new_name = base_name + suffix + ext
    return new_name


## Cleaning
def clean_filename(name, ignore_extension):
    """Remove unwanted characters (e.g., spaces, extra underscores), replacing hyphens with underscores and avoiding repeated underscores."""
    
    if ignore_extension:
        # Clean up: replace multiple spaces/underscores with a single one
        new_name = re.sub(r'[_\s]+', '_', name)  # Replace multiple spaces or underscores with a single underscore
        
        # Remove unwanted characters: keep alphanumeric, _, ., and -
        new_name = re.sub(r'[^a-zA-Z0-9._-]', '', new_name)
        
        # Replace hyphens with underscores
        new_name = re.sub(r'\s?-\s?', '_', new_name)  # Replace hyphens with underscores
        
        # Replace consecutive underscores with a single one
        new_name = re.sub(r'_{2,}', '_', new_name)  # Replace multiple underscores with a single one

    else:
        base_name, ext = os.path.splitext(name)

        # Clean up base name: replace multiple spaces/underscores, remove unwanted characters
        new_base_name = re.sub(r'[_\s]+', '_', base_name)  # Replace multiple spaces or underscores with a single underscore
        new_base_name = re.sub(r'[^a-zA-Z0-9._-]', '', new_base_name)  # Remove non-alphanumeric characters, except _ and -
        
        # Replace hyphens with underscores
        new_base_name = re.sub(r'\s?-\s?', '_', new_base_name)  # Replace hyphens with underscores
        
        # Replace consecutive underscores with a single one
        new_base_name = re.sub(r'_{2,}', '_', new_base_name)  # Replace multiple underscores with a single one

        # If there are spaces after numbers, remove them (e.g., (14))
        new_base_name = re.sub(r'(?<=\d)\s+', '', new_base_name)  # Remove spaces after numbers (e.g., (14))

        new_name = new_base_name + ext  # Add the extension back

    return new_name

## Replace
def replace_in_filename(name, old, new, ignore_extension):
    """Replace old text with new text in filenames."""
    if ignore_extension:
        new_name = name.replace(old, new)
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = base_name.replace(old, new)
        new_name = new_base_name + ext
    return new_name

def replace_separator(name, new_separator, ignore_extension=False):
    """Replace any common separators (., -, _, space) with the new separator."""
    separators = [".", ",", "-", "_", " "]

    if ignore_extension:
        for sep in separators:
            name = name.replace(sep, new_separator)
    else:
        base_name, ext = os.path.splitext(name)
        for sep in separators:
            base_name = base_name.replace(sep, new_separator)
        name = base_name + ext

    return name


def regex_replace_in_filenames(name, pattern, replacement, ignore_extension):
    """Use regex to replace a pattern in filenames."""
    if ignore_extension:
        new_name = re.sub(pattern, replacement, name)
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = re.sub(pattern, replacement, base_name)
        new_name = new_base_name + ext
    return new_name

def replace_word_by_index(name, separator, index, new_text, ignore_extension):
    """Replace the word at the specified index with new text using the specified separator."""
    if ignore_extension:
        parts = name.split(separator)
        if 0 <= index < len(parts):
            parts[index] = new_text
        new_name = separator.join(parts)
    else:
        base_name, ext = os.path.splitext(name)
        parts = base_name.split(separator)
        if 0 <= index < len(parts):
            parts[index] = new_text
        new_base_name = separator.join(parts)
        new_name = new_base_name + ext
    return new_name

def swap_words(name, word1, word2, ignore_extension):
    """Swap two words in a filename while preserving existing separators and formatting."""
    if ignore_extension:
        base_name = name
    else:
        base_name, ext = os.path.splitext(name)

    # Split the base name into words and separators
    words_and_separators = _split_words_and_separators(base_name)

    # Swap word1 and word2 in the list of words
    words_and_separators = [
        word2 if item == word1 else word1 if item == word2 else item
        for item in words_and_separators
    ]

    # Rebuild the name from the swapped words and preserved separators
    new_name = "".join(words_and_separators)

    return new_name + (ext if not ignore_extension else "")


def _split_words_and_separators(name):
    """Split the filename into words and separators (spaces, dashes, underscores, etc.)"""
    # This regex captures words and separators (non-alphanumeric characters)
    split_pattern = r'([a-zA-Z0-9]+|[^a-zA-Z0-9]+)'

    # Use regex to split the name into words and separators while preserving them
    return re.findall(split_pattern, name)

def testswap_words(name, word1, word2, ignore_extension):
    """Swap two words in a filename while preserving existing separators and handling non-alphanumeric word boundaries."""
    if ignore_extension:
        base_name = name
    else:
        base_name, ext = os.path.splitext(name)

    # We want to match words separated by any non-alphanumeric characters
    # Match words surrounded by non-word characters (spaces, underscores, hyphens, etc.)
    pattern = rf'(?<!\w){re.escape(word1)}(?!\w)|(?<!\w){re.escape(word2)}(?!\w)'

    def replacement(match):
        """Swap matched words correctly."""
        return word2 if match.group(0) == word1 else word1

    # Swap the words using the replacement function
    base_name = re.sub(pattern, replacement, base_name)

    return base_name + (ext if not ignore_extension else "")



## Removing
def remove_numbers(name, ignore_extension):
    """Remove all digits from the filename."""
    if ignore_extension:
        new_name = re.sub(r'\d+', '', name)
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = re.sub(r'\d+', '', base_name)
        new_name = new_base_name + ext
    return new_name

def remove_special_characters(name, ignore_extension):
    """Remove all characters except letters, numbers, dots, and underscores."""
    if ignore_extension:
        new_name = re.sub(r'[^a-zA-Z0-9._]', '', name)
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = re.sub(r'[^a-zA-Z0-9._]', '', base_name)
        new_name = new_base_name + ext
    return new_name

def remove_non_ascii(name, ignore_extension):
    """Remove all non-ASCII characters from the filename."""
    if ignore_extension:
        new_name = ''.join([char for char in name if ord(char) < 128])
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = ''.join([char for char in base_name if ord(char) < 128])
        new_name = new_base_name + ext
    return new_name

def remove_leading(name, values, ignore_extension):
    """Remove specified leading character(s) from the filename."""
    char = values[0]
    if not char:
        return name  # If no character is provided, return the original name
    
    if ignore_extension:
        return re.sub(f'^{re.escape(char)}+', '', name)

    base_name, ext = os.path.splitext(name)
    new_base_name = re.sub(f'^{re.escape(char)}+', '', base_name)
    
    return new_base_name + ext

def remove_trailing(name, values, ignore_extension):
    """Remove specified trailing character(s) from the filename."""
    char = values[0]
    if not char:
        return name  # If no character is provided, return the original name
    
    if ignore_extension:
        return re.sub(f'{re.escape(char)}+$', '', name)

    base_name, ext = os.path.splitext(name)
    new_base_name = re.sub(f'{re.escape(char)}+$', '', base_name)
    return new_base_name + ext

def _split_into_parts(name):
    """Splits the name into words and separators."""
    # This function will split the name into words and separators and store them as a dictionary
    parts = re.findall(r'(\b\w+\b|[^a-zA-Z0-9]+)', name)  # Words and separators
    part_dict = []
    
    for part in parts:
        if re.match(r'\b\w+\b', part):  # If it's a word (not a separator)
            part_dict.append({'type': 'word', 'value': part})
        else:
            part_dict.append({'type': 'separator', 'value': part})

    return part_dict

def remove_duplicate_words(name, ignore_extension):
    """Remove duplicate words while preserving original separators and formatting (case-sensitive)."""
    # Separate the extension from the base name
    if ignore_extension:
        base_name = name
        ext = ""
    else:
        base_name, ext = _split_extension(name)

    # Split the base name into words and separators
    parts = _split_into_parts(base_name)

    # Track repeating words
    seen = set()
    repeating_words = set()
    
    print(f"This is all parts {parts}")
    # Identify repeating words
    for part in parts:
        if part['type'] == 'word':  # Only check for words
            print(f"This is a word: {part['value']}")
            if part['value'] in seen:
                repeating_words.add(part['value'])
            else:
                seen.add(part['value'])
        elif part['type'] == 'separator':
            print(f"This is a separator: {part['value']}")

    # Rebuild the base name, preserving the first occurrence of each word
    new_base_name = ""
    seen_words = set()  # Keep track of words we've already added to the new name

    for part in parts:
        if part['type'] == 'word':
            # Add the word only if it's not in the seen_words set
            if part['value'] not in seen_words:
                new_base_name += part['value']
                seen_words.add(part['value'])
            elif part['value'] not in repeating_words:
                # Skip repeating words, but only if they haven't already been added
                continue
        elif part['type'] == 'separator':
            # Always add separators
            new_base_name += part['value']

    # Return the final name with or without extension
    return new_base_name + (ext if not ignore_extension else "")

def remove_connected_repeating_input(name, values, ignore_extension):
    """Remove repeating connected characters/words in filenames."""
    base_name, ext = os.path.splitext(name) if not ignore_extension else (name, "")

    # For each value in values, remove connected repeating occurrences of the word
    for value in values:
        # Create a regular expression to match repeating connected occurrences of the word
        # Example: 'hejhejhej' -> 'hej'
        pattern = re.compile(rf"({re.escape(value)})\1+")
        base_name = re.sub(pattern, r"\1", base_name)  # Replace repeats with a single instance of the word

    return base_name + ext

def remove_in_filename(name, values, ignore_extension):
    """Replace old text with new text in filenames."""
    base_name, ext = os.path.splitext(name) if not ignore_extension else (name, "")

    print(f"Values {values} \n"*20)
    for value in values:
        base_name = base_name.replace(value, "")

    return base_name + ext


## Misc
def reverse_string(name, ignore_extension):
    """Reverse the entire filename or just the base name."""
    if ignore_extension:
        new_name = name[::-1]
    else:
        base_name, ext = os.path.splitext(name)
        new_base_name = base_name[::-1]
        new_name = new_base_name + ext
    return new_name

def normalize_filename(name, ignore_extension, preserve_leading_dot=True):
    """Normalize filenames by collapsing repeated spaces, underscores, dashes, and dots."""
    if ignore_extension:
        base_name = name
    else:
        base_name, ext = os.path.splitext(name)

    # Check if the filename starts with a dot (for hidden files like .gitignore)
    has_leading_dot = base_name.startswith(".") if preserve_leading_dot else False

    # Collapse repeated separators but preserve single ones
    base_name = re.sub(r'([._\s-])\1+', r'\1', base_name).strip("._- ")

    # Restore leading dot if necessary
    if has_leading_dot and not base_name.startswith("."):
        base_name = "." + base_name

    return base_name + (ext if not ignore_extension else "")


def limit_filename_length(name, max_length, ignore_extension):
    """Limit the length of the filename, keeping the extension intact, and adjust the base name accordingly."""
    if ignore_extension:
        return name[:max_length]  # Truncate the whole name

    base_name, ext = os.path.splitext(name)
    
    # Ensure max_length is greater than or equal to the length of the extension
    if max_length < len(ext):
        raise ValueError("Max length is smaller than the extension length, unable to truncate properly.")

    # Calculate the max base name length
    max_base_name_length = max_length - len(ext)
    
    # Truncate the base name if it's too long
    if len(base_name) > max_base_name_length:
        base_name = base_name[:max_base_name_length]

    return base_name + ext

def add_separators(name, separator="_", ignore_extension=False, split_numbers=False):
    """Add separators to camel case words and between numbers in filenames."""
    base_name, ext = os.path.splitext(name) if not ignore_extension else (name, "")

    # Insert separator for camel case: Lowercase -> Uppercase transitions
    base_name = re.sub(r'([a-z])([A-Z])', r'\1' + separator + r'\2', base_name)
    
    if split_numbers:
        # Insert separator before and after numbers
        base_name = re.sub(r'([a-zA-Z])(\d)', r'\1' + separator + r'\2', base_name)  # Letter -> number
        base_name = re.sub(r'(\d)([a-zA-Z])', r'\1' + separator + r'\2', base_name)  # Number -> letter

    return base_name + ext


## Time

def add_timestamp(name, granularity=None, ignore_extension=False, separator="_"):
    """Append a timestamp to the filename with specified granularity or custom format."""
    if granularity[0] == "%":
        try:
            timestamp = datetime.now().strftime(granularity)
        except ValueError:
            return name
            print("Invalid custom format provided. Falling back to default 'full' format.")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    else:
        # Default granularity-based timestamp
        if granularity == 'year':
            timestamp = datetime.now().strftime("%Y")
        elif granularity == 'month':
            timestamp = datetime.now().strftime("%Y%m")
        elif granularity == 'day':
            timestamp = datetime.now().strftime("%Y%m%d")
        elif granularity == 'hour':
            timestamp = datetime.now().strftime("%Y%m%d_%H")
        elif granularity == 'minute':
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        elif granularity == 'second':
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        else:  # Default 'full' format
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Add timestamp to filename
    if ignore_extension:
        new_name = f"{name}{separator}{timestamp}"
    else:
        base_name, ext = os.path.splitext(name)
        new_name = f"{base_name}{separator}{timestamp}{ext}"

    return new_name


## Helper Functions
def _split_extension(filename):
    """Splits filename into (name, extension), where extension includes the dot."""
    name, ext = os.path.splitext(filename)
    return name, ext

def _split_into_words(name, split_numbers=False):
    # Replace common separators with spaces (underscore, hyphen, dot, slash)
    name = name.replace('_', ' ').replace('-', ' ').replace('.', ' ').replace('/', ' ')

    # Split camel case (myFileName -> my File Name)
    name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)

    if split_numbers:
        # Split words and numbers (e.g., "Hello2World" -> ["Hello", "2", "World"])
        name = re.sub(r'([A-Za-z])(\d)', r'\1 \2', name)  # Letter followed by number
        name = re.sub(r'(\d)([A-Za-z])', r'\1 \2', name)  # Number followed by letter

    # Normalize all spacing and split into words
    words = re.split(r'\s+', name.strip())

    # Return only non-empty words (i.e., words that contain alphanumeric characters)
    return [word for word in words if word]

def _preserve_caps_transform(text, transform_func):
    """
    Helper to transform text (either to lower or upper), while preserving fully uppercase segments.
    Separators like _, -, and spaces are untouched.
    """
    def preserve_or_transform(match):
        word = match.group(0)
        if word.isupper():
            return word  # Preserve fully uppercase words
        return transform_func(word)  # Otherwise, apply the case transformation

    # Regex matches words (alphanumeric runs) and separators (non-alphanumeric runs) separately
    return re.sub(r'[A-Za-z0-9]+', preserve_or_transform, text)