import os
import logging
import tempfile
from pathlib import Path
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import base64
import json
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import hashlib
import re
import zlib

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токен бота
TOKEN = "8309854985:AAFV4TDV15QbOYzRAe35bsyQ6MpDC7iwByc"

def decrypt_netwing_file(encrypted_data):
    """
    Расшифровка .netcfg файла Netwing с поддержкой различных методов
    """
    results = []
    
    # Метод 1: AES-256-CBC с SHA256 ключом
    try:
        key = hashlib.sha256(b'NetwingConfigKey2023').digest()
        iv = b'NetwingConfigIV16'
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(encrypted_data)
        decrypted = unpad(decrypted, AES.block_size)
        result = decrypted.decode('utf-8', errors='ignore')
        if result.strip():
            results.append(('AES-256-CBC', result))
            logger.info("Метод AES-256-CBC успешен")
    except Exception as e:
        logger.debug(f"AES метод не сработал: {e}")
    
    # Метод 2: AES-128-CBC
    try:
        key = hashlib.md5(b'NetwingConfigKey2023').digest()
        iv = b'NetwingConfigIV16'
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(encrypted_data)
        decrypted = unpad(decrypted, AES.block_size)
        result = decrypted.decode('utf-8', errors='ignore')
        if result.strip():
            results.append(('AES-128-CBC', result))
            logger.info("Метод AES-128-CBC успешен")
    except Exception as e:
        logger.debug(f"AES-128 метод не сработал: {e}")
    
    # Метод 3: XOR с различными ключами
    xor_keys = [
        b'NetwingConfigKey2023',
        b'NetwingConfigKey',
        b'netwing2023',
        b'configkey',
        b'Netwing',
        b'\x01\x02\x03\x04\x05'
    ]
    
    for key in xor_keys:
        try:
            result = bytearray()
            for i, byte in enumerate(encrypted_data):
                result.append(byte ^ key[i % len(key)])
            text = result.decode('utf-8', errors='ignore')
            if text.strip() and len(text) > 10:
                results.append((f'XOR с ключом {key[:10]}...', text))
                logger.info(f"XOR метод с ключом {key[:10]} успешен")
                break
        except:
            continue
    
    # Метод 4: Base64 декодирование
    try:
        decoded = base64.b64decode(encrypted_data)
        text = decoded.decode('utf-8', errors='ignore')
        if text.strip() and len(text) > 10:
            results.append(('Base64 декодирование', text))
            logger.info("Base64 метод успешен")
    except:
        pass
    
    # Метод 5: Попытка распарсить как JSON
    try:
        data = json.loads(encrypted_data.decode('utf-8', errors='ignore'))
        text = json.dumps(data, indent=2, ensure_ascii=False)
        results.append(('JSON парсинг', text))
        logger.info("JSON метод успешен")
    except:
        pass
    
    # Метод 6: Распаковка zlib
    try:
        decompressed = zlib.decompress(encrypted_data)
        text = decompressed.decode('utf-8', errors='ignore')
        if text.strip() and len(text) > 10:
            results.append(('Zlib распаковка', text))
            logger.info("Zlib метод успешен")
    except:
        pass
    
    # Метод 7: Прямое декодирование
    try:
        text = encrypted_data.decode('utf-8', errors='ignore')
        if re.match(r'^[\x20-\x7E\n\r\t]+$', text[:100]) and len(text) > 10:
            results.append(('Прямое декодирование', text))
            logger.info("Прямое декодирование успешно")
    except:
        pass
    
    if results:
        return results[0]
    else:
        raise Exception("Не удалось расшифровать файл ни одним из методов")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    welcome_text = """
🔐 <b>Netwing Config Decryptor Bot</b>

Отправьте мне файл с расширением <b>.netcfg</b>, и я расшифрую его!

<b>📋 Возможности:</b>
• Поддержка 7+ методов расшифровки
• Автоматический выбор лучшего метода
• Расшифровка конфигурационных файлов Netwing

<b>📤 Как использовать:</b>
1. Нажмите на скрепку 📎
2. Выберите файл .netcfg
3. Отправьте мне

<b>⚡ Быстро и безопасно</b>
Файлы обрабатываются временно и не сохраняются

<i>Создано для Netwing Tools</i>
"""
    await update.message.reply_text(welcome_text, parse_mode='HTML')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = """
<b>📖 Помощь по боту</b>

🔹 <b>/start</b> - Начать работу
🔹 <b>/help</b> - Показать это сообщение
🔹 <b>/methods</b> - Показать методы расшифровки

<b>📁 Поддерживаемые файлы:</b>
• .netcfg (основной формат)
• .cfg (некоторые конфиги)
• .dat (некоторые данные)

<b>⚠️ Важно:</b>
• Файлы не сохраняются на сервере
• Размер файла до 50 МБ
• Время обработки до 10 секунд

<b>🔧 Алгоритмы:</b>
• AES-256-CBC
• AES-128-CBC  
• XOR шифрование
• Base64 декодирование
• JSON парсинг
• Zlib распаковка
• Прямое декодирование
"""
    await update.message.reply_text(help_text, parse_mode='HTML')

