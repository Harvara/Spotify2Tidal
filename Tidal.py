import os
import tidalapi


class Tidal:


    def __init__(self):
        self.token_type = os.getenv('TOKEN_TYPE')
        self.token = os.getenv('BEARER_TOKEN')
        self.refresh_token = os.getenv('REFRESH_TOKEN')
        self.expiry_date = os.getenv('EXPIRY_DATE')
        self.session = None

    def connect(self):
        self.session = tidalapi.Session()
        #print(self.session.login_oauth_simple())
        self.session.load_oauth_session(
            token_type=self.token_type,
            access_token=self.token,
            expiry_time=self.expiry_date,
            refresh_token=self.refresh_token
        )

    def search(self, query):
        if not self.session:
            self.connect()
        self.session.search(query=query, models=[tidalapi.media.Track])

