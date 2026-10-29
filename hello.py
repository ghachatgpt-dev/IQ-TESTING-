import streamlit as st
import hashlib
import secrets
import random
from datetime import datetime

# ==========================================================
# SMART IQ PRACTICE & CAREER EXPLORER — STREAMLIT VERSION
#
# Demo app: accounts and quiz results live in session memory.
# They disappear when the session ends or the app restarts.
# This is a reasoning practice quiz, NOT a standardized IQ test.
# ==========================================================

st.set_page_config(
    page_title="Smart IQ Practice & Career Explorer",
    page_icon="🧠",
    layout="centered",
)

QUESTIONS = [
    {
        "question": "What number comes next: 2, 4, 6, 8, __?",
        "options": ["9", "10", "12", "14"],
        "answer": "10",
        "explanation": "The sequence increases by 2 each time.",
    },
    {
        "question": "Which item is different from the others?",
        "options": ["Apple", "Mango", "Carrot", "Orange"],
        "answer": "Carrot",
        "explanation": "Carrot is usually classified as a vegetable; the others are fruits.",
    },
    {
        "question": "If 5 + 3 = 8, what is 8 + 7?",
        "options": ["13", "14", "15", "16"],
        "answer": "15",
        "explanation": "8 + 7 = 15.",
    },
    {
        "question": "What letter comes next: A, C, E, G, __?",
        "options": ["H", "I", "J", "K"],
        "answer": "I",
        "explanation": "The sequence skips one letter each time: A, C, E, G, I.",
    },
    {
        "question": "A notebook costs ₦500. How much do 2 notebooks cost?",
        "options": ["₦750", "₦1,000", "₦1,200", "₦1,500"],
        "answer": "₦1,000",
        "explanation": "2 × ₦500 = ₦1,000.",
    },
    {
        "question": "Which shape has exactly three sides?",
        "options": ["Square", "Circle", "Triangle", "Rectangle"],
        "answer": "Triangle",
        "explanation": "A triangle has three sides.",
    },
    {
        "question": "If today is Monday, what day is tomorrow?",
        "options": ["Sunday", "Tuesday", "Wednesday", "Friday"],
        "answer": "Tuesday",
        "explanation": "Tuesday follows Monday.",
    },
    {
        "question": "Complete the pattern: 3, 6, 12, 24, __?",
        "options": ["30", "36", "42", "48"],
        "answer": "48",
        "explanation": "Each number is doubled to get the next number.",
    },
    {
        "question": "Which is the largest decimal number?",
        "options": ["0.5", "0.75", "0.25", "0.6"],
        "answer": "0.75",
        "explanation": "0.75 is greater than 0.5, 0.25, and 0.6.",
    },
    {
        "question": "All roses are flowers. Which statement follows from this?",
        "options": [
            "All flowers are roses",
            "Roses are flowers",
            "No roses are flowers",
            "All roses are trees",
        ],
        "answer": "Roses are flowers",
        "explanation": "This repeats the relationship given in the question.",
    },
]

CAREERS = {
    "Technology": [
        "Software Developer",
        "Cybersecurity Analyst",
        "Data Analyst",
        "Computer Engineer",
    ],
    "Science and Health": [
        "Scientist",
        "Medical Laboratory Scientist",
        "Environmental Scientist",
        "Public Health Professional",
    ],
    "Business": [
        "Entrepreneur",
        "Accountant",
        "Business Analyst",
        "Marketing Specialist",
    ],
    "Arts and Creativity": [
        "Graphic Designer",
        "Writer",
        "Animator",
        "Content Creator",
    ],
    "Helping People": [
        "Teacher",
        "Counsellor",
        "Social Worker",
        "Community Development Officer",
    ],
    "Engineering": [
        "Civil Engineer",
        "Electrical Engineer",
        "Mechanical Engineer",
        "Renewable Energy Engineer",
    ],
}

FUNNY_COMMENTS = [
    "Your brain has finished its shift. Please pay it in snacks!",
    "Even Google needs a moment to think sometimes. Keep going!",
    "Your brain deserves applause... and possibly a doughnut.",
    "Quiz complete! Your brain may now request a short holiday.",
    "Keep practising. Even superheroes started with beginner missions.",
    "Your neurons showed up today. That already beats a snooze button!",
]


def init_state():
    defaults = {
        "users": {},
        "current_user": None,
        "page": "auth",
        "auth_mode": "Login",
        "quiz_questions": [],
        "quiz_index": 0,
        "quiz_answers": [],
        "quiz_score": 0,
        "quiz_interest": "Technology",
        "last_result": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def password_digest(password: str, salt: bytes | None = None):
    if salt is None:
        salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, 200_000
    )
    return digest, salt


