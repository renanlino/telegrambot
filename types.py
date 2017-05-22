from ._aux import *
from datetime import datetime
import json
import time

class Update:
    """
    Update class as defined by Telegram API at https://core.telegram.org/bots/api#update
    Represents an update.

        Attribute        Type        Optional
        update_id        int         N
        message          Message     N
    """
    def __init__(self, updateData):
        """
        (dict) -> constructor
        Update class constructor. 'updateData' must be a valid JSON representation of update information
        """
        self.update_id = updateData["update_id"]
        self.message = Message(updateData["message"])


class User:
    """
    User class as defined by Telegram API at https://core.telegram.org/bots/api#user
    Represents an user or bot.

        Attribute       Type        Optional
        id              int         N
        first_name      string      N
        last_name       string      Y
        user_name       string      Y
    """
    def __init__(self, userData):
        """
        (dict) -> constructor
        User class constructor. 'userData' must be a valid JSON representation of user information
        """
        self.id = userData["id"]
        self.first_name = userData["first_name"]
        if "last_name" in userData:
            self.last_name = userData["last_name"]
        else:
            self.last_name = None
        if "username" in userData:
            self.username = userData["username"]
        else:
            self.username = None

    def __str__(self):
        """
        () -> str
        Human readable representation for User object
        """
        string = "User: " + self.first_name
        if self.last_name != None:
            string += " " + self.last_name
        if self.username != None:
            string += " (@" + self.username + ")"
        return string

    def __repr__(self):
        """
        () -> str
        Formal representantion for User object (a valid dictionary representation)
        """
        return str(self.__dict__)


class Chat:
    """
    Chat class as defined by Telegram API at https://core.telegram.org/bots/api#chat
    """

    def __init__(self, chatData):
        self.id = chatData["id"]
        self.type = chatData["type"]

        if "title" in chatData:
            self.title = chatData["title"]
        else:
            self.title = None

        if "username" in chatData:
            self.username = chatData["username"]
        else:
            self.username = None

        if "first_name" in chatData:
            self.first_name = chatData["first_name"]
        else:
            self.first_name = None

        if "last_name" in chatData:
            self.first_name = chatData["last_name"]
        else:
            self.last_name = None

    def __str__(self):
        """
        () -> str
        Human readable representation for Chat object
        """
        string = self.type.title() + " Chat: " + str(self.title)
        return string

    def __repr__(self):
        """
        () -> str
        Formal representantion for Chat object (a valid dictionary representation)
        """
        return str(self.__dict__)



class Message:
    """
    Message class as defined by Telegram API at https://core.telegram.org/bots/api#message
    Represents a message.
    The 'content' attribute contains the actual message data and can be an object of the followings
    classes: PhotoSize, Audio, Voice, Document, Sticker, Video, Contact, Location, Update, InputFile, UserProfilePhotos.
    The 'type' attribute can be used for content classification.
    The 'forwarded' attribute is True is the message was forwarded. If True, then the attributes forward_from and
    forward_date are available.

        Attribute           Type            Optional
        from_user           User            N            * named 'from' at Bot API
        message_id          int             N
        date                Datetime        N
        chat                Chat            N
        forwarded           bool            N
        forward_from        User            Y            * may not exist, check the bool 'forwarded'
        forward_date        Datetime        Y            * may not exist, check the bool 'forwarded'
        reply               bool            N
        reply_to_message    Message         Y            * may not exist, check the bool 'reply'
        content             *               N            * may be PhotoSize, Audio, Document, Sticker, Video, Contact, Location, Update, InputFile, UserProfilePhotos
    """
    def __init__(self, messageData):
        """
        (dict) -> constructor
        Message class constructor. 'messageData' must be a valid JSON representation of message information
        """

        self.from_user = User(messageData["from"])
        self.message_id = messageData["message_id"]
        self.date = datetime.fromtimestamp(messageData["date"])
        self.chat = Chat(messageData["chat"])

        if "forward_from" in messageData and "forward_date" in messageData:
            self.forwarded = True
            self.forward_from = User(messageData["forward_from"])
            self.forward_date = datetime.fromtimestamp(messageData["forward_date"])
        else:
            self.forwarded = False

        if "reply_to_message" in messageData:
            self.reply = True
            self.reply_to_message = Message(messageData["reply_to_message"])
        else:
            self.reply = False

        self.content = "Data type not supported yet"
        if "text" in messageData:
            self.type = "text"
            self.content = messageData["text"]
        elif "photo" in messageData:
            self.type = "photo"
            self.content = [PhotoSize(photo) for photo in messageData["photo"]]
        elif "audio" in messageData:
            self.type = "audio"
            self.content = Audio(messageData["audio"])
        elif "document" in messageData:
            self.type = "document"
            self.content = Document(messageData["document"])
        elif "sticker" in messageData:
            self.type = "sticker"
            self.content = Sticker(messageData["sticker"])
        elif "video" in messageData:
            self.type = "video"
            self.content = Video(messageData["video"])
        elif "contact" in messageData:
            self.type = "contact"
            self.content = Contact(messageData["contact"])
        elif "location" in messageData:
            self.type = "location"
            self.content = Location(messageData["location"])
        elif "voice" in messageData:
            self.type = "voice"
            self.content = Voice(messageData["voice"])
        else:
            self.type = "unknown"

    def __str__(self):
        """
        () -> str
        Human readable representation for Message object
        """
        string = "Message of type " + self.type + " sended by " + str(self.from_user)
        if isinstance(self.chat, Chat):
            string += " on " + str(self.chat)
        string += ".\nDate: " + self.date.strftime("%A, %d %B %Y %I:%M%p")
        if self.type != "photo":
            string += "\nContent: " + str(self.content)
        else:
            string += "\nContent: " + str(self.content[0])
        return string

    def __repr__(self):
        """
        () -> str
        Formal representantion for Message object (a valid dictionary representation)
        """
        reprdict = {}
        for key in self.__dict__:
            if key != "date" and key != "from_user" and key != "content" and key != "forward_date":
                reprdict[key] = self.__dict__[key]
            elif key == "from_user":
                reprdict["from"] = self.__dict__[key]
            elif key == "content":
                reprdict[ self.__dict__["type"] ] = self.__dict__[key]
            else:
                reprdict[key] = time.mktime( self.__dict__[key].timetuple() )
        return str(reprdict)


