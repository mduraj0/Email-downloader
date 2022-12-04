import imaplib
import email
from email.header import decode_header
import yaml
import os
import click
import re


class Mail:
    def __init__(self, subject):
        self.subject = subject
        self.contents = []
        self.attachments = []


class MailBox:
    def __init__(self, server, login, password):
        self.server = server
        self.login = login
        self.password = password
        self.imap_server = None

    def connect(self):
        self.imap_server = imaplib.IMAP4_SSL(host=self.server)
        self.imap_server.login(user=self.login, password=self.password)
        self.imap_server.select('[Gmail]/Spam')

    def _get_emails_ids(self):
        message_ids = self.imap_server.search(None, 'ALL')
        return message_ids[1][0].split()

    def _parse_email(self, message):
        msg = email.message_from_bytes(message)
        subject, subject_encoding = decode_header(msg['Subject'])[0]
        if subject_encoding is not None:
            subject = subject.decode('utf-8')

        mail = Mail(subject)

        for part in msg.walk():
            if part.get_filename() is not None:
                mail.attachments.append(part)
            else:
                mail.contents.append(part)

        return mail

    def get_emails(self):
        mails = []
        for message_id in self._get_emails_ids():
            _, message = self.imap_server.fetch(message_id, '(RFC822)')
            mails.append(self._parse_email(message[0][1]))

        return mails


class Filter:
    def __init__(self, pattern, search_in_content, search_in_attachment_name):
        self.pattern = r'{}'.format(pattern)
        self.search_in_content = search_in_content
        self.search_in_attachment_name = search_in_attachment_name
        self._is_mail_ok = False
        self.email = None

    def _search_in_content(self, part):
        return True if re.search(self.pattern, part.as_string(), re.IGNORECASE) else False

    def _search_in_attachment_name(self, part):
        return part.get_filename() is not None and re.match(self.pattern, part.get_filename(), re.IGNORECASE)

    def check(self):
        if self.email is None:
            raise ValueError("email object is not set")

        if self.search_in_content:
            for part in self.email.contents:
                self._is_mail_ok = self._search_in_content(part)

        if self.search_in_attachment_name:
            for attachment in self.email.contents:
                self._is_mail_ok = self._search_in_attachment_name(attachment)

        return self._is_mail_ok


@click.command()
@click.option('--uploads-to', type=click.Path(), default='zalaczniki')
@click.option('--search', help='Patter no search in ...')
@click.option('--search-in-content', is_flag=True, help='Should I check content?')
@click.option('--search-in-attachment-name', is_flag=True, help='Should I check attachment name?')
def main(uploads_to, search, search_in_content, search_in_attachment_name):
    os.makedirs(uploads_to, exist_ok=True)

    choice = Filter(search, search_in_content, search_in_attachment_name)

    with open('cfg.yaml', 'r') as file:
        credentials = yaml.safe_load(file)

        for credential in credentials['mails']:
            mailbox = MailBox(**credential)
            mailbox.connect()

            for e_mail in mailbox.get_emails():
                choice.email = e_mail

                if choice.check():
                    with open(os.path.join(uploads_to, part.get_filename()), 'wb') as f:
                        f.write(part.get_payload(decode=True))
                        print(credential['login'], e_mail.subject)


if __name__ == '__main__':
    main()
