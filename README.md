# whitelist-telegram-bot
Este codigo controlara un bot de telegram y gestionara la expulsion de usuarios que se unan a un grupo gracias a una lista blanca

# Instrucciones para Whitelist Telegram Bot
Con guración Inicial
- TELEGRAM_GROUP: De ne el identi cador del grupo que deseas gestionar. Si no conoces este ID, agrega el bot al grupo y envíale cualquier comando; el bot te proporcionará el ID que debes usar.
- TELEGRAM_TOKEN: Proporciona el token de acceso de tu bot de Telegram.

# Volúmenes
Es crucial mapear la ruta: /whitelistbot/path/to/configure:/app/files para preservar
la lista blanca entre reinicios del bot.

# Archivos Necesarios
Se crearán los siguienes cheros en la ruta mapeada:
- banned.txt: Lista de usuarios baneados (sin @).
- whitelist.txt: Lista de usuarios permitidos (sin @).

# Comandos
/addwhitelist
Añade usuarios a la whitelist y los desbanea si estaban en la lista de baneados.
Ejemplo:
/addwhitelist user1,user2,user3
/addwhitelist @user1,@user2,@user3

/removewhitelist
Elimina usuarios de la whitelist. Estos usuarios no podrán unirse al grupo y serán expulsados si ya
están dentro. Ejemplo:
/removewhitelist user1,user2,user3
/removewhitelist @user1,@user2,@user3

/stats
Muestra estadísticas, incluyendo la cantidad de usuarios en la lista blanca y cuántos intrusos han
sido detectados y baneados.
Si se ejecuta en privado (fuera del grupo), proporciona un listado completo de usuarios en la lista
blanca y los baneados.

# Notas Adicionales
Solo los administradores pueden ejecutar estos comandos para mantener el control sobre la lista
blanca y la seguridad del grupo. Si cualquier usuario los ejecuta, su mensaje será eliminado para
evitar el ood.
Los comandos pueden ser ejecutados tanto dentro del grupo como en una conversación privada
con él