# Facebook Messenger Chat-Bot (GPT-2)
A fun little-side project that i worked on:
* In short, it uses downloaded facebook messages in .json to train a model, and then automates responses using selenium.
* I used it to create a silly bot for my friend group that responds with the same humour as ours, and the results were hilarious
* It's split into steps, should make it easier for a begginer to create their own chat-bot, from your own messages. 
* To get started, grab the requirements
```pip install -r requirements.txt```
and follow steps below.

# step1_messages
This file prepares text messages.
* It reads multiple facebook json files from directory and saves them to .txt for machine learning.
* It's pre-set to save two txt files - one with raw messages, the other with separation between question and the answer.

# step2_training
This file loads the already formatted messages with defined separator and begins training.

* It is essential to get CUDA support for that step, as its way more efficiant than CPU.
Go to https://github.com/pytorch/pytorch/blob/main/RELEASE.md to find out about latest compatible NVIDIA CUDA version + CUDNN version to install.
* Mind the cache directory, that defaults to C:\Users\username\.cache\huggingface. Loaded model may be copied there and take a lot of space.

# step3_chatting
This file has the responding logic. 
* U can use it for testing the conversation with your trained model.
* It can be customized, in this example i remove the name that triggers the bot from prompt, and filter the multiline responses

# step4_selenium
This the final file that handles: 
* Logging into facebook account, 
* Monitoring the messages with a trigger word,
* Answering them using chat function from step3, that was trained in step2, with messages from step1.
* Additionaly, it can send random gifs, videos, audios and photos from downloaded facebook data folders.
You can trigger it by using trigger words at the end of message, or with set random chance
