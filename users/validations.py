import re

from my_settings  import SECRET
from users.models import User

class Validation:
    def validate_email(self, email):
        regex = re.compile('^[0-9a-zA-Z]([-_.]?[0-9a-zA-Z])*@[0-9a-zA-Z]([-_.]?[0-9a-zA-Z])*.[a-zA-Z]{2,3}$')
        if regex.match(email):
            return True
        return False

    def validate_password(self, password):
        regexs = [
                re.compile('^(?=.*[a-zA-Z])(?=.*\d)[A-Za-z\d!@#$%^&*]{6,15}$'),
                re.compile('^(?=.*[a-zA-Z])(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{6,15}$'),
                re.compile('^(?=.*\d)(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{6,15}$')
                ]

        for regex in regexs:
            if regex.match(password):
                return True
        return False

    def validate_name(self, name):
        regex = re.compile('^.{2,}$')
        if regex.match(name):
            return True
        return False

    def validate_duplication(self, email):
        if User.objects.filter(email=email).exists():
            return False
        return True
