# -*- coding: utf-8 -*-

import aiogram
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from models import db_session
from models.users import User

import re
import datetime
import string
import time
import json
import requests
import speech_recognition as speech_recog
import subprocess
import os

db_session.global_init('database.db')

bot_token = '<token>'

#bot = telebot.TeleBot(bot_token)
bot = Bot(token=bot_token)
dp = Dispatcher(bot)

GROUP_ID = -329119522  # ID моей группы

# считаем для статистики
allwords = 1022
matwords = 92
filescan = 28
lastword = 'codeendmats'
usersid = '1218845111'
chatsid = ''
users = 14

def check_mats(message, text):
	global matwords, allwords
	with open("dist/mats.txt", encoding='utf-8') as openfile:
		mat = False
		part = ''
		word = ''
		text = text.lower()
		ntext = text.translate(str.maketrans('', '', string.punctuation)).lower()
		allwords += 1
		for line in openfile:
			for part in line.split():
				part = part.rstrip(',')
				if part == "codeendmats":
					if mat == True:
						if message.from_user.username != None:
							return '🤐 @' + message.from_user.username + '\n' + text
						else:
							return '🤐 ' + message.from_user.first_name + '\n' + text
					else:
						return False
					break
				for word in ntext.split():
					if word == part:
						text = text.replace(part, '▓' * len(word), 1000)
						mat = True
						matwords += 1

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
	global users
	keyboard = types.InlineKeyboardMarkup()
	url_button = types.InlineKeyboardButton(
		text="🔗 Создатель", url="https://t.me/vsecoder")
	keyboard.add(url_button)
	#
	iduser = message.from_user.id
	session = db_session.create_session()
	#
	user_all = session.query(User).all()
	T = True
	for all in user_all:
		if all.id == iduser:
			T = False

	if T:
		if message.from_user.username:
			session = db_session.create_session()
			name = message.from_user.first_name
			url = message.from_user.username
			iduser = message.from_user.id
			user = User(
				id=iduser,
				name=name,
				username='@'+url,
				carma=0
			)
			users += 1
			session.add(user)
			session.commit()
		else:
			session = db_session.create_session()
			name = message.from_user.first_name
			url = message.from_user.username
			iduser = message.from_user.id
			user = User(
				id=iduser,
				name=name,
				username='@...',
				carma=0
			)
			users += 1
			session.add(user)
			session.commit()

	await bot.send_message(message.chat.id, '🙋Здравствуйте, я бот, который будет модерировать чат \n/help 👨‍💻выдаст вам инструкцию \n/info 🕵️‍♂️расскажет про меня подробнее', reply_markup=keyboard)

@dp.message_handler(commands=['help'])
async def send_help(message: types.Message):
	keyboard = types.InlineKeyboardMarkup()
	url_button = types.InlineKeyboardButton(
		text="🔗 Добавить себе", url="https://t.me/modermodBot?startgroup=0")
	keyboard.add(url_button)
	await bot.send_message(message.chat.id, '📝Добавить меня можно очень быстро: \n1. Нажми на кнопку под сообщением \n2. Выбери чат \n3. Выдай мне право на удаление сообщений', reply_markup=keyboard)

@dp.message_handler(commands=['info', 'me'])
async def info(message: types.Message):
	await bot.send_chat_action(message.chat.id, 'typing')
	await bot.send_message(message.chat.id, 'Ну раз спросил, то в мои возможности входят несколько функций, '
                        'я обрабатываю сообщения на маты, при необходимости ставлю цензуру: \n'
                        '<b>мат => ▓▓▓</b>\n'
                        'Из этого я веду статистик(/stat для её просмотра), а также перевожу голосовые сообщения в текст. ', parse_mode='html')

@dp.message_handler(commands=['newmat'])
async def neword(message: types.Message):
	if message.from_user.id == 1218845111:
		mt = message.text.replace('/newmat ', '')
		f1 = open('dist/mats.txt', 'r', encoding='utf-8')
		old = f1.read().replace(', codeendmats', '')
		f = open('dist/mats.txt', 'w', encoding='utf-8')
		f.write(old + ', ' + mt + ', codeendmats')
		await bot.send_message(message.chat.id, '📝Новый мат: ' + str(mt))
	else:
		mt = message.text.replace('/newmat ', '')
		await bot.send_message(message.chat.id, '👨‍🔧Вы предложили добавить: ' + str(mt))
		await bot.send_message(1218845111, '👨‍🔧Вам предложили добавить: ' + str(mt))

