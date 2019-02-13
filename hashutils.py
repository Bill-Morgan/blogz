import random
import string
import hashlib

def make_salt():
    return ''.join([random.choice(string.ascii_letters) for x in range(5)])
    
def make_pw_hash(password, salt=None):
    if salt==None:
        salt = make_salt()
    hash = hashlib.sha256(str.encode(password+salt)).hexdigest()
    return ('{0},{1}'.format(hash, salt))

def check_pw_hash(password, pw_hash):
    salt = pw_hash.split(',')[1]
    return pw_hash == make_pw_hash(password, salt)