[![Quality Gate Status](http://216.80.104.71:9005/api/project_badges/measure?project=rapheeBeauty&metric=alert_status&token=sqb_48233a0fe21452f98719d27faff796868cdd721d)](http://216.80.104.71:9005/dashboard?id=rapheeBeauty)
[![Security Rating](http://216.80.104.71:9005/api/project_badges/measure?project=rapheeBeauty&metric=security_rating&token=sqb_48233a0fe21452f98719d27faff796868cdd721d)](http://216.80.104.71:9005/dashboard?id=rapheeBeauty)
[![Bugs](http://216.80.104.71:9005/api/project_badges/measure?project=rapheeBeauty&metric=bugs&token=sqb_48233a0fe21452f98719d27faff796868cdd721d)](http://216.80.104.71:9005/dashboard?id=rapheeBeauty)
[![Technical Debt](http://216.80.104.71:9005/api/project_badges/measure?project=rapheeBeauty&metric=sqale_index&token=sqb_48233a0fe21452f98719d27faff796868cdd721d)](http://216.80.104.71:9005/dashboard?id=rapheeBeauty)<br>
Dev Branch: 
![dev branch](https://github.com/AfriTech-DevOps/RapheeBeauty/actions/workflows/rapheebeauty_cicd.yaml/badge.svg?branch=dev)<br>
QA Branch:
![qa branch](https://github.com/AfriTech-DevOps/RapheeBeauty/actions/workflows/rapheebeauty_cicd.yaml/badge.svg?branch=qa)<br>
Prod Branch:
![prod branch](https://github.com/AfriTech-DevOps/RapheeBeauty/actions/workflows/rapheebeauty_cicd.yaml/badge.svg?branch=prod)
# RapheeBeauty

This is an ecommerce website for Rahpee Beauty, a beauty product seller partnered with Oriflame. This website is built using Flask, a Python web framework, and MySQL database.

### Prerequisites

- Python 3.6 or higher
- Docker

### Installing

1. Clone this repository
 ```bash
 git clone https://github.com/AfriTech-DevOps/rapheeBeauty.git
 ```
2. Create a virtual environment
 ```bash
    python3 -m venv venv
```

3. Activate the virtual environment
    - Windows
        ```bash
            venv\Scripts\activate
        ```
    - Linux / MacOS
        ```bash
            source venv/bin/activate
        ```
4. Install the dependencies
    ```bash
        pip install -r requirements.txt --no-cache-dir
    ```
5. Create a `.env` file in the root directory and add the following environment variables
    ```bash
        FLASK_APP=run.py
        FLASK_ENV=development
        FLASK_DEBUG=1
        SECRET_KEY=your_secret_key
        SQLALCHEMY_DATABASE_URI=your_database_uri
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    ```
6. Run the application locally using the command
    ```bash
        flask run
    ```
7. Building the docker image
    - For development
        ```bash
            git checkout dev
            docker build -t raphee-beauty:dev  .
        ``` 
    - For QA/Testing
        ```bash
            git checkout qa
            docker build -t raphee-beauty:qa  .
        ```
    - For Production
        ```bash
            git checkout master
            docker build -t raphee-beauty:prod  .
        ```
8. Running the docker container
    - For development
        ```bash
            docker run -d -p 5000:5000 raphee-beauty:dev
        ``` 
    - For QA/Testing
        ```bash
            docker run -d -p 5000:5000 raphee-beauty:qa
        ```
    - For Production
        ```bash
            docker run -d -p 5000:5000 raphee-beauty:prod
        ```
9. Access the application on `http://localhost:5000`

## BRANCE GUIDELINES
- Devlopment: Utilize the `dev` branch for development. This branch is protected and requires a pull request to merge into it. This is used for ongoing development work.
- QA: Utilize the `qa` branch for QA/Testing. This branch is protected and requires a pull request to merge into it. This is used to test and validate changes before merging into the `master` or `production` branch.
- Production: Utilize the `master` branch for production. This branch is protected and requires a pull request to merge into it. This is used for production ready code.