# Rapport — mémoire de l'agent et points vus en session

## Sommaire

- [1. La branche locale et le remote](#branche-locale)
- [2. Installer requirements.txt](#installer-requirements)
- [3. Enregistrer une réponse ne donne pas de mémoire au modèle](#enregistrer-reponse)
  - [Corriger l'appel](#corriger-appel)
  - [Relire le fichier avant chaque question](#relire-fichier)
- [4. À quoi sert *history](#etoile-history)
- [5. Historique passé à ask_llm](#historique-ask-llm)
- [6. Pourquoi agent = Conversation_Manager()](#agent-conversation-manager)
- [7. st.session_state.messages.append(...)](#session-state-append)
- [8. À quoi correspond st](#alias-st)

<a id="branche-locale"></a>

## 1. La branche locale et le remote

La branche locale `feature/user-interface-for-llm-agent` n'était pas la branche distante. Elle a été créée à partir de `main` (le commit `Initial commit`) et n'avait pas d'upstream : `git status` affichait le nom de la branche sans `[origin/...]`.

Sur GitHub, `origin/feature/user-interface-for-llm-agent` était 4 commits plus loin :

- `requirements.txt`
- appel LLM via API
- personnalité de l'agent
- v1 de l'interface (`app.py`, `context.txt`, `llm_agent.py`)

Pour s'aligner sur le remote :

```bash
git checkout feature/user-interface-for-llm-agent
git branch -u origin/feature/user-interface-for-llm-agent
git pull
```

<a id="installer-requirements"></a>

## 2. Installer `requirements.txt`

`pip install requirements.txt` et `pip install requirements` demandent à pip un paquet qui porte ce nom. Le paquet n'existe pas.

Le drapeau `-r` dit à pip de lire le fichier et d'installer les paquets listés (`groq`, `python-dotenv`, `streamlit`) :

```bash
pip install -r requirements.txt
```

<a id="enregistrer-reponse"></a>

## 3. Enregistrer une réponse ne donne pas de mémoire au modèle

Écrire dans `memory.txt` et faire se souvenir le modèle sont deux actions distinctes. Le modèle ne voit que ce qu'on met dans `messages`.

`generate_response_memory` écrivait l'échange, mais :

- dans `app.py`, Streamlit n'appelait que `ask_llm` ;
- dans le bloc `if __name__ == "__main__"`, l'appel était `generate_response_memeory(response)` : le nom était faux, et la question n'était pas passée ;
- `ask_llm` n'envoyait que `context.txt` et la question du tour en cours.

`memory.txt` pouvait donc rester vide, et même rempli il était ignoré.

<a id="corriger-appel"></a>

### Corriger l'appel

La fonction attend la question et la réponse. On l'appelle une fois que `ask_llm` a renvoyé le texte, avec les deux arguments. `print(generate_response_memory(...))` affichait `None`, parce que la fonction écrit dans le fichier et ne renvoie rien : on l'appelle sans `print`.

`open(file_path="./memory.txt", "a")` est invalide. Le premier argument de `open` s'appelle `file`, pas `file_path`. La forme correcte est `open("./memory.txt", "a")`.

La fonction était aussi indentée après le `return` de `ask_llm`, donc jamais définie. Elle doit être au niveau du module.

<a id="relire-fichier"></a>

### Relire le fichier avant chaque question

Cette relecture se place au début de `ask_llm`, avant la création du client Groq. Un `return read_file(...)` à la fin de `generate_response_memory` arrive trop tard : la réponse est déjà partie.

1. Déclarer une variable `memory` juste sous `def ask_llm(question):`.
2. Tester si `./memory.txt` existe avec `os.path.isfile` (`os` est déjà importé). `read_file` fait un `open` en lecture : si le fichier n'existe pas, Python lève `FileNotFoundError`.
3. S'il existe, `memory = read_file("./memory.txt")`. Sinon, `memory = ""`. Un fichier vide renvoie déjà `""`.
4. Ajouter `memory` au message `system`, à la suite de `context.txt`, avec une phrase du type « voici la conversation déjà eue ». Tant que ce texte n'est dans aucun `messages`, la lecture ne change rien pour le modèle.

Au premier message, le fichier est vide : seul `context.txt` part. Aux tours suivants, l'historique est renvoyé au modèle.

<a id="etoile-history"></a>

## 4. À quoi sert `*history`

`ask_llm` peut recevoir une liste `history` de tours déjà eus. Chaque tour est un dictionnaire `role` / `content`.

`*history` déplie cette liste et place ses dictionnaires, un par un, dans `messages`, entre le personnage et la nouvelle question :

```python
messages = [
    {"role": "system", "content": "...contexte..."},
    {"role": "user", "content": "salut"},
    {"role": "assistant", "content": "Ahoy, moussaillon"},
    {"role": "user", "content": "tu te souviens de moi ?"},
]
```

Sans l'étoile, Python mettrait la liste entière comme un seul élément. L'API attend une suite de dictionnaires, pas une liste imbriquée.

Si `history` est vide, `*history` n'ajoute rien : il ne reste que le message système et la question.

Deux erreurs empêchaient cette liste de se construire :

- `*histoty` pointait vers un nom qui n'existe pas. Le bon nom est `*history`.
- Il manquait la virgule après cet élément, donc Python ne pouvait pas enchaîner avec le message utilisateur.

`history=[]` en argument par défaut est remplacé par `None`, puis une liste vide est créée dans la fonction. Une liste écrite dans la signature est partagée entre tous les appels.

<a id="historique-ask-llm"></a>

## 5. Historique passé à `ask_llm`

`app.py` garde les tours dans `st.session_state.messages`. À chaque question, cette liste est passée à `ask_llm` dans `history`, avant d'y ajouter le nouveau message. `*history` déplie donc les tours précédents dans l'appel Groq.

Chaque tour enregistré a le rôle `user` ou `assistant`. Groq attend `assistant` pour les réponses du modèle. Après l'appel, la question et la réponse sont ajoutées à `st.session_state.messages`, puis affichées. Au prochain message, elles font partie de l'historique.

<a id="agent-conversation-manager"></a>

## 6. Pourquoi `agent = Conversation_Manager()`

Le nom `agent` garde cet objet. Ensuite `agent.ask_llm(...)` rappelle le même objet, avec le même client Groq et la même `conversation_history`. Le nom pourrait être `manager` : ce qui compte, c'est de ranger le résultat.

Écrire `Conversation_Manager().ask_llm(...)` directement marche pour un seul appel, mais chaque question construit un objet neuf. L'historique posé sur cet objet repart à vide et disparaît à la fin de l'appel.

<a id="session-state-append"></a>

## 7. `st.session_state.messages.append(...)`

`st.session_state.messages.append({"role": "user", "content": user_input})` ajoute ta question à la liste gardée dans la session, pour que le tour suivant puisse la renvoyer au modèle.

`st.session_state.messages` est la liste des tours de cet onglet. `append` colle un élément à la fin. L'élément est un dictionnaire avec deux champs :

- `role` vaut `"user"`, pour dire que c'est toi qui parles.
- `content` vaut `user_input`, le texte tapé dans le chat.

La ligne d'après fait la même chose avec la réponse, en `"assistant"`. Au message suivant, cette liste part dans `history`, et `*history` la déplie dans l'appel à Groq.

<a id="alias-st"></a>

## 8. À quoi correspond `st`

`st` est le raccourci du module Streamlit. La première ligne de `app.py` fait `import streamlit as st`, donc `st.session_state` signifie `streamlit.session_state`.

Le nom `st` n'a rien de spécial : c'est l'alias choisi à l'import. `st.chat_input`, `st.title` et `st.session_state` sont des fonctions et des objets fournis par Streamlit.
