# bp-tracker

#### Video Demo: <URL HERE>

### Description

BP Tracker is a web application designed to help users track their blood pressure readings over time. Developed as the final project for Harvard's CS50x course, the platform allows users to log in, record their bp readings, view their history, and manage their profiles. The application supports multiple languages (Turkish and English) and handles time zone conversions for accurate logging of readings.

### Features

- User authentication and session management
- Blood pressure recording and classification
- Viewing and editing blood pressure history
- User profile management, including name, timezone and password updates
- Language support (Turkish and English)
- Secure password hashing
- Time zone handling for accurate time stamping
- Tips, articles and guidelines on blood pressure management 

### Usage

1. Register or log in to your account.
2. Record new blood pressure readings through the 'Record Readings' module in the navigation bar.
3. View and analyze your blood pressure trends in the dashboard.
4. View and edit full history of blood pressure recordings.
5. Access educational resources for better blood pressure management.
6. Update profile information like name, timezone and password

### Prerequisites

Before you can run this application, you need to have the following installed on your system:

- Python 3.6+
- Flask
- SQLite

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/Belifon/bp-tracker.git
    cd bp-tracker
    ```
2. Create and activate a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```
2. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```
2. Set up the database:
    ```bash
    flask db init
    flask db migrate -m "Initial migration."
    flask db upgrade
    ```
3. Run the application:
    ```bash
    flask run
    ```

### Project Files

- **app.py**: The main Python file that sets up the Flask application. Handles routes, loading language data, user authentication, recording and editing blood pressure, viewing history, timezone conversion, updating user information, session handling, database interactions and more.
- **helpers.py**: Contains helper functions used throughout the application to enhance code reusability and manage common tasks like displaying error messages, classifying blood pressure, etc.
- **layout.html**: Defines the overall layout of the application using Bootstrap for styling.
- **en.json** and **tr.json**: JSON files containing language strings for English and Turkish.
-- **templates/**: Directory containing HTML templates for different pages like apology, dashboard, edit, history, index, login, profile, record, register, and resources.

### Key Routes

- `/`: Home page with a welcome message and an overview of the application.
- `/dashboard`: Displays the user's recent readings and average statistics.
- `/history`: Shows the complete history of blood pressure readings.
- `/login`: Handles user login.
- `/profile`: Allows users to update their profile information, including their name, timezone, and password.
- `/record`: Enables users to record new blood pressure readings.
- `/register`: Handles user registration.
- `/resources`: Provides educational content on blood pressure management.


### Design Choices


- **Reuse of CS50x Finance Project Components**: Adapted and extended layout, Bootstrap choices and login system from CS50x finance project.
- **Database**: Utilizes SQLite for managing blood pressure data.
- **Internationalization**: Supports multiple languages through JSON files.
- **User Authentication**: Ensures security using Flask-Session for session management and Werkzeug for password hashing.
- **Frontend Framework**: Uses Bootstrap for a responsive and visually appealing design.


### Contributing
1. Clone the repo and create a new branch:
    ```bash
    $ git checkout -b name_for_new_branch
    ```
2. Make changes and test.
3. Submit a pull request with a comprehensive description of changes.

### Acknowledgements

I would like to extend my heartfelt gratitude to David J. Malan for his exceptional lecturing. Special thanks to the entire CS50x team and EdX for making this invaluable course accessible and beginner-friendly. 

This project marks my first development endeavor from start to finish, and I am incredibly proud of the outcome. Transforming my understanding from basic concepts to a fully functional application has been an extraordinary journey.

### Summary

Blood Pressure Tracker is a robust and user-friendly application designed to assist users in managing their blood pressure effectively. By providing tools for tracking, analyzing, and educating users about their blood pressure, this project aims to make a positive impact on users' health management routines. The detailed thought process behind each design choice ensures that the application is not only functional but also secure and easy to use. 