AvitoSearch
Version 1.0

Данный скрипт ищет информацию по заполненным фильтрам.
В результате выводит в results.csv файл следующие данные:
	- Заголовок объявления
	- Адрес
	- Цена
	- Телефон продавца
	- Ссылка на объявление
	
Что необходимо для запуска:
	- ПО
		chrome browser							        # Браузер
		python 3.5+								# Яз. прог
		selenium								# ПО для связи python-driver
		chromedriver for selenium				                # ПО для связи chrome-driver
		pytesseract								# ПО для распознавания текста на картинке
	- Настройки
		driverPath								# Расположение chromedriver.exe
		pytesseract.pytesseract.tesseract_cmd	# Расположение tesseract.exe
		startPage								# Стартовая страница avito
		workDir									# Папка для вывода результата и хранения временных файлов
		resultFile								# Название файла с результатами
		tempImgFile								# Название временного файла картинки

Входные данные:
		city									# Название города для поиска
		category								# В какой категории производить поиск
		word									# Слово для поиска
		price									# Минимальная цена за товар


Функции:
	def fillFilters()							# Заполняет фильтры для поиска
	def getItemURLs()							# Получает массив URLов для найденных товаров
	def getItemsInfo(itemURLs)					# Собирает информацию для отчета из входящих URLов
	def writeToFile(result)						# Записыват в файл массив резултатов из словаря созданного getItemsInfo
	def getPhone()								# Получает телефон декодируя картинку и распознает с нее текстовые данные

