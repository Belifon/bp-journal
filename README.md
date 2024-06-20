# bp-tracker

#### Video Demo: <URL HERE>

#### Description

Blood Pressure Tracker is a comprehensive web application designed to help users monitor and manage their blood pressure readings. Developed as the final project for Harvard's CS50x course, this application provides users with a simple interface to record, view, and analyze their blood pressure data over time. The project aims to empower users in their health journey by providing a place to record blood pressure recordings and educational resources on blood pressure management.


### Project Description


#### Purpose
The primary purpose of Blood Pressure Tracker is to offer users a reliable tool to track their blood pressure readings consistently. By logging their systolic and diastolic pressures along with pulse rate and notes, users can maintain a detailed history of their readings. This is particularly beneficial for individuals with hypertension or those who need to keep a close eye on their cardiovascular health.


#### Features
- **Track Your Progress**: Record systolic and diastolic blood pressure, pulse rate, notes, and the time of recording.
- **Insightful Analytics**: Visualize health trends to gain insights into blood pressure patterns with a user-friendly dashboard.
- **Educational Resources**: Access essential information on blood pressure management, including tips, articles, and guidelines.
- **Internalization**: The application supports multiple languages, currently English and Turkish, to cater to a diverse user base.


### Project Files

#### app.py
This is the main Python file that sets up the Flask application. It includes routes for handling user authentication, blood pressure recording, viewing history, displaying the dashboard, and more. The file also manages session handling, database interactions, and rendering templates.

Key routes and functionalities include:
- `/`: The home page, displaying a welcome message and an overview of the application.
- `/dashboard`: Displays the user's recent readings and average statistics, including converting times to the user's timezone.
- `/history`: Shows the complete history of blood pressure readings, with times converted to the user's timezone.
- `/login`: Handles user login, including session management and password verification.
- `/logout`: Logs the user out and clears the session.
- `/profile`: Allows users to update their profile information, including their name, timezone, and password.
- `/record`: Enables users to record new blood pressure readings.
- `/register`: Handles user registration, including validation and storing user credentials.
- `/resources`: Provides educational content on blood pressure management.

#### helpers.py
This file contains helper functions used throughout the application to manage common tasks and enhance code reusability.

Key functions include:
- `apology(message, code=400)`: Renders an apology message to the user with a specific error code.
- `classify_bp(systolic, diastolic)`: Classifies blood pressure readings into categories (Normal, Elevated, High1, High2, Crisis).
- `login_required(f)`: A decorator to enforce user authentication on specific routes, redirecting unauthenticated users to the login page.


#### layout.html
This HTML file defines the overall layout of the application, including the navigation bar, footer, and the structure for the pages. It uses Bootstrap for styling and ensures a consistent look across all pages.

#### en.json
This JSON file contains all the English language strings used in the application. It supports internationalization by allowing easy translation and modification of text displayed to the user.

#### tr.json
This JSON file contains all the Turkish language strings used in the application. It supports internationalization by allowing easy translation and modification of text displayed to the user.

#### templates/
This directory contains all HTML templates used by the Flask application. Each route in `app.py` renders a corresponding template:
- `index.html`: The home page template.
- `dashboard.html`: Displays the user's recent readings and average statistics.
- `history.html`: Shows the complete history of blood pressure readings.
- `login.html`: The login page template.
- `register.html`: The registration page template.
- `profile.html`: Allows users to update their profile information.
- `record.html`: The page for recording new blood pressure readings.
- `resources.html`: Provides educational content on blood pressure management.

### Design Choices


#### Reuse of CS50x Finance Project Components
This project builds upon the foundation laid by the CS50x finance project. Specifically:
- **Layout and CSS**: The layout and CSS styles from the finance project were adapted and extended to fit the needs of this application. Significant modifications were made to the `styles.css` file to improve the user interface and experience.
- **Login System**: The user authentication system, including session handling and password hashing, was reused and extended to include additional functionalities like changing the password, the name and timezone of the user.
- **Database Interaction**: The structure and methods for database interaction were adapted to suit the requirements of managing blood pressure data.


#### Database
The application uses SQLite3 for the database.

#### Internationalization
The application supports multiple languages by using JSON files to store language strings. This design choice allows for easy addition of new languages and ensures that the application can cater to a diverse user base.

#### User Authentication
User authentication is handled using Flask-Session for session management and Werkzeug for password hashing. This ensures that user data is secure and that only authenticated users can access their data.

#### Frontend Framework
Bootstrap is used for the frontend framework to provide a responsive and visually appealing design. It simplifies and ensures consistency across different pages and devices.

### Conclusion

Blood Pressure Tracker is a robust and user-friendly application designed to assist users in managing their blood pressure effectively. By providing tools for tracking, analyzing, and educating users about their blood pressure, this project aims to make a positive impact on users' health management routines. The detailed thought process behind each design choice ensures that the application is not only functional but also secure and easy to use.

With this README, I aim to provide a comprehensive overview of the project, its features, and the rationale behind key design decisions. I hope this application serves as a valuable tool for anyone looking to monitor and manage their blood pressure effectively.