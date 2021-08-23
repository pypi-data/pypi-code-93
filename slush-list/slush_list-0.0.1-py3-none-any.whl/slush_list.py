"""
 Чтение slush-list
"""

import logging


logging.basicConfig(level=logging.INFO)


class Student:
    """
    Класс, объектом которого является каждый слушатель
    """

    def __init__(self, fio, fullname, login):
        """
        Параметры слушателя

        Args:
                fio:        ФИО слушателя
                fullname:   fullname слушателя
                login:      login слушателя
        """

        self.fio = fio
        self.fullname = fullname
        self.login = login

    def change_fullname(self, new_fullname):
        """
        Функция изменения fullname слушателя

        Args:
                new_fullname:   Новый fullname слушателя
        """
        self.fullname = new_fullname

    def change_login(self, new_login):
        """
        Функция изменения login слушателя

        Args:
                new_login:      Новый login слушателя
        """
        self.login = new_login

    def show_fullname(self):
        """Функция отображения fullname слушателя"""
        return self.fullname

    def show_login(self):
        """Функция отображения login слушателя"""
        return self.login


class Students:
    """
    Реализация чтения slush-list
    """

    def __init__(self, year='', number=''):

        """
        Init a address

        Args:
               year:       год поступления
               number:     номер группы
        """

        self.year = year
        self.group_number = number

        self.group_list = []
        self.group_name = 'NoName'

    def read_slush(self, address):

        """Функция чтения списка слушателей

        Args:
               address:    путь до файла со слушателями

        Returns:
               True for success

        Raises:
               FileNotFoundError:   Файл не найден
        """

        try:
            with open(address, 'r') as fl_link:
                for line in fl_link:

                    if line[0] == "#":
                        continue

                    fio, fullname, login = line.split(';')
                    login = login[:-1]

                    if not self.check_name(fullname):
                        self.group_list.clear()

                        return False

                    self.group_list.append(Student(fio, fullname, login))

            logging.info("Группа прочитана")

            return True

        except FileNotFoundError as read_ex:
            print(read_ex)
            raise

    def load_slush(self):

        """Функция загрузки списка слушателей"""

        if self.group_list:

            if self.year != '' and self.group_number != '':
                self.group_name = f"{self.year}-{self.group_number}"
                print(f"Имя группы -> {self.group_name}")
            elif self.year == '' and self.group_number != '':
                self.group_name = self.group_number
                print("Год группы не задан")
                print(f"Имя группы -> {self.group_name}")
            elif self.year != '' and self.group_number == '':
                self.group_name = self.year
                print("Номер группы не задан")
                print(f"Имя группы -> {self.group_name}")
            else:
                print(f"Имя группы не задано -> {self.group_name}")

            logging.info("Группа успешно загружена")

        else:
            logging.info("Список слушатлей пуст")
            return False

        return self.group_name

    def relogin(self, old_login, new_login):

        """
        Функция изменения логина слушателя

        Args:
              old_login:    старый логин слушателя
              new_login:    новый логин слушателя

        Returns:
              'login успешно изменен'

        Raises:
              ValueError:   login отсутвует в списке
        """

        for i in range(len(self.group_list)):
            if old_login == self.group_list[i].show_login():
                print(f"Старый login -> {self.group_list[i].show_login()}")

                self.group_list[i].change_login(new_login)

                print(f"Новый login -> {self.group_list[i].show_login()}")

                logging.info("login успешно изменен")

                return True

        raise ValueError("login отсутвует в списке")

    def rename(self, login, new_name):

        """
        Функция изменения fullname слушателя

        Args:
              login:         логин слушателя
              new_name:      новый fullname слушателя

        Returns:
              True for success

        Raises:
              ValueError:   login отсутвует в списке
        """

        if self.check_name(name=new_name):

            for i in range(len(self.group_list)):
                if login == self.group_list[i].show_login():
                    print(f"Старый fullname -> {self.group_list[i].show_fullname()}")

                    self.group_list[i].change_fullname(new_name)

                    print(f"Новый fullname -> {self.group_list[i].show_fullname()}")

                    logging.info("fullname успешно изменен")

                    return True

            raise ValueError("login отсутвует в списке")

        return False

    def check_name(self, name):

        """
        Функция проверки корректности fullname

        Args:
             name:  аргумент, используемый в функции rename, для проверки new_name

        Returns:
             True for success
             False for failure
        """

        name_comp = name.split("-")

        if len(name_comp) < 4:
            logging.info("имя введено не верно (len) -> %s", name)
            return False

        if name_comp[0] != self.year:
            logging.info("имя введено не верно (year) -> %s", name)
            return False

        if name_comp[1] != self.group_number:
            logging.info("имя введено не верно (number) -> %s", name)
            return False

        return True



    def show_list(self):
        """Функция отображения списка слушателей"""
        return self.group_list
