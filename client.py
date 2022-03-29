import typing, os
from telethon import sync
from sqlite3 import OperationalError
from telethon.sessions import Session
from telethon.sync import TelegramClient
from telethon.errors.rpcerrorlist import AuthKeyDuplicatedError
from telethon.errors import SessionPasswordNeededError, rpcerrorlist
from telethon.network import MTProtoSender, ConnectionTcpFull, Connection



class Client(TelegramClient):
    
    code: int
    _apiId: int
    _api: tuple
    _apiHash: str
    errors: list
    connection: bool
    _proxy: typing.Union[tuple, dict] = None
    _use_connection: 'typing.Type[Connection]' = ConnectionTcpFull

    def __init__(
                self: 'Client', 
                session: 'typing.Union[str, Session]' = str
        ):

        self.session = session
        self._apiId = None
        self._apiHash = None
        self._api = ()
        self.errors = []
        self.code = None
        self.connection = False
        self._proxy = None
        self._use_connection = ConnectionTcpFull

    def set_session(self, value: 'typing.Union[str, Session]' = str):

        self.session = value
        return self

    def set_api_full(self, value: tuple):

        self._api = value
        return self

    def set_apiId(self, value: int):

        self._apiId = value

        return self

    def set_apiHash(self, value: str):

        self._apiHash = value

        return self

    def use_connection(self, connection):

        self._use_connection = connection

        return self

    def set_proxy(self, proxy: tuple|dict):

        self._proxy = proxy

        return self

    def get_params(self):

        params = ()
        if self._api:
            params += self._api  
        elif self._apiId and self._apiHash:
            params += (self._apiId, self._apiHash)
        return params

    def perform(self):

        if (self._apiId  and self._apiHash) or (self._api):

            try:
                api_id, api_hash = self.get_params()

                self._client = TelegramClient(self.session, api_id, api_hash, connection = self._use_connection, proxy = self._proxy)

                self._client.connect()

                if self.is_authorized():

                    self.code = 200
                else:
                    self.code = 201

            except AuthKeyDuplicatedError as authkeyduplicate:

                self.errors.append(authkeyduplicate)
                self.code = 101

            except OperationalError as operationalError:

                self.errors.append(operationalError)
                self.code = 301

            except Exception as exception:

                self.errors.append(exception)
                self.code = 401
        else:
            self.errors.append(ValueError('App ID or Api ID has been not set!'))
            self.code = 501
        return self

    def login(self):
        
        self._client.send_code_request(self.session)

        try:
            self._client.sign_in( self.session, input(' Enter the code: ') )
            self.code = 200
        except SessionPasswordNeededError:
            try:
                self._client.sign_in( password = input(' Enter the password: ') )
                self.code = 200
            except rpcerrorlist.PasswordHashInvalidError as invalidPassword:
                self.errors.append(invalidPassword)
                self.code = 203
        return self
        
    def is_authorized(self)->bool: 

        if self._client:
            if self._client.is_user_authorized():
                self.connection = True
            else:
                self.connection = False

        return self.connection

    async def disconnect(self):
        
        try:
            await self._client.disconnect()
            self.code = 200
            # os.remove('{}.session'.format(self.session))
        except:
            self.code = 205
        
    def logout(self):
        if self.is_authorized():
            if self._client.log_out():
                self.code = 200


    def get(self):
        return self._client