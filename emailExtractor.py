import imaplib
import email
from email.header import decode_header
import webbrowser
import os
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import string
import enum
from googleapiclient.discovery import build
from google.oauth2 import service_account
import smtplib
from email.message import EmailMessage
import html
import re
from database import queryData

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
    username = input("Email: ")
    password = input("Password: ")

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
    imap.select("ToBeProcessed")
    retcode, messages = imap.search(None, '(UNSEEN)')

    spreadsheetInputs = []
    caseidPattern = 'CASE:(\d+)'
    for i in messages[0].split():
        currentInput = []
        caseID = ""
        finalBodyMessage = ""
        bodyText = ""
        subjectText = ""
        # fetch the email message by ID
        res, msg = imap.fetch(i, "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                # parse a bytes email into a message object
                msg = email.message_from_bytes(response[1])
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
                caseID = re.findall(caseidPattern, subjectText)
                inDatabase = queryData(str("".join(caseID)))
                if (inDatabase == False):
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
                            if content_type == "text/plain" and "attachment" not in content_disposition:
                                # print text/plain emails and skip attachments
                                bodyText = body
                                # text_tokens = word_tokenize(body)
                                # tokens_without_sw = [word for word in text_tokens if not word in stopwords.words()]
                                # finalBodyMessage = " ".join(tokens_without_sw)
                            # elif "attachment" in content_disposition:
                            #     # download attachment
                            #     filename = part.get_filename()
                            #     if filename:
                            #         folder_name = clean(subject)
                            #         if not os.path.isdir(folder_name):
                            #             # make a folder for this email (named after the subject)
                            #             os.mkdir(folder_name)
                            #         filepath = os.path.join(folder_name, filename)
                            #         # download attachment and save it
                            #         open(filepath, "wb").write(part.get_payload(decode=True))
                    else:
                        # extract content type of email
                        content_type = msg.get_content_type()
                        # get the email body
                        body = msg.get_payload(decode=True).decode()
                        if content_type == "text/plain":
                            bodyText = body
                            # text_tokens = word_tokenize(body)
                            # tokens_without_sw = [word for word in text_tokens if not word in stopwords.words()]
                            # finalBodyMessage = " ".join(tokens_without_sw)
                    # processBodyMessage(bodyText)
                    # Forward email to respective developer
                    # msg = EmailMessage()
                    # msg['Subject'] = subjectText
                    # msg['From'] = username
                    # msg['To'] = username # future elif statement
                    # msg.set_content(bodyText)
                    # with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                    #     smtp.login(username, password)
                    #     smtp.send_message(msg)

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












