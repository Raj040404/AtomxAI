# AtomXAI
AtomXAI is a machine learning-based exam proctoring system using TensorFlow. It monitors students during online exams, detecting suspicious activities like multiple faces, mobile phones, and browser/tab switching. The system locks the browser, logs events, and provides teachers with real-time insights and detailed logs for exam integrity.

## 👨‍🏫 Target Audience
AtomXAI is primarily designed for teachers or educators who need to conduct secure, proctored online exams. Instead of directly providing students with a Google Form link to an exam, AtomXAI allows teachers to create exam rooms on the platform, much like setting up an MCQ-based Google Form exam. Teachers can securely manage their exams, ensuring academic integrity.


## 🚀 Features

- **Real-Time Monitoring**: Uses machine learning models for continuous monitoring during online exams.
- **Face Detection**: Detects faces to ensure the student is present throughout the exam.
- **Suspicious Behavior Detection**: Identifies multiple people in the frame, unauthorized devices (e.g., mobile phones), or any abnormal activity.
- **Tab-Switching Detection**: Logs attempts to switch tabs or exit the exam page.
- **Teacher Dashboard**: Teachers can create and manage exam rooms, track student progress, and view detailed activity logs.
- **Secure Exam Environment**: Locks the browser to prevent cheating and ensures that the student cannot access any external resources during the exam.

## 📋 Prerequisites

Before you begin, make sure you have the following installed:

- Python 3.x
- Django 5.1.1 (or as specified in `requirements.txt`)

## ⚙️ Installation

Follow these steps to set up the project on your local machine:

1. **Clone the repository**:
    ```bash
    git clone https://github.com/nayan2soni/AtomXAI.git
    ```

2. **Navigate to the project directory**:
    ```bash
    cd AtomXAI
    ```

3. **Set up a virtual environment (optional but recommended)**:
    ```bash
    python -m venv .venv
    ```

4. **Activate the virtual environment**:

    **For Windows**:
    ```bash
    .venv\Scripts\activate
    ```

    **For macOS/Linux**:
    ```bash
    source .venv/bin/activate
    ```

5. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

6. **Run the development server**:
    ```bash
    python manage.py runserver
    ```

**The application should now be running at [http://127.0.0.1:8000/](http://127.0.0.1:8000/).**

## 📂 Project Structure

**Here's a quick overview of the main directories and files in the project:**

- AtomXAI/: Contains the main Django application.
- monitoring/: Contains the files related to exam proctoring.
- users/: Contains the files related to user login and signup.
- static/: Contains static files like images, CSS, and JavaScript used in the project.
- templates/: Includes HTML templates for the front-end UI.
- requirements.txt: Lists the Python dependencies for the project.

## 🎮 Usage

1. **Teacher Login: Log in to create exam rooms.**
2. **Create Exam Room: Provide a Google Form link to generate a unique exam room for students.**
3. **Student Join: Students can join the exam by entering their details, exam code and starting the test.**
4. **Real-Time Monitoring: The system will monitor student activity, including face detection, suspicious behavior, and tab-switching.**
5. **Activity Logs: Teachers can view detailed logs of student activities created during exam**

## 🤝 Contributing

**We welcome contributions to improve the AtomXAI project! Here's how you can contribute:**

**Areas That Need Help:**
- AI Features: Although the system uses TensorFlow models for face detection and suspicious behavior detection, additional machine learning models or features like gaze tracking or anomaly detection could be added. Contributions are welcome in this area.
- Front-End UI: We are still working on improving the user interface for both the student and teacher dashboards. If you're skilled in front-end development, your help would be appreciated.
- Testing and Debugging: We need help with testing different functionalities and ensuring the system works across multiple environments. Bug fixes and edge cases are crucial.
- Documentation: If you have ideas for enhancing documentation or would like to improve the README or code comments, feel free to contribute.
- Create MCQ Exam Feature

**If you’d like to contribute to any of these areas, feel free to fork the repository and submit a pull request.**

## 📞 Contact
Feel free to reach out to me via LinkedIn. [LinkedIn](https://www.linkedin.com/in/adityajadhav24/)

## 🔖 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