class PhotoSize:
    """
    PhotoSize class as defined by Telegram API at https://core.telegram.org/bots/api#photosize
    Represents a photo or sticker data.

        Attribute        Type        Optional
        file_id          string      N
        width            int         N
        height           int         N
        file_size        int         Y
    """
    def __init__(self, photoData):
        """
        (dict) -> constructor
        PhotoSize class constructor. 'photoData' must be a valid JSON representation of photo information
        """
        self.file_id = photoData["file_id"]
        self.width = photoData["width"]
        self.height = photoData["height"]
        if "file_size" in photoData:
            self.file_size = photoData["file_size"]
        else:
            self.file_size = None

    def __str__(self):
        """
        () -> str
        Human readable representation for PhotoSize object
        """
        string = "PhotoSize object with ID " + self.file_id
        return string

    def __repr__(self):
        """
        () -> str
        Formal representantion for PhotoSize object (a valid dictionary representation)
        """
        return str(self.__dict__)



class Audio:
    """
    Audio class as defined by Telegram API at https://core.telegram.org/bots/api#audio
    Represents a audio file (voice note).

        Attribute        Type        Optional
        file_id          string      N
        duration         int         N
        mime_type        string      Y
        file_size        int         Y

    """
    def __init__(self, audioData):
        """
        (dict) -> constructor
        Audio class constructor. 'audioData' must be a valid JSON representation of audio information
        """
        self.file_id = audioData["file_id"]
        self.duration = audioData["duration"]
        if "mime_type" in audioData:
            self.mime_type = audioData["mime_type"]
        else:
            self.mime_type = None
        if "file_size" in audioData:
            self.file_size = audioData["file_size"]
        else:
            self.file_size = None

    def __str__(self):
        """
        () -> str
        Human readable representation for Audio object
        """
        string = "Audio object with ID " + self.file_id
        return string

    def __repr__(self):
        """
        () -> str
        Formal representantion for Audio object (a valid dictionary representation)
        """
        return str(self.__dict__)



class Voice:
    """
    Voice class as defined by Telegram API at https://core.telegram.org/bots/api#voice
    Represents a voice file (voice note).

        Attribute        Type        Optional
        file_id          string      N
        duration         int         N
        mime_type        string      Y
        file_size        int         Y

    """
    def __init__(self, audioData):
        """
        (dict) -> constructor
        Voice class constructor. 'voiceData' must be a valid JSON representation of audio information
        """
        self.file_id = audioData["file_id"]
        self.duration = audioData["duration"]
        if "mime_type" in audioData:
            self.mime_type = audioData["mime_type"]
        else:
            self.mime_type = None
        if "file_size" in audioData:
            self.file_size = audioData["file_size"]
        else:
            self.file_size = None

    def __str__(self):
        """
        () -> str
        Human readable representation for Voice object
        """
        string = "Voice object with ID " + self.file_id
        return string

    def __repr__(self):
        """
        () -> str
        Formal representantion for Audio object (a valid dictionary representation)
        """
        return str(self.__dict__)



