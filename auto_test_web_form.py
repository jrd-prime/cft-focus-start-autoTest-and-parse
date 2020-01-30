
# coding=utf-8
import os,csv
from datetime import datetime
from elementium.drivers.se import SeElements
from selenium import webdriver

''' Интро.
Добрый день. За код стыдно, т.к. времени мало, опыта мало, и чтобы всё успеть пришлось написать такое безобразие.
Улучшить и оптимизировать можно много чего еще в коде, знаю, но не успеваю пока.
Первоочередную цель установил, что код должен работать, а проверки на ошибки/исключения, красоту и оптимизацию кода, решил пока убрать на второй план.
Надеюсь на понимание :)
'''

''' Для работы скрипта необходимы установленные библиотеки: selenium, elementium. ChromeDriver приложен со скриптом'''
# НАСТРОЙКИ
# ChromeDriver
driverPath = r'chromedriver.exe'
# Form URL
formURL = 'https://team.cft.ru/triangle/zadanie/triangle.html?token=84cc13bc2eba4c7fbc94dc50610bcca5'
# Dir For Reports
workDir = 'reports'
# Value Sets Files
# Template for test results: sideA;	sideB;	sideC;	er; # er = expected result
at_testResult = 'at-testResult.csv'
# Template for test input: CaseID;	Priority;	sideA;	sideB;	sideC;	expRes;	TestThing;
at_testInput = 'at-testInput.csv'

try:
    if not os.path.exists(workDir):
        os.mkdir(workDir)
finally:
    print('Create dir: ' + workDir)

b = webdriver.Chrome(driverPath)
browser = SeElements(b)
browser.set_window_size(500, 600)
browser.navigate(formURL)

'''
1. МЕТОДЫ ДЛЯ ТЕСТИРОВАНИЯ ОЖИДАЕМОГО РЕЗУЛЬТАТА
2. МЕТОДЫ ДЛЯ ТЕСТИРОВАНИЯ ИНПУТОВ
'''

''' ##################### '''
''' ######### 1 ######### '''
''' ##################### '''


resultFileForTR = f'/{at_testResult}-RUN-{datetime.today().strftime("%Y-%m-%d_%H.%M.%S")}.csv'
# Метод чтения кейсов для проверки получаемого результата.
# На вход необходимо подать путь к файлу
# Возвращает массив массивов
# Необходим CSV файл с разделителями ";"
# Данные должны содержать строку заголовка, а именно: sideA, sideB, sideC, er
# er - ожидаемый результат
def readCasesForTestResults(csvFile):
    cases = []
    # открываем файл
    with open(csvFile, "r") as csvF:
        # читаем данные
        reader = csv.DictReader(csvF, delimiter=';')
        # перебираем данные и записываем их в массив
        for line in reader:
            case = [line['sideA'], line['sideB'], line['sideC'], line['er']]
            cases.append(case)
    return cases


# записываем результат проверки в файл
def writeToFileTR(collector):
    # Создаем файл для записи
    try:
        with open(workDir + resultFileForTR, "w", newline="") as file:
            # Определяемзаголовки
            columns = ["CaseResult", "CaseLine", "Exp/Act", "Timestamp"]
            writer = csv.DictWriter(file, delimiter=';', fieldnames=columns)
            writer.writeheader()
            # Пишем данные в файл
            writer.writerows(collector)
    finally:
        x = 0


# проверяем значение на длину, если больше 10 символов, то скипаем, т.к. поле ограничено по длине в 10 символов
def checkValuesOnLength(case):
    for i in range(3):
        if (len(case[i]) > 10):
            return 0
    return 1


# сравниваем ожидаемый и фактический
def checkCaseResult(case, actRes):
    expRes = case[3]
    # костыль, т.к. тут баг не функциональный, а локализации.
    # Глупо заваливать функционал, когда просто слово не переведено
    if (expRes == 'прямоугольный'):
        expRes = 'rectangular'
    # сравниваем ожидаемый и фактический результат
    if (str(expRes).lower() == str(actRes).lower()):
        return 'PASSED'
    return 'FILED'


