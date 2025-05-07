import json
from pathlib import Path
from ollama import Client

# Initialize Ollama client
ollama = Client()

def read_transcript(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

def read_config(config_path):
    with open(config_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_summary_and_quiz(text, summary_prompt, quiz_prompt, model='mistral', num_questions=5):
    # Summarize the transcript
    summary_response = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": "You are an assistant that summarizes text."},
            {"role": "user", "content": f"{summary_prompt}\n{text}"}
        ]
    )
    summary = summary_response['message']['content']

    # Create quiz questions and answers
    quiz_response = ollama.chat(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates quiz questions and answers."},
            {"role": "user", "content": f"{quiz_prompt}\n{text}\nGenerate {num_questions} objective questions with options and answers in JSON format."}
        ]
    )
    quiz = quiz_response['message']['content']

    return summary, quiz

def save_to_json(output_path, summary, quiz):
    data = {
        "summary": summary,
        "quiz": quiz
    }
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def main():
    config = read_config('res/config.json')

    text = read_transcript(config['transcript_path'])
    summary, quiz = generate_summary_and_quiz(
        text,
        config.get('summary_prompt', 'Summarize the following text:'),
        config.get('quiz_prompt', 'Generate a quiz from the following text:'),
        config.get('model', 'mistral'),
        config.get('num_questions', 5)
    )
    save_to_json(config.get('output_path', 'output.json'), summary, quiz)

if __name__ == '__main__':
    main()
