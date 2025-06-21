import tkinter as tk
import json
import random
import os
import re

class QuizApp(tk.Tk):
    def __init__(self, question_file="aws_saa_questions_with_votes.json", wrong_file="wrong_questions.json"):
        super().__init__()
        self.title("AWS SAA-C03 Quiz App by ik0nw")
        self.geometry("900x800")
        # Fonts
        self.title_font = ("Arial", 18, "bold")
        self.subtitle_font = ("Arial", 12, "italic")
        self.mode_font = ("Arial", 14)
        self.question_font = ("Arial", 14)
        self.radio_font = ("Arial", 12)
        self.button_font = ("Arial", 14)
        self.feedback_font = ("Arial", 14, "italic")
        self.summary_font = ("Arial", 16, "bold")
        self.wraplength = 800

        # Files
        self.question_file = question_file
        self.wrong_file = wrong_file
        self.load_questions()
        self.load_wrong_ids()

        # Session state
        self.mode = None
        self.num_questions = 0
        self.question_pool = []
        self.current_index = 0
        self.correct_count = 0
        self.incorrect_count = 0

        # UI state
        self.selected_var = tk.StringVar()
        self.help_shown = False

        # Start
        self.create_mode_frame()

    def load_questions(self):
        with open(self.question_file, 'r', encoding='utf-8') as f:
            self.questions = json.load(f)

    def load_wrong_ids(self):
        if os.path.exists(self.wrong_file):
            with open(self.wrong_file, 'r', encoding='utf-8') as f:
                self.wrong_ids = set(json.load(f))
        else:
            self.wrong_ids = set()

    def save_wrong_ids(self):
        with open(self.wrong_file, 'w', encoding='utf-8') as f:
            json.dump(list(self.wrong_ids), f, ensure_ascii=False, indent=2)

    def create_mode_frame(self):
        self.clear_frame()
        self.help_shown = False
        frame = tk.Frame(self)
        frame.pack(pady=30)
        # Header
        tk.Label(frame, text="AWS Certified Solutions Architect Associate (SAA-C03)", font=self.title_font).grid(row=0, column=0, columnspan=2, pady=5)
        tk.Label(frame, text="Author: ik0nw", font=self.subtitle_font).grid(row=1, column=0, columnspan=2, pady=5)
        # Mode selection
        tk.Label(frame, text="Select Mode:", font=self.mode_font).grid(row=2, column=0, columnspan=2, pady=10)
        tk.Button(frame, text="In Order Mode", font=self.button_font, width=18, command=self.setup_in_order).grid(row=3, column=0, padx=10, pady=5)
        tk.Button(frame, text="Exam Mode", font=self.button_font, width=18, command=self.setup_exam).grid(row=3, column=1, padx=10, pady=5)
        tk.Button(frame, text="Revision Mode", font=self.button_font, width=38, command=self.setup_revision).grid(row=4, column=0, columnspan=2, pady=5)
        # Help toggle
        self.help_btn = tk.Button(frame, text="Show Help ▼", font=self.button_font, width=10, command=self.toggle_help)
        self.help_btn.grid(row=5, column=0, columnspan=2, pady=10)
        # Help text container
        self.help_frame = tk.Frame(self)
        help_text = (
            "In Order Mode:\n  Walk through questions sequentially; specify how many to attempt.\n"
            "Exam Mode:\n  Random set of 60 questions for full-practice exam.\n"
            "Revision Mode:\n  Revisit only the questions you previously answered incorrectly."
        )
        tk.Label(self.help_frame, text=help_text, font=self.question_font, justify='left').pack(padx=20, pady=10)

    def toggle_help(self):
        if self.help_shown:
            self.help_frame.pack_forget()
            self.help_btn.config(text="Show Help ▼")
        else:
            self.help_frame.pack(fill='x')
            self.help_btn.config(text="Hide Help ▲")
        self.help_shown = not self.help_shown

    def setup_in_order(self):
        self.clear_frame()
        frame = tk.Frame(self)
        frame.pack(pady=50)
        tk.Label(frame, text="Enter number of questions:", font=self.question_font).grid(row=0, column=0, pady=5)
        self.num_entry = tk.Entry(frame, font=self.question_font)
        self.num_entry.grid(row=0, column=1, pady=5)
        tk.Button(frame, text="Start Quiz", font=self.button_font, width=20, command=self.start_in_order).grid(row=1, column=0, columnspan=2, pady=10)
        self.mode = 'in_order'

    def setup_exam(self):
        self.mode = 'exam'
        self.num_questions = 60
        self.start_quiz()

    def setup_revision(self):
        self.clear_frame()
        self.mode = 'revision'
        self.question_pool = [self.questions[i] for i in sorted(self.wrong_ids)]
        self.num_questions = len(self.question_pool)
        if self.num_questions == 0:
            frame = tk.Frame(self)
            frame.pack(pady=50)
            tk.Label(frame, text="No revision questions available.", font=self.title_font).pack(pady=10)
            tk.Button(frame, text="Main Menu", font=self.button_font, width=14, command=self.create_mode_frame).pack(pady=10)
        else:
            self.start_quiz()

    def start_in_order(self):
        try:
            n = int(self.num_entry.get())
        except ValueError:
            return
        self.num_questions = min(n, len(self.questions))
        self.question_pool = self.questions[:self.num_questions]
        self.start_quiz()

    def start_quiz(self):
        # Reset session counts
        self.current_index = 0
        self.correct_count = 0
        self.incorrect_count = 0
        if self.mode == 'exam':
            self.question_pool = random.sample(self.questions, self.num_questions)
        self.show_question()

    def show_question(self):
        self.clear_frame()
        q = self.question_pool[self.current_index]
        correct = q.get('votes')[0].split()[0] if q.get('votes') else None
        q['correct'] = correct

        frame = tk.Frame(self, bd=2, relief='groove')
        frame.pack(fill='both', expand=True, padx=20, pady=20)
        tk.Label(frame, text=f"Question {self.current_index+1}/{self.num_questions}", font=self.title_font).pack(anchor='w', pady=(0,10))

        raw_q = q['question'].strip()
        clean_q = re.sub(r'Question\s*#\d+\s*', '', raw_q)
        tk.Label(frame, text=clean_q, font=self.question_font, wraplength=self.wraplength, justify='left').pack(fill='x', pady=(0,20))

        for opt, txt in q['options'].items():
            clean_txt = txt.split("Correct Answer:")[0].strip()
            tk.Radiobutton(
                frame, text=f"{opt}. {clean_txt}", variable=self.selected_var, value=opt,
                font=self.radio_font, wraplength=self.wraplength, justify='left'
            ).pack(anchor='w', pady=5)

        self.feedback_label = tk.Label(frame, text="", font=self.feedback_font)
        self.feedback_label.pack(pady=10)

        self.submit_btn = tk.Button(frame, text="Submit", font=self.button_font, width=12, command=self.check_answer)
        self.submit_btn.pack(pady=10)

    def check_answer(self):
        sel = self.selected_var.get()
        if not sel:
            return
        q = self.question_pool[self.current_index]
        correct = q['correct']
        if sel == correct:
            self.feedback_label.config(text="Correct!", fg="green")
            self.correct_count += 1
        else:
            self.feedback_label.config(text=f"Incorrect!  Answer: {correct}", fg="red")
            self.incorrect_count += 1
            self.wrong_ids.add(self.questions.index(q))
            self.save_wrong_ids()
        self.submit_btn.config(text="Next", command=self.next_question)

    def next_question(self):
        self.selected_var.set("")
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
        stats_frame = tk.Frame(frame)
        stats_frame.pack(pady=20)
        tk.Label(stats_frame, text="Correct:", font=self.summary_font).grid(row=0, column=0, sticky='e', padx=5)
        tk.Label(stats_frame, text=str(self.correct_count), font=self.summary_font, fg='green').grid(row=0, column=1, sticky='w', padx=5)
        tk.Label(stats_frame, text="Wrong:", font=self.summary_font).grid(row=1, column=0, sticky='e', padx=5)
        tk.Label(stats_frame, text=str(self.incorrect_count), font=self.summary_font, fg='red').grid(row=1, column=1, sticky='w', padx=5)
        accuracy = self.correct_count / self.num_questions * 100
        tk.Label(stats_frame, text="Accuracy:", font=self.summary_font).grid(row=2, column=0, sticky='e', padx=5)
        tk.Label(stats_frame, text=f"{accuracy:.1f}%", font=self.summary_font, fg='blue').grid(row=2, column=1, sticky='w', padx=5)

        tk.Button(frame, text="Main Menu", font=self.button_font, width=14, command=self.create_mode_frame).pack(pady=20)

    def clear_frame(self):
        for widget in self.winfo_children():
            widget.destroy()

if __name__ == '__main__':
    app = QuizApp()
    app.mainloop()
