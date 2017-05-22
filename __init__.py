"""
Python package for Telegram Bots API
"""

__version__ = "0.1"
__author__ = "renan.lino@gmail.com"

from .types import (Update, User, Chat, Message, PhotoSize,
					Audio, Voice, Document, Sticker, Video, Contact,
					Location, InputFile, UserProfilePhotos, File,
					ReplyKeyboardMarkup, ReplyKeyboardHide, ForceReply)
from .bot import Bot
from ._aux import openFile

__all__ = [Update, User, Chat, Message, PhotoSize,
					Audio, Voice, Document, Sticker, Video, Contact,
					Location, InputFile, UserProfilePhotos, File,
					ReplyKeyboardMarkup, ReplyKeyboardHide, ForceReply]
