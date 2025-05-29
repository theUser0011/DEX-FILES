from get_zip_ile_by_id import download_zip
from get_json_from_zip import get_json_data
from concurrent.futures import ThreadPoolExecutor, as_completed
import os,json,requests,time
from send_file_to_bot import save_data,initilize_bot

data_json = None

def start_main(chat_id,bot_token):
    global start,end
    
    # Global parameters
    MAX_RETRIES = 3
    WAIT_SECONDS = 30
    MAX_WORKERS = 20  # Adjust this for parallelism
    SLEEP_AFTER = 40
    SLEEP_DURATION = 30
    MAX_DURATION = 5 * 3600  # 5 hours

    # Load data if not loaded
    if 'data' not in globals() or data is None or not isinstance(data, list):
        print("📥 Loading data from JSON...")
        try:
            data_json_temp = get_json_data()
            global data_json
            data_json = data_json_temp[start:end]
        except Exception as e:
            print(f"Failed to load data.json: {e}")
            data = []
        

    start += 0


    def get_mangadex_server_data(chapter_id):
        url = f"https://api.mangadex.org/at-home/server/{chapter_id}?forcePort443=false"
        headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "referer": "https://mangadex.org/",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"'
        }

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                return response.json()
            except requests.RequestException as e:
                if attempt < MAX_RETRIES:
                    time.sleep(WAIT_SECONDS)
                else:
                    return None

    def process_chapter(index_obj):
        index, obj = index_obj
        try:
            attributes = obj.get('attributes', {})
            chapter_value = attributes.get('chapter')

            if chapter_value and float(chapter_value) > 0:
                chapter_id = obj.get('id')
                if not chapter_id:
                    return index, None

                server_data = get_mangadex_server_data(chapter_id)
                if not server_data:
                    return index, None

                baseUrl = server_data.get('baseUrl')
                chapter_info = server_data.get('chapter', {})
                chapter_hash = chapter_info.get('hash')
                chapter_data = chapter_info.get('data')

                if baseUrl and chapter_hash and chapter_data:
                    formatted_response = {
                        "baseUrl": baseUrl,
                        "chapter": {
                            "hash": chapter_hash,
                            "data": chapter_data
                        }
                    }
                    return index, formatted_response
                else:
                    return index, None
            else:
                return index, None
        except Exception:
            return index, None

    # Main execution
    start_time = time.time()

    try:
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = []
            for idx, obj in enumerate(data_json):
                elapsed_time = time.time() - start_time
                if elapsed_time > MAX_DURATION:
                    print("⏰ Maximum runtime of 5 hours exceeded. Stopping early and saving progress.")
                    break

                futures.append(executor.submit(process_chapter, (idx, obj)))
                print(f"{idx}/{len(data_json)}")
                # Sleep logic every N tasks submitted
                if (idx + 1) % SLEEP_AFTER == 0:
                    print("Wait time Started at ",idx)
                    clear_output(wait=True)
                    time.sleep(SLEEP_DURATION)
                    print("Wait time Completed..")

            for future in as_completed(futures):
                idx, chapter_images_data = future.result()
                if chapter_images_data:
                    data[idx]['chapter_images_data'] = chapter_images_data

    finally:
        bot = initilize_bot(chat_id,bot_token)
        save_data(bot,chat_id,data_json,start,end)
