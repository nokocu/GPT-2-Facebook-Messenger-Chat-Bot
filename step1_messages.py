import os
import json
import re

# Step1 - This file reads multiple facebook json files from directory and saves them to .txt for machine learning.
# Currently it saves two txt files - one with raw messages, the other with separation between question and answer


# converts facebook messages from multiple JSON files to one TXT
def load_facebook_data(directory):
    messages_list = []
    current_author = None
    combined_message = ""

    # Collect all json files and sort them by number in descending order
    files = [f for f in os.listdir(directory) if f.endswith('.json')]
    files.sort(key=lambda x: int(re.search(r'(\d+)', x).group()), reverse=True)

    for file in files:
        file_path = os.path.join(directory, file)
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            messages = data['messages']

            # Reverses the order (messages are stored latest first)
            messages.reverse()

            # Combines multiple messages in a row from the same person to 1 message
            for message in messages:
                if 'content' in message:
                    author = message.get('sender_name')
                    content = message['content'].encode('latin1').decode('utf-8')

                    if author == current_author:
                        combined_message += " " + content
                    else:
                        if combined_message:
                            messages_list.append(combined_message)
                        combined_message = content
                        current_author = author

    if combined_message:
        messages_list.append(combined_message)
    return messages_list


def message_dump(directory, output_raw, separator_token, output_separated):

    # prepare facebook json
    messages = load_facebook_data(directory)

    # write raw messages
    with open(output_raw, 'w', encoding='utf-8') as f:
        for text in messages:
            f.write(text + '\n')

    # read raw messages
    with open(output_raw, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # separate raw messages
    with open(output_separated, 'w', encoding='utf-8') as f:
        for i in range(0, len(lines) - 1, 2):
            prompt = lines[i].strip()
            answer = lines[i + 1].strip()
            combined_line = f"{prompt} {separator_token} {answer}\n"
            f.write(combined_line)


if __name__ == "__main__":
    message_dump(directory='fb/your_facebook_activity/messages/inbox/groupchat_1337468645506280',
                 output_raw='fb_messages_raw.txt',
                 output_separated='fb_messages.txt',
                 separator_token='(separator)')
