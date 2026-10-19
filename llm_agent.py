from groq import Groq

from dotenv import load_dotenv
import os

load_dotenv()


class Conversation_Manager:
    def __init__(self):
        self.groq_client = Groq(api_key=os.environ["GROQ_KEY"])
        self.conversation_history = []

    @staticmethod #self n'est pas appélé ici donc la méthode est statique
    def read_file(file_path):
        with open(file_path, "r") as file:
            return file.read()

    def ask_llm(self, question, history=None):
        # Liste vide par défaut : on n'en crée pas une partagée entre les appels.
        if history is None:
            history = []

        chat_completion = self.groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": self.read_file("./context.txt")
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

        response = chat_completion.choices[0].message.content
        return response


agent = Conversation_Manager()


def ask_llm(question, history=None):
    return agent.ask_llm(question, history=history)


if __name__ == "__main__":
    question = input("Pose ta question :\n")
    response = ask_llm(question)
    print("\n")
    print(response)
