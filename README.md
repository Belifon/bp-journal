# bp-tracker

#### Video Demo: <URL HERE>

### Description

Blood Pressure Tracker is a web application designed to help users monitor and manage their blood pressure readings. Developed as the final project for Harvard's CS50x course, this application provides users with a simple interface to record, view, and analyze their blood pressure data over time.

### Features

- **Track Your Progress**: Record systolic and diastolic blood pressure, pulse rate, notes, and the time of recording.
- **Insightful Analytics**: View categorized blood pressure readings (e.g., Normal, Elevated, High) for better understanding and management of blood pressure patterns.
- **Educational Resources**: Access essential information on blood pressure management, including tips, articles, and guidelines.
- **Internalization**: The application supports multiple languages, currently English and Turkish, to cater to a diverse user base.
- **Timezone Localization**: Automatically converts and displays times based on the user's timezone for accurate and personalized tracking. 

### Usage

1. Register or log in to your account.
2. Record new blood pressure readings through the 'Record Readings' module in the navigation bar.
3. View and analyze your blood pressure trends in the dashboard.
4. Access educational resources for better blood pressure management.

### Installation

1. Clone the repository:
    ```bash
    $ git clone https://github.com/Belifon/bp-tracker.git
    ```
2. Install the necessary dependencies:
    ```bash
    $ pip install -r requirements.txt
    ```
3. Run the application:
    ```bash
    $ flask run
    ```

### Project Files

- **app.py**: The main Python file that sets up the Flask application. Handles routes, user authentication, blood pressure recording, viewing history, session handling, database interactions and more.
- **helpers.py**: Contains helper functions used throughout the application to manage common tasks and enhance code reusability.
- **layout.html**: Defines the overall layout of the application using Bootstrap for styling.
- **en.json** and **tr.json**: JSON files containing language strings for English and Turkish.
-- **templates/**: Directory containing HTML templates for different pages like index, dashboard, history, login, register, profile, record, and resources.

### Key Routes

- `/`: Home page with a welcome message and an overview of the application.
- `/dashboard`: Displays the user's recent readings and average statistics.
- `/history`: Shows the complete history of blood pressure readings.
- `/login`: Handles user login.
- `/logout`: Logs the user out and clears the session.
- `/profile`: Allows users to update their profile information, including their name, timezone, and password.
- `/record`: Enables users to record new blood pressure readings.
- `/register`: Handles user registration.
- `/resources`: Provides educational content on blood pressure management.


### Design Choices


- **Reuse of CS50x Finance Project Components**: Adapted and extended layout, CSS, login system, and database interaction from CS50x finance project.
- **Database**: Utilizes SQLite for managing blood pressure data.
**Internationalization**: Supports multiple languages through JSON files.
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