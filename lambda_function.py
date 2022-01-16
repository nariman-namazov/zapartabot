import json, boto3, requests, random
from datetime import datetime

def log_payload(event, file=0, what=0):
    if not what:
        txt_data = bytes(json.dumps(event), "utf-8")
    else:
        txt_data = bytes(what, "utf-8")
    if not file:
        incoming = S3.Object("zapartabucket", f"{FOLDER}/{FILE}")
    else:
        incoming = S3.Object("zapartabucket", f"{FOLDER}/{file}")
    result = incoming.put(Body=txt_data)
    return 100

def read_file():
    with open("phrases.txt", "r") as file:
        contents = file.readlines()
    return contents

def send_message(event, phrase, phrase_bank):
    # Body is forwarded as a string of text rather than something else
    event_dict = json.loads(event["body"])

    #dump_it = ""
    try:    # inline query
        message = 0 # setting to 0 for if-else statements later on
        query_id = str(event_dict["inline_query"]["id"])
        chat_id = int(event_dict["inline_query"]["from"]["id"])
        #dump_it += f"inline chat_id OK - {chat_id}"
        query_message = event_dict["inline_query"]["query"]
        #dump_it += f"inline message OK - {query_message}"
    except KeyError as e:   # message directly to the bot
        query = 0
        #dump_it += f"caught KeyError - {str(e)}"
        sender_id = int(event_dict["message"]["from"]["id"])
        #dump_it += f"sender_id OK - {sender_id}"
        chat_id = int(event_dict["message"]["chat"]["id"])
        #dump_it += f"chat_id OK - {chat_id}"
        message = event_dict["message"]["text"]
        #dump_it += f"message OK - {message}"

    if message:
        payload = {
            "chat_id": chat_id,
            "text": "УВАГА! Террор входит в активную фазу.",
            "is_personal": False
        }
        msg = requests.post("https://api.telegram.org/ТОКЕН ХУЯРИТЬ СЮДИ/sendMessage", headers=HEADERS, data=json.dumps(payload))
        #log_payload(event, "response.json", msg.content.decode())
    else:
        # According to Telegram Bot API docs, there may be no more than 50 items in the inline query response.
        # We will only accept 49 matches from the phrase bank. Every item on the list will have the same structure for which template can be found below.
        item_template = {"type": "article", "id": "", "title": "", "input_message_content": ""}
        
        # match_count is set to 1 and not 0 because we already have "Random" as the first item
        match_count = 1; payload_result = [{"type": "article", "id": "1", "title": "Random", "input_message_content": {"message_text": phrase}}]
        for row in phrase_bank:
            if query_message.upper() in row.upper() and query_message != "":    # a workaround for Python's case sensitivity
                match_count += 1
                if match_count >= 51:
                    break
                # API docs do not say how many characters are allowed, 30 is a balanced value
                _item_template = {"type": "article", "id": str(match_count), "title": str(row[0:30] + "..."), "input_message_content": {"message_text": row}}
                payload_result.append(_item_template)

        payload = {
            "inline_query_id": query_id,
            "results": payload_result,
            "is_personal": False,
            "cache_time": 0
        }
        msg = requests.post("https://api.telegram.org/ТОКЕН ХУЯРИТЬ СЮДИ/answerInlineQuery", headers=HEADERS, data=json.dumps(payload))
        #log_payload(event, "response.json", msg.content.decode())
    #log_payload(event, "dump.txt", dump_it)
    return 100

def lambda_handler(event, context):
    #req = requests.get("https://api.telegram.org/", verify=False, timeout=5, allow_redirects=False)
    global S3, FOLDER, FILE, HEADERS
    S3 = boto3.resource("s3"); FOLDER = datetime.now().strftime("%d-%m-%Y"); FILE = datetime.now().strftime("%H_%M_%S") + ".json"
    HEADERS = {
        "Content-Type": "application/json",
        "Cache-Control": "no-cache"
    }
    
    if event == {} or event == "":
        return {
            "statusCode": 200,
            "body": "Most probably came from ALB."
        }
    elif event["path"] == "/health":
        return {
            "statusCode": 200,
        }
    elif event["path"] == "/":
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type":	"text/html; charset=UTF-8"
            },
            "body": "ACK"
        }
    elif event["path"] == "/terror":
        phrase_bank = read_file(); phrase = phrase_bank[random.randrange(0, len(phrase_bank))]
        result = log_payload(event, "loggs.txt")
        result_1 = send_message(event, phrase, phrase_bank)
        if result + result_1 == 200:
            return {"statusCode": 200}
