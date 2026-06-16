# Human Evaluation Tool

The Human Evaluation Tool is a Django-based web application designed to facilitate manual review and validaton of automated classification results for aviation safety reports (specifically mapping to ICAO accident/incident data reporting (ADREP) taxonomies).

This tool connects to a backend FastAPI service to retrieve evaluation tasks and submit human judgments.

## Features

- **Evaluator Authentication**: Google OAuth login for authorized evaluators, with legacy access-code login available as a local fallback.
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
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

The application is configured through environment variables:

- `SECRET_KEY`: Django secret key. Set this in any non-local environment.
- `DEBUG`: `1`/`true` for development, `0`/`false` for production.
- `ALLOWED_HOSTS`: comma-separated hostnames, for example `localhost,127.0.0.1`.
- `FASTAPI_BASE_URL`: backend API URL, default `http://localhost:58510`.
- `GOOGLE_CLIENT_ID`: Google OAuth client ID.
- `GOOGLE_CLIENT_SECRET`: Google OAuth client secret.
- `GOOGLE_ALLOWED_DOMAINS`: optional comma-separated allowlist, for example `example.org`.
- `GOOGLE_EVALUATOR_MAP`: optional email-to-evaluator mapping, for example `person@example.org:RONNIE,other@example.org:JB`.

If `GOOGLE_EVALUATOR_MAP` does not contain a signed-in email, the evaluator ID defaults to the email local-part in uppercase. For example, `ronnie@example.org` becomes `RONNIE`.

Configure the Google OAuth redirect URI as:

```text
http://localhost:8000/accounts/google/login/callback/
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

1.  **Login**: Sign in with your authorized Google account. The access-code form remains available for local fallback use.
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

## Docker Deployment

This project includes Docker support for easy deployment.

### Prerequisites
- Docker Desktop installed and running.

### Running with Docker Compose

1.  **Build and Run:**
    ```bash
    docker-compose up --build
    ```
    This command will build the Docker image and start the container on port `8000`.

2.  **Access the Application:**
    Navigate to [http://localhost:8000](http://localhost:8000) in your browser.

3.  **Stopping the Container:**
    Press `Ctrl+C` in the terminal or run:
    ```bash
    docker-compose down
    ```

### Environment Variables

The `docker-compose.yml` file sets the following environment variables:
- `DEBUG=1`: Enables Django debug mode.
- `FASTAPI_BASE_URL=http://host.docker.internal:58510`: Points to the backend API running on the host machine. If your API is running elsewhere, update this value in `docker-compose.yml`.
- `GOOGLE_CLIENT_ID` and `GOOGLE_CLIENT_SECRET`: Enable Google OAuth login.
