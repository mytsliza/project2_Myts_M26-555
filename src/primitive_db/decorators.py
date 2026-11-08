import functools
import time


def handle_db_errors(func):
    """Перехватывает ошибки БД и выводит понятные сообщения."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print("Ошибка: Файл данных не найден."
                  "Возможно, база данных не инициализирована."
                  )
        except KeyError as e:
            print(f"Ошибка: Таблица или столбец {e} не найден.")
        except ValueError as e:
            print(f"Ошибка валидации: {e}")
        except Exception as e:
            print(f"Произошла непредвиденная ошибка: {e}")
    return wrapper


def confirm_action(action_name):
    """Запрашивает подтверждение перед опасной операцией."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            answer = input(f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: ')
            if answer.lower() != "y":
                print("Операция отменена.")
                return None  # Или возвращаем то, что было (args[0])
            return func(*args, **kwargs)
        return wrapper
    return decorator


def log_time(func):
    """Замеряет время выполнения функции."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        end = time.monotonic()
        print(f"Функция {func.__name__} выполнилась за {end - start:.3f} секунд.")
        return result
    return wrapper


def create_cacher():
    """Создает функцию-кэшер с замыканием."""
    cache = {}
    
    def cache_result(key, value_func):
        if key in cache:
            print(f"Результат для ключа '{key}' взят из кэша.")
            return cache[key]
        
        result = value_func()
        cache[key] = result
        return result
    
    return cache_result