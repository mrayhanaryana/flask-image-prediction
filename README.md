# flask-image-prediction

Simple Website to Predict image from User

## Pre-requisites

Before you begin, ensure that you have the following installed:

- Python (recommended version: Python 3.x)
- `virtualenv` package

## Setup Instructions

1. Install `virtualenv` package:

    ```bash
    pip install virtualenv
    ```

2. Clone this repository:

    ```bash
    git clone <repo-url>
    ```

3. Change directory to the cloned repository:

    ```bash
    cd flask-image-prediction
    ```

4. Create a virtual environment:

    ```bash
    virtualenv env
    ```

5. Activate the virtual environment:

    ```bash
    env\Scripts\activate
    ```

6. Install the dependencies:

    ```bash
    pip install -r requirements.txt
    ```

7. Copy data.json.example to data.json:

    ```bash
    cp data.json.example data.json
    ```

8. Create dump directory:

    ```bash
   mkdir dump
    ```

9. Run the application:

    ```bash
    python app.py
    ```
