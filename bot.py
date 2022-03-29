import re
import time
import traceback
from .client import Client
from datetime import datetime
from telethon import events, sync
from telethon.tl.functions.messages import StartBotRequest
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.errors.rpcerrorlist import *
from .helpers import *
class Bot(Client):

    """
    Class Bot
    =========
    được kế thừa từ đặc tính của `Client`.\n
    Class này được dùng để khởi tạo một session kết nối với
    đối tượng Bot Telegram để thực hiện các hành động như
    get, set, send.\n
    Phục vụ cho: `Airdrop Bot`\n
    Kế thừa: `Telegram Client`\n
    Input: `client, bot_id, peer_id, params`\n
    Return: `Object`|`int`|`string`|`dict`|`list`\n
    Để khởI tạo một Bot mới\n
    Ví dụ:
    >>> from .client import Client
    >>> client = Client(...)...
    >>> if client.code == 200:
    ...     client = client.get()
    ...     bot_id = 'NicolasTesla_Bot'
    ...     peer_id = bot_id
    ...     params = 'r199434545'
    ...     bot = Bot(client, bot_id, peer_id, params)
    ...     
    ...

    """
    _bot: None
    _client: Client
    _bot_id: str|int
    errors: list
    def __init__(
        self, 
        client: Client, 
        bot_id: str|int, 
        peer_id: str|int = None, 
        params: str = None
        ):
        """
        Thông số của bot bao gồm:
        -------------------------
        `@params` : Có thể là refId hoặc thông số khác tuỳ thuộc mỗi con bot\n
        `@peer_id`: username của bot hay bất kỳ đối tượng telegram nào đều là đối tượng Peer\n
        `@bot_id`: **[`bắt buộc`] Là username của bot hoặc bất kỳ đối tượng nào tương tự như Peer\n
        `@client`: **[`bắt buộc`] Là đối tượng quan trọng nhất cần phải có để khởi tạo một session mới để bắt đầu 
        làm việc với bot
        """
        self._client = client
        self._bot_id = bot_id
        self._peer_id = peer_id
        self._params = params
        self.message: str = None
        self.media: str = None
        self._message: str = None
        self.code: int = None
        self.errors: list = []
        self.tmp: str = None
        if self._params:
           
            try: 
                self._bot = self._client(StartBotRequest(self._bot_id, self._peer_id, self._params))
            except BotInvalidError as bot_invalid:
                self.errors.append(bot_invalid)
            except PeerIdInvalidError as peer_invalid:
                self.errors.append(peer_invalid)
            except StartParamEmptyError as params_empty:
                self.errors.append(params_empty)
            except StartParamInvalidError as params_invalid:
                self.errors.append(params_invalid)
        else:
            """
            Khi người dùng không nhập refId hoặc user ref Id thì client sẽ kích hoạt bot thủ công bằng 
            lệnh /start thông thường.
            """
            self._bot = self._client.send_message(self._bot_id, '/start')

    def with_message(self, value: str):
        """
        with_message
        ------------
        Thuộc tính set message.
        Type: `Attribute`
        Input: `string`
        Return: `object 'Bot'`
        """
        self.message = value
        return self

    def with_media(self, value: str):
        """
        with_media
        ----------
        Thuộc tính set media: ảnh, video, tệp tin khác....
        Type: `Attribute`
        Input: `string`
        Return: `object 'Bot'`
        """
        self.media = value
        return self

    async def send_message(self, message: str = None):
        try:
            if message:
                await self._client.send_message(self._bot_id, message)
        except Exception as exception:
            self.errors.append(exception)
            traceback.print_exc()
    async def send(self):
        """
        Hành động send các thuộc tính đã set:
        -------------------------------------
        Type: `Action`
        Input: `None`
        Return: `None`

        Ví dụ: Để gửi một tin nhắn cho một bot:\n
        python [code-block]:
        >>> client = Client(...)
        >>> if client.code == 200:
        ...    client = client.get()
        ...    bot = Bot(client, "username_bot", "peer_bot_id", "r9111133883")
        ...    bot.with_message("Chao ban toi la nguoi chat voi ban").send()
        
        Đoạn code trên thực hiện gửi tin nhắn đến một thực thể Telegram là `username_bot` có `peer_bot_id`
        """
        entity = self._client.get_entity(self._bot_id)
        if self.media and not self.message: 
            # Gửi file
            await self._client.send_file(entity, self.media)
            self.code = 200
            
        elif self.message and not self.media:
            # Gửi tin nhắn bình thường
            await self._client.send_message(entity, self.message)
            self.code = 200
        else:
            # Gửi tin nhắn thông thường nếu các điều kiện trên không hợp lệ
            await self._client.send_message(entity, self.message)
            self.code = 200

    async def get_messages(self):
        """
        get_message
        -----------
        Hành động get_message:
        Type: `Action`
        Input: `None`
        Return: `list`, `tuple`, `dict`
        """
        messages = await self._client.get_messages(self._bot_id)
        if messages:
            self.code = 200
            return messages

    async def get_lastest_message(self, index: int = 0)->str: 
        """
        Hành động get_last_message:
        Lấy một tin nhắn mới bao gồm cả incomming và outcomming
        Type: `Action`
        Input: `int` is `Số nguyên`
        Return: `string`
        """
        current_message = None

        message = await self.get_messages()

        if message:

            current_message = message[index].message
            self._message = current_message

        return current_message

    async def get_bot_id(self):
        return await self._client.get_entity(self._bot_id)

    async def get_wating_reply_message(self, message: str, timeout: int = 20):
        
        begin = datetime.now()

        while True:
            lastest_message = await self.get_lastest_message()
            if self.raw_search(message, lastest_message):
                print(lastest_message)
                return lastest_message
            elif (datetime.now() - begin).seconds >= timeout: 
                print('Timeout to retrive message')
                return None
            else:
                print("Trying find message '{}' in {} seconds".format(message, (datetime.now() - begin).seconds),sep="", end="")
                continue

    async def find_and_send_message(self, search: str, search_in: str, message):
        
        if self.raw_search(search, search_in):
            
            await self.send_message(message)
            print("[+] SENDED")

    async def find_in_current_message(self, search_text: str)->bool:

        current_message = await self.get_messages()[0]

        recompile = re.compile("[\n\t\r]")

        message_clean = recompile.sub("", current_message.message)

        if message_clean.find(search_text) > -1:
            self.tmp = search_text
            return True
            
        else:
            return False

    async def force_search(self, search_text: str):
        while True:
            message = await self.find_in_current_message(search_text)
            if message:
                self.code = 200
                return False
            else:
                self.code = 201
                return True
                
    def raw_search(self, search_word: str, search_in: str)->bool:

        if search_in.find(search_word) > -1:
            
            return True
        else:
            return False

    async def click_text(self, text: str=None, data:str=None):

        message = await self.get_messages()
        try:
            if message and text:
                
                await message[0].click(text='{}'.format(text), data=data)
            else:
                await message[0].click(0)
        except Exception as e:
            print(e)
            traceback.print_exc()
            
    def join_channel(self, channel: str): 

        self._client(JoinChannelRequest(channel))
        

    def join_group(self, group: str):

        self.join_channel(group)

    def join_multiple_groups(self, groups: dict|tuple):
        
        if len(groups)>0:
            for group in groups:
                self.join_group(group)
                
                
    def join_multiple_channels(self, channels: dict|tuple):
        
        if len(channels)>0:
            for channel in channels:
                self.join_channel(channel)
    def completed(self):
        return 'completed'