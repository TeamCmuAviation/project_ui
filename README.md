# Human Evaluation Tool

The Human Evaluation Tool is a Django-based web application designed to facilitate manual review and validaton of automated classification results for aviation safety reports (specifically mapping to ICAO accident/incident data reporting (ADREP) taxonomies).

This tool connects to a backend FastAPI service to retrieve evaluation tasks and submit human judgments.

## Features

- **Evaluator Authentication**: Simple access-code based login system for authorized evaluators.
- **Task Management**: Browse a list of all available classification results and select cases to evaluate.
- **Data Visualization**: Displays detailed origin data and automated classification results for review.
- **Evaluation Interface**: User-friendly form to submit:
  - Corrected ICAO Category (dropdown with descriptions)
  - Confidence Score
  - Reasoning/Justification
- **API Integration**: Seamless integration with an external FastAPI backend for data retrieval and submission.

## Prerequisites

- Python 3.8+
- A running instance of the backend FastAPI service (default expected at `http://localhost:58510`)

## Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd project_ui/human_eval_tool
    ```

2.  **Install Dependencies:**
    Since a `requirements.txt` is not provided, install the core dependencies manually:
    ```bash
    pip install django requests
    ```

## Configuration

The application is configured to communicate with a backend API. You can change the API base URL in `human_eval_project/settings.py`:

```python
# human_eval_project/settings.py

FASTAPI_BASE_URL = 'http://localhost:58510' # Update this port/url if your backend differs
```

## Database Setup

The project uses a local SQLite database by default. Run migrations to initialize it:

```bash
python manage.py migrate
```

## Running the Application

1.  **Start the Django development server:**
    ```bash
    python manage.py runserver
    ```

2.  **Access the application:**
    Open your browser and navigate to `http://127.0.0.1:8000/`.

## Usage

1.  **Login**: Enter your assigned **Access Code** on the login page.
    - **Available Codes**:
        - `BARAKA`
        - `RONNIE`
        - `NASIRU`
        - `JB`
2.  **Select Task**:
    - You will be redirected to the **Task List**.
    - Browse the table of classification results.
    - Click **Evaluate** on the specific case you wish to work on.
3.  **Evaluate**:
    - Review the "Origin Data" (Description, Title, etc.).
    - Select the appropriate **Human Category** from the dropdown.
    - Enter your **Confidence** score (0.0 - 1.0).
    - Provide a **Reasoning** for your decision.
    - Click **Submit Evaluation**.
    - You will be redirected back to the Task List.

## Project Structure

- `evaluation_app/`: Main application directory.
    - `models.py`: Database models.
    - `views.py`: Logic for login, fetching tasks, and submitting evaluations.
    - `templates/`: HTML templates for the UI.
- `human_eval_project/`: Project configuration settings.
- `manage.py`: Django command-line utility.
