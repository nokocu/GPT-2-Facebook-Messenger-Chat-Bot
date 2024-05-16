import os
import random

import unicodedata
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import ElementClickInterceptedException, StaleElementReferenceException
import time
import undetected_chromedriver as uc
from step3_chatting import chat

# Step4 - This the final file that handles logging into facebook account, monitoring the messages with a trigger word,
# and answering them using chat function from step3, that was trained in step2, with messages from step1.
# Additionaly, it can send random gifs, videos, audios and photos from downloaded facebook data folders.
# You can trigger it by using trigger words at the end of message, or with set random chance


# automates facebook messaging
def messenger_bot(trained_model_path, gif_trigger, video_trigger, audio_trigger, photo_trigger, media_folder_path,
                  name_trigger, welcome_message, input_field_element, last_message_element, conversation_url,
                  email, password, chance_textresponse_with_added_media, chance_mediaresponse_with_added_text, polling_rate,
                  max_length, temperature, truncation, do_sample, top_k, top_p,
                  chance_of_one_response, chance_of_second_response, chance_of_third_response, chance_of_all_responses):

    name_trigger = name_trigger.lower()
    media_paths = {
        gif_trigger: os.path.join(media_folder_path, "gifs"),
        video_trigger: os.path.join(media_folder_path, "videos"),
        audio_trigger: os.path.join(media_folder_path, "audio"),
        photo_trigger: os.path.join(media_folder_path, "photos")
    }

    # rolls random file
    def get_random_file(folder_path):
        files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        if files:
            return os.path.join(folder_path, random.choice(files))
        else:
            print("[get_random_file] failed")
            return None

    # uploads file using javascript input injection
    def javascript_upload_file(driver, file_path, delay=1):
        # Convert relative path to absolute path
        absolute_path = os.path.abspath(file_path)
        try:
            # JavaScript to set the file directly on the input
            file_input_js = """
            var input = document.querySelector('input[type=file]');
            input.style.display = 'block';
            return input;
            """
            file_input = driver.execute_script(file_input_js)
            file_input.send_keys(absolute_path)
            time.sleep(delay)
        except Exception as e:
            print(f"[javascript_upload_file] Exception occurred: {str(e)}")
            time.sleep(delay)

    def find_media_command(message, triggers):
        # normalize the message
        message = unicodedata.normalize('NFKD', message)
        message = "".join([c for c in message if not unicodedata.combining(c)])

        words = message.split()
        for word in words:
            for trigger, path in triggers.items():
                if trigger.split('_')[0] in word:  # Assuming the trigger format is "keyword_trigger"
                    return trigger
        return None

    # safely finds elements
    def safe_find_element(driver, by, value):
        try:
            element = WebDriverWait(driver, 7).until(EC.visibility_of_element_located((by, value)))
            return element
        except Exception as e:
            print(f"[safe_find_element] Error finding element by {by} with value {value}: {str(e)}")
            return None

    # retry till succesfull
    def retry_operation(operation, delay=3):
        while True:
            try:
                return operation()
            except StaleElementReferenceException:
                print("[retry_operation] Stale element reference encountered, retrying...")
                time.sleep(delay)
                continue
            except ElementClickInterceptedException:
                print("[retry_operation] Element click intercepted, retrying...")
                time.sleep(delay)
                continue
            except Exception as e:
                print(f"[retry_operation] Operation failed: {str(e)}")
                print(f"[retry_operation] Retrying in {delay} seconds...")
                time.sleep(delay)
                continue

    # handles multimedia sending
    def chat_multimedia(command=None, delay=0.750):
        # Possible commands
        commands = [gif_trigger, video_trigger, photo_trigger, audio_trigger]

        if command:
            file_path = get_random_file(media_paths[command])
            print(f"[chat_multimedia] {name_trigger} responds to: '{last_message_text}'")
        else:
            command = random.choice(commands)
            file_path = get_random_file(media_paths[command])
            print(f"[chat_multimedia] {name_trigger} decided to send a {command}")

        javascript_upload_file(driver, file_path)
        time.sleep(delay)
        message_paragraph = retry_operation(lambda: safe_find_element(driver, By.CSS_SELECTOR, input_field_element))
        message_paragraph.send_keys(Keys.RETURN)

    # handles text sending
    def chat_text(prompt=None, force_text=None, delay=0.750):
        message_paragraph = retry_operation(lambda: safe_find_element(driver, By.CSS_SELECTOR, input_field_element))
        if message_paragraph:
            if force_text:
                retry_operation(lambda: message_paragraph.click())
                time.sleep(delay)
                message_paragraph.send_keys(force_text)
                time.sleep(delay)
                message_paragraph.send_keys(Keys.RETURN)
            else:
                retry_operation(lambda: message_paragraph.click())
                response = chat(prompt, name_trigger, trained_model_path,
                                max_length=max_length,
                                temperature=temperature,
                                truncation=truncation,
                                do_sample=do_sample,
                                top_k=top_k,
                                top_p=top_p,
                                chance_of_one_response=chance_of_one_response,
                                chance_of_second_response=chance_of_second_response,
                                chance_of_third_response=chance_of_third_response,
                                chance_of_all_responses=chance_of_all_responses,
                                )

                # (optional) normalizing the output (because selenium doesn't like it)
                response = unicodedata.normalize('NFKD', response)
                response = "".join([c for c in response if not unicodedata.combining(c)])

                # Split the response into lines
                response_lines = response.split('\n')

                # Loop through each line in the response
                for line in response_lines:
                    while True:
                        try:
                            message_paragraph = retry_operation(lambda: safe_find_element(driver, By.CSS_SELECTOR, input_field_element))
                            break
                        except Exception as e:
                            time.sleep(1)
                            continue

                    message_paragraph.send_keys(line)
                    time.sleep(delay)
                    message_paragraph.send_keys(Keys.RETURN)
                    time.sleep(delay)


    # Initialize WebDriver
    options = uc.ChromeOptions()
    options.add_argument("--disable-notifications")
    options.add_argument("--mute-audio")
    driver = uc.Chrome(headless=True, options=options)
    driver.get(conversation_url)

    # Log into Facebook
    email_input = retry_operation(lambda: safe_find_element(driver, By.ID, "email"))
    if email_input:
        email_input.send_keys(email)

    pass_input = retry_operation(lambda: safe_find_element(driver, By.ID, "pass"))
    if pass_input:
        pass_input.send_keys(password + Keys.RETURN)

    # Wait for login to complete and navigate to the conversation
    WebDriverWait(driver, 7)
    driver.get(conversation_url)

    # Variable to store the last responded message
    last_responded_message = None

    # Welcome message
    while True:
        try:
            chat_text(force_text=welcome_message)
            print(f"[while welcome message] {name_trigger} online")
            break

        except Exception as e:
            error_message = str(e).split('\n')[0]
            print(f"[while welcome message] An error occurred: {error_message}")
            time.sleep(1)

    # Monitor for new messages and respond
    while True:
        try:
            # get latest message
            messages = retry_operation(lambda: WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, last_message_element))
            ))

            if messages:
                last_message_text = messages[-1].text.lower()
                if name_trigger in last_message_text and (last_responded_message is None or last_message_text != last_responded_message):
                    command = find_media_command(last_message_text, media_paths)
                    # send multimedia
                    if last_message_text != last_responded_message and command in media_paths:
                        last_responded_message = last_message_text
                        chat_multimedia(command=command)
                        time.sleep(4)  # buffor to wait for media to be send
                        if random.random() < chance_mediaresponse_with_added_text:
                            chat_text(last_message_text)

                    # Else block logic
                    else:
                        last_responded_message = last_message_text
                        chat_text(last_message_text)

                        if random.random() < chance_textresponse_with_added_media:
                            chat_multimedia()

        except Exception as e:
            error_message = str(e).split('\n')[0]
            print(f"[while monitor] An error occurred: {error_message}")
        time.sleep(polling_rate)

if __name__ == "__main__":

    messenger_bot(

        # paths
        trained_model_path="./results/yourmodel",
        media_folder_path="fb/your_activity_across_facebook/messages/inbox/groupchat_1337468645506280/",

        # strings
        name_trigger="jacek",
        gif_trigger="gif",
        video_trigger="wideo",
        audio_trigger="audio",
        photo_trigger="zdjecie",
        welcome_message="jestem",

        # selenium
        conversation_url="https://www.facebook.com/messages/t/1337468645506280",
        polling_rate=0.5,
        input_field_element="p.xat24cr.xdj266r",
        last_message_element="div.x18lvrbx",
        email=os.getenv("LOGIN"),
        password=os.getenv("PASS"),

        # chat response parameters
        max_length=54,
        temperature=1,
        truncation=True,
        do_sample=True,
        top_k=66110,
        top_p=0.5,

        # chat response randomness
        chance_of_one_response=1.0,
        chance_of_second_response=0.5,
        chance_of_third_response=0.2,
        chance_of_all_responses=0.08,
        chance_textresponse_with_added_media=0.1,
        chance_mediaresponse_with_added_text=0.7,)
