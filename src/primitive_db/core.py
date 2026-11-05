def create_table(metadata, table_name, columns):
    """Создает новую таблицу в метаданных."""
    if table_name in metadata:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata

    # Проверяем типы данных
    valid_types = {"int", "str", "bool"}
    for col in columns:
        if ":" not in col:
            print(f"Некорректное значение: {col}. Попробуйте снова.")
            return metadata
        
        col_name, col_type = col.split(":", 1)
        if col_type not in valid_types:
            print(f"Некорректное значение: {col_type}. Попробуйте снова.")
            return metadata

    # Автоматически добавляем столбец ID в начало
    # Формат хранения: список словарей [{"name": "ID", "type": "int"}, ...]
    parsed_columns = [{"name": "ID", "type": "int"}]
    for col in columns:
        col_name, col_type = col.split(":", 1)
        parsed_columns.append({"name": col_name, "type": col_type})

    # Сохраняем в метаданные
    metadata[table_name] = parsed_columns
    
    # Формируем красивый вывод
    cols_str = ", ".join([f"{c['name']}:{c['type']}" for c in parsed_columns])
    print(f'Таблица "{table_name}" успешно создана со столбцами: {cols_str}')
    
    return metadata


def drop_table(metadata, table_name):
    """Удаляет таблицу из метаданных."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del metadata[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata


def list_tables(metadata):
    """Выводит список всех таблиц."""
    if not metadata:
        print("Таблиц пока нет.")
        return

    for table_name in metadata:
        print(f"- {table_name}")