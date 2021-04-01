import numpy as np
import pandas as pd
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from keras.models import Sequential
from keras.layers import Dense, Embedding, LSTM, SpatialDropout1D
from sklearn.model_selection import train_test_split
from keras.callbacks import EarlyStopping
import re
from nltk.corpus import stopwords
import nltk
from nltk import pos_tag
from nltk import word_tokenize
from nltk.stem import WordNetLemmatizer

STOPWORDS = set(stopwords.words('english'))
CONTEXTUAL_STOPWORDS = ['&gt;', 'hello', 'said', 'regards', 'hi', 'all', 'please', 'assist', 'kindly', 'help', 'thx', 'thank', 'thankyou', 'you', 'thu', 'fwd', 'forwarded', 'message', 'iappsasiacom', 'date',
                        'jan', 'feb', 'mar', 'apr', 'may', 'jun', 'jul', 'aug', 'sep', 'oct', 'nov', 'dec', 'gmail', 'gmailcom', 'com', 'tell', 'am', 'pm', 'subject', 'query', 'mon', 'tue', 'wed', 'thur', 'fri', 'sat', 'sun']
STOPWORDS.update(CONTEXTUAL_STOPWORDS)
REPLACE_BY_SPACE_RE = re.compile('[/(){}\[\]\|@,;]')
BAD_SYMBOLS_RE = re.compile('[^0-9a-z #+_]')
wordnet_lemmatizer = WordNetLemmatizer()
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')

def lemmatize(x):
    dirty = word_tokenize(x)
    tokens = []
    for word in dirty:
        if word.strip('.') == '':
            pass
        else:
            tokens.append(word.strip('.'))
    tokens = pos_tag(tokens)
    lemms = ' '.join(wordnet_lemmatizer.lemmatize(key.lower())
                     for key, value in tokens if value != 'NNP')  # getting rid of proper nouns
    return lemms


def remove_confidentiality_notice(after_split):
    cleaned = []
    counter = 7
    found = False
    for each in after_split:
        if '*CONFIDENTIALITY NOTICE' in each:
            found = True
            counter -= 1
        else:
            if found:
                counter -= 1
                if counter == 0:
                    found = False
                else:
                    continue
            else:
                cleaned.append(each)
    return cleaned


def remove_fixed_address(after_split):
    cleaned = []
    counter = 5
    found = False
    for each in after_split:
        if 'ActiveSG Technical Helpdesk' in each:
            found = True
            counter -= 1
        else:
            if found:
                counter -= 1
                if counter == 0:
                    found = False
                else:
                    continue
            else:
                cleaned.append(each)
    return cleaned


def clean_text(text):
    temp = text.split("\r")
    temp = remove_confidentiality_notice(temp)
    temp = remove_fixed_address(temp)
    text = ''.join(word for word in temp if 'From:' not in word and 'To:' not in word and '<' not in word and 'Forwarded' not in word and
                   'Date' not in word and 'Subject' not in word and 'Cc' not in word
                   and 'n[O]' not in word and '[F]' not in word and 'Sent:' not in word and '@' not in word)
    text = text.lower()
    text = text.replace("\n", " ")
    text = REPLACE_BY_SPACE_RE.sub(' ', text)
    text = BAD_SYMBOLS_RE.sub('', text)
    text = lemmatize(text)
    text = ' '.join(word for word in text.split() if word not in STOPWORDS)
    text = ''.join([i for i in text if not i.isdigit()])
    text = " ".join(text.split())
    return text


class Assigner:

    issueTypes = {'Wallet': 0,
              'Admin Panel': 1,
              'Android': 2,
              'iOS': 3,
              'Internet': 4,
              'Receipt Printer': 5,
              'GO panel': 6,
              'Gym panel': 7,
              'POS': 8,
              'iPAD': 9,
              'Nexus': 10,
              'WIFI': 11,
              'Web': 12,
              'Merchant': 13,
              'Turnstile': 14,
              'Network': 15,
              'Power Adapter': 16,
              'Scanner': 17,
              'Switches': 18,
              'OCBC gateway': 19,
              'DBS Gateway': 20,
              'Service Request': 21,
              'Swim Panel': 22,
              'SwimSafer': 23,
              'SEP': 24,
              'Booking': 25,
              'Feedback': 26,
              'Transaction': 27,
              'Enquiries': 28,
              'Membership': 29,
              'Programme': 30,
              'Public Programme': 31,
              'Data Patch Receipt': 32
              }

    # The maximum number of words to be used. (most frequent)
    MAX_WORDS = 50000
    # Max number of words in each complaint.
    MAX_SEQUENCE_LENGTH = 250
    # This is fixed.
    EMBEDDING_DIM = 100

    def __init__(self, csv):
        self.issueTypes = Assigner.issueTypes
        self.MAX_WORDS = Assigner.MAX_WORDS
        self.MAX_SEQUENCE_LENGTH = Assigner.MAX_SEQUENCE_LENGTH
        self.EMBEDDING_DIM = Assigner.EMBEDDING_DIM

        self.df = pd.read_csv(csv)
        self.df['cleaned_content'] = self.df['content'].apply(clean_text)

        self.tokenizer = Tokenizer(
            num_words=self.MAX_WORDS, filters='!"#$%&()*+,-./:;<=>?@[\]^_`{|}~', lower=True)
        self.tokenizer.fit_on_texts(self.df['cleaned_content'].values)

        self.X = self.tokenizer.texts_to_sequences(
            self.df['cleaned_content'].values)
        self.X = pad_sequences(self.X, maxlen=self.MAX_SEQUENCE_LENGTH)

        self.y = pd.get_dummies(self.df['issue'])
        self.y = self.y.values

        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.model = None
        self.epochs = 30
        self.batch_size = 64

    def train(self, size, num):
        self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
            self.X, self.y, test_size=size, random_state=2021)

        temp = Sequential()
        temp.add(Embedding(self.MAX_WORDS, self.EMBEDDING_DIM,
                           input_length=self.X.shape[1]))
        temp.add(SpatialDropout1D(0.2))
        temp.add(LSTM(100, dropout=0.2, recurrent_dropout=0.2))
        temp.add(Dense(num, activation='softmax'))
        temp.compile(loss='categorical_crossentropy',
                     optimizer='adam', metrics=['accuracy'])

        temp.fit(self.X_train, self.y_train, epochs=self.epochs, batch_size=self.batch_size,
                 validation_split=0.1, callbacks=[EarlyStopping(monitor='val_loss', patience=3, min_delta=0.0001)])
        self.model = temp

        acc = self.model.evaluate(self.X_test, self.y_test)
        print('Test set\n  Loss: {:0.3f}\n  Accuracy: {:0.3f}'.format(
            acc[0], acc[1]))

    def assign(self, text):
        new_case = [text]
        seq = self.tokenizer.texts_to_sequences(new_case)
        padded = pad_sequences(seq, maxlen=self.MAX_SEQUENCE_LENGTH)
        pred = self.model.predict(padded)
        labels = list(sorted(set(self.df['issue'])))
        predicted_issue = labels[np.argmax(pred)]
        predicted_number = self.issueTypes[predicted_issue]
        return predicted_number
