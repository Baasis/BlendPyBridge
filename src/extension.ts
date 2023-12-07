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

    return { pathCurrPyFile, pathWorkspace, pathInitFile };
}



// Здесь мы не проверяем наличие пути, проверим перед вызовом !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
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
    let disposableStart = vscode.commands.registerCommand('blendpybridge.start', async () => {

        // Проверка запущен ли в данный момент терминал чтобы заблокировать старт дубля
        if (terminal) {
            vscode.window.showWarningMessage('Экземпляр уже работает', 'OK');
            return;
        }
        
        // Использование сохраненного пути к Blender
        const pathExecBlender = context.globalState.get<string>('pathExecBlender');
        if (!pathExecBlender) {
            vscode.window.showErrorMessage('Необходимо указать путь к Blender', 'OK');
            return;
        }

        // Использование сохраненного пути к Python интерпретатору Blender
        const pathExecPython = context.globalState.get<string>('pathExecPython');
        if (!pathExecPython) {
            vscode.window.showErrorMessage('Необходимо указать путь к интерпретатору Python в Blender', 'OK');
            return;
        }

        // Создание терминала и запуск главного скрипта в нем
        // VS Code срать хотел, что у тебя стоит в PATH и что по дефолту запускается в ms-python, поэтому указываем путь напрямую
        terminal = vscode.window.createTerminal({
            name: terminalName,
            shellPath: pathExecPython,
            shellArgs: [scriptPath, pathExecBlender]
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



    // !!!!!!!!!!!!!!! Нельзя отправлять пока Blender не запущен
    let disposableSendCommandToBlender = vscode.commands.registerCommand('blendpybridge.sendCommandToBlender', async () => {
        const { pathCurrPyFile, pathWorkspace, pathInitFile } = await getPathsProject();
        const scriptPath = path.join(context.extensionPath, 'scripts', 'socketSendCommand.py');

        // Использование сохраненного пути к Python интерпретатору Blender
        const pathExecPython = context.globalState.get<string>('pathExecPython');
        if (!pathExecPython) {
            vscode.window.showErrorMessage('Необходимо указать путь к интерпретатору Python в Blender', 'OK');
            return;
        }

        const command = `${pathExecPython} "${scriptPath}" "${pathCurrPyFile}" "${pathWorkspace}" "${pathInitFile}"`;
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
                    vscode.window.showErrorMessage('Ошибка подключения: конечный компьютер отверг запрос на подключение', 'OK');
                } else {
                    // Вывод общего сообщения об ошибке
                    vscode.window.showErrorMessage('Произошла ошибка, но я пока не знаю какая. Пожалуйста пришлите мне её в Issuie.', 'OK');
                }
                return;
            }
            if (stdout) {
                // vscode.window.showErrorMessage(`stdout`, 'OK');
                console.error('------------>>>> stdout <<<<------------');
                console.error(stdout);
                return;
            }
            if (stderr) {
                vscode.window.showErrorMessage(`Ошибка stderr`, 'OK');
                console.error('------------>>>> stderr <<<<------------');
                console.error(stderr);
                return;
            }
            vscode.window.showInformationMessage(`Команда отправлена`, 'OK');
        });
    });

    context.subscriptions.push(disposableSendCommandToBlender);




    // Выбор пути к blender.exe и его Python интерпретатору
    // В linux всегда отображение всех файлов !!!!!!!!!!!!!!!!!!!!!!!!!!!!
    let pathExecSel = vscode.commands.registerCommand('blendpybridge.pathExecSel', async () => {
        // Диалоговое окно File browser, для выбора файла blender
        const options: vscode.OpenDialogOptions = {
            // Позволяет выбрать только один файл.
            canSelectMany: false,
            // Текст, который будет отображаться на кнопке для подтверждения выбора файла в диалоговом окне
            openLabel: 'Select',
            filters: {
                // Фильтр для .exe, .sh, файлы без расширения не отображаются
                'Executable Files': ['exe', 'sh', ''],
                // Строка фильтра для отображения всех файлов
                'All Files': ['*']
            }
        };

        // Отображение диалогового окна и ожидание выбора файла пользователем
        const fileUri = await vscode.window.showOpenDialog(options);
        if (fileUri && fileUri[0]) {
            // Если файл выбран, получаем его путь
            let pathExecBlender = fileUri[0].fsPath;
            // Сохраняем путь к исполняемому файлу Blender в глобальном состоянии расширения
            await context.globalState.update('pathExecBlender', pathExecBlender);
            // Показываем сообщение с выбранным путем

            try {
                const blenderVersion = await getBlenderVersion(pathExecBlender);
                console.log(`Определена версия Blender: ${blenderVersion}`);
    
                // Удаление 'blender.exe' из пути, чтобы получить базовый путь
                let blenderBasePath = path.dirname(pathExecBlender);
    
                // Формирование пути к Python
                let pathExecPython = path.join(blenderBasePath, `${blenderVersion}`, 'python', 'bin', 'python.exe');
    
                // Проверка существования файла Python
                if (fs.existsSync(pathExecPython)) {
                    await context.globalState.update('pathExecPython', pathExecPython);
                    vscode.window.showInformationMessage(`Blender path selected:\n${pathExecBlender}`, 'OK');
                    vscode.window.showInformationMessage(`Python path: ${pathExecPython}`, 'OK');
                } else {
                    vscode.window.showErrorMessage('Не найден интерпретатор Python для данной версии Blender');
                }
    
            } catch (error) {
                if (error instanceof Error) {
                    vscode.window.showErrorMessage(error.message);
                } else {
                    vscode.window.showErrorMessage('Произошла неизвестная ошибка');
                }
            }
        } else {
            // Если файл не был выбран, показываем предупреждающее сообщение
            vscode.window.showWarningMessage('Исполняемый файл Blender не выбран', 'OK');
        }
    });

    // Добавление команд в подписки контекста расширения, для очистки после отключения расширения
    context.subscriptions.push(pathExecSel);


    // Зачистка глобальных переменных
    let pathExecClean = vscode.commands.registerCommand('blendpybridge.pathExecClean', async () => {
        // Здесь список ключей, которые вы хотите удалить
        const keysToDelete = ['blenderPaths', 'pathBlenderExe', 'pathExecBlender', 'pathExecPython'];

        keysToDelete.forEach(async (key) => {
            await context.globalState.update(key, undefined);
        });

        vscode.window.showInformationMessage('Путь к Blender из глобальных переменных был удален', 'OK');
    });

    context.subscriptions.push(pathExecClean);




    // ######## ######## ######## ######## DEBUG ZONE ######## ######## ######## ########
    // Вывод путей к Blender и к Python
    let pathExecShow = vscode.commands.registerCommand('blendpybridge.pathExecShow', async () => {
        // Заменить на путь Python Blender <---------------------------------
        // const pathPythonExe = await getPathPythonExe(context);
        const pathExecPython = context.globalState.get<string>('pathExecPython');
        const pathExecBlender = context.globalState.get<string>('pathExecBlender');

        if (pathExecPython) {
            vscode.window.showInformationMessage(`Текущий путь Python: ${pathExecPython}`, 'OK');
            
        } else {
            vscode.window.showWarningMessage(`Текущий путь Python не определен`, 'OK');
        }
        
        if (pathExecBlender) {
            vscode.window.showInformationMessage(`Текущий путь Blender: ${pathExecBlender}`, 'OK');
        } else {
            vscode.window.showWarningMessage(`Текущий путь Blender не определен`, 'OK');
        }
    });

    context.subscriptions.push(pathExecShow);



    // Вывод всех путей для формирования команд
    let disposableShowActivePyFilePath = vscode.commands.registerCommand('blendpybridge.showActivePyFilePath', async () => {
        const { pathCurrPyFile, pathWorkspace, pathInitFile } = await getPathsProject();
    
        if (pathCurrPyFile) {
            vscode.window.showInformationMessage(`Путь Python файла: ${pathCurrPyFile}`, 'OK');
        } else {
            vscode.window.showWarningMessage('Нет активного Python файла', 'OK');
        }
    
        if (pathWorkspace) {
            vscode.window.showInformationMessage(`Путь главной папки проекта: ${pathWorkspace}`, 'OK');
            if (pathInitFile) {
                vscode.window.showInformationMessage(`В рабочей области есть __init__.py файл: ${pathInitFile}`, 'OK');
            } else {
                vscode.window.showWarningMessage('В рабочей области нет __init__.py файла', 'OK');
            }
        } else {
            vscode.window.showWarningMessage('Нет рабочей области', 'OK');
        }
    });

    context.subscriptions.push(disposableShowActivePyFilePath);



}



// Функция, срабатывающая при деактивации аддона
export function deactivate() {}

