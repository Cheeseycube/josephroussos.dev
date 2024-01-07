import pymongo
import sys
import os
from dotenv import load_dotenv
import datetime


class Wordle_db:
    def __init__(self):
        """Creates a connection to MongoDB and stores it in `self.client`.

        Warning:
            Requires a .env with MONGO_HOST, MONGO_USERNAME, and MONGO_PASSWORD specified."""
        load_dotenv("/var/www/josephroussos.dev/.env")
        load_dotenv()
        try:
            self.client = pymongo.MongoClient(os.getenv('MONGO_HOST'), username=os.getenv('MONGO_USERNAME'),
                                              password=os.getenv('MONGO_PASSWORD'))
        except pymongo.errors.ConfigurationError as e:
            print(f"Encountered a known error while connecting to MongoDB from WordleApp/Mongodb.py: {e}", file=sys.stderr)
            self.client = None

    def initialize_database(self) -> bool:
        """Drops the `used_words` table if it exists, and creates a new `used_words` table with `wordle_num` as the primary key

        Returns:
            A boolean depending on whether the connection to the MongoDB database was successful
        """
        if self.client is None:
            print('no mongodb client found in WordleApp/Mongodb.py: line 30', file=sys.stderr)
            return False

        self.client.Wordle_db.used_words.drop()
        used_words = self.client.Wordle_db.used_words
        used_words.create_index('order', unique=True)

        #self.client.Wordle_db.all_wordle_words.drop()
        #all_wordle_words = self.client.Wordle_db.all_wordle_words
        #all_wordle_words.create_index('word', unique=True)

        #self.client.Wordle_db.all_words.drop()
        #all_words = self.client.Wordle_db.all_words
        #all_words.create_index('word', unique=True)
        return True

    def add_used_words(self, words: list) -> list:
        if self.client is None:
            print('no mongodb client found')
            return []

        db = self.client["Wordle_db"]
        collection = db["used_words"]
        try:
            x = collection.insert_many(words, ordered=False)
            print(len(x.inserted_ids))
        except pymongo.errors.BulkWriteError as e:
            print('Most likely a duplicate word was detected')
        return words

    def parse_used_words(self, path):
        used_words_file = open(path, 'r')
        used_words = []
        for line in used_words_file:
            split_line = line.split()
            word = split_line[0]
            order = split_line[1].replace('#', '')
            date = datetime.datetime.strptime(split_line[2], '%m/%d/%y')
            print(f"{word} {order} {date}")
            used_word_dict = {'word': word, 'order': order, 'date': date}
            used_words.append(used_word_dict)
        return used_words

    def add_all_wordle_words(self, words: list) -> list:
        if self.client is None:
            print('no mongodb client found')
            return []

        db = self.client["Wordle_db"]
        collection = db["all_wordle_words"]
        try:
            x = collection.insert_many(words, ordered=False)
            print(len(x.inserted_ids))
        except pymongo.errors.BulkWriteError as e:
            print('Most likely a duplicate word was detected')
        return words

    def add_all_words(self, words: list) -> list:
        if self.client is None:
            print('no mongodb client found')
            return []

        db = self.client["Wordle_db"]
        collection = db["all_words"]
        try:
            x = collection.insert_many(words, ordered=False)
            print(len(x.inserted_ids))
        except pymongo.errors.BulkWriteError as e:
            print('Most likely a duplicate word was detected')
        return words
    def parse_words(self, path):
        words_file = open(path, 'r')
        word_list = []
        for word in words_file.read().split('\n'):
            word_dict = {'word': word}
            word_list.append(word_dict)
        return word_list

    def get_used_words(self):
        if self.client is None:
            print('no mongodb client found')
            return []
        db = self.client['Wordle_db']
        collection = db['used_words']
        return list(collection.find({}, {'_id': False}))

    def get_wordle_words(self):
        if self.client is None:
            print('no mongodb client found')
            return []
        db = self.client['Wordle_db']
        collection = db['all_wordle_words']
        return list(collection.find({}, {'_id': False}))




if __name__ == "__main__":
    load_dotenv()
    # parse a txt and use the add_words function
    #wordle_db = Wordle_db()
    #wordle_db.initialize_database()
    #wordle_db.add_used_words(wordle_db.parse_used_words('used_words.txt'))

