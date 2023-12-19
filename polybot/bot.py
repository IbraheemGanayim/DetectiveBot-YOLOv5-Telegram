import telebot
from loguru import logger
import os
import time
from telebot.types import InputFile
import requests
import boto3
from botocore.exceptions import ClientError
from bardapi import BardCookies
#import google.generativeai as genai

class Bot:

    def __init__(self, token, telegram_chat_url):
        # create a new instance of the TeleBot class.
        # all communication with Telegram servers are done using self.telegram_bot_client
        self.telegram_bot_client = telebot.TeleBot(token)

        # remove any existing webhooks configured in Telegram servers
        self.telegram_bot_client.remove_webhook()
        time.sleep(0.5)
        
        # set the webhook URL
        self.telegram_bot_client.set_webhook(url=f'{telegram_chat_url}/{token}/', timeout=60)

        logger.info(f'Telegram Bot information\n\n{self.telegram_bot_client.get_me()}')

    def send_text(self, chat_id, text):
        self.telegram_bot_client.send_message(chat_id, text)

    def send_text_with_quote(self, chat_id, text, quoted_msg_id):
        self.telegram_bot_client.send_message(chat_id, text, reply_to_message_id=quoted_msg_id)

    def send_animation(self, chat_id, gif):
        return self.telegram_bot_client.send_animation(chat_id=chat_id, animation=gif)

    def delete_message(self, chat_id, msg_id):
        self.telegram_bot_client.delete_message(chat_id=chat_id, message_id=msg_id)
        
    def is_current_msg_photo(self, msg):
        return 'photo' in msg

    def download_user_photo(self, msg):
        """
        Downloads the photos that sent to the Bot to `photos` directory (should be existed)
        :return:
        """
        if not self.is_current_msg_photo(msg):
            raise RuntimeError(f'Message content of type \'photo\' expected')

        file_info = self.telegram_bot_client.get_file(msg['photo'][-1]['file_id'])
        data = self.telegram_bot_client.download_file(file_info.file_path)
        folder_name = file_info.file_path.split('/')[0]

        if not os.path.exists(folder_name):
            os.makedirs(folder_name)

        with open(file_info.file_path, 'wb') as photo:
            photo.write(data)

        return file_info.file_path

    def send_photo(self, chat_id, img_path):
        if not os.path.exists(img_path):
            raise RuntimeError("Image path doesn't exist")

        self.telegram_bot_client.send_photo(
            chat_id,
            InputFile(img_path)
        )

    def handle_message(self, msg):
        """Bot Main message handler"""
        logger.info(f'Incoming message: {msg}')
        self.send_text(msg['chat']['id'], f'Your original message: {msg["text"]}')

class QuoteBot(Bot):
    def handle_message(self, msg):
        logger.info(f'Incoming message: {msg}')

        #if msg["text"] != 'Please don\'t quote me':
        if msg["text"] != 'Shut up':
            self.send_text_with_quote(msg['chat']['id'], msg["text"], quoted_msg_id=msg["message_id"])

