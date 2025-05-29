
import telebot,os,pickle,gzip
from google.colab import drive


MAX_SIZE_MB = 48
CHUNK_SIZE = MAX_SIZE_MB * 1024 * 1024




def save_data(bot,chat_id,data,start,end):
    file_path = f"{start}_{end}_data.pkl.gz"

    # Save data to compressed pickle locally
    with gzip.open(file_path, 'wb') as pkl_file:
            pickle.dump(data, pkl_file, protocol=pickle.HIGHEST_PROTOCOL)

    print("Data saved successfully to 'data.pkl.gz'")


    # Send to Telegram
    send_via_bot(bot,chat_id,file_path)


def initilize_bot(bot_token_para):
    # Initialize the bot
    bot = telebot.TeleBot(bot_token_para)
    return bot

def send_via_bot(bot,chat_id,filepath, filename_prefix="data_part"):
    file_size = os.path.getsize(filepath)
    if file_size <= CHUNK_SIZE:
        print(f"📤 Sending {filepath} to Telegram")
        with open(filepath, 'rb') as f:
            bot.send_document(chat_id, f, caption=os.path.basename(filepath))
    else:
        print("⚠️ File too large, splitting into parts...")
        split_and_send(bot,chat_id,filepath, filename_prefix)

def split_and_send(bot,chat_id,filepath, prefix):
    part = 1
    with open(filepath, 'rb') as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            part_file = f"{prefix}_part{part}.pkl.gz"
            with open(part_file, 'wb') as pf:
                pf.write(chunk)
            print(f"📤 Sending part {part} to Telegram")
            with open(part_file, 'rb') as pf:
                bot.send_document(chat_id, pf, caption=part_file)
            os.remove(part_file)
            part += 1