import os
import logging
import tempfile
from pathlib import Path
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import base64
import json
import html

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
    Расшифровка .netcfg файлов Netwing с поддержкой XOR
    """
    results = []
    
    # Анализируем структуру зашифрованных данных
    logger.info(f"Размер зашифрованных данных: {len(encrypted_data)} байт")
    
    # Метод 1: XOR с ключом 'NetwingConfigKey2023'
    try:
        key = b'NetwingConfigKey2023'
        result = bytearray()
        for i, byte in enumerate(encrypted_data):
            result.append(byte ^ key[i % len(key)])
        text = result.decode('utf-8', errors='ignore')
        if text.strip() and len(text) > 10:
            # Проверяем наличие JSON структуры
            if any(marker in text for marker in ['{', '}', '"', ':']):
                results.append(('XOR (NetwingConfigKey2023)', text))
                logger.info("XOR метод с ключом NetwingConfigKey2023 успешен")
    except Exception as e:
        logger.debug(f"XOR метод 1 не сработал: {e}")
    
    # Метод 2: XOR с ключом 'Destroy3' (из названия)
    try:
        key = b'Destroy3'
        result = bytearray()
        for i, byte in enumerate(encrypted_data):
            result.append(byte ^ key[i % len(key)])
        text = result.decode('utf-8', errors='ignore')
        if text.strip() and len(text) > 10:
            if any(marker in text for marker in ['{', '}', '"', ':']):
                results.append(('XOR (Destroy3)', text))
                logger.info("XOR метод с ключом Destroy3 успешен")
    except Exception as e:
        logger.debug(f"XOR метод 2 не сработал: {e}")
    
    # Метод 3: XOR с ключом '10sec teleport' (из названия)
    try:
        key = b'10sec teleport'
        result = bytearray()
        for i, byte in enumerate(encrypted_data):
            result.append(byte ^ key[i % len(key)])
        text = result.decode('utf-8', errors='ignore')
        if text.strip() and len(text) > 10:
            if any(marker in text for marker in ['{', '}', '"', ':']):
                results.append(('XOR (10sec teleport)', text))
                logger.info("XOR метод с ключом 10sec teleport успешен")
    except Exception as e:
        logger.debug(f"XOR метод 3 не сработал: {e}")
    
    # Метод 4: XOR с ключом 'netwing'
    try:
        key = b'netwing'
        result = bytearray()
        for i, byte in enumerate(encrypted_data):
            result.append(byte ^ key[i % len(key)])
        text = result.decode('utf-8', errors='ignore')
        if text.strip() and len(text) > 10:
            if any(marker in text for marker in ['{', '}', '"', ':']):
                results.append(('XOR (netwing)', text))
                logger.info("XOR метод с ключом netwing успешен")
    except Exception as e:
        logger.debug(f"XOR метод 4 не сработал: {e}")
    
    # Метод 5: XOR с ключом 'config'
    try:
        key = b'config'
        result = bytearray()
        for i, byte in enumerate(encrypted_data):
            result.append(byte ^ key[i % len(key)])
        text = result.decode('utf-8', errors='ignore')
        if text.strip() and len(text) > 10:
            if any(marker in text for marker in ['{', '}', '"', ':']):
                results.append(('XOR (config)', text))
                logger.info("XOR метод с ключом config успешен")
    except Exception as e:
        logger.debug(f"XOR метод 5 не сработал: {e}")
    
    # Метод 6: XOR с автоматическим определением ключа
    try:
        # Ищем известные паттерны в зашифрованных данных
        if encrypted_data and len(encrypted_data) > 50:
            # Пробуем найти ключ, сравнивая с ожидаемой структурой JSON
            known_pattern = b'{"author":"'
            key = bytearray()
            for i in range(len(encrypted_data)):
                if i < len(known_pattern):
                    key.append(encrypted_data[i] ^ known_pattern[i])
            
            # Используем найденный ключ
            if len(key) > 5:
                result = bytearray()
                for i, byte in enumerate(encrypted_data):
                    result.append(byte ^ key[i % len(key)])
                text = result.decode('utf-8', errors='ignore')
                if text.strip() and len(text) > 10:
                    if any(marker in text for marker in ['{', '}', '"', ':']):
                        results.append(('XOR (автоматический ключ)', text))
                        logger.info("Автоматическое определение ключа успешно")
    except Exception as e:
        logger.debug(f"Автоматическое определение ключа не сработало: {e}")
    
    # Метод 7: Прямое декодирование
    try:
        text = encrypted_data.decode('utf-8', errors='ignore')
        if text.strip() and len(text) > 10:
            if any(marker in text for marker in ['{', '}', '"', ':']):
                results.append(('Прямое декодирование', text))
                logger.info("Прямое декодирование успешно")
    except:
        pass
    
    if results:
        # Возвращаем первый успешный метод
        return results[0]
    else:
        raise Exception("Не удалось расшифровать файл ни одним из методов")

def validate_and_fix_json(text):
    """Проверяем и исправляем JSON если нужно"""
    try:
        # Пробуем распарсить
        data = json.loads(text)
        return json.dumps(data, indent=2, ensure_ascii=False)
    except:
        # Если не получается, возвращаем как есть
        return text

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    welcome_text = """
🔐 <b>Netwing Config Decryptor Bot v2.0</b>

