import imaplib
import email
import json
import shutil
from email.header import decode_header
import webbrowser
import os
import string
import enum
from googleapiclient.discovery import build
from google.oauth2 import service_account
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.message import EmailMessage
import html
import re
from database import queryData
import pathlib
import os.path
from os import path
from os import listdir
from os.path import isfile, join


class issueType(enum.Enum):
    accountIssue = 0
    paymentIssue = 1
    refundIssue = 2
    checkoutIssue = 3
    scanIssue = 4
    merchantIssue = 5
    bookingIssue = 6
    gymswimbookingIssue = 7
    swimsaferIssue = 8
    receiptIssue = 9

def clean(text):
    # clean text for creating a folder
    return "".join(c if c.isalnum() else "_" for c in text)

def extractEmail():
    # account credentials
    # username = input("Email: ")
    # password = input("Password: ")
    with open('user.json', 'r') as f:
        user_token = json.load(f)
    username = user_token['username']
    password = user_token['password']

    # create an IMAP4 class with SSL, use your email provider's IMAP server
    imap = imaplib.IMAP4_SSL("imap.gmail.com")
    # authenticates
    try:
        imap.login(username, password)
    except:
        print("Invalid email or password. Please run the program again.")
        exit()

    # select a mailbox (in this case, the inbox mailbox)
    # use imap.list() to get the list of mailboxes
    imap.select("testing")
    (retcode, messages) = imap.search(None, '(UNSEEN)')

    spreadsheetInputs = []
    caseidPattern = 'CASE:(\d+)'
    for i in messages[0].split():
        currentInput = []
        caseID = ""
        finalBodyMessage = ""
        bodyText = ""
        subjectText = ""
        folderPath = ""
        emailWithAttachment = 0
        # fetch the email message by ID
        res, msg = imap.fetch(i, "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                # parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])
                # raw_email_string = msg[0][1].decode('utf-8')
                # email_message = email.message_from_string(raw_email_string)
                # decode the email subject
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    # if it's a bytes, decode to str
                    subject = subject.decode(encoding)
                # decode email sender
                From, encoding = decode_header(msg.get("From"))[0]
                if isinstance(From, bytes):
                    From = From.decode(encoding)
                currentInput.append(From)
                subjectText = subject.replace("\r", "").replace("\n", "")
                currentInput.append(subjectText)
                # caseID = re.findall(caseidPattern, subjectText)
                # inDatabase = queryData(str("".join(caseID)))
                # if (inDatabase == False):
                # if the email message is multipart
                if msg.is_multipart():
                    # iterate over email parts
                    for part in msg.walk():
                        # extract content type of email
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        try:
                            # get the email body
                            body = part.get_payload(decode=True).decode()
                        except:
                            pass
                        if content_type == "text/plain" and ("attachment" or "inline") not in content_disposition:
                            # print text/plain emails and skip attachments
                            bodyText = body
                            print(type(body))
                            print(body)
                        elif ("attachment" in content_disposition) or ("inline" in content_disposition):
                            emailWithAttachment = 1
                            # download attachment and inline img
                            filename = part.get_filename()
                            if filename:
                                folder_name = clean(subject)
                                if not os.path.isdir(folder_name):
                                    # make a folder for this email (named after the subject)
                                    os.mkdir(folder_name)
                                    absolutePath = pathlib.Path(__file__).parent.absolute()
                                    folderPath = os.path.join(absolutePath, folder_name)
                                filepath = os.path.join(folder_name, filename)
                                # download attachment and save it
                                open(filepath, "wb").write(part.get_payload(decode=True))
                else:
                    # extract content type of email
                    content_type = msg.get_content_type()
                    # get the email body
                    body = msg.get_payload(decode=True).decode()
                    if content_type == "text/plain":
                        bodyText = body
                        print(type(body))
                        print(body)
                    # processBodyMessage(bodyText)

                if content_type == "text/html":
                    # if it's HTML, create a new HTML file and open it in browser
                    folder_name = clean(subject)
                    if not os.path.isdir(folder_name):
                        # make a folder for this email (named after the subject)
                        os.mkdir(folder_name)
                        absolutePath = pathlib.Path(__file__).parent.absolute()
                        folderPath = os.path.join(absolutePath, folder_name)
                    filename = "index.html"
                    filepath = os.path.join(folder_name, filename)
                    # write the file
                    open(filepath, "w").write(body)

                msg = MIMEMultipart()
                msg['From'] = username
                msg['To'] = "samuel@iappsasia.com"
                msg['Subject'] = subjectText
                msg.attach(MIMEText(body, 'html'))
                if emailWithAttachment == 1:
                    for file in listdir(folderPath):
                        with open(os.path.join(folderPath, file), 'rb') as f:
                            file_data = f.read()
                            file_name = f.name
                        # instance of MIMEBase and named as p
                        p = MIMEBase('application', 'octet-stream')
                        # To change the payload into encoded form
                        p.set_payload(file_data)
                        encoders.encode_base64(p)
                        p.add_header('Content-Disposition', "attachment; filename= %s" % file)
                        msg.attach(p)
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    smtp.login(username, password)
                    smtp.send_message(msg)
        # Delete folder containing current attachments
        shutil.rmtree(folderPath)
            # Email from developer side (Phase 3)
            # else:
            #     if From == "erik@iappsasia.com" or "jianchuan@iappsasia.com":
                    # Forward email to helpdesk
                    # msg = EmailMessage()
                    # msg['Subject'] = subjectText
                    # msg['From'] = username
                    # msg['To'] = "helpme@iappsasia.com"
                    # msg.set_content(bodyText)
                    # with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    #     smtp.login(username, password)
                    #     smtp.send_message(msg)

    # close the connection and logout
    imap.close()
    imap.logout()

# def updateGooglesheet():
#     SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
#     SERVICE_ACCOUNT_FILE = 'credentials.json'
#     creds = None
#     creds = service_account.Credentials.from_service_account_file(
#             SERVICE_ACCOUNT_FILE, scopes=SCOPES)
#
#     # The ID spreadsheet.
#     SAMPLE_SPREADSHEET_ID = '1mz4_KQxdGBoY8XqslY9q45LrqKUdmyUjrxEtN7fB1BI'
#
#     service = build('sheets', 'v4', credentials=creds)
#
#     # Call the Sheets API
#     sheet = service.spreadsheets()
#     # result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
#     #                             range=SAMPLE_RANGE_NAME).execute()
#     # values = result.get('values', [])
#
#     request = sheet.values().append(spreadsheetId=SAMPLE_SPREADSHEET_ID,
#                                     range="Main Page!A2", valueInputOption="USER_ENTERED", body={"values":spreadsheetInputs}).execute()


if __name__== "__main__":
    extractEmail()
    # updateGooglesheet()












