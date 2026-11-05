import shlex

from primitive_db import core, utils

DB_FILE = "db_meta.json"


def print_help():
    """Prints the help message for the current mode."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run():
    """Основной цикл программы."""
    print("***База данных***")
    print_help()

    while True:
        try:
            user_input = input(">>>Введите команду: ").strip()
        except KeyboardInterrupt:
            print("\nВыход...")
            break
        except EOFError:
            break

        if not user_input:
            continue

        # Разбираем строку на команду и аргументы
        try:
            args = shlex.split(user_input)
        except ValueError:
            print("Ошибка парсинга команды.")
            continue

        command = args[0]

        if command == "exit":
            break
        elif command == "help":
            print_help()
        elif command == "list_tables":
            metadata = utils.load_metadata(DB_FILE)
            core.list_tables(metadata)
        elif command == "create_table":
            if len(args) < 3:
                print("Некорректное значение: недостаточно аргументов."
                "Попробуйте снова.")
                continue
            
            table_name = args[1]
            columns = args[2:]
            
            metadata = utils.load_metadata(DB_FILE)
            new_metadata = core.create_table(metadata, table_name, columns)
            utils.save_metadata(DB_FILE, new_metadata)
            
        elif command == "drop_table":
            if len(args) != 2:
                print("Некорректное значение: неверное количество аргументов."
                "Попробуйте снова.")
                continue
                
            table_name = args[1]
            
            metadata = utils.load_metadata(DB_FILE)
            new_metadata = core.drop_table(metadata, table_name)
            utils.save_metadata(DB_FILE, new_metadata)
            
        else:
            print(f"Функции {command} нет. Попробуйте снова.")