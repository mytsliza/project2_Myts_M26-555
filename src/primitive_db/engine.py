import shlex

from prettytable import PrettyTable

from primitive_db import core, parser, utils
from primitive_db.constants import META_FILE
from primitive_db.decorators import create_cacher

select_cacher = create_cacher()

def print_help():
    """Prints the help message for the current mode."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("\n***Операции с данными***")
    print("Функции:")
    print(
        '<command> insert into <таблица> values ("знач1", знач2, ...)'
        " - создать запись"
    )
    print(
        "<command> select from <таблица> [where <столбец> = <значение>]"
        " - прочитать записи"
    )
    print(
        "<command> update <таблица> set <столбец> = <значение>"
        " where <условие> - обновить"
    )
    print("<command> delete from <таблица> where <столбец> = <значение> - удалить")
    print("<command> info <таблица> - информация о таблице")
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run():
    """Основной цикл программы."""
    global select_cacher
    print("***База данных***")
    print_help()

    while True:
        try:
            user_input = input(">>> Введите команду: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nВыход...")
            break

        if not user_input:
            continue

        try:
            args = shlex.split(user_input)
        except ValueError:
            print("Ошибка парсинга команды.")
            continue

        command = args[0].lower()

        if command == "exit":
            break
        elif command == "help":
            print_help()
        elif command == "list_tables":
            metadata = utils.load_metadata(META_FILE)
            core.list_tables(metadata)
        elif command == "create_table":
            if len(args) < 3:
                print("Некорректное значение: недостаточно аргументов.")
                continue
            table_name = args[1]
            columns = args[2:]
            metadata = utils.load_metadata(META_FILE)
            new_metadata = core.create_table(metadata, table_name, columns)
            utils.save_metadata(META_FILE, new_metadata)
        elif command == "drop_table":
            if len(args) != 2:
                print("Некорректное значение: неверное количество аргументов.")
                continue
            table_name = args[1]
            metadata = utils.load_metadata(META_FILE)
            new_metadata = core.drop_table(metadata, table_name)
            utils.save_metadata(META_FILE, new_metadata)
        
        # --- CRUD ОПЕРАЦИИ ---
        elif command == "insert" and len(args) >= 5 and args[1] == "into":
            table_name = args[2]
            if args[3] != "values":
                print("Ошибка: ожидалось 'values'.")
                continue
            
            # Собираем значения из скобок
            values_str = " ".join(args[4:])
            if values_str.startswith("(") and values_str.endswith(")"):
                values_str = values_str[1:-1]
            
            # Разбиваем по запятым, убираем пробелы и кавычки
            values = [v.strip().strip('"').strip("'") for v in values_str.split(",")]
            
            metadata = utils.load_metadata(META_FILE)
            new_data = core.insert(metadata, table_name, values)
            if new_data is not None:
                utils.save_table_data(table_name, new_data)
                select_cacher = create_cacher()
                
        elif command == "select" and len(args) >= 3 and args[1] == "from":
            table_name = args[2]
            metadata = utils.load_metadata(META_FILE)
            if table_name not in metadata:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
                continue
            
            table_data = utils.load_table_data(table_name)
            where_clause = None
            if len(args) > 3 and args[3] == "where":
                where_str = " ".join(args[4:])
                where_clause = parser.parse_condition(where_str)
            
            # Формируем уникальный ключ для кэша (имя таблицы + условие)
            cache_key = f"{table_name}_{where_clause}"
            
            # Вызываем кэшер. Если результат есть в памяти — он вернется сразу.
            # Если нет — вызовется core.select, результат сохранится в кэш.
            result = select_cacher(
                cache_key,
                lambda: core.select(table_data, where_clause)
            )
            
            # Выводим через PrettyTable
            table = PrettyTable()
            columns = metadata[table_name]
            table.field_names = [col["name"] for col in columns]
            
            for row in result:
                table.add_row([row.get(col["name"]) for col in columns])
            
            print(table)
            
        elif command == "update" and len(args) >= 6:
            table_name = args[1]
            if args[2] != "set":
                print("Ошибка: ожидалось 'set'.")
                continue
            
            metadata = utils.load_metadata(META_FILE)
            if table_name not in metadata:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
                continue
            
            # Парсим set и where
            # Ищем индекс "where"
            try:
                where_idx = args.index("where")
                set_str = " ".join(args[3:where_idx])
                where_str = " ".join(args[where_idx+1:])
            except ValueError:
                print("Ошибка: отсутствует 'where'.")
                continue
            
            set_clause = parser.parse_set_clause(set_str)
            where_clause = parser.parse_condition(where_str)
            
            table_data = utils.load_table_data(table_name)
            new_data, count = core.update(table_data, set_clause, where_clause)
            
            if count > 0:
                utils.save_table_data(table_name, new_data)
                select_cacher = create_cacher()
                print(
                    f"Записи в таблице \"{table_name}\" успешно обновлены "
                    f"({count} шт.).")
            else:
                print("Записи не найдены.")
                
        elif command == "delete" and len(args) >= 5 and args[1] == "from":
            table_name = args[2]
            if args[3] != "where":
                print("Ошибка: ожидалось 'where'.")
                continue
            
            where_str = " ".join(args[4:])
            where_clause = parser.parse_condition(where_str)
            
            metadata = utils.load_metadata(META_FILE)
            if table_name not in metadata:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
                continue
            
            table_data = utils.load_table_data(table_name)
            new_data, count = core.delete(table_data, where_clause)
            
            if count > 0:
                utils.save_table_data(table_name, new_data)
                select_cacher = create_cacher()
                print(f"Записи из таблицы \"{table_name}\" успешно удалены "
                      f"({count} шт.)."
                      )
            else:
                print("Записи не найдены.")
                
        elif command == "info":
            if len(args) != 2:
                print("Некорректное значение: укажите имя таблицы.")
                continue
            table_name = args[1]
            metadata = utils.load_metadata(META_FILE)
            if table_name not in metadata:
                print(f'Ошибка: Таблица "{table_name}" не существует.')
                continue
            
            table_data = utils.load_table_data(table_name)
            columns_str = ", ".join(
                [f"{c['name']}:{c['type']}" for c in metadata[table_name]]
            )
            print(f"Таблица: {table_name}")
            print(f"Столбцы: {columns_str}")
            print(f"Количество записей: {len(table_data)}")
            
        else:
            print(f"Функции {command} нет. Попробуйте снова.")