import tkinter as tk
import json
import random
import re
import requests
import os
from pathlib import Path
from dotenv import load_dotenv
import markdown
from tkhtmlview import HTMLLabel

# ─── Load environment variables ──────────────────────────────────────────────
env_path = Path(__file__).parent / ".env"
loaded = load_dotenv(dotenv_path=env_path, override=True)
if not loaded:
    print(f"⚠️ Warning: failed to load .env from {env_path}")

API_KEY = os.getenv('API_KEY')
API_URL = os.getenv('API_URL')
LANGUAGE = os.getenv('LANGUAGE', '中文')
MODEL = os.getenv('MODEL', 'gpt-4o')
USE_AI = os.getenv('USE_AI', 'False').lower() in ('1', 'true', 'yes')

CACHE_FILE = "explanation_cache.json"
WRONG_FILE = "wrong_questions.json"

# ─── Explanation cache ───────────────────────────────────────────────────────
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, 'r', encoding='utf-8') as f:
        explanation_cache = json.load(f)
else:
    explanation_cache = {}

def query_chatgpt(question_text, options_text):
    cache_key = question_text + "\n" + options_text
    if cache_key in explanation_cache:
        return explanation_cache[cache_key]

    prompt = (
        f"Q: {question_text}\n"
        f"Options:\n{options_text}\n\n"
        f"请用{LANGUAGE}回答：\n"
        "- **标出题干关键点**\n"
        "- **分析每个选项**，说明对错并加粗关键词\n"
    )
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        resp = requests.post(API_URL, headers=headers, json=payload)
        resp.raise_for_status()
        explanation = resp.json()["choices"][0]["message"]["content"]
    except Exception as e:
        explanation = f"[Error querying ChatGPT: {e}]"

    explanation_cache[cache_key] = explanation
    with open(CACHE_FILE, 'w', encoding='utf-8') as f:
        json.dump(explanation_cache, f, ensure_ascii=False, indent=2)

    return explanation

