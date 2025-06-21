# AWS SAA-C03 Quiz App by ik0nw

A lightweight Python/Tkinter GUI application for practicing AWS Certified Solutions Architect Associate (SAA-C03) exam questions.

---

## 📦 Repository

**GitHub**: https://github.com/Ik0nw/aws_saa_questionBank

---

## ✨ Features

- **In Order Mode**: Walk through questions sequentially (you choose how many to attempt).
- **Exam Mode**: Random set of 60 questions for a full-practice exam.
- **Revision Mode**: Revisit only the questions you previously answered incorrectly.
- **Persistent Wrong-Answer Tracking**: Incorrect question IDs are stored in `wrong_questions.json` for later review.
- **Session Summary**: Displays count of correct/incorrect answers and overall accuracy percentage.

---

## 📋 Requirements

- **Python** 3.7 or newer
- **Tkinter** (bundled with most Python distributions)

_No external dependencies are required beyond the Python standard library._

---

## ⚙️ Setup & Installation

1. **Clone this repository**:

   ```bash
   git clone https://github.com/Ik0nw/aws_saa_questionBank.git
   cd aws_saa_questionBank
   ```

2. (Optional) **Create and activate a virtual environment**:

   ```bash
   python3 -m venv venv
   source venv/bin/activate    # on Linux/macOS
   venv\Scripts\activate     # on Windows
   ```

3. **Verify files**:
   - `aws_quiz_app.py` &rarr; main application script
   - `aws_saa_questions_with_votes.json` &rarr; question bank data
   - `wrong_questions.json` &rarr; (generated after first run)

4. **Run the application**:

   ```bash
   python aws_quiz_app.py
   ```

---

## 🚀 Usage

1. Launch the app by running `python aws_quiz_app.py`.
2. On the start screen, choose one of three modes:
   - **In Order Mode**: Enter a number of questions to attempt in sequential order.
   - **Exam Mode**: Automatically start a 60-question randomized practice exam.
   - **Revision Mode**: Review only questions you previously answered incorrectly.
3. Select your answer and click **Submit**.
4. Click **Next** to proceed through the quiz.
5. At the end, view your **Session Summary** (Correct, Wrong, Accuracy).
6. Click **Main Menu** to start another session or exit.

---

## 👨‍💻 Author

**ik0nw**

© 2025 ik0nw. All rights reserved.

