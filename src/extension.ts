import * as os from 'os';
import * as fs from 'fs';
import * as path from 'path';
import * as vscode from 'vscode';
import * as childProcess from 'child_process';




// Функция для получения путей pathCurrPyFile, pathWorkspace, pathInitFile у проекта
async function getPathsProject() {
    // Получаем активный текстовый редактор
    const activeEditor = vscode.window.activeTextEditor;
    let pathCurrPyFile = activeEditor && activeEditor.document.languageId === 'python' ? activeEditor.document.uri.fsPath : undefined;
    let pathWorkspace = vscode.workspace.workspaceFolders ? vscode.workspace.workspaceFolders[0].uri.fsPath : undefined;

    let pathInitFile;
    if (pathWorkspace) {
        // Кроссплатформенное формирование пути к файлу __init__.py
        const initFilePath = path.join(pathWorkspace, '__init__.py');
        const initFileUri = vscode.Uri.file(initFilePath);

        try {
            await vscode.workspace.fs.stat(initFileUri);
            // Файл существует
            pathInitFile = initFileUri.fsPath;
        } catch (error) {
            pathInitFile = undefined;
        }
    }

    return { pathCurrPyFile, pathInitFile, pathWorkspace };
}



// Получаем версию Blender запуская исполняемый файл с аргументом --version и разбирается через регулярные выражения
async function getBlenderVersion(pathExecBlender: string): Promise<string> {
    return new Promise((resolve, reject) => {
        childProcess.exec(`"${pathExecBlender}" --version`, (error, stdout, stderr) => {
            if (error) {
                reject(`Ошибка при получении версии Blender: ${error}`);
                return;
            }
            const versionLine = stdout.split('\n')[0];
            const versionMatch = versionLine.match(/Blender (\d+\.\d+)/);
            if (versionMatch && versionMatch.length > 1) {
                resolve(versionMatch[1]);
            } else {
                reject('Не удалось определить версию Blender.');
            }
        });
    });
}




