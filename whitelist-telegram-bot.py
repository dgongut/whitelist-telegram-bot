import re
import os
import telebot
from config import *

# Comprobación inicial de variables
if "abc" == TELEGRAM_TOKEN:
	print("Se necesita configurar el token del bot con la variable TELEGRAM_TOKEN")
	sys.exit(1)

# Se crean los ficheros de usuarios baneados y de lista blanca
if not os.path.exists(FILE_BANNED):
	# Si no existe, crea el archivo vacío
	with open(FILE_BANNED, 'w') as file:
		pass

if not os.path.exists(FILE_WHITELIST):
	# Si no existe, crea el archivo vacío
	with open(FILE_WHITELIST, 'w') as file:
		pass

# Instanciamos el bot
bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(content_types=["new_chat_members"])
def entry_control(event):
	chatId = event.chat.id
	if not is_configured():
		bot.send_message(chatId, f'<b><i>===ERROR===</i></b>\n\nSe necesita configurar la variable de entorno TELEGRAM_GROUP. Si este mensaje está apareciendo en el grupo que deseas gestionar añade <code>TELEGRAM_GROUP={chatId}</code> a las variables de entorno (toca para copiarlo).\n\nEl bot <b>no funcionará</b> mientras este parametro no esté configurado.', parse_mode="HTML")
		return

	for newMember in event.new_chat_members:
		username = newMember.username
		userId = newMember.id
		wasBannedBefore = is_in_bannedlist(username)
		if not is_admin(userId) and (wasBannedBefore or not is_in_whitelist(username)):
			ban(username, userId)
			if not wasBannedBefore:
				bot.send_message(chatId, f'<b><i>===Intruso detectado===</i></b>\nEl usuario @{username} <b>ha sido fulminado</b>.', parse_mode="HTML")
			else:
				bot.send_message(chatId, f'<b><i>===Intruso detectado===</i></b>\nEl usuario @{username} sigue tratando de unirse, no va a poder.', parse_mode="HTML")

@bot.message_handler(commands=["stats", "addwhitelist", "removewhitelist"])
def command_controller(message):
	chatId = message.chat.id
	senderId = message.from_user.id

	if not is_configured():
		bot.delete_message(chatId, message.message_id)
		bot.send_message(chatId, f'<b><i>===ERROR===</i></b>\n\nSe necesita configurar la variable de entorno TELEGRAM_GROUP. Si este mensaje está apareciendo en el grupo que deseas gestionar añade <code>TELEGRAM_GROUP={chatId}</code> a las variables de entorno (toca para copiarlo).\n\nEl bot <b>no funcionará</b> mientras este parametro no esté configurado.', parse_mode="HTML")
		return

	if not is_admin(senderId):
		bot.delete_message(chatId, message.message_id)
		return

	parts = message.text.split()
	command = parts[0]

	users = []
	if len(parts) > 1:
		usersRaw = parts[1].split(',')
		for user in usersRaw:
			user = user.replace(" ", "")
			if user != "":
				users.append(user.replace("@", ""))
	
	if command in ('/addwhitelist'):
		if not users:
			this_command_needs_users(chatId)
		for userToAdd in users:
			if is_in_whitelist(userToAdd):
				bot.send_message(chatId, f'El usuario @{userToAdd} <b>ya se encontraba en la lista blanca</b>.', parse_mode="HTML")
				continue
			elif is_in_bannedlist(userToAdd):
				unban(userToAdd, chatId)
				continue
			add_to_whitelist(userToAdd)
			bot.send_message(chatId, f'El usuario @{userToAdd} <b>ha sido <u>añadido</u> a la lista blanca</b>.', parse_mode="HTML")
	if command in ('/removewhitelist'):
		if not users:
			this_command_needs_users(chatId)
		for userToRemove in users:
			if not is_in_whitelist(userToRemove):
				bot.send_message(chatId, f'El usuario @{userToRemove} <b>no se encontraba en la lista blanca</b>.', parse_mode="HTML")
				continue
			remove_from_whitelist(userToRemove)
			bot.send_message(chatId, f'El usuario @{userToRemove} <b>ha sido <u>eliminado</u> de la lista blanca</b>.', parse_mode="HTML")
	elif command in ('/stats'):
		stats(chatId)

@bot.message_handler(content_types=["text"])
def text_controller(message):
	chatId = message.chat.id
	userId = message.from_user.id
	username = message.from_user.username
	wasBannedBefore = is_in_bannedlist(username)
	if not is_admin(userId) and (wasBannedBefore or not is_in_whitelist(username)):
		ban(username, userId)
		if not wasBannedBefore:
			bot.send_message(chatId, f'<b><i>===Intruso detectado===</i></b>\nEl usuario @{username} <b>ha sido fulminado</b>.', parse_mode="HTML")
		else:
			bot.send_message(chatId, f'<b><i>===Intruso detectado===</i></b>\nEl usuario @{username} sigue tratando de unirse, no va a poder.', parse_mode="HTML")

def this_command_needs_users(chatId):
	bot.send_message(chatId, f'Para usar este comando es necesario especificar uno o varios usuarios separados por comas (sin espacios).', parse_mode="HTML")

def is_admin(userId):
	infoUser = bot.get_chat_member(TELEGRAM_GROUP, userId)
	if infoUser.status in ["creator", "administrator"]:
		return True
	return False