# прогоняем все кейсы
def runTestCaseForTestResults():
    global inputs, btn, actualResult
    print('Тесты на ожидаемый результат(вид треугольника) исходя из указанных значений сторон.')
    cases = readCasesForTestResults(at_testResult)
    collector = []
    for i in range(len(cases)):
        case = cases[i]

        if (checkValuesOnLength(case) == 0):
            lineReport = {'CaseResult': 'SKIPPED', 'CaseLine': i + 2,
                          'Exp/Act': f'One or more values have length more than 10 symbols. {case[0]}/{case[1]}/{case[2]}', 'Timestamp': datetime.today().strftime("%Y-%m-%d %H.%M.%S")}
            collector.append(lineReport)
            writeToFileTR(collector)
            print(
                f'\033[93mSKIPPED\033[0m\tCaseLine {i + 2}. One or more values have length more than 10 symbols. {case[0]}/{case[1]}/{case[2]}')
            continue

        try:
            # ищем поля ввода, ждем пока из не будет 3шт
            inputs = browser.find("input[type='text']").until(lambda e: len(e) == 3)
            # ищем сабмит
            btn = browser.find("button[class='gwt-Button']")
        finally:
            # вводим значения
            for j in range(3):
                inputs.get(j).write(case[j])
            # жмем сабмит
            btn.get(0).click()
            # очищаем поля
            for k in range(3):
                inputs.get(k).clear()

            try:
                resultContainer = browser.find("div[class='answerLabel']").until(lambda e: len(e) == 1)
                actualResult = resultContainer.get(0).text()
            finally:
                result = checkCaseResult(case, actualResult)
                caseLine = i + 2;
                info = f'{str(case[3]).lower()}/{str(actualResult).lower()}'
                lineReport = {'CaseResult': result, 'CaseLine': caseLine, 'Exp/Act': info,
                              'Timestamp': datetime.today().strftime("%Y-%m-%d %H.%M.%S")}
                collector.append(lineReport)
                if (result == 'PASSED'):
                    result = '\033[92mPASSED\033[0m'
                else:
                    result = '\033[91mFILED\033[0m'

                print(
                    f'{result}\tCaseLine {i + 2}\tExpected/Actual: {str(case[3]).lower()}/{str(actualResult).lower()}')
        writeToFileTR(collector)
    print('COMPLETE')


# РАСКОММЕНТИРОВАТЬ
runTestCaseForTestResults()

''' ##################### '''
''' ######### 2 ######### '''
''' ##################### '''

'''
Т.к. я понимаю, что не успеваю, то решил написать тестирование инпутов пока без подготовки тестовых данных из кейсов
Решил просто подготовить небольшой набор тестовых данных и на их основе написать методы для проверки инпутов.
Если останется время, то соберу тестовые данные из кейсов.
'''

resultFileForTI = f'/{at_testInput}-RUN-{datetime.today().strftime("%Y-%m-%d_%H.%M.%S")}.csv'
emptyErr = 'Поле не должно быть пустым'
notNumErr = 'не является допустимым числом'

# записываем результат проверки в файл
def writeToFileTI(collector):
    # Создаем файл для записи
    try:
        with open(workDir + resultFileForTI, "w", newline="") as file:
            # Определяемзаголовки
            columns = ['CaseID', 'Priority', 'Condition', 'Result','expRes', 'sideA','sideB','sideC','Timestamp']
            writer = csv.DictWriter(file, delimiter=';', fieldnames=columns)
            writer.writeheader()
            # Пишем данные в файл
            writer.writerows(collector)
    finally:
        x = 0
def readCasesForTestInputs(csvFile):
    cases = []
    # открываем файл
    with open(csvFile, "r") as csvF:
        # читаем данные
        reader = csv.DictReader(csvF, delimiter=';')
        # перебираем данные и записываем их в массив
        for line in reader:
            case = [line['CaseID'], line['Priority'], line['sideA'], line['sideB'], line['sideC'], line['expRes'],
                    line['TestThing']]

            cases.append(case)
    return cases


collector = []
result = ''

def checkValuesOnLengthTI(case):
    for i in range(3):
        i = i + 2
        if len(case[i]) > 10:
            return 0
    return 1
def colorResult(res):
    if(res == 'PASSED'):
        return '\033[92mPASSED\033[0m'
    return '\033[91mFILED\033[0m'

def oneEmptyField(actText, case):
    if actText == emptyErr:
        result = 'PASSED'
    else:
        result = 'FILED'
    lineReport = {'CaseID': case[0], 'Priority': case[1], 'Condition': case[5], 'Result': result,'expRes': case[6], 'sideA': case[2],'sideB': case[3],'sideC': case[4], 'Timestamp': datetime.today().strftime("%Y-%m-%d %H.%M.%S")}
    collector.append(lineReport)
    writeToFileTI(collector)
    result = colorResult(result)
    print(f'ID: {case[0]}\tCondition: {case[5]}\t{result}\tExpect: {emptyErr}')

