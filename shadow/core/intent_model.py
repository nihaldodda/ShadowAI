# intent_model.py

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from shadow.core.learning_manager import load_learned_data

# --------------------------
# Base Training Data
# --------------------------

training_sentences = [

    # TIME (7)
    "what time is it",
    "tell me the time",
    "current time",
    "check the clock",
    "can you tell me the time",
    "what is the time now",
    "show me the time",

    # SHUTDOWN (6)
    "shutdown the system",
    "turn off computer",
    "power off pc",
    "shut down the machine",
    "switch off the computer",
    "turn off the system",

    # NEW QUEST (9)
    "new quest",
    "assign quest",
    "give me a mission",
    "i want a quest",
    "start a quest",
    "create a mission",
    "give me a new quest",
    "assign me a task",
    "begin a quest",

    # COMPLETE QUEST (7)
    "quest completed",
    "quest done",
    "i finished the quest",
    "mission completed",
    "i completed the quest",
    "mark quest complete",
    "the quest is finished",

    # STATUS (15)
    "check my status",
    "show my progress",
    "what is my level",
    "what is my rank",
    "show my stats",
    "how am i doing",
    "what is my current level",
    "show my current rank",
    "tell me my rank",
    "tell me my level",
    "how much xp do i have",
    "show my experience points",
    "what is my xp",
    "how strong am i",
    "display my shadow status",

    # --------------------------
    # BROWSER INTENTS
    # --------------------------

    # OPEN WEBSITE (10)
    "open youtube",
    "open google",
    "open github",
    "open reddit",
    "go to youtube",
    "go to google",
    "launch youtube",
    "visit github",
    "open a website",
    "open the browser",

    # SEARCH GOOGLE (8)
    "search google",
    "search for something",
    "google this",
    "look up python",
    "search the web",
    "find something online",
    "google search",
    "search on the internet",

    # LIST TABS (8)
    "what tabs are open",
    "show open tabs",
    "list my tabs",
    "which tabs are open",
    "show browser tabs",
    "what websites are open",
    "show all tabs",
    "display open tabs",

    # SWITCH TAB (7)
    "switch tab",
    "switch to youtube tab",
    "go to gmail tab",
    "focus on chrome tab",
    "change tab",
    "move to another tab",
    "switch browser tab",

    # CLOSE TAB (6)
    "close tab",
    "close current tab",
    "close this tab",
    "remove tab",
    "exit tab",
    "close the browser tab",

    # CLOSE ALL TABS (6)
    "close all tabs",
    "close browser",
    "exit browser",
    "shut down browser",
    "terminate browser",
    "close everything",
]

training_labels = (

    ["time_intent"] * 7 +
    ["shutdown_intent"] * 6 +
    ["new_quest_intent"] * 9 +
    ["complete_quest_intent"] * 7 +
    ["status_intent"] * 15 +

    ["open_website_intent"] * 10 +
    ["search_google_intent"] * 8 +
    ["list_tabs_intent"] * 8 +
    ["switch_tab_intent"] * 7 +
    ["close_tab_intent"] * 6 +
    ["close_all_tabs_intent"] * 6
)

training_labels = list(training_labels)

# --------------------------
# Merge Auto-Learned Data
# --------------------------

learned_data = load_learned_data()

for intent, sentences in learned_data.items():
    for sentence in sentences:
        training_sentences.append(sentence)
        training_labels.append(intent)

# --------------------------
# Vectorizer + Model
# --------------------------

vectorizer = TfidfVectorizer(
    ngram_range=(1, 3),
    stop_words="english",
    min_df=1
)

X = vectorizer.fit_transform(training_sentences)

model = LogisticRegression(max_iter=1000)
model.fit(X, training_labels)

# --------------------------
# Prediction Function
# --------------------------

def predict_intent(user_input: str):

    if not user_input.strip():
        return None, 0.0

    user_vector = vectorizer.transform([user_input])

    prediction = model.predict(user_vector)[0]
    confidence = max(model.predict_proba(user_vector)[0])

    return prediction, confidence
