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

def read_file(event):
    with open("phrases.txt", "r") as file:
        contents = file.readlines()
    return contents

def send_message(event, phrase):
    # Body is forwarded as a string of text rather than something else
    event_dict = json.loads(event["body"])

    dump_it = ""
    try:    # inline query
        message = 0 # setting to 0 for if-else statements later on
        query_id = str(event_dict["inline_query"]["id"])
        chat_id = int(event_dict["inline_query"]["from"]["id"])
        dump_it += f"inline chat_id OK - {chat_id}"
        message = event_dict["inline_query"]["query"]
        dump_it += f"inline message OK - {message}"
    except KeyError as e:   # message directly to the bot
        query = 0
        dump_it += f"caught KeyError - {str(e)}"
        sender_id = int(event_dict["message"]["from"]["id"])
        dump_it += f"sender_id OK - {sender_id}"
        chat_id = int(event_dict["message"]["chat"]["id"])
        dump_it += f"chat_id OK - {chat_id}"
        message = event_dict["message"]["text"]
        dump_it += f"message OK - {message}"

    if message:
        payload = {
            "chat_id": chat_id,
            "text": "УВАГА! Террор входит в активную фазу.",
            "is_personal": False
        }
        msg = requests.post("https://api.telegram.org/ТОКЕН ХУЯРИТЬ СЮДИ/sendMessage", headers=HEADERS, data=json.dumps(payload))
        log_payload(event, "response.json", msg.content.decode())
    else:
        payload = {
            "inline_query_id": query_id,
            "results": [{"type": "article", "id": "1", "title": "Fire away", "input_message_content": {"message_text": phrase}}],
            "is_personal": False,
            "cache_time": 0
        }
        msg = requests.post("https://api.telegram.org/ТОКЕН ХУЯРИТЬ СЮДИ/answerInlineQuery", headers=HEADERS, data=json.dumps(payload))
        log_payload(event, "response.json", msg.content.decode())
    log_payload(event, "loggs.txt", dump_it)
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
        phrases = read_file(event); phrase = phrases[random.randrange(0, len(phrases))]
        result = log_payload(event)
        result_1 = send_message(event, phrase)
        if result + result_1 == 200:
            return {"statusCode": 200}