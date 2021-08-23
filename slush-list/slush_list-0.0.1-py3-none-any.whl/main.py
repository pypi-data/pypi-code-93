"""
Микросервис
"""

# pylint: disable= no-else-return
# Отключено, т.к. ловим ошибку при возврате на основную страницу после работы функций relogin,
# rename и т.д.


# pylint: disable= too-many-nested-blocks
# Отлючено, т.к. для работы необходимо большое количество вложенных блоков

import argparse
from fileinput import FileInput
from flask import Flask, render_template, request, redirect
import slush_list

app = Flask(__name__)
app.config.from_json('microservice_cfg.json')


@app.route('/', methods=['GET', 'POST'])
def index():
    """Основная страница web-приложения"""

    if request.method == 'POST':
        fullname = request.form['fullname']

        info = get_stud(fullname).copy()

        return render_template('getstud.html', info=info)

    else:

        return render_template("index.html")


groups_dir = {}
groups_addr = {}
groups = []
NUM = 0


@app.route('/load', methods=['GET', 'POST'])
def load():
    """Страница загрузки списка группы"""

    if request.method == 'POST':
        year = request.form['year']
        number = request.form['number']
        file = request.form['file']
        dpv = request.form.get('dpv')

        load_list = slush_list.Students(year, number)
        key = f"{year}-{number}"
        if key in groups_dir:
            url = 'load'
            message = "ERROR (Группа с таким названием уже загружена)"

            return render_template("message.html", message=message, url=url)

        if load_list.read_slush(file):

            if dpv is None:
                group_name = load_list.load_slush()
                groups_dir[group_name] = load_list

                groups_addr[group_name] = file

                dpv = 'no'
                push = [dpv, load_list.load_slush()]
                groups.append(list(push))

                push.clear()
            else:
                groups_dir[load_list.load_slush()] = load_list

                push = [dpv, load_list.load_slush()]
                groups.append(list(push))

                push.clear()

            return redirect('/')
        else:
            url = 'load'
            message = "ERROR (Введенные данные указаны неверно)"

            return render_template("message.html", message=message, url=url)
    else:
        return render_template("load.html")


@app.route('/list')
def grouplist():
    """Cтраница со спискаком загруженных групп"""

    return render_template("list.html", groups=groups)


@app.route('/list/<string:number>')
def slushlist(number):
    """Страница, отображающая список загруженных слушателей
       в определенной группе """

    group = groups_dir[number].show_list().copy()

    sl_list = []
    slush = []

    for gr_index in enumerate(group):
        slush.append(gr_index[1].show_fullname())
        slush.append(gr_index[1].show_login())
        sl_list.append(list(slush))

        slush.clear()

    return render_template("sllist.html", sl_list=sl_list, number=number)


@app.route('/delete', methods=['GET', 'POST'])
def delete_group():
    """страница удаления загруженной группы"""

    if request.method == 'POST':
        group = request.form['group']

        try:
            del groups_dir[group]

            for elem in groups:
                if group == elem[1]:
                    groups.remove(elem)

            url = ''
            message = 'Группа удалена'

            return render_template("message.html", message=message, url=url)

        except KeyError:

            url = 'delete'
            message = "ERROR (Введенный номер группы отсутствует в списке)"

            return render_template("message.html", message=message, url=url)

    return render_template("groupdel.html")


@app.route('/relogin', methods=['GET', 'POST'])
def relogin():
    """страница изменения login слушателя"""

    if request.method == 'POST':
        group = request.form['group']
        old_login = request.form['old']
        new_login = request.form['new']

        try:
            groups_dir[group].relogin(old_login, new_login)

            for key in groups_addr:
                if key == group:
                    for line in FileInput(groups_addr[key], inplace=True):
                        login = line.split(';')
                        login[2] = login[2][:-1]
                        if login[2] == old_login:
                            login[2] = new_login + '\n'
                            line = ';'.join(login)
                        print(line, end='')

            url = ''
            message = 'Login успешно изменен'

            return render_template("message.html", message=message, url=url)

        except ValueError:

            url = 'relogin'
            message = "ERROR (Введенный login отсутствует в списке)"

            return render_template("message.html", message=message, url=url)
    else:

        group = list(groups_dir.keys())

        return render_template("relogin.html", group=group)


@app.route('/rename', methods=['GET', 'POST'])
def rename():
    """Страница изменения fullname слушателя"""

    if request.method == 'POST':
        group = request.form['group']
        login = request.form['login']
        new_name = request.form['new']

        try:
            if groups_dir[group].rename(login, new_name):

                for key in groups_addr:
                    if key == group:
                        for line in FileInput(groups_addr[key], inplace=True):
                            fullname = line.split(';')
                            fullname[2] = fullname[2][:-1]
                            if fullname[2] == login:
                                fullname[1] = new_name
                                line = ';'.join(fullname) + '\n'
                            print(line, end='')

                url = ''
                message = 'Fullname успешно изменен'

                return render_template("message.html", message=message, url=url)

            else:

                url = 'rename'
                message = "ERROR (Новый fullname введен некорректно)"

                return render_template("message.html", message=message, url=url)

        except ValueError:

            url = 'rename'
            message = "ERROR (Введенный login отсутствует в списке)"

            return render_template("message.html", message=message, url=url)
    else:

        group = list(groups_dir.keys())

        return render_template("rename.html", group=group)