def ban(user, userId):
	bot.ban_chat_member(TELEGRAM_GROUP, userId)
	if not is_in_bannedlist(user):
		with open(FILE_BANNED, "a+", encoding="utf-8") as f:
			f.write(f"{user}|{userId}\n")

def unban(user, chatId):
	usersBanned = []
	userFound = False
	with open(FILE_BANNED, 'r', encoding="utf-8") as f:
		lines = f.readlines()
		for line in lines:
			if not line.split(sep='|')[0] == user.strip().lower():
				usersBanned.append(line)
			else:
				userFound = True
				try:
					bot.unban_chat_member(TELEGRAM_GROUP, line.split(sep='|')[1], only_if_banned=True)
				except:
					#En grupos pequeños esto no es necesario y lanza una excepcion
					pass

	if not userFound:
		bot.send_message(chatId, f'El usuario @{user} <b>no se encontraba baneado</b>.', parse_mode="HTML")
		return

	# Escribir los usuarios baneados
	with open(FILE_BANNED, 'w') as f:
		f.writelines(usersBanned)

	add_to_whitelist(user)

	bot.send_message(chatId, f'El usuario @{user} <b>ha sido <u>desbaneado</u></b> (y añadido a la lista blanca).', parse_mode="HTML")

def stats(chatId):
	numBanned = 0
	numWhiteList = 0
	with open(FILE_BANNED, 'r', encoding="utf-8") as f:
		lines = f.readlines()
		numBanned = len(lines)
	with open(FILE_WHITELIST, 'r', encoding="utf-8") as f:
		lines = f.readlines()
		numWhiteList = len(lines)
	bot.send_message(chatId, f'<b><i>===Estadísticas===</i></b>\n😇 Usuarios en lista: {numWhiteList}\n🥷 Intrusos detectados: {numBanned}', parse_mode="HTML")
	if str(chatId) != str(TELEGRAM_GROUP):
		MAX_SIZE = 100
		whitelist = get_whitelist()
		if len(whitelist) > MAX_SIZE:
			parts = [whitelist[i:i+MAX_SIZE] for i in range(0, len(whitelist), MAX_SIZE)]
			for i, part in enumerate(parts, start=1):
				bot.send_message(chatId, f'<b><i>===Usuarios en lista===</i></b>\n<i>(Parte {i})</i>\n{part}', parse_mode="HTML")
		else:
			bot.send_message(chatId, f'<b><i>===Usuarios en lista===</i></b>\n{get_whitelist()}', parse_mode="HTML")

		bannedList = get_bannedlist()
		if len(bannedList) > MAX_SIZE:
			parts = [bannedList[i:i+MAX_SIZE] for i in range(0, len(bannedList), MAX_SIZE)]
			for i, part in enumerate(parts, start=1):
				bot.send_message(chatId, f'<b><i>===Usuarios baneados===</i></b>\n<i>Parte {i}</i>\n{part}', parse_mode="HTML")
		else:
			bot.send_message(chatId, f'<b><i>===Usuarios baneados===</i></b>\n{get_bannedlist()}', parse_mode="HTML")

def add_to_whitelist(user):
	with open(FILE_WHITELIST, "a+", encoding="utf-8") as f:
		f.write(f"{user.strip().lower()}\n")

def remove_from_whitelist(user):
	usersWhiteList = []
	with open(FILE_WHITELIST, 'r', encoding="utf-8") as f:
		lines = f.readlines()
		for line in lines:
			if not line.strip().lower() == user:
				usersWhiteList.append(line)
	
	# Escribir los usuarios en lista
	with open(FILE_WHITELIST, 'w') as f:
		f.writelines(usersWhiteList)

def is_in_whitelist(user):
	with open(FILE_WHITELIST, 'r', encoding="utf-8") as f:
		lines = f.readlines()
		for line in lines:
			if line.strip().lower() == user:
				return True
	return False

def is_in_bannedlist(user):
	with open(FILE_BANNED, 'r', encoding="utf-8") as f:
		lines = f.readlines()
		for line in lines:
			if line.split(sep='|')[0] == user.strip().lower():
				return True
	return False

def get_bannedlist():
	lines = []
	with open(FILE_BANNED, 'r', encoding="utf-8") as f:
		allLines = f.readlines()
		for line in allLines:
			lines.append(line.split(sep='|')[0].replace('\n', ''))
	return lines

def get_whitelist():
	lines = []
	with open(FILE_WHITELIST, 'r', encoding="utf-8") as f:
		allLines = f.readlines()
		for line in allLines:
			lines.append(line.replace('\n', ''))
	return lines

def is_configured():
	return "abc" != TELEGRAM_GROUP

if __name__ == '__main__':
	bot.set_my_commands([ # Comandos a mostrar en el menú de Telegram
        telebot.types.BotCommand("/stats", "Muestra estadísticas"),
        telebot.types.BotCommand("/addwhitelist", "Añade uno o más (separados por comas) usuarios a la lista blanca. Desbanea si estaba baneado."),
        telebot.types.BotCommand("/removewhitelist", "Elimina uno o más (separados por comas) usuarios a la lista blanca")
        ])
	bot.infinity_polling(timeout=60)