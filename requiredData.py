import enum
import re

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

nricPattern = 'NRIC:(.*)' #\s+\w\d+\w
phoneNumberPattern = 'PHONE NUMBER:(.*)' #\s+\d+
namePattern = 'NAME OF CUSTOMER:(.*)'
osPattern = 'ANDROID OR IOS:(.*)'
osVersionPattern = 'OS VERSION:(.*)'

def parseData(issue, body):
    # re.findall(caseidPattern, subjectText)

    if issueType(issue) == issueType.accountIssue:
        print()
    elif issueType(issue) == issueType.paymentIssue:
        print()
    elif issueType(issue) == issueType.refundIssue:
        print()
    elif issueType(issue) == issueType.checkoutIssue:
        print()
    elif issueType(issue) == issueType.scanIssue:
        print()
    elif issueType(issue) == issueType.merchantIssue:
        print()
    elif issueType(issue) == issueType.bookingIssue:
        print()
    elif issueType(issue) == issueType.gymswimbookingIssue:
        print()
    elif issueType(issue) == issueType.swimsaferIssue:
        print()
    elif issueType(issue) == issueType.receiptIssue:
        print()

text = "NRIC:               sada \n" + "NAME OF CUSTOMER:       SAMUEL LEOW           "
nric = re.findall(nricPattern, text)
if len("".join(nric).strip()) == 0:
    print("empty fill")


