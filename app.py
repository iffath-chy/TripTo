import os
import threading
import tkinter as tk
from tkinter import scrolledtext
import re

from langgraph.graph import StateGraph, END
from typing import TypedDict

from langchain_google_genai import ChatGoogleGenerativeAI


API_KEY = "AQ.Ab8RN6LYpkYc5iO0-Bn9Mu_8-748rL3DNWnTAul-993FAu6w-g"



llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest",
    google_api_key=API_KEY,
    temperature=0.4
)


def speak(text):
    text = text.replace('"', "")
    os.system(f'say -v Karen "{text}"')



class TripState(TypedDict):
    user_input: str
    response: str



def travel_agent(state):

    prompt = f"""
You are TripTo ✈️, an intelligent travel planning assistant.

Keep responses concise.

If the user only provides a destination name,
give:

• Brief overview
• Best time to visit
• Top attractions
• Ask a follow-up question

Keep responses under 200 words unless the user
explicitly requests a detailed itinerary.

User:
{state["user_input"]}
"""

    result = llm.invoke(prompt)

    try:

        if isinstance(result.content, list):

            response_text = ""

            for item in result.content:

                if isinstance(item, dict):

                    response_text += item.get("text", "")

        else:

            response_text = str(result.content)

    except Exception:

        response_text = str(result.content)

    response_text = re.sub(r"\*\*(.*?)\*\*", r"\1", response_text)
    response_text = re.sub(r"#+\s*", "", response_text)    

    return {
        "response": response_text
    }



builder = StateGraph(TripState)

builder.add_node(
    "travel_agent",
    travel_agent
)

builder.set_entry_point(
    "travel_agent"
)

builder.add_edge(
    "travel_agent",
    END
)

trip_graph = builder.compile()



BG = "#0B1220"
CARD = "#111827"
INPUT = "#1E293B"

TEXT = "#FFFFFF"
SUBTEXT = "#CBD5E1"

SEND_GREEN = "#00C853"
VOICE_ORANGE = "#FF9800"


class TripToGUI:

    def __init__(self, root):

        self.root = root

        root.title("TripTo ✈️")
        root.geometry("1000x700")
        root.configure(bg=BG)

        self.last_response = ""

        # Header

        header = tk.Frame(root, bg=BG)
        header.pack(pady=20)

        title = tk.Label(
            header,
            text="Welcome to TripTo ✈️",
            font=("Helvetica", 28, "bold"),
            fg=TEXT,
            bg=BG
        )
        title.pack()

        subtitle = tk.Label(
            header,
            text="How can I help you with your travel plan?",
            font=("Helvetica", 14),
            fg=SUBTEXT,
            bg=BG
        )
        subtitle.pack()

        self.status = tk.Label(
            root,
            text="Ready",
            bg=BG,
            fg=SUBTEXT
        )
        self.status.pack()

        # Chat

        self.chat_area = scrolledtext.ScrolledText(
            root,
            bg=CARD,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            wrap=tk.WORD,
            font=("Helvetica", 12)
        )

        self.chat_area.pack(
            fill=tk.BOTH,
            expand=True,
            padx=20,
            pady=15
        )

        self.chat_area.insert(
            tk.END,
            "TripTo ✈️: Welcome! Ask me anything about your travel plans.\n\n"
        )

        self.chat_area.config(state="disabled")

        # Bottom

        bottom = tk.Frame(root, bg=BG)
        bottom.pack(fill=tk.X, padx=20, pady=15)

        self.entry = tk.Entry(
            bottom,
            bg=INPUT,
            fg=TEXT,
            insertbackground=TEXT,
            relief="flat",
            font=("Helvetica", 12)
        )

        self.entry.pack(
            side=tk.LEFT,
            fill=tk.X,
            expand=True,
            ipady=12
        )

        self.entry.bind(
            "<Return>",
            lambda event: self.send_message()
        )

        send_btn = tk.Button(
            bottom,
            text="Send",
            bg="#22C55E",
            fg="black",
            font=("Helvetica", 12, "bold"),
            width=12,
            height=2,
            command=self.send_message
        )

        send_btn.pack(side=tk.LEFT, padx=10)

        speak_btn = tk.Button(
            bottom,
            text="🔊 Speak",
            bg="#F97316",
            fg="black",
            font=("Helvetica", 12, "bold"),
            width=12,
            height=2,
            command=self.speak_response
        )

        speak_btn.pack(side=tk.LEFT)

        threading.Thread(
            target=lambda: speak(
                "Welcome to TripTo. How can I help you with your travel plan?"
            ),
            daemon=True
        ).start()

    def add_message(self, sender, msg):

        self.chat_area.config(state="normal")

        self.chat_area.insert(
            tk.END,
            f"{sender}: {msg}\n\n"
        )

        self.chat_area.see(tk.END)

        self.chat_area.config(state="disabled")

    def send_message(self):

        text = self.entry.get().strip()

        if not text:
            return

        self.entry.delete(0, tk.END)

        self.add_message("You", text)

        self.status.config(
            text="TripTo is planning your trip..."
        )

        threading.Thread(
            target=self.generate_response,
            args=(text,),
            daemon=True
        ).start()

    def generate_response(self, text):

        try:

            print("Calling Gemini...")

            result = trip_graph.invoke(
                {
                    "user_input": text
                }
            )

            print("Gemini Returned")

            response = result["response"]

            self.last_response = response

            self.root.after(
                0,
                lambda: self.add_message(
                    "TripTo ✈️",
                    response
                )
            )

            self.root.after(
                0,
                lambda: self.status.config(
                    text="Ready"
                )
            )

        except Exception as e:

            print("ERROR:", e)

            self.root.after(
                0,
                lambda: self.add_message(
                    "ERROR",
                    str(e)
                )
            )

            self.root.after(
                0,
                lambda: self.status.config(
                    text="Error"
                )
            )

    def speak_response(self):

        if not self.last_response:
            return

        threading.Thread(
            target=lambda: speak(
                self.last_response[:500]
            ),
            daemon=True
        ).start()


if __name__ == "__main__":

    root = tk.Tk()

    app = TripToGUI(root)

    root.mainloop()