// activate срабатывает при активации расширения
export function activate(context: vscode.ExtensionContext) {

    // Имя терминала
    const terminalName = "BlendPyBridge";
    // Ссылка на созданный терминал
    let terminal: vscode.Terminal | undefined;
    // Путь к главному скрипту проекта
    const scriptPath = path.join(context.extensionPath, 'scripts', 'socketStartProject.py');

    // Регистрация команды 'blendpybridge.start' в контексте расширения, оперделённую в package.json
    let disposableStart = vscode.commands.registerCommand('blendpybridge.startBlender', async () => {

        // Проверка запущен ли в данный момент терминал чтобы заблокировать старт дубля
        if (terminal) {
            vscode.window.showWarningMessage('Экземпляр уже работает');
            return;
        }
        
        // Использование сохраненного пути к Blender
        const pathExecBlender = context.globalState.get<string>('pathExecBlender');
        if (!pathExecBlender) {
            vscode.window.showErrorMessage('Необходимо указать путь к Blender');
            return;
        }

        // Использование сохраненного пути к Python интерпретатору Blender
        const pathExecPython = context.globalState.get<string>('pathExecPython');
        if (!pathExecPython) {
            vscode.window.showErrorMessage('Необходимо указать путь к интерпретатору Python в Blender');
            return;
        }


        let pathEnd;
        let pathBegin;
        const scriptServerSocket = path.join(context.extensionPath, 'scripts', 'socketBlenderBridge.py');

        console.log('%cPython executable:', 'color: yellow');
        // Получение последнего компонента пути и его покраска
        pathEnd = path.basename(pathExecPython);
        pathBegin = pathExecPython.slice(0, pathExecPython.lastIndexOf(pathEnd));
        console.log(`%c${pathBegin}%c${pathEnd}`, 'color: normal', 'color: orange');

        console.log('%cBlender executable:', 'color: yellow');
        // Получение последнего компонента пути и его покраска
        pathEnd = path.basename(pathExecBlender);
        pathBegin = pathExecBlender.slice(0, pathExecBlender.lastIndexOf(pathEnd));
        console.log(`%c${pathBegin}%c${pathEnd}`, 'color: normal', 'color: orange');

        console.log('%cСерверный скрипт:', 'color: yellow');
        pathEnd = path.basename(scriptServerSocket);
        pathBegin = scriptServerSocket.slice(0, scriptServerSocket.lastIndexOf(pathEnd));
        console.log(`%c${pathBegin}%c${pathEnd}`, 'color: normal', 'color: orange');

        console.log('\n------->->>-->>>->>>> %cSTART_BRIDGE%c <<<<-<<<--<<-<-------', 'color: #FF69B4', 'color: reset');


        // [HKEY_LOCAL_MACHINE\Software\Microsoft\Command Processor\Autorun]
        // New String -> Autorun -> @chcp 65001>nul
        // Создание терминала и запуск Blender с Socket сервером
        terminal = vscode.window.createTerminal({
            name: terminalName,
            shellPath: pathExecBlender,
            shellArgs: ["--python", scriptServerSocket]
        });
        

        // Отображение окна терминала, если он был скрыт и переключение на нужный
        terminal.show();

        // Обоработчик жизненного цикла терминала
        const onDidCloseTerminal = vscode.window.onDidCloseTerminal(closedTerminal => {
            if (closedTerminal === terminal) {
                terminal = undefined;
            }
        });

        context.subscriptions.push(onDidCloseTerminal);
    });

    context.subscriptions.push(disposableStart);



    // Отправляем в Blender команду запуска проекта
    async function sendCommandToBlender(pathPyFile: string, pathWorkspace: string) {
        // const { pathCurrPyFile, pathWorkspace, pathInitFile } = await getPathsProject();
        const scriptPath = path.join(context.extensionPath, 'scripts', 'socketSendCommand.py');

        // Использование сохраненного пути к Python интерпретатору Blender
        const pathExecPython = context.globalState.get<string>('pathExecPython');
        if (!pathExecPython) {
            vscode.window.showErrorMessage('Необходимо указать путь к интерпретатору Python в Blender');
            return;
        }

        // const command = `${pathExecPython} "${scriptPath}" "${pathCurrPyFile}" "${pathWorkspace}" "${pathInitFile}"`;
        const command = `${pathExecPython} "${scriptPath}" "${pathPyFile}" "${pathWorkspace}"`;
        // const command = `${pathExecPython} "${scriptPath}" "${pathInitFile}" "${pathWorkspace}"`;

        // Если вывод слишком большой, стоит использовать childProcess.spawn или настроить параметр maxBuffer
        childProcess.exec(command, (err, stdout, stderr) => {
            // err - содержит информацию об ошибке, возникшей во время выполнения команды
            // stdout - это выхлоб самого запускаемого скрипта или программы во время выполнения
            // stderr - стандартный поток ошибок команды, выводятся сообщения самой запускаемой программы

            if (err) {
                // Нельзя выводить логи в всплывающее табло, оно не выводится
                // Подключение не установлено, т.к. конечный компьютер отверг запрос на подключение
                console.error('------------>>>> err <<<<------------');
                console.error(err);

                // Проверка на конкретное сообщение об ошибке
                if (err.message && err.message.includes('ConnectionRefusedError')) {
                    vscode.window.showErrorMessage('Ошибка подключения: конечный компьютер отверг запрос на подключение');
                } else {
                    // Вывод общего сообщения об ошибке
                    vscode.window.showErrorMessage('Произошла ошибка, но я пока не знаю какая. Пожалуйста пришлите мне её в Issuie.');
                }
                return;
            }
            if (stdout) {
                console.error('------------>>>> stdout <<<<------------');
                console.error(stdout);
                return;
            }
            if (stderr) {
                vscode.window.showErrorMessage(`Ошибка stderr`);
                console.error('------------>>>> stderr <<<<------------');
                console.error(stderr);
                return;
            }
            vscode.window.showInformationMessage(`Команда отправлена`);
        });
    }


    // Обработчик команды для запуска текущего скрипта
    let disposableRunCurrScript = vscode.commands.registerCommand('blendpybridge.runCurrScript', async () => {
        // Проверяем, запущен ли в данный момент терминал с Blender
        if (!terminal) {
            vscode.window.showErrorMessage('Blender не запущен, некуда отправлять.');
            return;
        }

        const { pathCurrPyFile, pathWorkspace } = await getPathsProject();
    
        if (typeof pathCurrPyFile === 'string' && typeof pathWorkspace === 'string') {
            sendCommandToBlender(pathCurrPyFile, pathWorkspace);
        } else {
            // Обработка случая, когда один из путей не определен
            vscode.window.showErrorMessage('Не удалось получить путь к файлу скрипта или рабочей области.');
        }
    });

    // Обработчик команды для запуска всего пакета
    let disposableRunEntirePackage = vscode.commands.registerCommand('blendpybridge.runEntirePackage', async () => {
        // Проверяем, запущен ли в данный момент терминал с Blender
        if (!terminal) {
            vscode.window.showErrorMessage('Blender не запущен, некуда отправлять.');
            return;
        }

        const { pathInitFile, pathWorkspace } = await getPathsProject();
    
        if (typeof pathInitFile === 'string' && typeof pathWorkspace === 'string') {
            sendCommandToBlender(pathInitFile, pathWorkspace);
        } else {
            // Обработка случая, когда один из путей не определен
            vscode.window.showErrorMessage('Не удалось получить путь к __init__ файлу или рабочей области');
        }
    });
    
    context.subscriptions.push(disposableRunCurrScript, disposableRunEntirePackage);




    // Выбор пути к blender и его Python интерпретатору
    let disposablePathExecSel = vscode.commands.registerCommand('blendpybridge.pathExecSel', async () => {

        // Проверяем, запущен ли в данный момент терминал
        if (terminal) {
            vscode.window.showWarningMessage('Нельзя изменять путь к Blender и Python, пока Blender запущен');
            return;
        }

        // Win
        // \APP\blender-2.83.20-windows-x64\2.83\python\bin\python.exe
        // \APP\blender-2.93.18-windows-x64\2.93\python\bin\python.exe
        // \APP\blender-3.0.1  -windows-x64\3.0 \python\bin\python.exe
        // \APP\blender-3.1.2  -windows-x64\3.1 \python\bin\python.exe
        // \APP\blender-3.3.12 -windows-x64\3.3 \python\bin\python.exe
        // \APP\blender-3.6.5  -windows-x64\3.6 \python\bin\python.exe
        // \APP\blender-4.0.2  -windows-x64\4.0 \python\bin\python.exe

        // Lin
        // \blender-2.83.20-linux-x64\2.83\python\bin\python3.7m
        // \blender-2.93.18-linux-x64\2.93\python\bin\python3.9
        // \blender-3.3.15 -linux-x64\3.3 \python\bin\python3.10
        // \blender-3.6.8  -linux-x64\3.6 \python\bin\python3.10
        // \blender-4.0.2  -linux-x64\4.0 \python\bin\python3.10

        // 'win32' ? 'windows' : 'linux'
        const platform = os.platform();

        let filters;
        if (platform === "win32") {
            // Для Windows показываем только .exe и все файлы
            filters = {
                'Executable Files': ['exe'],
                'All Files': ['*']
            };
        } else {
            // Для Linux (и других систем, не являющихся Windows) показываем все файлы
            filters = {
                'All Files': ['*'],
                'Executable Files': ['sh'],
            };
        }
    
        const options: vscode.OpenDialogOptions = {
            canSelectMany: false,
            openLabel: 'Select',
            filters: filters
        };


        // Отображение диалогового окна и ожидание выбора файла пользователем
        const fileUri = await vscode.window.showOpenDialog(options);
        if (fileUri && fileUri[0]) {
            // Если файл выбран, получаем его путь
            let pathExecBlender = fileUri[0].fsPath;
            // console.log(`Выбранный путь: ${pathExecBlender}`);

            // Получаем имя файла из полного пути
            const fileName = path.basename(pathExecBlender);
            // console.log(`Имя выбранного файла: ${fileName}`);

            // Проверяем, начинается ли имя файла с 'blender' или 'blender.exe' для различных ОС
            if ((platform === "win32" && fileName === "blender.exe") || (platform !== "win32" && fileName.startsWith("blender"))) {

                // Опеределяем версию Blender
                let blenderVersion;
                try {
                    blenderVersion = await getBlenderVersion(pathExecBlender);
                    console.log(`Определена версия Blender: ${blenderVersion}`);
                    // Если getBlenderVersion успешно выполнилась, значит, выбранный файл вероятно является Blender
                    await context.globalState.update('pathExecBlender', pathExecBlender);
                } catch (error) {
                    vscode.window.showErrorMessage("Произошла ошибка при определении версии Blender.");
                    return;
                }
                
                // Папка выбранного файла
                let blenderBasePath = path.dirname(pathExecBlender);
                // console.log(`Имя директории: ${blenderBasePath}`);
                // Формирование пути к Python директории Blender-а
                const pythonDir = path.join(blenderBasePath, `${blenderVersion}`, 'python', 'bin');
                // console.log(`Путь к директории Python: ${pythonDir}`);

                // Существует ли ожидаемый путь до папки с python интерпретатором
                if (!fs.existsSync(pythonDir)) {
                    vscode.window.showErrorMessage('Не найдена директория Python для данной версии Blender');
                    return;
                }

                let pathExecPython;
                // Формирование пути к Python интерпретатору Blender-а в завимости от особеннсоей систем и версий Blender для них
                if (platform === "win32") {
                    pathExecPython = path.join(pythonDir, 'python.exe');
                } else {
                    const files = fs.readdirSync(pythonDir);
                    const pythonExec = files.find(file => file.startsWith('python'));
                    pathExecPython = pythonExec ? path.join(pythonDir, pythonExec) : null;
                }

                // Проверка существования файла Python по собранному пути
                if (pathExecPython && fs.existsSync(pathExecPython)) {
                    await context.globalState.update('pathExecPython', pathExecPython);
                    vscode.window.showInformationMessage(`Blender path selected:\n${pathExecBlender}`);
                    vscode.window.showInformationMessage(`Python path: ${pathExecPython}`);
                } else {
                    vscode.window.showErrorMessage('Не найден интерпретатор Python для данной версии Blender');
                }

            } else {
                vscode.window.showErrorMessage("Выбранный файл не соответствует ожидаемому названию исполняемого файла Blender.");
            }

        } else {
            // Если файл не был выбран, показываем предупреждающее сообщение
            vscode.window.showWarningMessage('Исполняемый файл Blender не выбран');
        }
    });

    // Добавление команд в подписки контекста расширения, для очистки после отключения расширения
    context.subscriptions.push(disposablePathExecSel);


    // Зачистка глобальных переменных
    let disposablePathExecClean = vscode.commands.registerCommand('blendpybridge.pathExecClean', async () => {

        // Проверяем, запущен ли в данный момент терминал
        if (terminal) {
            vscode.window.showWarningMessage('Нельзя очистить пути, пока Blender запущен');
            return;
        }

        // Здесь список ключей, которые вы хотите удалить
        const keysToDelete = ['blenderPaths', 'pathBlenderExe', 'pathExecBlender', 'pathExecPython'];

        keysToDelete.forEach(async (key) => {
            await context.globalState.update(key, undefined);
        });

        vscode.window.showInformationMessage('Путь к Blender из глобальных переменных был удален');
    });

    context.subscriptions.push(disposablePathExecClean);




    // ######## ######## ######## ######## DEBUG ZONE ######## ######## ######## ########
    // Вывод путей к Blender и к Python
    let disposablePathExecShow = vscode.commands.registerCommand('blendpybridge.pathExecShow', async () => {
        // Заменить на путь Python Blender <---------------------------------
        // const pathPythonExe = await getPathPythonExe(context);
        const pathExecPython = context.globalState.get<string>('pathExecPython');
        const pathExecBlender = context.globalState.get<string>('pathExecBlender');

        if (pathExecPython) {
            vscode.window.showInformationMessage(`Текущий путь Python: ${pathExecPython}`, 'OK');
            
        } else {
            vscode.window.showWarningMessage(`Текущий путь Python не определен`);
        }
        
        if (pathExecBlender) {
            vscode.window.showInformationMessage(`Текущий путь Blender: ${pathExecBlender}`, 'OK');
        } else {
            vscode.window.showWarningMessage(`Текущий путь Blender не определен`);
        }
    });

    context.subscriptions.push(disposablePathExecShow);



    // Вывод всех путей для формирования команд
    let disposableShowPathsProject = vscode.commands.registerCommand('blendpybridge.showPathsProject', async () => {
        const { pathCurrPyFile, pathWorkspace, pathInitFile } = await getPathsProject();
    
        if (pathCurrPyFile) {
            vscode.window.showInformationMessage(`Путь к исполняемому Python файлу: ${pathCurrPyFile}`, 'OK');
        } else {
            vscode.window.showWarningMessage('Нет активного Python файла');
        }
    
        if (pathWorkspace) {
            vscode.window.showInformationMessage(`Путь главной папки проекта: ${pathWorkspace}`, 'OK');
            if (pathInitFile) {
                vscode.window.showInformationMessage(`В рабочей области есть __init__.py файл - это пакет`);
            } else {
                vscode.window.showWarningMessage('В рабочей области нет __init__.py файла - проект не является пакетом');
            }
        } else {
            vscode.window.showWarningMessage('Нет рабочей области');
        }
    });

    context.subscriptions.push(disposableShowPathsProject);



}



// Функция, срабатывающая при деактивации аддона
export function deactivate() {}