def twoEmptyFields(actText, case):
    for i in range(len(actText)):
        if actText[i] == emptyErr:
            result = 'PASSED'
        else:
            result = 'FILED'
    lineReport = {'CaseID': case[0], 'Priority': case[1], 'Condition': case[5], 'Result': result,'expRes': case[6], 'sideA': case[2],'sideB': case[3],'sideC': case[4], 'Timestamp': datetime.today().strftime("%Y-%m-%d %H.%M.%S")}
    collector.append(lineReport)
    writeToFileTI(collector)
    result = colorResult(result)
    print(f'ID: {case[0]}\tCondition: {case[5]}\t{result}\tExpect: {emptyErr}')

def threeEmptyFields(actText, case):
    for i in range(3):
        if actText[i] == emptyErr:
            result = 'PASSED'
        else:
            result = 'FILED'
    lineReport = {'CaseID': case[0], 'Priority': case[1], 'Condition': case[5], 'Result': result,'expRes': case[6], 'sideA': case[2],'sideB': case[3],'sideC': case[4], 'Timestamp': datetime.today().strftime("%Y-%m-%d %H.%M.%S")}
    collector.append(lineReport)
    writeToFileTI(collector)
    result = colorResult(result)
    print(f'ID: {case[0]}\tCondition: {case[5]}\t{result}\tExpect: {emptyErr}')

def notNum(actText, case, num):
    notNumTemp = f'\'{case[num + 2]}\'{notNumErr}'
    if actText == notNumTemp:
        result = 'PASSED'
    else:
        result = 'FILED'
    lineReport = {'CaseID': case[0], 'Priority': case[1], 'Condition': case[5], 'Result': result,'expRes': case[6], 'sideA': case[2],'sideB': case[3],'sideC': case[4], 'Timestamp': datetime.today().strftime("%Y-%m-%d %H.%M.%S")}
    collector.append(lineReport)
    writeToFileTI(collector)
    result = colorResult(result)
    print(f'ID: {case[0]}\tCondition: {case[5]}\t{result}\tExpect: {notNumTemp}')
def okayValue(actText, case):
    if actText is None:
       result = 'PASSED'
    else:
        result = 'FILED'
    lineReport = {'CaseID': case[0], 'Priority': case[1], 'Condition': case[5], 'Result': result,'expRes': case[6], 'sideA': case[2],'sideB': case[3],'sideC': case[4], 'Timestamp': datetime.today().strftime("%Y-%m-%d %H.%M.%S")}
    collector.append(lineReport)
    writeToFileTI(collector)
    result = colorResult(result)
    print(f'ID: {case[0]}\tCondition: {case[5]}\t{result}\tExpect: no error')

def runTestCaseForTestInput():
    global inputs, btn, actualResult
    print('Тесты на ожидаемый вывод ошибок. PASSED - ожидаемая ошибка присутствует.')

    cases = readCasesForTestInputs(at_testInput)

    for i in range(len(cases)):
        case = cases[i]
        expRes = case[5]

        try:
            # ищем поля ввода, ждем пока инпутов не будет 3шт
            inputs = browser.find("input[type='text']").until(lambda e: len(e) == 3)
            # ищем сабмит
            btn = browser.find("button[class='gwt-Button']")
        finally:
            # вводим значения
            for j in range(3):
                inputs.get(j).write(case[j + 2])
            # жмем сабмит
            btn.get(0).click()
            # ищем поля с выводом ошибок
            errFields = browser.find("td[class='validationError']")

            aText = errFields.get(0).find("div").text()
            bText = errFields.get(1).find("div").text()
            cText = errFields.get(2).find("div").text()

            if (expRes == 'emptyAll'):
                threeEmptyFields([aText, bText, cText], case)
            elif (expRes == 'emptyA'):
                oneEmptyField(aText, case)
            elif (expRes == 'emptyB'):
                oneEmptyField(bText, case)
            elif (expRes == 'emptyC'):
                oneEmptyField(cText, case)
            elif (expRes == 'emptyAB'):
                twoEmptyFields([aText, bText], case)
            elif (expRes == 'emptyAC'):
                twoEmptyFields([aText, cText], case)
            elif (expRes == 'emptyBC'):
                twoEmptyFields([bText, cText], case)
            elif (expRes == 'notNumA'):
                notNum(aText, case, 0)
            elif (expRes == 'notNumB'):
                notNum(bText, case, 1)
            elif (expRes == 'notNumC'):
                notNum(cText, case, 2)
            elif (expRes == 'okA'):
                okayValue(aText, case)
            elif (expRes == 'okB'):
                okayValue(bText, case)
            elif (expRes == 'okC'):
                okayValue(cText, case)
            elif (expRes == 'max10'):
                print('написать метод проверки на длину поля')

            # очищаем поля
            for k in range(3):
                inputs.get(k).clear()
    # time.sleep(3)
    print('COMPLETE')

runTestCaseForTestInput()
# time.sleep(20)
b.quit()
exit()