@dp.message_handler(commands=['stat'])
async def statistic(message: types.Message):
	await bot.send_chat_action(message.chat.id, 'typing')
	await bot.send_message(
		message.chat.id, '<b>📈Всего слов обработанно:</b> <code>' + str(allwords) +
		'</code>\n<b>📉Слов с матами:</b> <code>' + str(matwords) +
		'</code>\n<b>🗄Файлов отсканировано:</b> <code>' + str(filescan) + '</code>\n' +
		'<b>👨‍💼Пользователей: </b><code>' + str(users) + '</code>', parse_mode='html')

@dp.message_handler(commands=['mute'])
async def mute(message: types.Message):
	try:
		info = await bot.get_chat_member(message.chat.id, message.from_user.id)
		if 'administrator' == str(info.status) or 'creator' == str(info.status):
			if message.reply_to_message.from_user.id != None:
				await bot.restrict_chat_member(
					message.chat.id, message.reply_to_message.from_user.id, until_date=time.time()+600)
				await bot.send_message(message.chat.id, '🤐Мут на 10 минут осуществлён!',
    	                            reply_to_message_id=message.message_id)
		else:
			await bot.send_message(message.chat.id, '🤕Хаха, права админа получи и возращайся',
    	                            reply_to_message_id=message.message_id)
	except:
		await bot.send_message(message.chat.id, '🤕Я только в чате могу это...')

@dp.message_handler(commands=['r', 'report'])
async def report(message: types.Message):
	try:
		if message.text == '/report' or message.text == '/r' or not message.reply_to_message:
			await bot.send_message(message.chat.id, '📖Введите причину репорта отвечая на сообщение с нарушением в формате /report spam|flud|18+ или другое')
		else:
			members = await message.chat.get_member(message.reply_to_message.from_user.id)
			info = await bot.get_chat_member(message.chat.id, message.from_user.id)
			report = message.text.replace('/r ', '')
			report = report.replace('/report ', '')
			admins = await bot.get_chat_administrators('@' + message.chat.username)
			send = 0
			for admin in admins:
				if admin.user.username != 'modermodBot':
					try:
						await bot.send_message(admin.user.id, f'📬 Репорт по причине ' + str(report) + f'\nhttps://t.me/{message.chat.username}/{message.reply_to_message.message_id}')
					except:
						pass
					send += 1

			if send == 0:
				await bot.send_message(message.chat.id, '👮Админы не оповещены, для отправки им репортов надо чтобы они запустили меня в лс!')
			else:
				await bot.send_message(message.chat.id, '👮Админы оповещены')
	except:
		pass

@dp.message_handler(commands=['rules'])
async def rules(message: types.Message):
	await bot.send_message(
		message.chat.id, 'Правила чата: \n'
		'<b> · </b>Не оскорбляйте других участников, не создавайте конфликтных ситуаций. Давайте формировать комьюнити, а не ругаться.'
		'\n<b> · </b>Не используйте нецензурную лексику — сразу удалится ботом.'
		'\n<b> · </b>Нельзя рекламировать услуги, товары, складчины, давать ссылки на конкурентные ресурсы.'
		'\n<b> · </b>Если вы хотите написать в чат, старайтесь уместить свою мысль в одно сообщение — никто не любит флуд.'
		'\n<b> · </b>Голосовые сообщения теперь разрешены, я их переведу в текст.', parse_mode='html')

