import * as path from 'path';
import * as vscode from 'vscode';
import * as childProcess from 'child_process';



// Странный финт ушами, я искал зачем-то python путь, но обычная Python команда и так бы отработала интерпретатором по умолчанию.



// Получение пути к активному python интерпретатору в ms-python
async function getPathPythonExe(context: vscode.ExtensionContext): Promise<string | undefined> {
    // Получение расширения ms-python для VS Code
    const pythonExtension = vscode.extensions.getExtension('ms-python.python');
    // Проверка, установлено ли и активировано расширение Python
    if (!pythonExtension) {
        vscode.window.showErrorMessage('Расширение Python не установлено или не активировано', 'OK');
        return;
    }

    // Активация расширения Python, если оно еще не активировано
    await pythonExtension.activate();

    // Получение информации об активной Python-среде от расширения Python
    const activeEnvironment = pythonExtension.exports.environments.getActiveEnvironmentPath();

    // Проверка, была ли найдена активная Python-среда и путь в ней
    if (activeEnvironment && activeEnvironment.path) {
        return activeEnvironment.path;
    } else {
        vscode.window.showWarningMessage('Активная Python-среда не найдена', 'OK');
        return undefined;
    }
}




// Функция для получения путей filePath, workspacePath, initFilePath у проекта
async function getPaths() {
    // Получаем активный текстовый редактор
    const activeEditor = vscode.window.activeTextEditor;
    let filePath = activeEditor && activeEditor.document.languageId === 'python' ? activeEditor.document.uri.fsPath : undefined;
    let workspacePath = vscode.workspace.workspaceFolders ? vscode.workspace.workspaceFolders[0].uri.fsPath : undefined;

    let initFilePath;
    if (workspacePath) {
        const initFileUri = vscode.Uri.file(`${workspacePath}/__init__.py`);
        try {
            await vscode.workspace.fs.stat(initFileUri);
            // Файл существует
            initFilePath = initFileUri.fsPath;
        } catch (error) {
            initFilePath = undefined;
        }
    }

    return { filePath, workspacePath, initFilePath };
}




