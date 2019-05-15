from flask import Flask, render_template, request, redirect, url_for
from createDBImportData import shortenSaveUrl
app = Flask(__name__)
from bson.objectid import ObjectId

@app.route('/')
def main_page():
    """
    this method is just the entry point to the
    main starting page.
    :return: start.html page
    """
    return render_template('start.html')


@app.route('/short', methods=['POST', 'GET'])
def get_short():
    """
    this method returns shorten url to the front end
    by saving the original URL into the mongodb.
    :return:
            returns start.html page with an alert
             containing the shortened URL.
    """
    status = "Failed to add"
    if request.method == 'POST':
        obj = shortenSaveUrl()
        result = request.form["org_url"]
        print("Inside Post: ", result)
        final_doc = obj.prepare_doc_to_insert([result])
        id = shortenSaveUrl.insert_one_url(final_doc[0])
        print("Return id: ", ObjectId(id.inserted_id))
        print(type(id))
        if id.inserted_id:
            short_url = shortenSaveUrl.find_by_id(ObjectId(id.inserted_id))
            status = short_url
    return render_template("start.html", status=status)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=6789)