@app.route('/repos', methods=['GET', 'POST'])
def repos():
    """Страница со списками репозиториев"""

    if request.method == 'POST':
        choice = request.form['choice']
        group = request.form['group']
        repo_name = request.form['repo_name']

        sl_list = []

        if choice == 'repo':
            flag = '-r'
            sl_list = get_repos(group, repo_name, flag)

            return render_template("showrepos.html", group=group, sl_list=sl_list)

        elif choice == 'group':
            flag = '-g'
            sl_list = get_repos(group, repo_name, flag)

            return render_template("showgroups.html", group=group, sl_list=sl_list)

        return None

    else:

        group = list(groups_dir.keys())

        return render_template("getrepos.html", group=group)


def create_args():
    """Функция создания аргуметов аргументов командной строки"""

    par = argparse.ArgumentParser(description='read slush_list')

    par.add_argument('-t', '--token', help="token")
    par.add_argument('-l', '--load', help="loading group")
    par.add_argument('-y', '--year', help="year of admission")
    par.add_argument('-n', '--number', help="group number")
    par.add_argument('-gs', '--getstud', help="search student")
    par.add_argument('-rl', '--relog', nargs="+", help="login change")
    par.add_argument('-rn', '--rename', nargs="+", help="fullname change")
    par.add_argument('-r', '--repo', nargs="+", help="name repo")
    par.add_argument('-g', '--group', nargs="+", help="name group with stud")
    par.add_argument('-sh', '--show', help="show group")

    return par


def get_stud(fullname):
    """
    Функция поиска слушателя по шаблону

    Args:
          fullname:   fullname слушателя, которого нужно найти

    Returns:
          True for success, False otherwise.
    """

    summ = 0

    mass = []

    for key in groups_dir:
        for line in groups_dir[key].show_list():
            if fullname in line.show_fullname():
                print(f"fullname ->{line.show_fullname()}\n"
                      f"login -> {line.show_login()}")
                print("Рабочий репозиторий -> ", end='')
                # https://gitwork.com для примера
                print(f"https://gitwork.ru/{line.show_login()}")

                mass.append(line.show_fullname())
                mass.append(line.show_login())
                mass.append(f"https://gitwork.ru/{line.show_login()}")

                return mass
            summ += 1
        summ = 0

    return False


def get_repos(num_group, repo_name, flags):
    """
    Функция получения списка репозиториев

    Args:
        num_group:  Номер группы
        repo_name:  имя репозитория
        flags:      флаг, необходимый для выбора режима работы

    Returns:
             True for success

    Raises:
             KeyError:  Неверно указан номер группы
    """

    mass = []
    temp_mass = []

    try:
        if flags == "-r":
            for line in groups_dir[num_group].show_list():
                # https://gitwork.com для примера
                login = line.show_login()
                temp_mass.append(f"https://gitwork.ru/{login}/{repo_name}")
                temp_mass.append(f"https://gitwork.ru/{login}/{repo_name}/-/issues")
                temp_mass.append(f"https://gitwork.ru/{login}/{repo_name}/-/milestones")

                mass.append(list(temp_mass))
                temp_mass.clear()

        elif flags == "-g":
            for line in groups_dir[num_group].show_list():
                # https://gitwork.com для примера
                fullname = line.show_fullname()
                mass.append(f"https://gitwork.ru/{repo_name}/{fullname}")

        return mass

    except KeyError as repo_ex:
        print(repo_ex)
        raise


if __name__ == '__main__':

    parser = create_args()
    args = parser.parse_args()

    if args.year or args.number or args.load:

        parser_list = slush_list.Students(args.year, args.number)
        parser_list.read_slush(args.load)

        groups_dir[parser_list.load_slush()] = parser_list

        if args.relog or args.rename or args.getstud or args.repo or args.group:

            if args.relog:
                parser_list.relogin(args.relog[0], args.relog[1])

            if args.rename:
                parser_list.rename(args.rename[0], args.rename[1])

            if args.getstud:
                get_stud(args.getstud)

            if args.repo:
                FLAG = '-r'
                get_repos(args.repo[0], args.repo[1], FLAG)

            if args.group:
                FLAG = '-g'
                get_repos(args.group[0], args.group[1], FLAG)

    else:
        app.run(debug=True, host='0.0.0.0')
