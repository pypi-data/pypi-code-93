# -*- coding: utf-8 -*-

import setuptools

# Открытие README.md и присвоение его long_description.
with open("README.md", "r") as fh:
	long_description = fh.read()

# Определение requests как requirements для того, чтобы этот пакет работал. Зависимости проекта.
# requirements = ["requests<=2.21.0"]

# Функция, которая принимает несколько аргументов. Она присваивает эти значения пакету.
setuptools.setup(
	# Уникальное имя дистрибутива пакета.
	name="sd-format",
	# Номер версии пакета.
	version="1.12.3",
	# Имя автора.
	author="DALITON",
	# Почта автора.
	author_email="products_support@daliton.org",
	# Краткое описание, которое будет показано на странице PyPi.
	description="Library for working with the .sd format designed to store configuration and service data",
	# Длинное описание, которое будет отображаться на странице PyPi. Использует README.md репозитория для заполнения.
	long_description=long_description,
	# Определяет тип контента, используемый в long_description.
	long_description_content_type="text/markdown",
	# URL-адрес, представляющий домашнюю страницу проекта.
	url="https://github.com/aleks-daliton/sd",
	# Находит все пакеты внутри проекта и объединяет их в дистрибутив.
	packages=setuptools.find_packages(),
	# requirements или dependencies, которые будут установлены вместе с пакетом, когда пользователь уст. его через pip.
	# install_requires=requirements,
	# Предоставляет pip некоторые метаданные о пакете. Также отображается на странице PyPi.
	classifiers=[
		"Programming Language :: Python :: 3.8",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
	# Требуемая версия Python.
	python_requires='>=3.6',
)