def register_user(full_name, username, password, confirmation):
    full_name = full_name.strip()
    username = username.strip().lower()

    if not full_name or not username or not password or not confirmation:
        return False, "Please complete every field."
    if len(username) < 3 or any(ch.isspace() for ch in username):
        return False, "Username must be at least 3 characters and contain no spaces."
    if len(password) < 6:
        return False, "Password must contain at least 6 characters."
    if password != confirmation:
        return False, "The passwords do not match."
    if username in st.session_state.users:
        return False, "That username is already registered."

    digest, salt = password_digest(password)
    st.session_state.users[username] = {
        "full_name": full_name,
        "password_hash": digest,
        "salt": salt,
        "results": [],
    }
    return True, "Account created. You can now log in."


def login_user(username, password):
    username = username.strip().lower()
    account = st.session_state.users.get(username)
    if account is None:
        return False
    candidate_hash, _ = password_digest(password, account["salt"])
    if not secrets.compare_digest(candidate_hash, account["password_hash"]):
        return False
    st.session_state.current_user = username
    st.session_state.page = "dashboard"
    return True


def start_quiz():
    st.session_state.quiz_questions = random.sample(QUESTIONS, len(QUESTIONS))
    st.session_state.quiz_index = 0
    st.session_state.quiz_answers = []
    st.session_state.quiz_score = 0
    st.session_state.last_result = None
    st.session_state.page = "quiz"


def finish_quiz():
    total = len(st.session_state.quiz_questions)
    score = st.session_state.quiz_score
    percentage = round((score / total) * 100)
    interest = st.session_state.quiz_interest
    result = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "score": score,
        "total": total,
        "percentage": percentage,
        "interest": interest,
        "careers": CAREERS[interest].copy(),
        "answers": st.session_state.quiz_answers.copy(),
        "funny_comment": random.choice(FUNNY_COMMENTS),
    }
    st.session_state.users[st.session_state.current_user]["results"].append(result)
    st.session_state.last_result = result
    st.session_state.page = "results"


def render_auth():
    st.title("🧠 Smart IQ Practice & Career Explorer")
    st.write("Create an account or log in to practise reasoning and explore careers.")
    st.info(
        "Demo storage: accounts and results exist only during the current session. "
        "They may disappear when the session ends or the app restarts."
    )

    mode = st.radio(
        "Choose an option",
        ["Login", "Register"],
        horizontal=True,
        key="auth_mode",
    )

    if mode == "Register":
        with st.form("register_form"):
            full_name = st.text_input("Full name")
            username = st.text_input("Username (at least 3 characters)")
            password = st.text_input("Password (at least 6 characters)", type="password")
            confirmation = st.text_input("Confirm password", type="password")
            submitted = st.form_submit_button("Create account", use_container_width=True)

        if submitted:
            success, message = register_user(full_name, username, password, confirmation)
            if success:
                st.success(message)
                st.session_state.auth_mode = "Login"
                st.rerun()
            else:
                st.error(message)
    else:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Log in", use_container_width=True)

        if submitted:
            if login_user(username, password):
                st.rerun()
            else:
                st.error("Login failed. Check your username and password, or register first.")


def render_dashboard():
    username = st.session_state.current_user
    account = st.session_state.users[username]
    st.title(f"👋 Welcome, {account['full_name']}!")
    st.write("Your student dashboard")
    st.metric("Quiz attempts this session", len(account["results"]))

    st.subheader("Choose your main career interest")
    interest = st.selectbox(
        "Your interest",
        list(CAREERS.keys()),
        index=list(CAREERS.keys()).index(st.session_state.quiz_interest),
    )
    st.session_state.quiz_interest = interest

    st.caption("Career ideas are based on your chosen interest, not your quiz score.")
    left, right = st.columns(2)
    with left:
        if st.button("🚀 Start reasoning quiz", use_container_width=True):
            start_quiz()
            st.rerun()
    with right:
        if st.button("📚 View previous results", use_container_width=True):
            st.session_state.page = "history"
            st.rerun()

    if st.button("Log out"):
        st.session_state.current_user = None
        st.session_state.page = "auth"
        st.session_state.auth_mode = "Login"
        st.rerun()