async function getBlenderVersion(pathBlenderExe: string): Promise<string> {
    return new Promise((resolve, reject) => {
        childProcess.exec(`"${pathBlenderExe}" --version`, (error, stdout, stderr) => {
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
    const scriptPath = `${context.extensionPath}/scripts/socketStartProject.py`;

    // Регистрация команды 'blendpybridge.start' в контексте расширения, оперделённую в package.json
    let disposableStart = vscode.commands.registerCommand('blendpybridge.start', async () => {

        // Проверка запущен ли в данный момент терминал чтобы заблокировать старт дубля
        if (terminal) {
            vscode.window.showWarningMessage('Экземпляр уже работает', 'OK');
            return;
        }
        


        // !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        // Получение пути к активному Python интерпретатору
        const pathPythonExe = await getPathPythonExe(context);
        if (!pathPythonExe) {
            // Если "активная среда не найдена", сообщение уже отобразилось в getPathPythonExe
            return;
        }


        
        // Извлекаем сохраненный путь к Blender из globalState
        const pathBlenderExe = context.globalState.get<string>('pathBlenderExe');
        if (!pathBlenderExe) {
            vscode.window.showErrorMessage('Необходимо указать путь к Blender', 'OK');
            return;
        }

        try {
            const blenderVersion = await getBlenderVersion(pathBlenderExe);
            console.log(`Определена версия Blender: ${blenderVersion}`);
    
            // Далее используйте blenderVersion для определения пути к Python и запуска вашего скрипта
            // ...
    
        } catch (error) {
            if (error instanceof Error) {
                vscode.window.showErrorMessage(error.message);
            } else {
                vscode.window.showErrorMessage('Произошла неизвестная ошибка');
            }
        }
        







        // Создание терминала и запуск главного скрипта в нем
        // VS Code срать хотел, что у тебя стоит в PATH и что по дефолту запускается в ms-python, поэтому указываем путь напрямую
        terminal = vscode.window.createTerminal({
            name: terminalName,
            shellPath: pathPythonExe,
            shellArgs: [scriptPath, pathBlenderExe]
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
    // Чё тут по пути к интерпретатору?
    let disposableSendCommandToBlender = vscode.commands.registerCommand('blendpybridge.sendCommandToBlender', async () => {
        const { filePath, workspacePath, initFilePath } = await getPaths();
        const scriptPath = path.join(context.extensionPath, 'scripts', 'socketSendCommand.py');

        // Получение пути к активному Python интерпретатору
        const pathPythonExe = await getPathPythonExe(context);
        if (!pathPythonExe) {
            // Если "активная среда не найдена", сообщение уже отобразилось в getPathPythonExe
            return;
        }

        const command = `${pathPythonExe} "${scriptPath}" "${filePath}" "${workspacePath}" "${initFilePath}"`;
        // Если вывод слишком большой, стоит использовать childProcess.spawn или настроить параметр maxBuffer
        childProcess.exec(command, (err, stdout, stderr) => {
            // err - содержит информацию об ошибке, возникшей во время выполнения команды
            // stdout - это выхлоб самого запускаемого скрипта или программы во время выполнения
            // stderr - стандартный поток ошибок команды, выводятся сообщения самой запускаемой программы

            if (err) {
                // Нельзя выводить логи в всплывающее табло, оно не выводится и почему-то после смены языка
                vscode.window.showErrorMessage(`Ошибка err.message`, 'OK');
                console.error('------------>>>> err <<<<------------');
                console.error(err);
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




    // Выбор нужного blender.exe
    let disposableSelectBlender = vscode.commands.registerCommand('blendpybridge.selectBlenderExecutable', async () => {
        // Диалоговое окно File browser, для выбора файла blender
        const options: vscode.OpenDialogOptions = {
            canSelectMany: false,
            openLabel: 'Select',
            filters: {
                // Фильтр для .exe, .sh, файлы без расширения не отображаются
                'Executable Files': ['exe', 'sh', ''],
                // Фильтр для всех файлов
                'All Files': ['*']
            }
        };
        
        const fileUri = await vscode.window.showOpenDialog(options);
        if (fileUri && fileUri[0]) {
            // Переменная Blender Executable
            let pathBlenderExe = fileUri[0].fsPath;
            await context.globalState.update('pathBlenderExe', pathBlenderExe);
            vscode.window.showInformationMessage(`Blender path selected:\n${pathBlenderExe}`, 'OK');
        } else {
            vscode.window.showWarningMessage('Исполняемый файл Blender не выбран', 'OK');
        }
    });

    // Добавление команд в подписки контекста расширения, для очистки после отключения расширения
    context.subscriptions.push(disposableSelectBlender);


    // Зачистка глобальных переменных
    let disposableCleanBlenderPath = vscode.commands.registerCommand('blendpybridge.cleanPathBlender', async () => {
        // Здесь список ключей, которые вы хотите удалить
        const keysToDelete = ['pathBlenderExe', 'blenderPaths'];

        keysToDelete.forEach(async (key) => {
            await context.globalState.update(key, undefined);
        });

        vscode.window.showInformationMessage('Пути Blender были удалены из глобального состояния', 'OK');
    });

    context.subscriptions.push(disposableCleanBlenderPath);




    // ######## ######## ######## ######## DEBUG ZONE ######## ######## ######## ########
    // Вывод путей к Blender и к Python
    let disposableShowPaths = vscode.commands.registerCommand('blendpybridge.showPaths', async () => {
        const pathPythonExe = await getPathPythonExe(context);
        const pathBlenderExe = context.globalState.get<string>('pathBlenderExe');

        if (!pathPythonExe) {
            vscode.window.showInformationMessage(`Текущий путь Python не определен`, 'OK');
        } else {
            vscode.window.showInformationMessage(`Текущий путь Python: ${pathPythonExe}`, 'OK');
        }
        
        if (!pathBlenderExe) {
            vscode.window.showWarningMessage(`Текущий путь Blender не определен`, 'OK');
        } else {
            vscode.window.showInformationMessage(`Текущий путь Blender: ${pathBlenderExe}`, 'OK');
        }
    });

    context.subscriptions.push(disposableShowPaths);



    // Вывод всех путей для формирования команд
    let disposableShowActivePyFilePath = vscode.commands.registerCommand('blendpybridge.showActivePyFilePath', async () => {
        const { filePath, workspacePath, initFilePath } = await getPaths();
    
        if (filePath) {
            vscode.window.showInformationMessage(`Путь Python файла: ${filePath}`, 'OK');
        } else {
            vscode.window.showWarningMessage('Нет активного Python файла', 'OK');
        }
    
        if (workspacePath) {
            vscode.window.showInformationMessage(`Путь главной папки проекта: ${workspacePath}`, 'OK');
            if (initFilePath) {
                vscode.window.showInformationMessage(`В рабочей области есть __init__.py файл: ${initFilePath}`, 'OK');
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

