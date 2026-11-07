from primitive_db import utils


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
def _validate_type(value_str, expected_type):
    """Вспомогательная функция для проверки типа значения."""
    if expected_type == "int":
        try:
            return int(value_str)
        except ValueError:
            return None
    elif expected_type == "bool":
        if value_str.lower() in ("true", "1", "yes"):
            return True
        elif value_str.lower() in ("false", "0", "no"):
            return False
        return None
    elif expected_type == "str":
        return str(value_str)
    return None


def insert(metadata, table_name, values):
    """Добавляет новую запись в таблицу."""
    if table_name not in metadata:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return None

    columns = metadata[table_name]
    # ID не входит в values, поэтому сравниваем с len(columns) - 1
    if len(values) != len(columns) - 1:
        print(f"Некорректное значение: ожидалось {len(columns) - 1}" 
              f"значений, получено {len(values)}."
              )
        return None

    table_data = utils.load_table_data(table_name)
    
    # Генерируем ID
    new_id = max([row["ID"] for row in table_data], default=0) + 1
    
    new_row = {"ID": new_id}
    
    # Валидация и добавление значений
    for i, col in enumerate(columns[1:]):  # Пропускаем ID
        val_str = values[i]
        val = _validate_type(val_str, col["type"])
        if val is None:
            print(f'Некорректное значение: {val_str}. Ожидался тип {col["type"]}.')
            return None
        new_row[col["name"]] = val

    table_data.append(new_row)
    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')
    return table_data


def select(table_data, where_clause=None):
    """Возвращает записи по условию (или все)."""
    if not where_clause:
        return table_data
    
    result = []
    for row in table_data:
        match = True
        for col, val in where_clause.items():
            if row.get(col) != val:
                match = False
                break
        if match:
            result.append(row)
    return result


def update(table_data, set_clause, where_clause):
    """Обновляет записи по условию."""
    updated_count = 0
    for row in table_data:
        match = True
        for col, val in where_clause.items():
            if row.get(col) != val:
                match = False
                break
        if match:
            for col, val in set_clause.items():
                row[col] = val
            updated_count += 1
    return table_data, updated_count


def delete(table_data, where_clause):
    """Удаляет записи по условию."""
    new_data = []
    deleted_count = 0
    for row in table_data:
        match = True
        for col, val in where_clause.items():
            if row.get(col) != val:
                match = False
                break
        if match:
            deleted_count += 1
        else:
            new_data.append(row)
    return new_data, deleted_count