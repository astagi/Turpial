# -*- coding: utf-8 -*-

"""Módulo genérico para manejar los post de microblogging en Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# May 20, 2010

class Status:
    def __init__(self):
        self.id = None
        self.text = None
        self.username = None
        self.avatar = None
        self.source = None
        self.timestamp = None   # Store the timestamp in Unix time
        self.in_reply_to_id = None
        self.in_reply_to_user = None
        self.is_favorite = False
        self.reposted_by = None
        self.datetime = None    # Store the date/time showed for the view
        self.type = None
        self.protocol = None
        self.is_own = False

class Response:
    def __init__(self, items=None):
        if not items:
            self.items = []
        else:
            self.items = items
    
    def __len__(self):
        len(self.items)
    
    def add(self, item):
        self.items.append(item)
        
class ErrorResponse:
    def __init__(self, message):
        self.errmsg = message
        
class StatusResponse(Response):
    def __init__(self, statuses=None):
        Response.__init__(self, statuses)
        
class ProfileResponse(Response):
    def __init__(self, profiles=None):
        Response.__init__(self, profiles)
        
class Account:
    def __init__(self):
        self.id = None
        self.fullname = None
        self.username = None
        self.avatar = None
        self.location = ''
        self.url = ''
        self.bio = ''
        self.following = None
        self.followers_count = None
        self.friends_count = None
        self.password = None
        self.profile_link_color = None
        self.statuses_count = None
        self.last_update = None
        self.last_update_id = None
        self.recent_updates = []
        self.tmp_avatar_path = None
        self.protocol = None
        self.key = None
        self.secret = None

class List:
    def __init__(self):
        self.id = None
        self.slug = None
        self.name = None
        self.mode = None
        self.user = None
        self.member_count = None
        self.description = None
        
class RateLimit:
    def __init__(self):
        self.hourly_limit = None
        self.remaining_hits = None
        self.reset_time = None
        self.reset_time_in_seconds = None
