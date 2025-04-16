import json
from difflib import get_close_matches
import google.generativeai as genai

def load_knowledge_base(file_path: str) -> dict:
    with open(file_path, 'r') as file:
        return json.load(file)

def save_knowledge_base(file_path: str, data: dict):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)

def find_best_match(user_question: str, questions: list[str]) -> str | None:
    matches = get_close_matches(user_question, questions, n=1, cutoff=0.6)
    return matches[0] if matches else None

def get_answer_for_question(question: str, knowledge_base: dict) -> str | None:
    for q in knowledge_base["questions"]:
        if q["question"] == question:
            return q["answer"]

def get_gemini_answer(prompt: str, api_key: str) -> str:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    response = model.generate_content(prompt)
    return response.text.strip()

def chat_bot():
    knowledge_base = load_knowledge_base('knowledge_base.json')

    # Ask for API key once at the start
    api_key = input("Please paste your Google Gemini API key: ").strip()

    while True:
        user_input = input('You: ')

        if user_input.lower() == 'quit':
            break

        best_match = find_best_match(user_input, [q["question"] for q in knowledge_base["questions"]])

        if best_match:
            answer = get_answer_for_question(best_match, knowledge_base)
            print(f'Bot: {answer}')
        else:
            print("Bot: I don't know the answer. Let me check with Gemini...")

            try:
                gemini_answer = get_gemini_answer(user_input, api_key)
                print(f'Bot (Gemini): {gemini_answer}')
                
                choice = input("Do you want me to remember this answer for next time? (yes/no): ")
                if choice.lower() == 'yes':
                    knowledge_base["questions"].append({"question": user_input, "answer": gemini_answer})
                    save_knowledge_base('knowledge_base.json', knowledge_base)
                    print("Bot: Got it! I'll remember that.")
            except Exception as e:
                print(f"Bot: Sorry, I couldn't get an answer from Gemini. ({e})")

if __name__ == '__main__':
    chat_bot()

