from aiogram import Bot, Dispatcher, executor, types

TOKEN = '7530326571:AAFOxgJC2ladLxG7ldYPYCMRHety23OAVHE'

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

@dp.message_handler(commands=['start', 'help'])
async def start_command(message: types.Message):
    await message.reply("Привет! Я бот, который ищет изображения по вашим запросам.\nЧтобы начать, пришлите мне любое слово или фразу.")

@dp.message_handler()
async def image_search(message: types.Message):
    keyword = message.text
    if keyword != None:
        try:
            # Запрос к API поиска изображений (например, Yandex.Images)
            response = requests.get(f"https://yandex.ru/images/search?text={keyword}")
            
            # Получение ссылки на первое изображение из результатов поиска
            link = BeautifulSoup(response.content, 'html.parser').find('img', class_='serp-item__link').get('src')
            await message.reply(f"<a href=\"{link}\">Картинка</a>", parse_mode="HTML")
        except Exception as e:
            await message.reply(f"Ошибка: {e}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