class Document:
    """
    Document class as defined by Telegram API at https://core.telegram.org/bots/api#document
    Represents a generic file.

        Attribute        Type        Optional
        file_id          string      N
        file_name        string      Y
        file_size        int         Y
        thumb            PhotoSize   Y
        mime_type        string      Y
    """
    def __init__(self, docData):
        """
        (dict) -> constructor
        Document class constructor. 'docData' must be a valid JSON representation of document information
        """
        self.file_id = docData["file_id"]
        if "thumb" in docData:
            self.thumb = PhotoSize(docData["thumb"])
        else:
            self.thumb = None
        if "file_name" in docData:
            self.file_name = docData["file_name"]
        else:
            self.file_name = None
        if "mime_type" in docData:
            self.mime_type = docData["mime_type"]
        else:
            self.mime_type = None
        if "file_size" in docData:
            self.file_size = docData["file_size"]
        else:
            self.file_size = None

    def __str__(self):
        """
        () -> str
        Human readable representation for Document object
        """
        string = "Document object with ID " + self.file_id
        if self.file_name != None:
            string += " named " + self.file_name
        return string

    def __repr__(self):
        """
        () -> str
        Formal representantion for Document object (a valid dictionary representation)
        """
        return str(self.__dict__)





class Sticker:
    """
    PhotoSize class as defined by Telegram API at https://core.telegram.org/bots/api#sticker
    Represents a photo or sticker data.

        Attribute        Type        Optional
        file_id          string      N
        width            int         N
        height           int         N
        thumb            PhotoSize   N
        file_size        int         Y

    """
    def __init__(self, stickerData):
        """
        (dict) -> constructor
        Sticker class constructor. 'stickerData' must be a valid JSON representation of sticker information
        """
        self.file_id = stickerData["file_id"]
        self.width = stickerData["width"]
        self.height = stickerData["height"]
        self.thumb = PhotoSize(stickerData["thumb"])
        if "file_size" in stickerData:
            self.file_size = stickerData["file_size"]
        else:
            self.file_size = None

    def __str__(self):
        """
        () -> str
        Human readable representation for Sticker object
        """
        string = "Sticker object with ID " + self.file_id
        return string

    def __repr__(self):
        """
        () -> str
        Formal representantion for Sticker object (a valid dictionary representation)
        """
        return str(self.__dict__)


class Video:
    """
    Video class as defined by Telegram API at https://core.telegram.org/bots/api#video
    Represents a video file.

        Attribute        Type        Optional
        file_id          string      N
        width            int         N
        height           int         N
        duration         int         N
        thumb            PhotoSize   Y
        mime_type        string      Y
        file_size        int         Y
        caption          string      Y
    """
    def __init__(self, videoData):
        """
        (dict) -> constructor
        Video class constructor. 'videoData' must be a valid JSON representation of video file information
        """
        self.file_id = videoData["file_id"]
        self.width = videoData["width"]
        self.height = videoData["height"]
        self.duration = videoData["duration"]
        if "thumb" in videoData:
            self.thumb = PhotoSize(videoData["thumb"])
        else:
            self.thumb = None
        if "mime_type" in videoData:
            self.mime_type = videoData["mime_type"]
        else:
            self.mime_type = None
        if "file_size" in videoData:
            self.file_size = videoData["file_size"]
        else:
            self.file_size = None
        if "caption" in videoData:
            self.caption = videoData["caption"]
        else:
            self.caption = None

    def __str__(self):
        """
        () -> str
        Human readable representation for Video object
        """
        string = "Video object with ID " + self.file_id
        return string

    def __repr__(self):
        """
        () -> str
        Formal representantion for Video object (a valid dictionary representation)
        """
        return str(self.__dict__)



