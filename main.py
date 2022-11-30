import imaplib
import email
from email.header import decode_header
import yaml

with open('cfg.yaml', 'r') as file:
    credentials = yaml.safe_load(file)
    for credential in credentials['mails']:

        imap_server = imaplib.IMAP4_SSL(host=credential['server'])
        imap_server.login(user=credential['login'], password=credential['password'])
        imap_server.select('[Gmail]/Spam')
        message_id = imap_server.search(None, 'ALL')
        n = 1

        for message in message_id[1][0].split():
            _, message = imap_server.fetch(message, '(RFC822)')
            msg = email.message_from_bytes(message[0][1])
            subject, subject_encoding = decode_header(msg['Subject'])[0]
            if subject_encoding is not None:
                subject = subject.decode('utf-8')
            print(f'{subject} ---- EMAIL NR{n}')
            n += 1
