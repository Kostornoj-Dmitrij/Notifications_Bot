class User:
    def __init__(self, user_id):
        self.user_id = ''
        self.state = 'chat_start'
        self.chat_id = ''
        self.chat_name = ''
        self.chat_link = ''
        self.keywords = ''
        self.keywords_id = ''
        self.t_user_id = user_id
        self.callback = self
        self.chat_count = 0