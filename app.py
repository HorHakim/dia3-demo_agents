import streamlit as st
from llm_agent import ConversationAgent


class ChatInterface:
    def __init__(self):
        st.set_page_config(page_title="Jarvis")
        st.title("Barbe-Quasar")

        # On crée l'agent UNE SEULE FOIS et on le garde dans la session,
        # sinon l'historique serait perdu à chaque rechargement de Streamlit
        if "agent" not in st.session_state:
            st.session_state.agent = ConversationAgent()

        self.agent = st.session_state.agent


    @staticmethod
    def display_message(role, content):
        with st.chat_message(role):
            st.markdown(content)


    def display_history(self):
        for message in self.agent.conversation_history:
            # On n'affiche pas le prompt système (la personnalité du pirate)
            if message["role"] == "system":
                continue
            self.display_message(role=message["role"], content=message["content"])


    def run(self):
        # 1. Réafficher toute la conversation déjà échangée
        self.display_history()

        # 2. Attendre une nouvelle question
        user_input = st.chat_input(
            "Que veux tu moussaillon ?",
            accept_file=False,
            accept_audio=False
        )

        # 3. Afficher la question, demander à l'agent, afficher la réponse
        if user_input:
            self.display_message(role="user", content=user_input)

            with st.chat_message("assistant"):
                with st.spinner("Le capitaine réfléchit..."):
                    response = self.agent.ask_llm(user_input)
                st.markdown(response)


if __name__ == "__main__":
    chat = ChatInterface()
    chat.run()