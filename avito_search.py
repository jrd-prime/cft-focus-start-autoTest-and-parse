from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from urllib.parse import urlparse
from PIL import Image
import os, io, csv, time, base64, pytesseract

# ВХОДНЫЕ ДАННЫЕ
city = 'новосибирск'
category = 'Коллекционирование'
word = 'lego'
price = 5000

# НАСТРОЙКИ
driverPath = r'E:\fs\chromedriver.exe'
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
startPage = 'https://avito.ru/krasnoyarsk'
workDir = 'C:/avitosearch'
resultFile = '/results.csv'
tempImgFile = '/temp_img.jpg'

# Решил вести лог, через print

try:
    if not os.path.exists(workDir):
        os.mkdir(workDir)
finally:
    print('Создали папку под временные файлы: ' + workDir)

browser = webdriver.Chrome(driverPath)
browser.get(startPage)

print('BEGIN ### Choose City ###')
print(f'\tТекущий url: {browser.current_url}')

# Жмем на смену города
browser.find_element_by_xpath('//div[@data-marker="search-form/location"]').click()

try:
    WebDriverWait(browser, 10)
    # Находим поле для ввода
    pole = browser.find_element_by_xpath('//input[@data-marker="popup-location/region/input"]')
    # Вводим город
    pole.send_keys(city)
finally:
    print('\tВвели город')

# Костыль
try:
    pole.send_keys(Keys.ENTER)
finally:
    print('\tУбрали фокус с инпута')

# Спим
time.sleep(3)
try:
    pole.send_keys(Keys.ENTER)
    # Жмем кнопку отправки формы
    browser.find_element_by_xpath('//button[@data-marker="popup-location/save-button"]').click()
finally:
    print('\tСабмитнули')

print(f'\tТекущий url: {browser.current_url}')
print('END ### Choose City ###')


def fillFilters():
    print('BEGIN ### fillFilters ###')

    agreeXPath = '//button[@data-marker="location/tooltip-agree"]'
    categoryXPath = f'//select[@name="category_id"]/option[text()="{category}"]'
    nameXPath = '//input[@id="search" and @data-marker="search-form/suggest"]'
    priceXPath = '//input[@data-marker="price/from"]'
    submitXPath = '//button[@data-marker="search-filters/submit-button"]'

    try:
        WebDriverWait(browser, 10)
        # Выбираем категорию
        browser.find_element_by_xpath(categoryXPath).click()
        print('\tКатегория выбрана')

        browser.get(browser.current_url)

        try:
            WebDriverWait(browser, 10)
            # Вводим поисковое слово
            browser.find_element_by_xpath(nameXPath).send_keys(word)
            print('\tСлово введено')

            try:
                WebDriverWait(browser, 10)
                # Вводим цену ОТ 5000
                browser.find_element_by_xpath(priceXPath).send_keys(price)
            finally:
                print('\tЦена введена')
        finally:
            print('\tФильтры заполнены и применены\n')

        # Применяем фильтр
        browser.find_element_by_xpath(submitXPath).click()
    finally:
        print('END ### fillFilters ###')


def getItemURLs():
    print('BEGIN ### getItemURLs ###')
    itemCountXPath = '//span[@class="page-title-count"]'
    linkXPath = '//a[@itemprop="url"]'

    browser.get(browser.current_url)

    try:
        WebDriverWait(browser, 10)
        # Получаем кол-во найденных результатов
        itemCount = len(browser.find_elements_by_xpath('//div[@data-marker="item"]'))

        currPath = urlparse(str(browser.current_url)).path
        currPath = currPath.split('/')
        currPath = currPath[1]

        print(f'\tНайдено: {itemCount}')

        # Достаем адреса айтемов #
        itemURLs = []
        for i in range(itemCount):
            # ищем линки с аттрибутом
            items = browser.find_elements_by_xpath(linkXPath)
            itemPath = urlparse(str(items[i].get_attribute('href'))).path
            itemPath = itemPath.split('/')
            itemPath = itemPath[1]

            # Если найдено совпадение,
            if (itemPath == currPath):
                # ..то добавляем линк в массив
                itemURLs.append(items[i].get_attribute('href'))
            else:
                # Иначе, прерываем итерации, считаем что пошли уже айтемы с доставкой из другого города
                break
    finally:
        # Смотрим что лежит в массиве #
        # for i in range(len(itemURLs)):
        #    print(itemURLs[i])

        print(f'\tЗаписано: {len(itemURLs)}')
        print('\tЗаписали адреса айтемов в массив\n')

    print('END ### getItemURLs ###')
    return itemURLs


