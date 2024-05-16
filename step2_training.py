import os
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
from transformers import TextDataset, DataCollatorForLanguageModeling

# Step2 - This file loads the already formatted messages with defined separator and begins training.
# It is essential to get CUDA support for that step, as its way more efficiant than CPU.
# Go to PyTorch github to find out about latest compatible NVIDIA CUDA version + CUDNN version to install.
# Mind the cache directory, that defaults to C:\Users\username\.cache\huggingface. Loaded model may be copied there.


def training(huggingface_model, output_model_path, messages_path, separator,
             block_size, epochs, train_batch_size, save_steps, save_total_limit):

    cuda_available = torch.cuda.is_available()
    print("Is CUDA available?", cuda_available)

    tokenizer = AutoTokenizer.from_pretrained(huggingface_model)
    model = AutoModelForCausalLM.from_pretrained(huggingface_model)

    # Add the separator token to the tokenizer
    special_tokens_dict = {'additional_special_tokens': [separator]}
    num_added_toks = tokenizer.add_special_tokens(special_tokens_dict)
    model.resize_token_embeddings(len(tokenizer))

    # Adjust model's embedding size to account for new tokens
    dataset = TextDataset(
        tokenizer=tokenizer,
        file_path=messages_path,
        block_size=block_size
    )
    data_collator = DataCollatorForLanguageModeling(
        tokenizer=tokenizer,
        mlm=False
    )

    # Define training arguments, possibly adjusting parameters for the new model
    training_args = TrainingArguments(
        output_dir='./results',
        overwrite_output_dir=True,
        num_train_epochs=epochs,
        per_device_train_batch_size=train_batch_size,
        save_steps=save_steps,
        save_total_limit=save_total_limit,
        gradient_accumulation_steps=2,
        fp16=True,
    )

    # Initialize Trainer with the new model and tokenizer
    trainer = Trainer(
        model=model,
        args=training_args,
        data_collator=data_collator,
        train_dataset=dataset,
    )

    # Allowing for retry after tweaking system settings
    while True:
        try:
            trainer.train()
            break
        except torch.cuda.OutOfMemoryError as e:
            print(e)
            torch.cuda.empty_cache()
            input("Press Enter to retry")

    # Save the final tokenizer and model
    tokenizer.save_pretrained(output_model_path)
    model.save_pretrained(output_model_path)

    # using pre-trained model as a base is recommended (get one from https://huggingface.co/models)
if __name__ == "__main__":

    # using pre-trained model as a base greatly improves the result (get one from https://huggingface.co/models)
    # im using a polish one for this example

    training(huggingface_model="sdadas/polish-gpt2-medium",
             output_model_path='./results/yourmodel',
             separator='(separator)',
             messages_path='fb_messages.txt',
             block_size=128,
             epochs=5,
             train_batch_size=4,
             save_steps=5000,
             save_total_limit=2)