@dp.message_handler(content_types=["new_chat_members"])
async def newuser(message: types.Message):
	try:
		await bot.send_chat_action(message.chat.id, 'typing')
		if message.new_chat_members[0].username == 'modermodBot':
			await message.reply('😳 О, я в чате! Всем привет, я новый модер этого чата!')
		else:
			await message.reply(
				'🙋Приветствую вас в чате, я <b>бот</b>, и вот <u>правила</u> чата: \n'
				'<b> · </b>Не оскорбляйте других участников, не создавайте конфликтных ситуаций. Давайте формировать комьюнити, а не ругаться.'
				'\n<b> · </b>Не используйте нецензурную лексику — сразу удалится ботом.'
				'\n<b> · </b>Нельзя рекламировать услуги, товары, складчины, давать ссылки на конкурентные ресурсы.'
				'\n<b> · </b>Если вы хотите написать в чат, старайтесь уместить свою мысль в одно сообщение — никто не любит флуд.'
				'\n<b> · </b>Голосовые сообщения теперь разрешены, я их переведу в текст.', parse_mode='html')
	except BaseException as e:
		await bot.send_message(
			message.chat.id, '🙋Приветствую вас в чате '
			', я <b>бот</b>, и вот <u>правила</u> чата: \n'
			'<b> · </b>Не оскорбляйте других участников, не создавайте конфликтных ситуаций. Давайте формировать комьюнити, а не ругаться.'
			'\n<b> · </b>Не используйте нецензурную лексику — сразу удалится ботом.'
			'\n<b> · </b>Нельзя рекламировать услуги, товары, складчины, давать ссылки на конкурентные ресурсы.'
			'\n<b> · </b>Если вы хотите написать в чат, старайтесь уместить свою мысль в одно сообщение — никто не любит флуд.'
			'\n<b> · </b>Голосовые сообщения теперь разрешены, я их переведу в текст.', parse_mode='html')

@dp.message_handler(content_types=["left_chat_member"])
async def leftuser(message: types.Message):
	await bot.send_chat_action(message.chat.id, 'typing')
	await bot.send_message(
		message.chat.id, '😞 Эх... минус один пользователь чата...', parse_mode='html')

@dp.message_handler(content_types=['photo'])
async def photo_check(message: types.Message):
	global allwords, matwords, lastword
	try:
		if message.caption != None:
			censor = check_mats(message, message.caption)
			if censor:
				await bot.delete_message(message.chat.id, message.message_id)
				photoid = message.photo[-1].file_id
				await bot.send_photo(message.chat.id, photoid, caption=str(censor))
	except BaseException as e:
		await bot.send_message(1218845111, 'В системе ошибка...\n<code>' + str(e) + '</code>', parse_mode='html')
		await bot.send_message(message.chat.id, 'Упс, ошибка...')

@dp.message_handler(content_types=["text"])
async def check(message: types.Message):
	global allwords, matwords, lastword, users
	try:
		if message.text == '@modermodBot':
			sti = open('dist/1.tgs', 'rb')
			await bot.send_sticker(message.chat.id, sti)
			await bot.send_message(message.chat.id, 'Я!')
		elif message.text == "+":
			if message.from_user.id == message.reply_to_message.from_user.id:
				await message.reply("🤨 Нельзя изменять карму самому себе.")
			else:
				mame = ''
				session = db_session.create_session()
				user_all = session.query(User).all()
				for user in user_all:
					if user.id == message.reply_to_message.from_user.id:
						user.carma += 1
						name = user.name

				session.commit()
				await message.reply('✏️Вы повысили карму ' + str(name))
		elif message.text == "-":
			if message.from_user.id == message.reply_to_message.from_user.id:
				await message.reply("🤨 Нельзя изменять карму самому себе.")
			else:
				mame = ''
				session = db_session.create_session()
				user_all = session.query(User).all()
				for user in user_all:
					if user.id == message.reply_to_message.from_user.id:
						user.carma -= 1
						name = user.name

				session.commit()
				await message.reply('✏️Вы понизили карму ' + str(name))
		elif message.text == 'Карма':
			carma = 0
			session = db_session.create_session()
			user_all = session.query(User).all()
			for user in user_all:
				if user.id == message.from_user.id:
					carma = user.carma

			await message.reply('✏️Ваша крама: ' + str(carma))
			session.commit()
		else:
			censor = check_mats(message, message.text)
			if censor:
				await bot.delete_message(message.chat.id, message.message_id)
				await bot.send_message(message.chat.id, str(censor))

		#
		iduser = message.from_user.id
		session = db_session.create_session()
		#
		user_all = session.query(User).all()
		T = True
		for all in user_all:
			if all.id == iduser:
				T = False

		if T:
			if message.from_user.username:
				session = db_session.create_session()
				name = message.from_user.first_name
				url = message.from_user.username
				iduser = message.from_user.id
				user = User(
                    id=iduser,
                    name=name,
                    username='@'+url,
                    carma=0
                )
				users += 1
				session.add(user)
				session.commit()
			else:
				session = db_session.create_session()
				name = message.from_user.first_name
				url = message.from_user.username
				iduser = message.from_user.id
				user = User(
                     id=iduser,
                     name=name,
                     username='@...',
                     carma=0
                )
				users += 1
				session.add(user)
				session.commit()
	except BaseException as e:
		await bot.send_message(1218845111, 'В системе ошибка...\n<code>' + str(e) + '</code>', parse_mode='html')
		await bot.send_message(message.chat.id, 'Упс, ошибка...')

