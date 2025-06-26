AWS SAA-C03 Quiz App by ik0nw

A lightweight Python and Tkinter application for practicing AWS Certified Solutions Architect Associate (SAA-C03) exam questions.

## Features

* **In Order Mode**: Progress through questions in sequence, with the option to specify how many questions to attempt and from which starting point.
* **Exam Mode**: Take a randomized 60-question mock exam to simulate real test conditions.
* **Revision Mode**: Review only the questions that were answered incorrectly in previous sessions.
* **Persistent Tracking**: Incorrect question IDs are saved in `wrong_questions.json` for focused revision.
* **AI-Powered Explanations** (optional): Receive detailed explanations for incorrect answers when AI assistance is enabled.
* **Session Summary**: View counts of correct and incorrect responses along with overall accuracy percentage.

## Requirements

* Python 3.7 or later
* Tkinter (included with most Python installations)
* Optional dependencies for AI support:

  * `requests`
  * `python-dotenv`
  * `markdown`
  * `tkhtmlview`

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/Ik0nw/aws_saa_questionBank.git
   cd aws_saa_questionBank
   ```
2. (Optional) Create and activate a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate    # macOS/Linux
   venv\Scripts\activate     # Windows
   ```
3. Install optional dependencies (if AI explanations are desired):

   ```bash
   pip install requests python-dotenv markdown tkhtmlview
   ```
4. Verify that the following files are present:

   * `aws_quiz_app.py`: Main application script
   * `aws_saa_questions_with_votes.json`: Question bank
   * `.env`: Environment file for API configuration (if using AI)

## Configuration

1. Create a `.env` file in the project root with the following variables:

   ```dotenv
   API_KEY=your_api_key_here
   API_URL=  # https://api.deerapi.com/v1/chat/completions
   LANGUAGE=your_preferred_language # EN
   MODEL=  #gpt-4o
   USE_AI=True
   ```
2. Ensure the file is included in `.gitignore` to protect your credentials.

## Usage

1. Run the application:

   ```bash
   python aws_quiz_app.py
   ```
2. On the main screen, select one of the three modes:

   * **In Order Mode**: Specify starting question and number of questions.
   * **Exam Mode**: Begin a full 60-question mock exam.
   * **Revision Mode**: Practice questions you previously answered incorrectly.
3. For each question, select an answer and click **Submit**.
4. If AI explanations are enabled and your answer is incorrect, a popup will provide detailed analysis.
5. Click **Next** to proceed to the following question.
6. After completing the session, review your results on the summary screen.

## License

This project is provided under the MIT License.

## Author

ik0nw