class Contact:
    """
    Contact class as defined by Telegram API at https://core.telegram.org/bots/api#contact
    Represents a phone contact.

        Attribute        Type        Optional
        phone_number     string      N
        frist_name       string      N
        last_name        string      Y
        user_id          string      Y
        userObj          User        Y            * exists only if an 'user_id' is provided
    """
    def __init__(self, contactData):
        """
        (dict) -> constructor
        Contact class constructor. 'contactData' must be a valid JSON representation of message information
        """
        self.phone_number = contactData["phone_number"]
        self.first_name = contactData["first_name"]
        if "last_name" in contactData:
            self.last_name = contactData["last_name"]
        else:
            self.last_name = None
        if "user_id" in contactData:
            self.user_id = contactData["user_id"]
            self.userObj = User({"id":self.user_id, "first_name":self.first_name})
        else:
            self.user_id = None

    def __str__(self):
        """
        () -> str
        Human readable representation for Contact object
        """
        string = "Contact object:\n"
        string += "Name: " + self.first_name + "\n"
        if self.last_name != None:
            string += "Last Name: " + self.last_name + "\n"
        string += "Phone Number: " + self.phone_number
        if self.user_id != None:
            string += "\nTelegram User ID: " + str(self.user_id)

        return string

    def __repr__(self):
        """
        () -> str
        Formal representantion for Contact object (a valid dictionary representation)
        """
        return str(self.__dict__)


class Location:
    """
    Location class as defined by Telegram API at https://core.telegram.org/bots/api#location
    Represents a geolocation data.

        Attribute        Type        Optional
        longitude        float       N
        latitude         float       N
    """
    def __init__(self, locationData):
        """
        (dict) -> constructor
        Location class constructor. 'locationData' must be a valid JSON representation of location information
        Also, works with Google Maps API Result.
        """
        if "longitude" in locationData and "latitude" in locationData:
            self.longitude = locationData["longitude"]
            self.latitude = locationData["latitude"]
        elif "lng" in locationData and "lat" in locationData:
            self.longitude = locationData["lng"]
            self.latitude = locationData["lat"]


    def __str__(self):
        """
        () -> str
        Human readable representation for Location object
        """
        string = "Location object (Longitude: " + str(self.longitude) + " Latitude: " + str(self.latitude) + ")"
        return string

    def __repr__(self):
        """
        () -> str
        Formal representantion for Location object (a valid dictionary representation)
        """
        return str(self.__dict__)


class InputFile:
    """
    InputFile class as defined by Telegram API at https://core.telegram.org/bots/api#inputfile
    Represents a photo or sticker data.

        Attribute        Type        Optional
        file             file object N
    """
    def __init__(self, filepath):
        """
        (str) -> constructor
        InputFile class constructor. 'filepath' must be a existent file path.
        """
        self.file = openFile(filepath, "rb")

class UserProfilePhotos:
    """
    UserProfilePhotos class as defined by Telegram API at https://core.telegram.org/bots/api#userprofilephotos
    Represents a user's profile pictures.

        Attribute        Type        Optional
        total_count      int         N
        photos           [PhotoSize] N
    """
    def __init__(self, userProfileData):
        """
        (dict) -> constructor
        UserProfilePhotos class constructor. 'userProfileData' must be a valid JSON representation of message information
        """
        self.total_count = userProfileData["total_count"]
        self.photos = []
        for arrayPhotos in userProfileData["photos"]:
            phArray = []
            for photo in arrayPhotos:
                phArray.append( PhotoSize(photo) )
            self.photos.append(phArray)


class File:
    def __init__(self, fileData):
        self.file_id = fileData["file_id"]
        if "file_size" in fileData:
            self.file_size = fileData["file_size"]
        else:
            self.file_size = None

        if "file_path" in fileData:
            self.file_path = fileData["file_path"]
        else:
            self.file_path = None


    def __repr__(self):
        """
        () -> str
        Formal representantion for File object (a valid dictionary representation)
        """
        return str(self.__dict__)

class ReplyKeyboardMarkup:
    def __init__(self, keyboard, resize_keyboard=False, one_time_keyboard=False, selective=False):
        self.keyboard = keyboard
        self.resize_keyboard = resize_keyboard
        self.one_time_keyboard = one_time_keyboard
        self.selective = selective

    def toJSON(self):
        return json.dumps(self.__dict__)

    def __repr__(self):
        """
        () -> str
        Formal representantion for Location object (a valid dictionary representation)
        """
        return str(self.__dict__)

class ReplyKeyboardHide:
    def __init__(self, selective=False):
        self.hide_keyboard = True
        self.selective = selective

    def toJSON(self):
        return json.dumps(self.__dict__)

    def __repr__(self):
        """
        () -> str
        Formal representantion for Location object (a valid dictionary representation)
        """
        return str(self.__dict__)

class ForceReply:
    def __init__(self, selective=False):
        self.force_reply = True
        self.selective = selective

    def toJSON(self):
        return json.dumps(self.__dict__)

    def __repr__(self):
        """
        () -> str
        Formal representantion for Location object (a valid dictionary representation)
        """
        return str(self.__dict__)
