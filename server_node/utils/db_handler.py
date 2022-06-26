db = {"id1":"file text 1"}

def get_file_from_db(file_id):
    if file_id in db.keys():
        return db[file_id]
    return None

def edit_file_db(file_id, new_text):
    db[file_id] =  new_text

def create_file(file_id):
    db[file_id] = ""

def is_in_db(file_id):
    return file_id in db.keys()