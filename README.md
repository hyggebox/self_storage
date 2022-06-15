# Сайт сервиса хранения вещей SelfStorage

![](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=green)





### Требования

Для запуска проекта необходимо:
- Python 3.6+
- Почтовый ящик для рассылки данных для регистрации пользователя


### Переменные окружения

Определите переменные окружения в файле `.env` в формате: `ПЕРЕМЕННАЯ=значение`:
- `DEBUG` — дебаг-режим. Поставьте `True` для включения, `False` — для 
выключения отладочного режима. По умолчанию дебаг-режим отключен.
- `SECRET_KEY` — секретный ключ проекта, например: `fwei3$@K!fjslfji;erfkdsewyiwerlfskfhfjdslfsf3`
- `ALLOWED_HOSTS` — список разрешенных хостов.
________

- `EMAIL_HOST` — SMTP-сервер
- `EMAIL_HOST_USER` — адрес почтового ящика, с которого будет производится рассылка
- `EMAIL_HOST_PASSWORD` — пароль
- `DEFAULT_FROM_EMAIL` — адрес почтового ящика, с которого будет производится рассылка
_________

- `STATIC_URL` — отображаемый каталог со статичными файлами, по умолчанию `'/static/'`. 
- `MEDIA_ROOT` — каталог для хранения медиа-файлов, по умолчанию `'media'`.
- `MEDIA_URL` — отображаемый каталог с медиа-файлами, по умолчанию `'/media/'`
- `SECURE_HSTS_SECONDS` — по умолчанию противоположно значению `DEBUG`
- `SECURE_SSL_REDIRECT` — по умолчанию противоположно значению `DEBUG`
- `SESSION_COOKIE_SECURE` — по умолчанию противоположно значению `DEBUG`
- `CSRF_COOKIE_SECURE` — по умолчанию противоположно значению `DEBUG`

## Установка и запуск на локальном сервере

- Скачайте код из репозитория
- Установите зависимости командой:
```shell
pip install -r requirements.txt
```
- Создайте файл `.env` в корневой папке и пропишите необходимые переменные 
окружения в формате: `ПЕРЕМЕННАЯ=значение`


- Выполните миграцию БД:
```commandline
python manage.py migrate
```
- Запустите скрипт командой:
```commandline
python manage.py runserver
```


### Панель администратора

Панель администратора сайта доступна по адресу `sitename/admin/`. Для
создания учетной записи администратора используйте команду:
```commandline
python manage.py createsuperuser
```


## Демо-версия

Демо-версия сайта доступна по адресу 


## Цели проекта

Код написан в учебных целях.