from groq import Groq

from dotenv import load_dotenv
import os

load_dotenv()


class ConversationAgent:
    def __init__(self):
        self.groq_client = Groq(api_key=os.environ["GROQ_KEY"])
        self.conversation_history = [
                {
                    "role": "system",
                    "content": read_file(file_path="./context.txt")
                }
            ]

class Conversation_Manager:
    def __init__(self):
        self.groq_client = Groq(api_key=os.environ["GROQ_KEY"])
        self.conversation_history = []

    def ask_llm(self, question, history=None):
        if history is None:
            history = []

        chat_completion = self.groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": read_file("./context.txt")
                },
                *history,
                {
                    "role": "user",
                    "content": question,
                }
            ],
            model="openai/gpt-oss-120b",
            include_reasoning=False,
        )

        return chat_completion.choices[0].message.content


def read_file(file_path):
    with open(file_path, "r") as file:
        return file.read()


agent = Conversation_Manager()


def ask_llm(question, history=None):
    return agent.ask_llm(question, history=history)


if __name__ == "__main__":
    question = input("Pose ta question :\n")
    response = ask_llm(question)
    print("\n")
    print(response)