def getItemsInfo(itemURLs):
    print('BEGIN ### getItemsInfo ###')

    iHeadXPath = '//span[@class="title-info-title-text"]'
    iAddressXPath = '//span[@class="item-address__string"]'
    iPriceXPath = '//*[@id="price-value"]/span/span[1]'

    resultArray = []
    for i in range(len(itemURLs)):
        # переходим к айтему
        browser.get(itemURLs[i])

        # Устанавливаем текущий юрл
        browser.get(browser.current_url)

        # Собираем словарь
        resultDict = {}
        try:
            WebDriverWait(browser, 10)
            # Получаем инфо
            iHead = browser.find_element_by_xpath(iHeadXPath).text
            iAddress = browser.find_element_by_xpath(iAddressXPath).text
            iPrice = browser.find_element_by_xpath(iPriceXPath).get_attribute('content')
            iURL = itemURLs[i]
            iPhone = getPhone()
        finally:
            print(f'\tДанные получены для: {itemURLs[i]}')

        # Записываем данные айтема в словарь
        resultDict = {'Название': iHead, 'Адрес': iAddress, 'Цена': iPrice, 'Телефон': iPhone, 'Ссылка': iURL}
        # Добавляем запись в общий массив
        resultArray.append(resultDict)
        print('\t..и записаны в словарь')

    # Возвращаем массив, содержащий словари
    print('\tВсе данные записаны в словарь\n')
    print('END ### getItemsInfo ###')
    return resultArray


def writeToFile(result):
    print('BEGIN ### writeToFile ###')
    # Создаем файл для записи
    try:
        with open(workDir + resultFile, "w", newline="") as file:
            # Определяемзаголовки
            columns = ["Название", "Адрес", "Цена", "Телефон", "Ссылка"]
            writer = csv.DictWriter(file, delimiter=';', fieldnames=columns)
            writer.writeheader()
            # Пишем данные в файл
            writer.writerows(result)
    finally:
        print(f'\tДанные записаны в {workDir}{resultFile}')

    print('END ### writeToFile ###')


def getPhone():
    print('\tBEGIN ### getPhone ###')
    phoneXPath = '//div/a[@data-side="card"]'
    imgXPath = '//div[@class="item-phone-big-number js-item-phone-big-number"]/img'

    try:
        WebDriverWait(browser, 10)
        browser.find_element_by_xpath(phoneXPath).click()
    finally:
        print('\t\tОткрыли попап с телефоном')

    try:
        WebDriverWait(browser, 10)
        time.sleep(1)
        img = browser.find_element_by_xpath(imgXPath).get_attribute('src')
        img = img.split(',')
        img = str(img[1])
    finally:
        print('\t\tПолучили картинку')

    try:
        f = open(workDir + tempImgFile, 'wb')
        f.write(base64.b64decode(img))
        f.close()
    finally:
        print('\t\tДекодировали и сохранили картинку')

    try:
        img = Image.open(workDir + tempImgFile)
        phoneNum = pytesseract.image_to_string(img, lang="eng", config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789')
    finally:
        print('\t\tПолучили телефон с картинки')

    print('\tEND ### getPhone ###')
    return phoneNum


''' ДЕЛАЕМ МАГИЮ %) '''
fillFilters()
itemURLs = getItemURLs()
resultArray = getItemsInfo(itemURLs)
writeToFile(resultArray)

browser.close()
exit()
