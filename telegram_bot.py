
import os.path
import tempfile
import traceback
from dotenv import load_dotenv
import telebot
import speech_recognition
import soundfile as sf
from moviepy.editor import *

load_dotenv()
telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
bot = telebot.TeleBot(telegram_bot_token)


# @bot.message_handler(func=lambda message: True, content_types=['text'])
# def handle_message(message):
#     # Отправляем в ответ сообщение, содержащее chat_id группы
#     bot.reply_to(message, f"chat_id: {message.chat.id}")

@bot.message_handler(func=lambda message: True, content_types=['voice'])
def voice_processing(message):
    try:
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        with tempfile.NamedTemporaryFile(suffix='.ogg', delete=False) as ogg_file:
            ogg_file.write(downloaded_file)

            with sf.SoundFile(ogg_file.name) as f:
                samplerate = f.samplerate
                ogg_file.seek(0)
                ogg_data = f.read()

                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as wav_file:
                    sf.write(wav_file.name, ogg_data, samplerate)
                    wav_file.seek(0)
                    message_text = record_and_recognize_audio(wav_file.name)
                    if message_text:
                        bot.reply_to(message, f"{message_text}")

        os.unlink(ogg_file.name)
        os.unlink(wav_file.name)

    except Exception as e:
        print(traceback.format_exc())



@bot.message_handler(func=lambda message: True, content_types=['video_note'])
def video_processing(message):
    try:
        file_info = bot.get_file(message.video_note.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
            temp_file.write(downloaded_file)

            video = VideoFileClip(temp_file.name)
            with video:
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as audio_file:
                    audio = video.audio
                    audio.write_audiofile(audio_file.name)

                    message_text = record_and_recognize_audio(audio_file.name)
                    if len(message_text) > 0:
                        bot.reply_to(message, f"{message_text}")

        # удаление временных файлов
        os.unlink(temp_file.name)
        os.unlink(audio_file.name)

    except Exception as _ex:
        print(traceback.print_exc())




def record_and_recognize_audio(audio_stream):
    """
    Запись и распознавание аудио
    """
    recognized_data = ""

    try:
        # регулирование уровня окружающего шума
        recognizer = speech_recognition.Recognizer()

        # recognizer.adjust_for_ambient_noise(massage, duration=2)

        with speech_recognition.AudioFile(audio_stream) as source:
            audio_data = recognizer.record(source)

        # регулирование уровня окружающего шума

        print("Started recognition...")
        recognized_data = recognizer.recognize_google(audio_data, language="ru").lower()



    except Exception as _ex:
        print(_ex)
    # recognizer.adjust_for_ambient_noise(audio_data, duration=2)

    return recognized_data


bot.polling(none_stop=True, interval=0)