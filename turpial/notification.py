# -*- coding: utf-8 -*-

"""Clase para manejar todas las notificaciones de Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# Dic 27, 2009

import os
import logging

log = logging.getLogger('Notify')

try:
    import pynotify
    NOTIFY = True
except ImportError:
    log.debug("pynotify is not installed")
    NOTIFY = False

class Notification:
    """Manejo de notificaciones"""
    def __init__(self, disable):
        if disable:
            self.deactivate()
            log.debug('Módulo deshabilitado')
        else:
            self.activate()
        iconpath = os.path.join(os.path.dirname(__file__), 'data', 'pixmaps', 
            'turpial-notification.png')
        self.default_icon = os.path.realpath(iconpath)
    
    def __popup(self, title, message, icon=None):
        if not NOTIFY
            return
        
        if not self.active:
            log.debug('Módulo deshabilitado. No hay notificaciones')
            return
        
        try:
            if pynotify.init("Turpial"):
                if not icon:
                    icon = self.default_icon
                icon = "file://%s" % icon
                notification = pynotify.Notification(title, message, icon)
                notification.show()
        except Exception, e:
            log.debug('Error en notificacion: %s' % e)
    
    def toggle_activation(self):
        if self.active:
            self.active = False
        else:
            self.active = True
    
    def activate(self):
        self.active = True
        
    def deactivate(self):
        self.active = False
    
    def new_tweets(self, title, count, tobject, tweet, icon):
        self.__popup('%s (%i %s)' % (title, count, tobject), tweet, icon)
        
    def login(self, p):
        self.__popup('@%s' % p.username,
            '%s: %i\n%s: %i\n%s: %i' % 
            (_('Tweets'), p.statuses_count,
            _('Following'), p.friends_count, 
            _('Followers'), p.followers_count))
    
    def login_error(self, message):
        self.__popup(_('Authentication error'), message)
        
    def following(self, user, follow):
        name = user.username
        if follow:
            self.__popup(_('Turpial (Follow)'), 
                _('You are now following @%s') % name)
        else:
            self.__popup(_('Turpial (Unfollow)'), 
                _('You are no longer following @%s') % name)
                
    def following_error(self, message, follow):
        if follow:
            self.__popup(_('Turpial (Follow)'), message)
        else:
            self.__popup(_('Turpial (Unfollow)'), message)