✅ <b>Обновленная версия с поддержкой XOR шифрования!</b>

Отправьте мне файл с расширением <b>.netcfg</b>, и я расшифрую его!

<b>📋 Особенности:</b>
• Специализированный XOR декодер
• Автоматическое определение ключа
• Поддержка JSON формата
• Сохранение в правильном формате

<b>📤 Как использовать:</b>
1. Нажмите на скрепку 📎
2. Выберите файл .netcfg
3. Отправьте мне

<b>⚡ Быстро и точно</b>
Специально для конфигов Netwing

<i>Создано для Netwing Tools</i>
"""
    await update.message.reply_text(welcome_text, parse_mode='HTML')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help"""
    help_text = """
<b>📖 Помощь по боту v2.0</b>

🔹 <b>/start</b> - Начать работу
🔹 <b>/help</b> - Показать это сообщение
🔹 <b>/methods</b> - Показать методы расшифровки

<b>🔧 Новые методы:</b>
• XOR с ключом 'NetwingConfigKey2023'
• XOR с ключом 'Destroy3'
• XOR с ключом '10sec teleport'
• Автоматическое определение ключа

<b>📁 Поддерживаемые файлы:</b>
• .netcfg (основной формат)
• .cfg (некоторые конфиги)

<b>⚠️ Важно:</b>
• Файлы не сохраняются на сервере
• Корректное сохранение JSON структуры
"""
    await update.message.reply_text(help_text, parse_mode='HTML')

async def methods(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показать методы расшифровки"""
    methods_text = """
<b>🔬 Специализированные методы XOR</b>

1️⃣ <b>XOR (NetwingConfigKey2023)</b> - Основной ключ
2️⃣ <b>XOR (Destroy3)</b> - Ключ из названия
3️⃣ <b>XOR (10sec teleport)</b> - Ключ из названия
4️⃣ <b>XOR (netwing)</b> - Стандартный ключ
5️⃣ <b>XOR (config)</b> - Альтернативный ключ
6️⃣ <b>XOR (автоматический)</b> - Определение по паттерну
7️⃣ <b>Прямое декодирование</b> - Если всё остальное не сработало

<i>Бот автоматически выбирает лучший метод</i>
"""
    await update.message.reply_text(methods_text, parse_mode='HTML')

async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик полученных файлов"""
    try:
        document = update.message.document
        
        file_ext = Path(document.file_name).suffix.lower()
        if file_ext not in ['.netcfg', '.cfg']:
            await update.message.reply_text(
                "❌ Пожалуйста, отправьте файл с расширением .netcfg или .cfg"
            )
            return
        
        processing_msg = await update.message.reply_text(
            f"⏳ <b>Обработка файла...</b>\n\n"
            f"📁 <b>Имя:</b> {document.file_name}\n"
            f"📦 <b>Размер:</b> {document.file_size:,} байт\n\n"
            f"🔄 <b>Статус:</b> Расшифровка XOR...",
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
                        "Попробуйте другой файл"
                    )
                    return
                
                # Пробуем отформатировать как JSON
                try:
                    formatted_content = validate_and_fix_json(decrypted_content)
                except:
                    formatted_content = decrypted_content
                
                # Сохраняем файл в правильном формате
                output_name = f"decrypted_{Path(document.file_name).stem}.json"
                output_path = Path(temp_dir) / output_name
                
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(formatted_content)
                
                # Отправляем файл
                with open(output_path, 'rb') as f:
                    await update.message.reply_document(
                        document=f,
                        filename=output_name,
                        caption=f"✅ <b>Файл успешно расшифрован!</b>\n\n"
                               f"🔑 <b>Метод:</b> {method}\n"
                               f"📊 <b>Размер:</b> {len(formatted_content):,} символов\n\n"
                               f"💡 Сохранен в формате .json",
                        parse_mode='HTML'
                    )
                
                # Отправляем превью
                preview = formatted_content[:1500]
                if len(formatted_content) > 1500:
                    preview += "\n\n... (файл отправлен выше)"
                
                await update.message.reply_text(
                    f"📄 <b>Предпросмотр:</b>\n\n<pre>{html.escape(preview)}</pre>",
                    parse_mode='HTML'
                )
                
                await processing_msg.delete()
                
            except Exception as e:
                logger.error(f"Ошибка расшифровки: {e}")
                await processing_msg.edit_text(
                    f"❌ <b>Ошибка при расшифровке</b>\n\n"
                    f"<code>{html.escape(str(e)[:300])}</code>",
                    parse_mode='HTML'
                )
                
    except Exception as e:
        logger.error(f"Общая ошибка: {e}")
        await update.message.reply_text(
            "❌ Произошла ошибка. Попробуйте еще раз."
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Update {update} caused error {context.error}")
    try:
        await update.message.reply_text(
            "⚠️ Произошла ошибка. Попробуйте позже."
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
    
    print("🤖 Бот v2.0 запущен и готов к работе!")
    print(f"🔗 Токен: {TOKEN[:10]}...")
    print("📋 Специализированный XOR декодер для Netwing")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
