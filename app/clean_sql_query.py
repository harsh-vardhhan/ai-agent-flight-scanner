import re

def clean_sql_query(query: str) -> str:

    # Handle case where query might be None or not a string
    if not isinstance(query, str):
        return ""

    def remove_special_tokens(sql):
        # Remove the END_RESPONSE token and any similar markers
        sql = re.sub(r'<\|END_RESPONSE\|>', '', sql)
        sql = re.sub(r'<\|.*?\|>', '', sql)  # Remove any similar tokens
        return sql

    def remove_sql_comments(sql):
        # Remove single line comments
        sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
        # Remove multi-line comments
        sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
        return sql

    def standardize_whitespace(sql):
        # Replace multiple spaces with single space
        sql = re.sub(r'\s+', ' ', sql)
        # Add space after commas if missing
        sql = re.sub(r',(?!\s)', ', ', sql)
        # Remove space before commas
        sql = re.sub(r'\s+,', ',', sql)
        return sql.strip()

    def remove_code_blocks(sql):
        # Remove markdown code blocks
        sql = re.sub(r'```sql\s*', '', sql)
        sql = re.sub(r'```.*', '', sql)
        # Remove backticks
        sql = sql.replace('`', '')
        return sql

    def fix_quotes(sql):
        # Standardize quotes for string literals
        sql = re.sub(r'"([^"]*)"', r"'\1'", sql)
        # Fix cases where there might be nested quotes
        sql = re.sub(r"''", "'", sql)
        return sql

    def normalize_keywords(sql):
        # Common SQL keywords to uppercase
        keywords = ['SELECT', 'FROM', 'WHERE', 'AND', 'OR', 'ORDER BY', 
                   'GROUP BY', 'LIMIT', 'JOIN', 'LEFT JOIN', 'RIGHT JOIN',
                   'INNER JOIN', 'HAVING', 'UPDATE', 'DELETE', 'INSERT INTO']

        # Case-insensitive replacement of keywords
        pattern = r'\b(' + '|'.join(re.escape(word) for word in keywords) + r')\b'
        sql = re.sub(pattern, lambda m: m.group(0).upper(), sql, flags=re.IGNORECASE)
        return sql

    # Apply cleaning steps in sequence
    query = remove_special_tokens(query)
    query = remove_code_blocks(query)
    query = remove_sql_comments(query)
    query = standardize_whitespace(query)
    query = fix_quotes(query)
    query = normalize_keywords(query)

    return query
