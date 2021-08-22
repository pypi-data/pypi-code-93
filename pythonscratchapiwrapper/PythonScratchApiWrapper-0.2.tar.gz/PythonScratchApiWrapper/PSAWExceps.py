class InvalidCredentials(Exception):
    #Failed to log in, invalid username or password
    pass

class InvalidUser(Exception):
    #Username does not exist
    pass

class InvalidProjectID(Exception):
    #Project ID does not exist
    pass