def take_input(filename):
    from createDBImportData import shortenSaveUrl
    # Creating the class object to use
    workwithurl = shortenSaveUrl()

    # Read URLS from the input file
    listurls = workwithurl.read_urls_from_file(filename)

    # Make a a list of dictionaries from the inputs
    formattedUrls = workwithurl.prepare_doc_to_insert(listurls)

    # Insert the data into the database
    shortenSaveUrl.insert_many_urls(formattedUrls)

    shortenSaveUrl.imported = True

