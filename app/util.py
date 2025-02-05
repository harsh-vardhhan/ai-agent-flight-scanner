import ast

def parse_tuple_list(string_representation: str):
    """Parse string representation of a list of tuples into a Python list."""
    try:
        parsed_data = ast.literal_eval(string_representation)
        if isinstance(parsed_data, list) and all(isinstance(item, tuple) for item in parsed_data):
            return parsed_data
        else:
            raise ValueError("Invalid format: Expected a list of tuples.")
    except (SyntaxError, ValueError) as e:
        raise ValueError(f"Error parsing string: {e}") from e