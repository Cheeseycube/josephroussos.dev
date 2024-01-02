import pymongo
import sys
import os
from dotenv import load_dotenv
from mongoengine import connect, Document, StringField

if __name__ == "__main__":
    load_dotenv()
    '''client = None
    try:
        client = pymongo.MongoClient("75.69.157.19:27017", username=os.getenv('WORDLE_USERNAME'), password=os.getenv('WORDLE_PASSWORD'))
    except pymongo.errors.ConfigurationError as e:
        print(f"Encountered an error while connecting to MongoDB from Hubspot.py: {e}", file=sys.stderr)
        client = None
    print(client.list_database_names())'''

    connect(db='Wordle', host="75.69.157.19:27017", username=os.getenv('WORDLE_USERNAME'), password=os.getenv('WORDLE_PASSWORD'))

    class used_words(Document):
        name = StringField()






