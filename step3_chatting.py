import os
import random
import string
import re
from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM

# Step3 - This file has the responding logic. U can use it for testing the conversation with your trained model.
# It can be customized, i just remove the name that triggers the bot from prompt and filter the multiline


def chat(prompt, name, trained_model_path, max_length, truncation, temperature, do_sample, top_k, top_p,
         chance_of_one_response, chance_of_second_response, chance_of_third_response, chance_of_all_responses):

    tokenizer = AutoTokenizer.from_pretrained(trained_model_path)
    model = AutoModelForCausalLM.from_pretrained(trained_model_path)
    generator = pipeline('text-generation', model=model, tokenizer=tokenizer)

    # Remove the bot name from prompt
    name = name.lower()
    pattern = r'\s*\b{}\b\s*'.format(re.escape(name))
    prompt_clean = re.sub(pattern, ' ', prompt).strip()

    # Check if the last character is not a punctuation. If it's not, add a question mark
    # this may improve responses, as the model may try to generate longer prompt by himself

    if len(prompt_clean) > 0 and prompt_clean[-1] not in string.punctuation:
        prompt_clean += "?"

    print(f"[chat] {name} responds to: {prompt_clean}")
    response = generator(prompt_clean,
                         max_length=max_length,
                         truncation=truncation,
                         temperature=temperature,
                         do_sample=do_sample,
                         top_k=top_k,
                         top_p=top_p)
    output = response[0]["generated_text"]

    # Sanitize from emoji's (selenium doesnt support these), and a character "ć", that doesnt work well with input in selenium
    output = ''.join('c' if char == 'ć' else char for char in output if ord(char) <= 0xFFFF)

    # Find all positions of key characters (double space or \n)
    key_char_positions = [m.start() for m in re.finditer(r"  |\n", output)]
    key_char_positions.append(len(output))
    start_pos = 0
    first = True

    # Output response was prompt repeated, then answer, then another prompt based on that, and so on
    # So i filter it so it returns every second output (excluding the first segment)
    segment_count = 0
    collected_output = ""

    # chance of returning all responses (because its funny)
    if random.random() <= chance_of_all_responses:
        for pos in key_char_positions:
            segment = output[start_pos:pos].strip()
            if segment:
                collected_output += segment + "\n"
            start_pos = pos + 1

    # randomizing nr of responses
    else:
        for pos in key_char_positions:
            segment = output[start_pos:pos].strip()
            if segment:
                segment_count += 1
                if segment_count == 2 and random.random() <= chance_of_one_response:
                    collected_output += segment + "\n"
                elif segment_count in (3, 4) and random.random() <= chance_of_second_response:
                    collected_output += segment + "\n"
                elif segment_count in (5, 6) and random.random() <= chance_of_third_response:
                    collected_output += segment + "\n"
            start_pos = pos + 1

    print(f"[chat] {name}: {collected_output.strip()}")
    return collected_output.strip()


if __name__ == "__main__":

    # in this example, "jacek" is the name that will be later used to trigger the bot,
    # so it's important to provide it here so it gets removed from prompt

    while True:
        input_prompt = input("prompt: ")
        chat(
             # required
             prompt=input_prompt,
             name="jacek",
             trained_model_path="./results/yourmodel",

             # response parameters
             max_length=32,
             temperature=1,
             truncation=True,
             do_sample=True,
             top_k=66110,
             top_p=0.5,

             # multi responses
             chance_of_one_response=1.0,
             chance_of_second_response=0.5,
             chance_of_third_response=0.25,
             chance_of_all_responses=0.08,
             )
