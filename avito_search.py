from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait  # available since 2.4.0
import csv

# Входные данные
city = 'Новосибирск'
category = 'Коллекционирование'
word = 'lego'
price = 5000
# Имя файла для репорта
reportFileName = 'test.csv'

# Решил вести лог, через print
browser = webdriver.Chrome('E:/fs/chromedriver.exe')
browser.get('https://avito.ru/novosibirsk')


def fillFilters():
    print('### fillFilters ###')

    agreeXPath = '//button[@data-marker="location/tooltip-agree"]'
    categoryXPath = f'//select[@name="category_id"]/option[text()="{category}"]'
    nameXPath = '//input[@id="search" and @data-marker="search-form/suggest"]'
    priceXPath = '//input[@data-marker="price/from"]'
    submitXPath = '//button[@data-marker="search-filters/submit-button"]'

    try:
        WebDriverWait(browser, 10)
        # ищем кнопку соглашения "Это ваш город?"
        agreeTooltip = browser.find_element_by_xpath(agreeXPath)
        # Если кнопка отображается - жмем
        if (agreeTooltip.is_displayed()):
            agreeTooltip.click()
        # Выбираем категорию
        browser.find_element_by_xpath(categoryXPath).click()
        print('Категория выбрана')

        browser.get(browser.current_url)

        try:
            WebDriverWait(browser, 10)
            # Вводим поисковое слово
            browser.find_element_by_xpath(nameXPath).send_keys(word)
            print('Слово введено')
            # Вводим цену ОТ 5000
            browser.find_element_by_xpath(priceXPath).send_keys(price)
            print('Цена введена')
        finally:
            print()

        # Применяем фильтр
        browser.find_element_by_xpath(submitXPath).click()
    finally:
        print('Фильтры заполнены и применены\n')
    # Отправляем форму


def getItemURLs():
    print('### getItemURLs ###')
    itemCountXPath = '//span[@class="page-title-count"]'
    linkXPath = '//a[@itemprop="url"]'

    browser.get(browser.current_url)

    try:
        WebDriverWait(browser, 10)
        # Получаем кол-во найденных результатов
        itemCount = browser.find_element_by_xpath(itemCountXPath).text
        itemCount = int(itemCount)
        print(f'Найдено: {itemCount}')

        # Достаем адреса айтемов #
        itemURLs = []
        for i in range(itemCount):
            # ищем линки с аттрибутом
            items = browser.find_elements_by_xpath(linkXPath)

            # Финт ушами. Ищем вхождение города в тайтле ссылки
            nsk = f'в {city}е'
            st = items[i].get_attribute('title')
            st = str(st)
            # Если найдено совпадение,
            if (st.find(nsk)):
                # ..то добавляем линк в массив
                itemURLs.append(items[i].get_attribute('href'))
            else:
                # Иначе, прерываем итерации, считаем что пошли уже айтемы с доставкой из другого города
                break

    finally:
        # Смотрим что лежит в массиве #
        # for i in range(len(itemURLs)):
        #    print(itemURLs[i])

        print('Записали адреса айтемов в массив\n')

    return itemURLs


def getItemsInfo(itemURLs):
    print('### getItemsInfo ###')

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
        finally:
            print(f'Данные получены для: {itemURLs[i]}')

        # Записываем данные айтема в словарь
        resultDict = {'Название': iHead, 'Адрес': iAddress, 'Цена': iPrice, 'Ссылка': iURL}
        # Добавляем запись в общий массив
        resultArray.append(resultDict)
        print('..и записаны в словарь')
    # Возвращаем массив, содержащий словари
    print('Все данные записаны в словарь\n')
    return resultArray


def writeToFile(result):
    print('### writeToFile ###')

    # Создаем файл для записи
    try:
        with open(reportFileName, "w", newline="") as file:
            # Определяемзаголовки
            columns = ["Название", "Адрес", "Цена", "Ссылка"]
            writer = csv.DictWriter(file, delimiter=';', fieldnames=columns)
            writer.writeheader()
            # Пишем данные в файл
            writer.writerows(result)
    finally:
        print(f'Данные записаны в {reportFileName}')


''' ДЕЛАЕМ МАГИЮ %) '''
fillFilters()
itemURLs = getItemURLs()
resultArray = getItemsInfo(itemURLs)
writeToFile(resultArray)
