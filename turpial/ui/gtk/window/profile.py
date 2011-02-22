# -*- coding: utf-8 -*-

"""Ventana para mostrar perfiles de usuarios en Turpial"""
#
# Author: Wil Alvarez (aka Satanas)
# Feb 06, 2011

import gtk
import pango

from turpial.ui.gtk.waiting import CairoWaiting

class Profile(gtk.Window):
    def __init__(self, parent, profile=None):
        gtk.Window.__init__(self)
        
        self.padding = 8
        self.showed = False
        self.mainwin = parent
        self.set_title(_('Profile'))
        self.set_size_request(250, 280)
        self.set_transient_for(parent)
        self.set_resizable(False)
        self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        
        self.user_pic = gtk.Button()
        self.user_pic.set_size_request(60, 60)
        
        self.real_name = gtk.Label()
        self.real_name.set_alignment(0, 0.5)
        self.tweets_count = gtk.Label()
        self.tweets_count.set_alignment(0, 0.5)
        self.tweets_count.set_padding(5, 0)
        self.following_count = gtk.Label()
        self.following_count.set_alignment(0, 0.5)
        self.following_count.set_padding(5, 0)
        self.followers_count = gtk.Label()
        self.followers_count.set_alignment(0, 0.5)
        self.followers_count.set_padding(5, 0)
        self.location = gtk.Label()
        self.location.set_alignment(0, 0)
        self.location.set_padding(5, 2)
        self.url = gtk.Label()
        self.url.set_alignment(0, 0)
        self.url.set_padding(5, 2)
        
        self.bio = gtk.Label()
        self.bio.set_line_wrap(True)
        self.bio.set_alignment(0, 0)
        self.bio.set_padding(5, 0)
        self.bio.set_width_chars(30)
        
        self.web = gtk.Button(_('View profile'))
        self.dm = gtk.Button(_('DM'))
        
        self.lblerror = gtk.Label()
        self.lblerror.set_use_markup(True)
        self.waiting = CairoWaiting(self.mainwin)
        
        self.lblerror.set_markup("Hola mundo")
        self.waiting.stop(True)
        
        align = gtk.Alignment(xalign=1, yalign=0.5)
        align.add(self.waiting)
        
        pic_box = gtk.VBox(False)
        pic_box.pack_start(self.user_pic, False, False, 10)
        
        profile_box = gtk.VBox(False)
        profile_box.pack_start(self.real_name, False, False, 5)
        profile_box.pack_start(self.tweets_count, False, False)
        profile_box.pack_start(self.following_count, False, False)
        profile_box.pack_start(self.followers_count, False, False)
        
        info_box = gtk.HBox(False)
        info_box.pack_start(pic_box, False, False, self.padding)
        info_box.pack_start(profile_box, False, False)
        
        bio_box = gtk.HBox(False)
        bio_box.pack_start(self.bio, True, True, self.padding)
        
        location_box = gtk.HBox(False)
        location_box.pack_start(self.location, False, False, self.padding)
        
        url_box = gtk.HBox(False)
        url_box.pack_start(self.url, False, False, self.padding)
        
        buttons = gtk.HBox(True)
        buttons.pack_start(self.web, False, True, self.padding)
        buttons.pack_start(self.dm, False, True, self.padding)
        
        bottom = gtk.HBox(False)
        bottom.pack_start(self.lblerror, False, False, 2)
        bottom.pack_start(align, True, True, 2)
        
        vbox = gtk.VBox(False)
        vbox.pack_start(info_box, False, False)
        vbox.pack_start(bio_box, True, True)
        vbox.pack_start(location_box, False, False)
        vbox.pack_start(url_box, False, False)
        vbox.pack_start(buttons, False, False, self.padding)
        vbox.pack_start(bottom, False, False)
        
        self.connect('delete-event', self.__close)
        self.web.connect('clicked', self.__open_url)
        self.dm.connect('clicked', self.__send_dm)
        
        self.add(vbox)
        
    def __close(self, widget, event):
        if not self.working:
            self.user = None
            self.showed = False
            self.hide()
        return True
        
    def __open_url(self, widget):
        user_profile = '/'.join([self.mainwin.request_profiles_url(), self.user])
        self.mainwin.open_url(user_profile)
        
    def __send_dm(self, widget):
        dm = "D @%s " % self.user
        self.mainwin.show_update_box(dm,)
        
    def show(self, user):
        self.showed = True
        self.working = True
        self.user = user
        self.set_title(_('Profile: %s') % user)
        self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        avatar = gtk.Image()
        avatar.set_from_pixbuf(None)
        self.user_pic.set_image(avatar)
        self.real_name.set_markup('<b>%s</b>' % _('Loading...'))
        self.tweets_count.set_markup('')
        self.following_count.set_markup('')
        self.followers_count.set_markup('')
        self.location.set_text('')
        self.url.set_text('')
        self.bio.set_text('')
        self.show_all()
        self.start_update()
        
    def update(self, response):
        self.working = False
        # FIXME: Mejorar esta validación
        try:
            if response.type == 'error':
                self.stop_update(True, response.errmsg)
                return
            profile = response.items
        except:
            profile = response
        
        pix = self.mainwin.get_user_avatar(self.user, profile.avatar)
        avatar = gtk.Image()
        avatar.set_from_pixbuf(pix)
        self.user_pic.set_image(avatar)
        del pix
        self.real_name.set_markup('<b>%s</b>' % profile.fullname)
        self.tweets_count.set_markup('<span size="9000">%i Tweets</span>' % \
                                     profile.statuses_count)
        self.following_count.set_markup('<span size="9000">%i Following</span>' % \
                                        profile.friends_count)
        self.followers_count.set_markup('<span size="9000">%i Followers</span>' % \
                                        profile.followers_count)
        if profile.bio:
            self.bio.set_text(profile.bio)
        if profile.location:
            self.location.set_markup('<b>%s</b>: %s' % (_('Location'), 
                profile.location))
        if profile.url:
            self.url.set_markup('<b>%s</b>: %s' % (_('URL'), profile.url))
        self.stop_update()
        
    def update_user_pic(self, user, pic):
        if not self.showed or self.user != user:
            return
        pix = self.mainwin.load_avatar(self.mainwin.imgdir, pic, True)
        self.user_pic.set_image(pix)
        
    def lock(self):
        self.web.set_sensitive(False)
        self.dm.set_sensitive(False)
    
    def unlock(self):
        self.web.set_sensitive(True)
        self.dm.set_sensitive(True)
        
    def update_wrap(self, w):
        pass
        
    def start_update(self):
        self.lock()
        self.waiting.start()
        self.lblerror.set_markup("")
        
    def stop_update(self, error=False, msg=''):
        self.unlock()
        self.waiting.stop(error)
        self.lblerror.set_markup(u"<span size='small'>%s</span>" % msg)
