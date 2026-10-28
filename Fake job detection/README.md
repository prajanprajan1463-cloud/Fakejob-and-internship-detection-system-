# JobSafeGuard — Fake Job & Internship Detection System

A full-stack cybersecurity web application designed to help students, recent graduates, and job seekers identify potentially fraudulent employment advertisements and internship scams. The system uses Natural Language Processing (NLP), rule-based detection, and risk scoring to highlight suspicious job postings.

Developed as a **BCA Final Year Capstone Project**.

## Core Features

- **Fake Job Detection**
  - Analyzes job descriptions for suspicious keywords and fraud indicators.
  - Identifies requests for registration fees, training fees, or equipment deposits.
  - Flags requests for sensitive information such as passwords, OTPs, and banking credentials.
  - Detects suspicious recruitment methods and unrealistic salary promises.

- **Risk Assessment**
  - Generates a risk score between 0 and 100.
  - Categorizes postings as lower risk, requiring verification, or potentially suspicious.
  - Highlights indicators that contributed to the result.
  - Provides guidance to help users evaluate job opportunities.

- **User Dashboard**
  - Allows users to submit job descriptions for analysis.
  - Displays analysis results and risk indicators.
  - Supports viewing previous analyses when persistent database storage is configured.

- **Authentication and Security**
  - User registration and login.
  - Password hashing.
  - Role-based access for candidates and administrators.
  - CSRF protection and server-side input validation.

- **Administrator Dashboard**
  - Provides administrative features for managing users and viewing analysis records, subject to the configured permissions and database.

## Technology Stack

| Component | Technology |
|---|---|
| Backend | Python, Flask |
| Frontend | HTML5, CSS3, JavaScript |
| Machine Learning | Scikit-learn |
| Text Processing | NLP and TF-IDF, if enabled |
| Database | SQLite or another configured database |
| Data Processing | Pandas, NumPy, if used |
| Model Storage | Joblib, if used |
| Version Control | Git and GitHub |
| Deployment | Vercel configuration, subject to compatibility |

## How the System Works

1. The user enters a job or internship description.
2. The application preprocesses the submitted text.
3. Detection rules identify potential fraud indicators.
4. If the machine-learning model is configured, it evaluates the text.
5. The system combines available signals to calculate a risk score.
6. The application displays the result and relevant warnings.
7. Users should independently verify employers before sharing money or sensitive information.

## Project Structure

The exact files depend on the version of the project uploaded to GitHub.

```text
Fake job detection/
├── app.py or run.py
├── requirements.txt
├── config.py
├── app/
├── ml/
├── templates/
├── static/
├── tests/
├── .env.example
├── .gitignore
└── README.md
```

Some folders may not exist in every version of the project.

## Installation on Windows

### 1. Clone the Repository

```powershell
git clone https://github.com/prajanprajan1463-cloud/Fake-job-and-internship-detection-system-.git
cd Fake-job-and-internship-detection-system-
```

Alternatively, open your existing project folder in VS Code.

### 2. Create a Virtual Environment

```powershell
python -m venv .venv
```

### 3. Activate the Environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### 4. Install Dependencies

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 5. Run the Application

Use the command appropriate for your project entry point.

For an application configured to run directly from `app.py`:

```powershell
python app.py
```

If your project uses `run.py`, follow its configured startup instructions instead.

Open the local URL shown in the terminal, commonly:

```text
http://127.0.0.1:5000
```

## Deployment

This project is intended for web deployment using a compatible Python hosting platform.

Before deploying:

1. Confirm that all required source files and model artifacts are uploaded to GitHub.
2. Confirm that `requirements.txt` includes the necessary dependencies.
3. Configure secret keys and other environment variables in the hosting dashboard.
4. Configure persistent database storage for user accounts and analysis history.
5. Verify that templates, static assets, authentication, and analysis routes work in the deployed environment.

Vercel supports Flask applications, but the entry point, static asset paths, and database configuration may need changes. A local SQLite database file should not be treated as persistent serverless storage.

## Privacy and Security

- Never commit `.env` files, passwords, API keys, or database credentials.
- Keep authentication and access-control checks enabled.
- Use HTTPS for the public website.
- Use a persistent database for user accounts and saved analyses.
- Do not submit confidential personal information in job descriptions.

## Limitations

This application is a screening aid, not a guarantee that a job is genuine or fraudulent. A high risk score indicates suspicious signals, not legal proof of fraud. Users should independently verify employers, company websites, recruiter identities, and job offers.

## License

This project is intended for academic and educational purposes. Add a `LICENSE` file if you choose to distribute it under a specific open-source license.