class QuizApp(tk.Tk):
    def __init__(self,
                 question_file="aws_saa_questions_with_votes.json",
                 wrong_file=WRONG_FILE):
        super().__init__()
        self.title("AWS SAA-C03 Quiz App by ik0nw")
        self.geometry("900x800")

        # Fonts & wrapping
        self.title_font    = ("Arial", 18, "bold")
        self.question_font = ("Arial", 14)
        self.radio_font    = ("Arial", 12)
        self.button_font   = ("Arial", 14)
        self.feedback_font = ("Arial", 14, "italic")
        self.summary_font  = ("Arial", 16, "bold")
        self.wraplength    = 800

        # Files & data
        self.question_file = question_file
        self.wrong_file    = wrong_file
        self.load_questions()
        self.load_wrong_data()

        # Quiz state
        self.mode            = None
        self.num_questions   = 0
        self.question_pool   = []
        self.current_index   = 0
        self.correct_count   = 0
        self.incorrect_count = 0
        self.abs_start       = 1

        # UI state
        self.selected_var = tk.StringVar()

        self.create_mode_frame()

    def load_questions(self):
        with open(self.question_file, 'r', encoding='utf-8') as f:
            self.questions = json.load(f)

    def load_wrong_data(self):
        if os.path.exists(self.wrong_file):
            with open(self.wrong_file, 'r', encoding='utf-8') as f:
                raw = json.load(f)
            self.wrong_data = {int(k): v for k, v in raw.items()}
        else:
            self.wrong_data = {}

    def save_wrong_data(self):
        with open(self.wrong_file, 'w', encoding='utf-8') as f:
            json.dump({str(k): v for k, v in self.wrong_data.items()},
                      f, ensure_ascii=False, indent=2)

    # ─── Main Menu ──────────────────────────────────────────────────────
    def create_mode_frame(self):
        self.clear_frame()
        frame = tk.Frame(self)
        frame.pack(pady=30)
        tk.Label(frame,
                 text="AWS Certified Solutions Architect Associate (SAA-C03)",
                 font=self.title_font).grid(row=0, column=0, columnspan=2, pady=5)
        tk.Button(frame,
                  text="In Order Mode",
                  font=self.button_font,
                  width=18,
                  command=self.setup_in_order).grid(row=1, column=0, padx=5, pady=5)
        tk.Button(frame,
                  text="Exam Mode",
                  font=self.button_font,
                  width=18,
                  command=self.setup_exam).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(frame,
                  text="Revision Mode",
                  font=self.button_font,
                  width=38,
                  command=self.setup_revision).grid(row=2, column=0, columnspan=2, pady=5)

    # ─── Mode setups ───────────────────────────────────────────────────
    def setup_in_order(self):
        self.clear_frame()
        frame = tk.Frame(self)
        frame.pack(pady=50)
        tk.Label(frame,
                 text="Start from question #:",
                 font=self.question_font).grid(row=0, column=0, pady=5)
        self.start_entry = tk.Entry(frame, font=self.question_font, width=5)
        self.start_entry.grid(row=0, column=1, pady=5)
        tk.Label(frame,
                 text="Number of questions:",
                 font=self.question_font).grid(row=1, column=0, pady=5)
        self.num_entry = tk.Entry(frame, font=self.question_font, width=5)
        self.num_entry.grid(row=1, column=1, pady=5)
        tk.Button(frame,
                  text="Start Quiz",
                  font=self.button_font,
                  width=20,
                  command=self.start_in_order).grid(row=2, column=0, columnspan=2, pady=10)
        self.mode = 'in_order'

    def setup_exam(self):
        self.mode = 'exam'
        self.num_questions = 60
        self.start_quiz()

    def setup_revision(self):
        self.clear_frame()
        self.mode = 'revision'
        self.question_pool = [self.questions[i] for i in sorted(self.wrong_data.keys())]
        self.num_questions = len(self.question_pool)
        if self.num_questions == 0:
            tk.Label(self,
                     text="No revision questions available.",
                     font=self.title_font).pack(pady=20)
            tk.Button(self,
                      text="Main Menu",
                      font=self.button_font,
                      command=self.create_mode_frame).pack()
        else:
            self.current_index = 0
            self.correct_count = 0
            self.incorrect_count = 0
            self.start_quiz()

    def start_in_order(self):
        try:
            start = int(self.start_entry.get())
            count = int(self.num_entry.get())
        except ValueError:
            return
        total = len(self.questions)
        start = max(1, min(start, total))
        end = min(start - 1 + count, total)
        self.question_pool = self.questions[start - 1:end]
        self.num_questions = len(self.question_pool)
        self.abs_start = start
        self.current_index = 0
        self.correct_count = 0
        self.incorrect_count = 0
        self.start_quiz()

    # ─── Quiz flow ───────────────────────────────────────────────────────
    def start_quiz(self):
        if self.mode == 'exam':
            self.question_pool = random.sample(self.questions, self.num_questions)
        self.show_question()

    def show_question(self):
        self.clear_frame()
        q = self.question_pool[self.current_index]

        # Parse votes: first entry is highest; extract correct-token from it
        votes_list = q.get("votes", [])
        # e.g. "BCF (96%)"
        main_vote = votes_list[0] if votes_list else ""
        correct_token = re.match(r"([A-Z]+)", main_vote).group(1) if main_vote else ""
        # determine multiselect by length of correct_token
        self.is_multi = len(correct_token) > 1
        if self.is_multi:
            self.correct_set = set(correct_token)
        else:
            self.correct = correct_token

        frame = tk.Frame(self, bd=2, relief='groove')
        frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Display index
        if self.mode == 'in_order':
            label_text = (f"Question {self.current_index+1}/{self.num_questions} "
                          f"(Overall #{self.abs_start + self.current_index})")
        elif self.mode == 'exam':
            orig_idx = self.questions.index(q) + 1
            label_text = (f"Question {self.current_index+1}/{self.num_questions} "
                          f"(Orig #{orig_idx})")
        else:
            label_text = f"Question {self.current_index+1}/{self.num_questions}"

        tk.Label(frame, text=label_text, font=self.title_font).pack(anchor='w', pady=(0,10))

        # Show question text
        clean_q = re.sub(r'Question\s*#\d+\s*', '', q['question'].strip())
        tk.Label(frame,
                 text=clean_q,
                 font=self.question_font,
                 wraplength=self.wraplength,
                 justify='left').pack(fill='x', pady=(0,10))

        # In revision mode show last wrong
        qid = self.questions.index(q)
        if self.mode == 'revision' and qid in self.wrong_data:
            last = self.wrong_data[qid].get('last_wrong')
            if last:
                tk.Label(frame,
                         text=f"Last wrong answer: {last}",
                         font=self.feedback_font,
                         fg="orange").pack(anchor='w', pady=(0,10))

        # Options
        self.selected_var.set("")
        self.multi_vars = {}
        if self.is_multi:
            for opt, txt in q['options'].items():
                clean_txt = txt.split("Correct Answer:")[0].strip()
                var = tk.BooleanVar()
                cb = tk.Checkbutton(frame,
                                    text=f"{opt}. {clean_txt}",
                                    variable=var,
                                    font=self.radio_font,
                                    wraplength=self.wraplength,
                                    justify='left')
                cb.pack(anchor='w', pady=3)
                self.multi_vars[opt] = var
        else:
            for opt, txt in q['options'].items():
                clean_txt = txt.split("Correct Answer:")[0].strip()
                rb = tk.Radiobutton(frame,
                                    text=f"{opt}. {clean_txt}",
                                    variable=self.selected_var,
                                    value=opt,
                                    font=self.radio_font,
                                    wraplength=self.wraplength,
                                    justify='left')
                rb.pack(anchor='w', pady=3)

        # Feedback & Submit
        self.feedback_label = tk.Label(frame, text="", font=self.feedback_font)
        self.feedback_label.pack(pady=10)

        self.submit_btn = tk.Button(frame,
                                    text="Submit",
                                    font=self.button_font,
                                    width=12,
                                    command=self.check_answer)
        self.submit_btn.pack(pady=10)

    def check_answer(self):
        q = self.question_pool[self.current_index]
        qid = self.questions.index(q)

        # Gather selection
        if self.is_multi:
            selected = {opt for opt, var in self.multi_vars.items() if var.get()}
            sel_str = "".join(sorted(selected))
            is_right = (selected == self.correct_set)
        else:
            sel = self.selected_var.get()
            sel_str = sel
            is_right = (sel == self.correct)

        if is_right:
            # On correct, show all votes
            votes_text = ", ".join(self.question_pool[self.current_index].get("votes", []))
            self.feedback_label.config(text=f"Correct! Votes: {votes_text}", fg="green")
            self.correct_count += 1
            if self.mode == 'revision' and qid in self.wrong_data:
                self.wrong_data[qid]['correct_count'] = self.wrong_data[qid].get('correct_count', 0) + 1
                if self.wrong_data[qid]['correct_count'] >= 3:
                    del self.wrong_data[qid]
                self.save_wrong_data()
            self.submit_btn.config(text="Next", command=self.next_question)
        else:
            # Record wrong
            entry = self.wrong_data.get(qid, {'correct_count': 0, 'last_wrong': None})
            entry['last_wrong'] = sel_str
            entry.setdefault('correct_count', 0)
            self.wrong_data[qid] = entry
            self.save_wrong_data()

            # Show correct answer
            if self.is_multi:
                correct_ans = "".join(sorted(self.correct_set))
            else:
                correct_ans = self.correct
            self.feedback_label.config(text=f"Incorrect! Answer: {correct_ans}", fg="red")
            self.incorrect_count += 1

            if USE_AI:
                question_text = re.sub(r'Question\s*#\d+\s*', '', q['question'].strip())
                options_text = "\n".join(
                    f"{k}. {v.split('Correct Answer:')[0].strip()}"
                    for k, v in q['options'].items()
                )
                explanation = query_chatgpt(question_text, options_text)
                self.show_explanation_popup(explanation)
            else:
                self.submit_btn.config(text="Next", command=self.next_question)

    def show_explanation_popup(self, explanation):
        popup = tk.Toplevel(self)
        popup.title("AI 解析")
        popup.geometry("700x500")
        popup.transient(self)
        popup.grab_set()

        html = markdown.markdown(explanation)
        html_label = HTMLLabel(popup, html=html, background="white")
        html_label.pack(fill="both", expand=True, padx=10, pady=10)
        html_label.fit_height()

        tk.Button(popup,
                  text="Next",
                  font=self.button_font,
                  command=lambda: [popup.destroy(), self.next_question()])\
            .pack(pady=10)

    def next_question(self):
        self.current_index += 1
        if self.current_index < self.num_questions:
            self.show_question()
        else:
            self.show_summary()

    def show_summary(self):
        self.clear_frame()
        frame = tk.Frame(self)
        frame.pack(fill='both', expand=True, padx=20, pady=20)

        tk.Label(frame, text="Session Summary", font=self.title_font).pack(pady=10)
        stats = tk.Frame(frame)
        stats.pack(pady=20)

        tk.Label(stats, text="Correct:", font=self.summary_font)\
            .grid(row=0, column=0, sticky='e', padx=5)
        tk.Label(stats, text=str(self.correct_count), font=self.summary_font, fg='green')\
            .grid(row=0, column=1, sticky='w', padx=5)

        tk.Label(stats, text="Wrong:", font=self.summary_font)\
            .grid(row=1, column=0, sticky='e', padx=5)
        tk.Label(stats, text=str(self.incorrect_count), font=self.summary_font, fg='red')\
            .grid(row=1, column=1, sticky='w', padx=5)

        accuracy = (self.correct_count / self.num_questions * 100
                    if self.num_questions else 0)
        tk.Label(stats, text="Accuracy:", font=self.summary_font)\
            .grid(row=2, column=0, sticky='e', padx=5)
        tk.Label(stats, text=f"{accuracy:.1f}%", font=self.summary_font, fg='blue')\
            .grid(row=2, column=1, sticky='w', padx=5)

        tk.Button(frame, text="Main Menu", font=self.button_font, width=14,
                  command=self.create_mode_frame).pack(pady=20)

    def clear_frame(self):
        for w in self.winfo_children():
            w.destroy()

if __name__ == '__main__':
    app = QuizApp()
    app.mainloop()
