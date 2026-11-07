def parse_condition(condition_str):
    """Парсит строку вида 'col = value' в словарь {'col': value}."""
    parts = condition_str.split("=")
    if len(parts) != 2:
        return None
    
    col = parts[0].strip()
    val_str = parts[1].strip()
    
    # Если значение в кавычках, убираем их и оставляем как строку
    if val_str.startswith('"') and val_str.endswith('"'):
        val = val_str[1:-1]
    elif val_str.startswith("'") and val_str.endswith("'"):
        val = val_str[1:-1]
    else:
        # Пытаемся привести к int или bool
        if val_str.lower() in ("true", "false"):
            val = val_str.lower() == "true"
        else:
            try:
                val = int(val_str)
            except ValueError:
                val = val_str  # Если не число и не bool, оставляем как строку
    
    return {col: val}


def parse_set_clause(set_str):
    """Парсит строку вида 'col1 = val1, col2 = val2'."""
    result = {}
    parts = set_str.split(",")
    for part in parts:
        parsed = parse_condition(part.strip())
        if parsed:
            result.update(parsed)
    return result