@dp.message_handler(content_types=['document'])
async def file_handler(message: types.Message):
	global filescan, allwords, matwords, lastword
	try:
		if message.caption != None:
			censor = check_mats(message, message.caption)
			if censor:
				await bot.delete_message(message.chat.id, message.message_id)
				photoid = message.document.file_id
				await bot.send_document(message.chat.id, photoid, caption=str(censor))
		url_file_scan = 'https://www.virustotal.com/vtapi/v2/file/scan'
		params = dict(
			apikey='<token>')
		file_upload_id = await bot.get_file(message.document.file_id)
		url_upload_file = "https://api.telegram.org/file/bot{}/{}".format(
			bot_token, file_upload_id.file_path)
		recvfile = requests.get(url_upload_file)
		files = dict(file=(recvfile.content))
		response_file_scan = requests.post(url_file_scan, files=files, params=params)
		if response_file_scan.json()['response_code'] == 1:
			await bot.send_message(message.chat.id, "📎 <a href='" + response_file_scan.json()['permalink'] + "'>Информация</a> о отправленом файле", parse_mode='html')
		else:
			await bot.send_message(message.chat.id, response_file_scan.json()['verbose_msg'])
		filescan += 1
	except BaseException as e:
		await bot.send_message(1218845111, 'В системе ошибка...\n<code>' + str(e) + '</code>', parse_mode='html')
		await bot.send_message(message.chat.id, '🧩Файл слишком большой, не получается проверить на вирусы')

@dp.message_handler(content_types=['voice'])
async def repeat_all_message(message):
	try:
		os.remove("dist/voice.wav")
	except BaseException as e:
		pass

	await bot.send_chat_action(message.chat.id, 'typing')

	file_info = await bot.get_file(message.voice.file_id)
	file = requests.get(
		'https://api.telegram.org/file/bot{0}/{1}'.format(bot_token, file_info.file_path))

	#await bot.send_message(message.chat.id, '📝Запись')
	with open('dist/voice.ogg', 'wb') as f:
		f.write(file.content)

	src_filename = 'dist/voice.ogg'
	dest_filename = 'dist/voice.wav'

	#await bot.send_message(message.chat.id, '📄Конвертация')

	process = subprocess.run(['ffmpeg', '-i', src_filename, dest_filename])
	process.returncode = 1

	# speech_recog
	#await bot.send_message(message.chat.id, '📃Обработка')
	sample_audio = speech_recog.AudioFile('dist/voice.wav')
	recog = speech_recog.Recognizer()
	with sample_audio as audio_file:
		audio_content = recog.record(audio_file)
	data = recog.recognize_google(audio_content, language='ru-RU')

	text = data

	if message.from_user.username != None:
		await message.reply('🗣 @' + message.from_user.username + '\n' + str(text))
	else:
		await message.reply('🗣 ' + message.from_user.first_name + '\n' + str(text))
	try:
		os.remove("dist/voice.wav")
	except BaseException as e:
		print(e)
	finally:
		pass
#
if __name__ == "__main__":
	executor.start_polling(dp)
