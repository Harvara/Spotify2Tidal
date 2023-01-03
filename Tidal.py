import os
import tidalapi
import smtplib
import ssl

class Tidal:


    def __init__(self):
        self.token_type = os.getenv('TOKEN_TYPE')
        self.token = os.getenv('BEARER_TOKEN')
        self.refresh_token = os.getenv('REFRESH_TOKEN')
        self.expiry_date = os.getenv('EXPIRY_DATE')
        self.session = None

    def connect(self):
        self.session = tidalapi.Session()
        self.session.login_oauth_simple(function=self.send_email)
        """
        self.session.load_oauth_session(
            token_type=self.token_type,
            access_token=self.token,
            expiry_time=self.expiry_date,
            refresh_token=self.refresh_token
        )
        """

    def search(self, query):
        if not self.session:
            self.connect()
        return self.session.search(query=query, models=[tidalapi.media.Track])

    def send_email(self, code):
        port = 465
        password = os.getenv('SMTPLIB_PASSWORD')
        login = os.getenv('SMTPLIB_LOGIN')

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.gmail.com', port, context=context) as server:
            message = 'Subject: {}\n\n{}'.format("Request to copy playlist", code)
            server.login(login, password)
            server.sendmail(login, login, message)