class ObjectDetectionBot(Bot):

    session = boto3.Session(aws_access_key_id=os.environ['AWS_KEY_ID'],
                aws_secret_access_key=os.environ['AWS_ACCESS_KEY'],
                            region_name=os.environ['REGION'])

    def handle_message(self, msg):
        
        if(os.environ['BARD_FLAG'] == 'go'):
            #for GOOGLE BARD API - Gemeni PRO
            cookie_dict = {
                    "__Secure-1PSID": os.environ['__Secure-1PSID'],
                    "__Secure-1PSIDTS": os.environ['__Secure-1PSIDTS'],
                    "__Secure-1PSIDCC": os.environ['__Secure-1PSIDCC'],
                }
            bard = BardCookies(cookie_dict=cookie_dict)
            
            logger.info('\nBARD has been successfully configured.\n')

            # GOOGLE_API_KEY=os.environ['GOOGLE_API_KEY']
            # genai.configure(api_key=GOOGLE_API_KEY)
            # model = genai.GenerativeModel('gemini-pro')

        if self.is_current_msg_photo(msg):

            # Send loading.gif while predicting
            with open('loading.gif', 'rb') as gif:
               loading_msg = self.send_animation(chat_id=msg['chat']['id'], gif=gif)
            
            # TODO download the user photo (utilize download_user_photo)
            photo_path = self.download_user_photo(msg)
            
            s3_bucket = os.environ['BUCKET_NAME']

            s3_path = "photos/" + os.path.basename(photo_path)
            
            #logger.info(f'\n1. UPLOAD PHOTO:\nPHOTO PATH: {photo_path}\nS3 PATH: {s3_path}\n')
            # TODO upload the photo to S3
            uploaded = self.upload_to_s3(photo_path, s3_bucket, s3_path)
            if not uploaded:
                self.delete_message(msg['chat']['id'], loading_msg.message_id)
                self.send_text(msg['chat']['id'], "Failed to upload image to S3.")
            else:
                # TODO send a request to the `yolo5` service for prediction
                prediction = self.get_prediction(s3_path)
                self.delete_message(msg['chat']['id'], loading_msg.message_id)
                
                # TODO send results to the Telegram end-user
                if prediction:
                    # send the prediction summary
                    formatted_response = self.formatted_message(prediction)
                    self.send_text(msg['chat']['id'], text=formatted_response)

                    # send the prediction image
                    photo_path = str(photo_path.split("/")[1:])
                    photo_path = photo_path.strip("[]").replace("'", "")
                    s3_path = "predictions/" + photo_path

                    self.download_from_s3(s3_bucket, s3_path, photo_path)
                    self.send_photo(msg['chat']['id'], photo_path)
                    
                    # Tell a joke with the prediction using GOOGLE BARD API - Gemeni PRO
                    if(os.environ['BARD_FLAG'] == 'go'):
                        for_joke = self.format_prediction_to_bard(prediction)
                        bard_prompt = f'Tell me a short joke that includes one or more of the following:{for_joke}'
                        #bard_ans = model.generate_content(bard_prompt)
                        bans1 = bard.get_answer(bard_prompt)
                        bard_ans = bans1['content']
                        if(bans1['status_code'] == 200):
                            self.send_text(msg['chat']['id'], text=str(bard_ans))
                            logger.info('\nBARD answered to photo.\n')
                        else:
                            self.send_text(msg['chat']['id'], f'Your original message: {msg["text"]}\nTip: Send a photo!')
                    # self.delete_message(msg['chat']['id'], loading_msg.message_id)
                else:
                    self.send_text(msg['chat']['id'], "Failed to get prediction from YOLOv5 service.")
                    self.delete_message(msg['chat']['id'], loading_msg.message_id)
        elif "text" in msg:
            # Answer using GOOGLE BARD API - Gemeni PRO
            if(os.environ['BARD_FLAG'] == 'go'):
                bans = bard.get_answer(msg["text"])
                bard_ans_txt = bans['content']
                if(bans['status_code'] == 200):
                    self.send_text(msg['chat']['id'], text=str(bard_ans_txt))
                    logger.info('\nBARD answered to text.\n')
                else:
                    self.send_text(msg['chat']['id'], f'Your original message: {msg["text"]}\nTip: Send a photo!')
                #bard_ans_txt = model.generate_content(msg["text"])
            else:
                self.send_text(msg['chat']['id'], f'Your original message: {msg["text"]}\nTip: Send a photo!')
        else:
            self.send_text(msg['chat']['id'], 'Unsupported message type.\nTip: Send a photo!')

    def download_from_s3(self, bucket_name, object_name, local_path):

        s3_client = self.session.client('s3')
        try:
            s3_client.download_file(bucket_name, object_name, local_path)
        except ClientError as e:
            logger.error(f'\nERR: {e}\n')
            return False
        return True

    def upload_to_s3(self, file_path, bucket_name, object_name=None):
        if object_name is None:
            object_name = os.path.basename(file_path)
        s3_client = self.session.client('s3')
        try:
            s3_client.upload_file(file_path, bucket_name, object_name)
        except ClientError as e:
            logger.error(e)
            return False
        return True

    # Turn prediction JSON to readable text
    def formatted_message(self,json_ob):
        obj_count = {}
        formatted_string = f"Detected Objects:\n"
        for label in json_ob["labels"]:
            class_name = label["class"]
            if class_name in obj_count:
                obj_count[class_name] += 1
            else:
                obj_count[class_name] = 1
        for key, value in obj_count.items():
            formatted_string += f"{key}: {value}\n"
        return formatted_string

    # Utilize yolo5 service to get prediction
    def get_prediction(self, img_url):
        try:
            logger.info(f'\nimg_url = {img_url}\n')
            response = requests.post(f"http://yolo5-app:8081/predict?imgName={img_url}")
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Prediction request failed: {response.text}")
                return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error: {e}")
            return None

    def format_prediction_to_bard(self, input_message):
        obj_count = {}
        formatted_string = ""
        for label in input_message["labels"]:
            class_name = label["class"]
            if class_name in obj_count:
                obj_count[class_name] += 1
            else:
                obj_count[class_name] = 1
        for key, value in obj_count.items():
            formatted_string += f"{key}: {value}\n"
        return formatted_string
