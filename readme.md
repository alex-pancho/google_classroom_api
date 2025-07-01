# Google Classroom API Automation

Partly based on [Diksha-Rathi/Google-Classroom-Scripts](https://github.com/Diksha-Rathi/Google-Classroom-Scripts)

A modular Python toolkit to help teachers automate everyday tasks on Google Classroom, such as managing courses, students, announcements, topics, and materials.  
This project provides reusable classes and functions for interacting with the Google Classroom API, with improved logging and extensibility.

## Features

- **Course management**: List, create, and select courses.
- **Student management**: Add students individually or in bulk from CSV/JSON, export student lists.
- **Content automation**: Post announcements, create topics, and upload materials.
- **Logging**: All actions and errors are logged to `google_class.log`.
- **Extensible**: Easily add new scripts or extend existing functionality.

## Setup

1. Install Python from [https://www.python.org/downloads/](https://www.python.org/downloads/)
2. Create a GCP project with the Classroom API enabled ([guide](https://developers.google.com/workspace/guides/create-project))
3. Download `client_secret.json` for desktop applications ([guide](https://developers.google.com/workspace/guides/create-credentials)) and place it in the project root.
4. (Optional) For Zoom integration, create a JWT app at [Zoom Marketplace](https://marketplace.zoom.us/develop/create) and note your API key and secret.
5. Install dependencies:  
   ```
   pip install -r requirements.txt
   ```

## Usage

Import and use the provided classes in your own scripts to automate Google Classroom tasks.  
See the `classroom_api.py` file for examples of available classes and methods:

- `Courses` – Manage and select courses by name or ID.
- `CoursesCreation` – Create new courses.
- `Students` – Add, list, and export students.
- `Content` – Post announcements, create topics, and upload materials.

## ToDo

- [ ] Add a web UI using Flask

## Contributing

Create an issue or pull request to discuss improvements or new features!

## References

- [Google Classroom API Quickstart](https://developers.google.com/classroom/quickstart/python)
- [Google Classroom API Reference](https://developers.google.com/classroom/reference/rest)
- [Google API Python Client](https://googleapis.github.io/google-api-python-client/docs/dyn/classroom_v1.courses.html)
- [Zoom API Create a Meeting Reference](https://developers.zoom.us/docs/api/meetings/#tag/meetings/POST/users/{userId}/meetings)