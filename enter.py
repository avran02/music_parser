from main import Parser


if __name__ == '__main__':

	executor = Parser()
	try:
		songs_num = int(input('\t-Введите количество песен для скачивания(не больше 50):\n'))
		page_num = int(input(f'\t-С какой страницы? \n\t-Всего доступно {executor.num_pages} страниц\n\t-Для загрузки со случайной страницы введите 0\n'))
	except:
		print('\t-Вы ввели что-то не то, перезапустите скрипт')
		exit
	if page_num > executor.num_pages:
		print('\t-Столько страниц там нет, перезапустите скрипт')
		exit
	elif page_num == 0:
		executor.parce_random(songs_num)
	else:
		executor.parce_any(songs_num, page_num)