def render_quiz():
    questions = st.session_state.quiz_questions
    index = st.session_state.quiz_index
    question = questions[index]
    total = len(questions)

    st.title("🧩 Reasoning Practice Quiz")
    st.progress((index + 1) / total, text=f"Question {index + 1} of {total}")
    st.subheader(question["question"])

    answer = st.radio(
        "Choose one answer:",
        question["options"],
        index=None,
        key=f"answer_{index}",
    )

    if st.button("Submit answer", type="primary", use_container_width=True):
        if answer is None:
            st.warning("Please choose an answer before continuing.")
        else:
            is_correct = answer == question["answer"]
            if is_correct:
                st.session_state.quiz_score += 1

            st.session_state.quiz_answers.append({
                "question": question["question"],
                "chosen": answer,
                "correct": question["answer"],
                "is_correct": is_correct,
                "explanation": question["explanation"],
            })

            if index < total - 1:
                st.session_state.quiz_index += 1
                st.rerun()
            else:
                finish_quiz()
                st.rerun()

    if st.button("Cancel quiz"):
        st.session_state.page = "dashboard"
        st.rerun()


def render_results():
    result = st.session_state.last_result
    if not result:
        st.session_state.page = "dashboard"
        st.rerun()
        return

    percentage = result["percentage"]
    if percentage >= 80:
        level = "Excellent practice performance"
        advice = "Try more challenging puzzles and keep developing your skills."
    elif percentage >= 60:
        level = "Good practice performance"
        advice = "You have a useful foundation. Keep practising."
    elif percentage >= 40:
        level = "Developing your reasoning skills"
        advice = "Review the explanations and try another round."
    else:
        level = "A chance to learn and improve"
        advice = "Mistakes are part of learning. Practise and try again."

    st.title("🎉 Your Results")
    col1, col2 = st.columns(2)
    col1.metric("Correct answers", f"{result['score']} / {result['total']}")
    col2.metric("Practice score", f"{percentage}%")
    st.subheader(level)
    st.write(advice)

    st.subheader(f"💼 Career ideas: {result['interest']}")
    for career in result["careers"]:
        st.write(f"- {career}")

    st.info(f"😂 **Funny comment:** {result['funny_comment']}")
    st.warning(
        "This is a reasoning practice score, not an IQ score. It is not a "
        "standardized or clinically validated assessment. Explore careers using "
        "your interests, school subjects, skills, and goals too."
    )

    with st.expander("Review answers and explanations"):
        for number, answer in enumerate(result["answers"], start=1):
            st.markdown(f"**{number}. {answer['question']}**")
            st.write(f"Your answer: {answer['chosen']}")
            st.write(f"Correct answer: {answer['correct']}")
            st.write("✅ Correct" if answer["is_correct"] else "❌ Not correct")
            st.caption(answer["explanation"])
            st.divider()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Try again", use_container_width=True):
            start_quiz()
            st.rerun()
    with col2:
        if st.button("Back to dashboard", use_container_width=True):
            st.session_state.page = "dashboard"
            st.rerun()


def render_history():
    username = st.session_state.current_user
    results = st.session_state.users[username]["results"]
    st.title("📚 Previous Results")

    if not results:
        st.info("No results saved yet. Complete a quiz to see your history.")
    else:
        for i, result in enumerate(reversed(results), start=1):
            label = (
                f"{result['date']} — {result['score']}/{result['total']} "
                f"({result['percentage']}%) — {result['interest']}"
            )
            with st.expander(label):
                st.write(f"Practice score: **{result['percentage']}%**")
                st.write(f"Career interest: **{result['interest']}**")
                st.write("Career ideas: " + ", ".join(result["careers"]))
                for number, answer in enumerate(result["answers"], start=1):
                    st.markdown(f"**{number}. {answer['question']}**")
                    st.write(f"Your answer: {answer['chosen']}")
                    st.write(f"Correct answer: {answer['correct']}")
                    st.write("✅ Correct" if answer["is_correct"] else "❌ Not correct")
                    st.caption(answer["explanation"])

    if st.button("Back to dashboard"):
        st.session_state.page = "dashboard"
        st.rerun()


def main():
    init_state()

    with st.sidebar:
        st.header("🧠 IQ Career Explorer")
        st.caption("Reasoning practice and career exploration")
        if st.session_state.current_user:
            st.write(f"Logged in as: **{st.session_state.current_user}**")
            if st.button("Dashboard", use_container_width=True):
                st.session_state.page = "dashboard"
                st.rerun()
            if st.button("Previous results", use_container_width=True):
                st.session_state.page = "history"
                st.rerun()
            if st.button("Log out", use_container_width=True):
                st.session_state.current_user = None
                st.session_state.page = "auth"
                st.session_state.auth_mode = "Login"
                st.rerun()

    page = st.session_state.page
    if page == "auth" or not st.session_state.current_user:
        render_auth()
    elif page == "dashboard":
        render_dashboard()
    elif page == "quiz":
        render_quiz()
    elif page == "results":
        render_results()
    elif page == "history":
        render_history()
    else:
        st.session_state.page = "dashboard"
        st.rerun()


if __name__ == "__main__":
    main()