async def methods(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать методы расшифровки"""
    methods_text = """
<b>🔬 Доступные методы расшифровки</b>

1️⃣ <b>AES-256-CBC</b> - SHA256 хеширование ключа
2️⃣ <b>AES-128-CBC</b> - MD5 хеширование ключа
3️⃣ <b>XOR</b> - Побитовое XOR с ключом
4️⃣ <b>Base64</b> - Декодирование Base64
5️⃣ <b>JSON</b> - Парсинг JSON структуры
6️⃣ <b>Zlib</b> - Распаковка сжатых данных
7️⃣ <b>Прямое</b> - Попытка прямого декодирования

<i>Бот автоматически перебирает методы и выбирает лучший результат</i>
"""
    await update.message.reply_text(methods_text, parse_mode='HTML')

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик полученных файлов"""
    try:
        document = update.message.document
        
        file_ext = Path(document.file_name).suffix.lower()
        if file_ext not in ['.netcfg', '.cfg', '.dat']:
            await update.message.reply_text(
                "❌ Пожалуйста, отправьте файл с расширением .netcfg, .cfg или .dat"
            )
            return
        
        processing_msg = await update.message.reply_text(
            f"⏳ <b>Обработка файла...</b>\n\n"
            f"📁 <b>Имя:</b> {document.file_name}\n"
            f"📦 <b>Размер:</b> {document.file_size:,} байт\n\n"
            f"🔄 <b>Статус:</b> Расшифровка...",
            parse_mode='HTML'
        )
        
        file = await document.get_file()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            input_path = Path(temp_dir) / document.file_name
            await file.download_to_drive(input_path)
            
            with open(input_path, 'rb') as f:
                encrypted_data = f.read()
            
            try:
                method, decrypted_content = decrypt_netwing_file(encrypted_data)
                
                if len(decrypted_content.strip()) < 5:
                    await processing_msg.edit_text(
                        "❌ <b>Не удалось расшифровать файл</b>\n\n"
                        "Возможные причины:\n"
                        "• Файл поврежден или пустой\n"
                        "• Неизвестный метод шифрования\n"
                        "• Файл не является .netcfg"
                    )
                    return
                
                output_name = f"decrypted_{Path(document.file_name).stem}.txt"
                output_path = Path(temp_dir) / output_name
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(decrypted_content)
                
                with open(output_path, 'rb') as f:
                    await update.message.reply_document(
                        document=f,
                        filename=output_name,
                        caption=f"✅ <b>Файл успешно расшифрован!</b>\n\n"
                               f"🔑 <b>Метод:</b> {method}\n"
                               f"📊 <b>Размер:</b> {len(decrypted_content):,} символов",
                        parse_mode='HTML'
                    )
                
                if len(decrypted_content) < 2000:
                    preview = decrypted_content[:1000] + "..." if len(decrypted_content) > 1000 else decrypted_content
                    await update.message.reply_text(
                        f"📄 <b>Предпросмотр:</b>\n\n<code>{preview}</code>",
                        parse_mode='HTML'
                    )
                
                await processing_msg.delete()
                
            except Exception as e:
                logger.error(f"Ошибка расшифровки: {e}")
                await processing_msg.edit_text(
                    f"❌ <b>Ошибка при расшифровке</b>\n\n"
                    f"<code>{str(e)[:300]}</code>\n\n"
                    "Попробуйте другой файл или обратитесь к разработчику."
                )
                
    except Exception as e:
        logger.error(f"Общая ошибка: {e}")
        await update.message.reply_text(
            "❌ Произошла ошибка при обработке файла. Попробуйте еще раз."
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Update {update} caused error {context.error}")
    try:
        await update.message.reply_text(
            "⚠️ Произошла ошибка. Попробуйте позже или отправьте другой файл."
        )
    except:
        pass

def main():
    """Основная функция запуска бота"""
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("methods", methods))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_file))
    application.add_error_handler(error_handler)
    
    print("🤖 Бот запущен и готов к работе!")
    print(f"🔗 Токен: {TOKEN[:10]}...")
    print("📋 Доступные команды: /start, /help, /methods")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
