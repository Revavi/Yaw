import os

import telebot

from ..utils import generate_random_string

class Uploads:
    def __init__(self, bot: telebot.TeleBot) -> None:
        self.bot = bot

    def handle_document(self, message: telebot.types.Message):
        if not os.path.isdir("uploads"):
            os.mkdir("uploads")

        extension = message.document.file_name.split(".")[-1]
        file_name = f"uploads/file_{generate_random_string()}.{extension}"

        document_file_info = self.bot.get_file(message.document.file_id)
        document_file = self.bot.download_file(document_file_info.file_path)

        with open(file_name, "wb") as new_file:
            new_file.write(document_file)

        self.bot.send_message(message.chat.id, f"<i>Файл сохранён по пути <code>{file_name}</code>.</i>", reply_to_message_id=message.id)

    def handle_audio(self, message: telebot.types.Message):
        if not os.path.isdir("uploads"):
            os.mkdir("uploads")

        file_name = f"uploads/audio_{generate_random_string()}.ogg"

        audio_file_info = self.bot.get_file(message.audio.file_id)
        audio_file = self.bot.download_file(audio_file_info.file_path)

        with open(file_name, "wb") as new_file:
            new_file.write(audio_file)

        self.bot.send_message(message.chat.id, f"<i>Аудио сохранено в файл <code>{file_name}</code>.</i>", reply_to_message_id=message.id)

    def handle_video(self, message: telebot.types.Message):
        if not os.path.isdir("uploads"):
            os.mkdir("uploads")

        file_name = f"uploads/video_{generate_random_string()}.mp4"

        if message.content_type == "video":
            video_file_info = self.bot.get_file(message.video.file_id)
        else:
            video_file_info = self.bot.get_file(message.video_note.file_id)
        video_file = self.bot.download_file(video_file_info.file_path)

        with open(file_name, "wb") as new_file:
            new_file.write(video_file)

        self.bot.send_message(message.chat.id, f"<i>Видео сохранено в файл <code>{file_name}</code>.</i>", reply_to_message_id=message.id)
    
    def handle_voice(self, message: telebot.types.Message):
        if not os.path.isdir("uploads"):
            os.mkdir("uploads")

        file_name = f"uploads/voice_{generate_random_string()}.ogg"

        voice_file_info = self.bot.get_file(message.voice.file_id)
        voice_file = self.bot.download_file(voice_file_info.file_path)

        with open(file_name, "wb") as new_file:
            new_file.write(voice_file)

        self.bot.send_message(message.chat.id, f"<i>Голосовое сообщение сохранено в файл <code>{file_name}</code>.</i>", reply_to_message_id=message.id)

    def handle_photo(self, message: telebot.types.Message):
        if not os.path.isdir("uploads"):
            os.mkdir("uploads")

        file_name = f"uploads/photo_{generate_random_string()}.jpg"

        photo_file_info = self.bot.get_file(message.photo[-1].file_id)
        photo_file = self.bot.download_file(photo_file_info.file_path)

        with open(file_name, "wb") as new_file:
            new_file.write(photo_file)
            
        self.bot.send_message(message.chat.id, f"<i>Фото сохранено в файл <code>{file_name}</code>.</i>", reply_to_message_id=message.id)