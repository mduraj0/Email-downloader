# Email-downloader

Email Search and Attachment Downloader

# Description

This Python-based project connects to an email server and searches the mailbox for messages containing specific keywords. The application is configured using a YAML file, which allows the user to easily customize the search terms. If a message is found containing the desired text, the program automatically downloads the attachment from the message and saves it to disk. This project may be useful for individuals who receive a large volume of email attachments and want to automatically download and save them to a specified location


## Technologies
* Python 3.10+
* YAML

## Setup
* Clone this repository to your local machine
* Install required packages: `pip install -r requirements.txt`
* Update the config.yaml file with your email server information and desired search terms
* Run the application: python email_downloader.py
