import prompt

def welcome():
    """Выводит приветствие и запускает цикл ввода команд."""
    print("***")
    print("<command> exit - выйти из программы")
    print("<command> help - справочная информация")
    
    while True:
        # Используем prompt.string для запроса команды
        command = prompt.string("Введите команду: ")
        
        if command == "exit":
            break
        elif command == "help":
            print()
            print("<command> exit - выйти из программы")
            print("<command> help - справочная информация")
        else:
            # Если ввели неизвестную команду, можно просто ничего не делать
            # или вывести сообщение об ошибке (по желанию)
            pass