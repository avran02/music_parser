from main import Parser

def continue_(genre, parser):
	parser.get_pages_list(genre)
	try:
		songs_num = int(input('-Введите количество песен для скачивания(не больше 50):\n'))
		page_num = int(input(f'-С какой страницы? \n-Всего доступно {parser.num_pages} страниц\n-Для загрузки со случайной страницы введите 0\n'))
	except:
		print('-Вы ввели что-то не то, перезапустите скрипт')
		exit()
	if page_num > parser.num_pages:
		print('-Столько страниц там нет, перезапустите скрипт')
		exit()
	elif page_num == 0:
		parser.parce_random(songs_num)
	else:
		parser.parce_any(songs_num, page_num)


if __name__ == '__main__':
	parser = Parser()
	genres = parser.genres
	for genre in genres:
		print(f'@{genre}')
	g = input('-Введите жанр, который хотите скачать\n-Ввести нужно символ в символ, без собаки!\n')
	if g in genres:
		continue_(genres[g], parser)
	else:
		print('-Такого жанра нет в списке, перезапустите скрипт')


