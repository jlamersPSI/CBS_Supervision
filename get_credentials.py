import getpass

def get_credentials():
    """
    Prompt the user to enter their DHIS2 credentials.

    Returns:
        tuple: (username, password)
    """
    try:
        username = input("Enter your username: ")
        password = getpass.getpass("Enter your password: ")
        return username, password
    except Exception as e:
        print(f"An error occurred: {e}")
        return None, None