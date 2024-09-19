# Investment_Account_API
A Django Rest Framework (DRF) API for managing investment accounts that allows more than one users to belong to an investment account it should also allow a user to belong to more than one investment account and set permissions for these Accounts. 
# Django Project Setup

This repository contains a  Django Rest Framework (DRF) API. This README will guide you through the setup process, provide an overview of the structure, and outline key features.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Getting Started](#getting-started)
   - [Prerequisites](#prerequisites)
   - [Installation](#installation)
3. [Running the Project](#running-the-project)
   - [Database Setup](#database-setup)
   - [Running Migrations](#running-migrations)
   - [Starting the Server](#starting-the-server)
4. [File Structure](#file-structure)
5. [Links to Important Files](#links-to-important-files)
6. [Contributing](#contributing)
7. [License](#license)

---

## Project Overview

The project uses Django 5.1.1 and various other dependencies listed in `requirements.txt`.

---

## Getting Started

### Prerequisites

Before running this project, ensure you have the following installed:

- Python 3.10 or higher
- Django (version specified in the `requirements.txt`)
- PostgreSQL or your database of choice

### Installation

Follow these steps to set up the project on your local machine:

1. Clone this repository:
   ```bash
   git clone https://github.com/marshvin/Investment_Account_API.git

2. Navigate to the project directory:
   ```bash
   cd Investment_Account_API

3. Create a virtual environment:
   ```bash
   python3 -m venv venv

4. Activate virtual environment:    
   ```bash
   source venv/bin/activate

5. Install required dependencies:
   ```bash
   pip install -r requirements.txt

### Running the Project

1. Database Setup
   ```bash
   createdb your-database-name

2. Update the settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your-database-name',
        'USER': 'your-username',
        'PASSWORD': 'your-password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

3. Running Migrations
   ```bash
   python manage.py migrate

4. Starting the Server
   ```bash
   python manage.py runserver

## File Structure

- **manage.py**: The entry point for running Django commands.
- **requirements.txt**: Lists all the dependencies for the project.
- **settings.py**: Contains the configuration of the project (in `api/settings/`).
- **urls.py**: Defines the URL routing for the app.
- **models.py**: Contains the database models.
- **views.py**: Handles the logic for rendering pages and processing requests.

---

## Links to Important Files

- [Requirements File](./requirements.txt): Contains the list of dependencies for the project.
- [Settings File](./api/settings.py): Django settings for database, middleware, etc.
- [Views](./api/views.py): Logic to handle requests and responses.
- [Models](./api/models.py): Defines the database models.
- [Permissions](./api/permissions.py): Defines the Different Account Permissions.
- [Tests](./api/tests.py): Test cases for testing the functionality of the API.

  
