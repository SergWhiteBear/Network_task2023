# Класс для представления строк в таблице
class Row_view:
    def __init__(self, json):
        org = json.get('org') or '*'
        self.ip = json.get('ip') or '*'
        self.as_block = org.split()[0] or '*'
        self.provider = ' '.join(org.split()[1:]) or '*'
        self.country = json.get('country') or '*'
        # self.city = json.get('city') or '*'

