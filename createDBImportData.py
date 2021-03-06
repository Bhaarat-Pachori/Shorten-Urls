import pymongo, sys, re
from pymongo import MongoClient
import datetime, random
from insertSomeData import take_input
from bson.objectid import ObjectId

client = MongoClient('mongodb://localhost', 27017)

# create a db
db = client.urls

"""
Creating a collection. Collection is equivalent to table name in SQL
A collection is a group of documents stored in MongoDB
"""

urlCollection = db.top100urls

"""
Create documents in collection.
An important note about collections (and databases) in MongoDB is that 
they are created lazily - none of the above commands have actually 
performed any operations on the MongoDB server. Collections and 
databases are created when the first document is inserted into them.
"""


class shortenSaveUrl:
    imported = False

    def __init__(self):
        self.urlsList = list()
        self.final_list = list()

    @classmethod
    def shorten_url(cls, url):
        """
        this core logic to shorten the URL.
        :param url: the original URL sent by the
                    user from the frontend.
        :return: the shorten url
        """
        jumbled = url[len('https://'):]

        rng = random.sample(range(1, len(jumbled)), len(jumbled) // 4)

        lstchanged = list()

        for idx, each in enumerate(rng):
            if idx % 2 == 0 and not idx % 3 == 0:
                lstchanged.append(random.randint(48, 57))
            elif idx % 3 == 0 and not idx % 2 == 0:
                lstchanged.append(random.randint(65, 90))
            else:
                lstchanged.append(random.randint(97, 122))

        """
        48-57(0-9) 65-90(A-Z) 97-122(a-z) Ascii range for
        numbers and letters.
        """
        chrlst = list(map(lambda x: chr(x), lstchanged))
        newurl = url[:8] + "".join(chrlst)
        yield newurl

    def read_urls_from_file(self, filename):
        """
        this method is used to read the bunch of URLs
        from a text file and insert them into the DB.
        :param filename: the name of the input file
        :return: the of all the URLs read from the file
        """
        with open(filename, 'r') as top:
            self.urlsList = top.readlines()
        return self.urlsList

    def prepare_doc_to_insert(self, urls_list):
        """
        fields/keys in the docs as follows:
        _id:       autogenerated
        name:      name of the url
        org_url:   the original url
        short_url: the shortened url
        when:      time when the url was added
        """
        try:
            for item in urls_list:
                temp_doc = dict()
                """
                l = 'https://docs.python.org/3/library/re.html#module-re'
                m = re.search('[a-zA-Z0-9]/[a-zA-Z0-9]', l)
                m.span() --> returns tuple with start and end pos
                             (22, 25)
                we need the last value in the tuple so m.span()[1]-2
                str = l[:m.span()[1]-1]
                print(str) -->  https://docs.python.org
                """
                search_obj = re.search('[a-zA-Z0-9]/[a-zA-Z0-9]*', item)
                assert search_obj != None
                end_pos = search_obj.span()[1] -1
                part_1 = item[:end_pos]
                print(part_1)
                temp_doc['name'] = part_1
                temp_doc['org_url'] = item.strip("\n")
                temp_doc['org_len'] = len(item)
                shortened = shortenSaveUrl.shorten_url(item)
                temp_doc['short_url'] = next(shortened)
                temp_doc['short_len'] = len(temp_doc['short_url'])
                now = datetime.datetime.now()
                temp_doc['when'] = now.strftime("%m-%d-%Y %H:%M:%S")
                self.final_list.append(temp_doc)
        except AssertionError as error:
            print("Couldn't extract some fields")
        return self.final_list

    @staticmethod
    def insert_many_urls(many_urls):
        """
        this method is use to issue the Pymongo command
        to insert the data.
        :param many_urls: the list of URLs
        :return: the ids of all the URLs inserted in the
                 DB
        """
        ids = urlCollection.insert_many(many_urls)
        return ids

    @staticmethod
    def insert_one_url(url_to_insert):
        """
        this method is use to insert one URL at a time
        into the DB
        :param url_to_insert: the original URL to insert
                              into the DB
        :return: the id of the inserted URL.
        """
        ids = urlCollection.insert_one(url_to_insert)
        print(ids.inserted_id)
        return ids

    @staticmethod
    def find_by_part_name(searchparam):
        """
        this method is used to find the entry in the DB
        by using a keyword given by the user. This method
        at present can be used from the CLI.
        :param searchparam:
        :return: the shorten URL to send to the front end
        """
        item = dict()
        urlCollection.create_index([('name', pymongo.TEXT),('org_url', pymongo.TEXT)])
        found_docs = list(urlCollection.find({'$text': {'$search': searchparam}}))
        print("Found %d docs matching the querry" %len(found_docs))
        for item in found_docs:
            print("URL: ", item['org_url'])
        return item['short_url']

    @staticmethod
    def find_by_id(docid):
        """
        this method is used to find the document in the
        collection of the DB
        :param docid: the id of the document to find
        :return: the shorten URL to be shown on the
                front end.
        """
        item = urlCollection.find_one({"_id": ObjectId(docid)})
        return item['short_url']


def add_url():
    """
    the wrapper method that calls the instance method
    that prepares the input to be fed to the DB
    :return: None
    """
    workWithUrls = shortenSaveUrl()
    # Paste or type the URL(s) to insert into the DB
    print("Paste/Type the url to enter")
    user_input = str(input())

    # Making a dictionary from user input
    list_urls = workWithUrls.prepare_doc_to_insert([user_input])

    # Insert a single url into the DB
    shortenSaveUrl.insert_one_url(list_urls[0])


def search_by_name():
    """
    this method is a wrapper method to the static
    method of the class.
    :return: None
    """
    print("\tEnter the keyword for the url")
    search_name = str(input()).lower()
    search = shortenSaveUrl()
    search.find_by_part_name(search_name)


def delete_doc():
    """
    this is a wrapper method to delete the
    document from the DB
    :return: None
    """
    print("Following fields are present in the collection")
    print("Fields: [name, org_url, org_len, short_len, short_url, when]\n")
    print("{filed_name+val}")
    user_input = str(input())
    a, b = user_input.split(" ")
    # user_input = "\"" +a + "\"" + ":"+ "\""+b+"\""
    doc = dict()
    doc[a] = b
    urlCollection.delete_one(user_input)


def what_next():
    """
    this method is used to interact with the
    user through Command Line Interface.
    :return: None
    """
    print("What you want to do ?")
    print("\tAdd new url to DB or Search a url in the DB")
    print("\t\tType \"add\" or \"search\" ")
    print("\tDelete a document")
    print("\t\tType \"del\" or \"delete\"")
    print("\tType quit/Quit/q to quit")
    user_input = str(input())

    if user_input.lower() == "add":
        add_url()
    elif user_input.lower() == "search":
        search_by_name()
    elif user_input.lower() in ["delete", "del"]:
        delete_doc()
    elif user_input.lower() == "q" or user_input == "quit":
        sys.exit(1)
    else:
        what_next()

if __name__ == "__main__":
    if not urlCollection.find({}).count() >= 100:
        take_input('top100.txt')
    while True:
        what_next()
