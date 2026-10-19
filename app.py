import streamlit as st
from llm_agent import ask_llm

st.set_page_config(page_title="Jarvis")
st.title("Barbe-Quasar")

if "messages" not in st.session_state:
	st.session_state.messages = []

for message in st.session_state.messages:
	with st.chat_message(message["role"]):
		st.markdown(message["content"])

user_input = st.chat_input(
	"Que veux tu moussaillon ?",
	accept_file=False,
	accept_audio=False
	)

if user_input:
	# L'historique déjà affiché part avec la question. ask_llm ajoute la question courante.
	response = ask_llm(user_input, history=st.session_state.messages)
	st.session_state.messages.append({"role": "user", "content": user_input})
	st.session_state.messages.append({"role": "assistant", "content": response})

	with st.chat_message("user"):
		st.markdown(user_input)

	with st.chat_message("assistant"):
		st.markdown(response)
