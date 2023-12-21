# Blender Python Bridge for "VS Code"

Позволяет запускать Blender в режиме прослушивания и запуска как отдельных команд так и целых скриптов, пакетов или даже многофайловых аддонов от клиента. В процессе использования создаётся программпый мост между Blender (сервер) и клиентом через socket сервер.


## Как это устроено в общем

Пользователь создаёет скрипт/пакет/аддон в VS Code и запускает с использование горящей клавиши. Код передаётся в Blender устанавливает переданный код так как если бы вы его запаковали в zip архив и установили через Blender интерфейс. Разница лишь в том, что это всё происходит на лету и без файтической установки и работы с файлами на диске. Blender получает код и запуская, подхватывает все классы, функции, выполняет регистрации с фактического пути запуска в вашей папке проектов. При перезапуске код, все классы и модули разрегистрируются, удаляются, вычищаются, чтобы загрузить и выполнить новую версию кода. После выключения Blender ваш скрипт/пакет/аддон полностью вычищается.
Пространство имен поддерживается аналогично структуре Blender, что позволяет упаковать ваше творение в zip и установить на постоянной осве или передать кому либо не боясь проблем с абсолютными и относительными путями в импортах.

## Зависимости

Прямых зависимостей у расширения нет. Расширение требует указать путь до исполняемого файла Blender, после чего определяется путь до python интерпретатора встроенного в Blender. Будьте уверены в том, что код будет точно работать, так как использует встроенный в Blender интерпретатор.

## Что настроить

В Windows, системный терминал использует кодировку 866, что не позволяет отображать кирилицу в терминале, при получении сообщений от Blender в терминал. Кирилица на уровне VS Code и в скриптах поддерживается без проблем так как происходит декодирование вывода в utf расширением.

"CMD"
Чтобы переключить системный "CMD" терминал на UTF-8 на постоянной основе, нужно в реестре перейти в
"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Command Processor"
Создать там "Строковый параметр" с именем "Autorun" в значении которого ввести
"@chcp 65001>nul"

"PowerShell"
Создайте папку с файлом, если её еще нет по пути
"C:\Users\a_zhitkov\Documents\WindowsPowerShell\Microsoft.PowerShell_profile.ps1"
Внутри файла одна строка с конфигом на переключение терминала
[System.Console]::OutputEncoding = [System.Text.Encoding]::UTF8


Это позволит автоматически выполнять команду смены кодировки перед запуском терминала на уровне системы. Оставляю это задачу на плечах пользователя так как не хочу вносить системные изменения за пользователя.


## Описание обновлений

### 2023.12.28-01-beta

Первичная версия для тестирования среди узкого круга коллег

### 2024.Coming_Soon

Документация, шаблоны, багфиксы

---
