# -*- coding: utf-8 -*-

# Widget para mostrar tweets en Turpial
#
# Author: Wil Alvarez (aka Satanas)
# Dic 20, 2009

import gtk
import pango
import gobject
import logging
import webbrowser
import xml.sax.saxutils as saxutils

from waiting import *
from ui import util as util

log = logging.getLogger('Gtk:Tweetlist')

class TweetList(gtk.VBox):
    def __init__(self, mainwin, label='', menu=True):
        gtk.VBox.__init__(self, False)
        
        self.last = None    # Last tweets updated
        self.mainwin = mainwin
        
        self.list = gtk.TreeView()
        self.list.set_headers_visible(False)
        self.list.set_events(gtk.gdk.POINTER_MOTION_MASK)
        self.list.set_level_indentation(0)
        self.list.set_rules_hint(True)
        self.list.set_resize_mode(gtk.RESIZE_IMMEDIATE)
        '''
        try:
            self.list.set_has_tooltip(True)
        except:
            pass
        self.list.connect("query-tooltip", self.show_tooltip)
        '''
        self.label = gtk.Label(label)
        self.caption = label
        
        self.lblerror = gtk.Label()
        self.lblerror.set_use_markup(True)
        self.waiting = CairoWaiting(self)
        align = gtk.Alignment(xalign=1, yalign=0.5)
        align.add(self.waiting)
        
        bottombox = gtk.HBox(False)
        bottombox.pack_start(self.lblerror, False, False, 2)
        bottombox.pack_start(align, True, True, 2)
        
        scroll = gtk.ScrolledWindow()
        scroll.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        scroll.set_shadow_type(gtk.SHADOW_IN)
        scroll.add(self.list)
        
        self.model = gtk.ListStore(
            gtk.gdk.Pixbuf, # avatar
            str, #username
            str, #datetime
            str, #client
            str, #pango_message
            str, #real_message
            str, # id
            bool, #favorited?
            gobject.TYPE_PYOBJECT, # in_reply_to_id
            gobject.TYPE_PYOBJECT, # in_reply_to_user
            gobject.TYPE_PYOBJECT, # retweeted_by
            gobject.TYPE_PYOBJECT, # doing what operation?
            bool, #direct message?
        )
        self.list.set_model(self.model)
        cell_avatar = gtk.CellRendererPixbuf()
        cell_avatar.set_property('yalign', 0)
        self.cell_tweet = gtk.CellRendererText()
        self.cell_tweet.set_property('wrap-mode', pango.WRAP_WORD)
        self.cell_tweet.set_property('wrap-width', 260)
        self.cell_tweet.set_property('yalign', 0)
        self.cell_tweet.set_property('xalign', 0)
        
        column = gtk.TreeViewColumn('tweets')
        column.set_alignment(0.0)
        column.pack_start(cell_avatar, False)
        column.pack_start(self.cell_tweet, True)
        column.set_attributes(self.cell_tweet, markup=4)
        column.set_attributes(cell_avatar, pixbuf=0)
        self.list.append_column(column)
        
        if menu:
            self.list.connect("button-release-event", self.__popup_menu)
            
        self.pack_start(scroll, True, True)
        self.pack_start(bottombox, False, False)
        
    def __highlight_hashtags(self, text):
        hashtags = util.detect_hashtags(text)
        if len(hashtags) == 0: return text
        
        for h in hashtags:
            torep = '#%s' % h
            cad = '<span foreground="#FF6633">#%s</span>' % h
            text = text.replace(torep, cad)
        return text
        
    def __highlight_mentions(self, text):
        mentions = util.detect_mentions(text)
        if len(mentions) == 0: return text
        
        for h in mentions:
            if len(h) == 1: continue
            torep = '@%s' % h
            cad = '<span foreground="#FF6633">@%s</span>' % h
            text = text.replace(torep, cad)
        return text
        
    def __highlight_urls(self, text):
        urls = util.detect_urls(text)
        if len(urls) == 0: return text
        
        for u in urls:
            cad = '<span foreground="#FF6633">%s</span>' % u
            text = text.replace(u, cad)
        return text
        
    '''
    def show_tooltip(self, widget, x, y, keyboard_mode, tooltip):
        #rel_y = self.get_property('vadjustment').value
        
        #path = widget.get_path_at_pos(int(x), int(y + rel_y))
        path = widget.get_path_at_pos(int(x), int(y))
        if path is None: return False
        
        model = widget.get_model()
        iter = model.get_iter(path[0])
        
        pix = model.get_value(iter, 0)
        msg = "<b>En respuesta a</b>:\n%s" % model.get_value(iter, 4)
        tooltip.set_icon(pix)
        tooltip.set_markup(msg)
        del pix
        
        return True
    '''
    
    def __popup_menu(self, widget, event):
        model, row = widget.get_selection().get_selected()
        if (row is None): return False
        
        if (event.button == 3):
            user = model.get_value(row, 1)
            msg = model.get_value(row, 5)
            id = model.get_value(row, 6)
            
            menu = gtk.Menu()
            
            rtn = self.mainwin.request_popup_info(id, user)
            
            if rtn.has_key('busy'):
                busymenu = gtk.MenuItem(rtn['busy'])
                busymenu.set_sensitive(False)
                menu.append(deleting)
            else:
                re = "@%s " % user
                rt = "RT @%s %s" % (user, msg)
                dm = "D @%s " % user
                
                reply = gtk.MenuItem('Reply')
                retweet_old = gtk.MenuItem('Retweet (Old fashion)')
                retweet = gtk.MenuItem('Retweet')
                save = gtk.MenuItem('+ Fav')
                unsave = gtk.MenuItem('- Fav')
                delete = gtk.MenuItem('Delete')
                open = gtk.MenuItem('Open')
                search = gtk.MenuItem('Search')
                direct = gtk.MenuItem('DM')
                follow = gtk.MenuItem('Follow')
                unfollow = gtk.MenuItem('Unfollow')
                loading = gtk.MenuItem('Cargando amigos...')
                loading.set_sensitive(False)
                usermenu = gtk.MenuItem('@'+user)
                
                open_menu = gtk.Menu()
                
                total_urls = util.detect_urls(msg)
                total_users = util.detect_mentions(msg)
                
                for u in total_urls:
                    umenu = gtk.MenuItem(u)
                    umenu.connect('button-release-event', self.__open_url2, u)
                    open_menu.append(umenu)
                
                if len(total_urls) > 0 and len(total_users) > 0: 
                    open_menu.append(gtk.SeparatorMenuItem())
                
                for m in total_users:
                    if m == user: continue
                    user_prof = '/'.join(['http://www.twitter.com', m])
                    mentmenu = gtk.MenuItem('@'+m)
                    mentmenu.connect('button-release-event', self.__open_url2, user_prof)
                    open_menu.append(mentmenu)
                
                if not rtn['own']:
                    menu.append(reply)
                    menu.append(retweet_old)
                    menu.append(retweet)
                    menu.append(direct)
                    
                    if not rtn.has_key('friend'):
                        item = loading
                    elif rtn['friend'] is True:
                        item = unfollow
                    elif rtn['friend'] is False:
                        item = follow
                else:
                    menu.append(delete)
                    
                if rtn['fav']:
                    menu.append(unsave)
                else:
                    menu.append(save)
                    
                if (len(total_urls) > 0) or (len(total_users) > 0): 
                    open.set_submenu(open_menu)
                    menu.append(open)
                
                menu.append(gtk.SeparatorMenuItem())
                menu.append(usermenu)
                if not rtn['own']: menu.append(item)
                
                user_profile = '/'.join(['http://www.twitter.com', user])
                usermenu.connect('activate', self.__open_url, user_profile)
                reply.connect('activate', self.__show_update_box, re, id, user)
                retweet_old.connect('activate', self.__show_update_box, rt)
                retweet.connect('activate', self.__retweet, id)
                direct.connect('activate', self.__show_update_box, dm)
                save.connect('activate', self.__fav, True, id)
                unsave.connect('activate', self.__fav, False, id)
                delete.connect('activate', self.__delete, id)
                follow.connect('activate', self.__follow, True, user)
                unfollow.connect('activate', self.__follow, False, user)
            
            menu.show_all()
            menu.popup(None, None, None, event.button ,event.time)
        
    def __open_url2(self, widget, event, url):
        if (event.button == 1) or (event.button == 3):
            log.debug('Opening url %s' % url)
            webbrowser.open(url)
        
    def __open_url(self, widget, url):
        log.debug('Opening url %s' % url)
        webbrowser.open(url)
        
    def __show_update_box(self, widget, text, in_reply_id='', in_reply_user=''):
        self.mainwin.show_update_box(text, in_reply_id, in_reply_user)
        
    def __retweet(self, widget, id):
        self.mainwin.request_retweet(id)
        
    def __delete(self, widget, id):
        self.mainwin.request_destroy_status(id)
    
    def __fav(self, widget, fav, id):
        if fav:
            self.mainwin.request_fav(id)
        else:
            self.mainwin.request_unfav(id)
    
    def __follow(self, widget, follow, user):
        if follow:
            self.mainwin.request_follow(user)
        else:
            self.mainwin.request_unfollow(user)
        
    def update_wrap(self, val):
        self.cell_tweet.set_property('wrap-width', val - 80)
        iter = self.model.get_iter_first()
        
        while iter:
            path = self.model.get_path(iter)
            self.model.row_changed(path, iter)
            iter = self.model.iter_next(iter)
        
    def add_tweet(self, tweet):
        direct = False
        retweet_by = None
        if tweet.has_key('retweeted_status'):
            retweet_by = tweet['user']['screen_name']
            tweet = tweet['retweeted_status']
            
        if tweet.has_key('user'):
            username = tweet['user']['screen_name']
            avatar = tweet['user']['profile_image_url']
        elif tweet.has_key('sender'):
            direct = True
            username = tweet['sender']['screen_name']
            avatar = tweet['sender']['profile_image_url']
        elif tweet.has_key('from_user'):
            username = tweet['from_user']
            avatar = tweet['profile_image_url']
            
        client = util.detect_client(tweet)
        datetime = util.get_timestamp(tweet)
        
        pix = self.mainwin.get_user_avatar(username, avatar)
        #print 'message', tweet['text']
        tweet['text'] = saxutils.unescape(tweet['text'])
        message = gobject.markup_escape_text(tweet['text'])
        #print 'pango_message', message
        message = '<span size="9000"><b>@%s</b> %s</span>' % (username, message)
        message = self.__highlight_hashtags(message)
        message = self.__highlight_mentions(message)
        message = self.__highlight_urls(message)
        interline = '<span size="2000">\n\n</span>'
        
        footer = '<span size="small" foreground="#999">%s' % datetime
        if client:
            footer += ' desde %s' % client
        
        in_reply_to_id = None
        in_reply_to_user = None
        if tweet.has_key('in_reply_to_status_id'):
            in_reply_to_id = tweet['in_reply_to_status_id']
            in_reply_to_user = tweet['in_reply_to_screen_name']
            if in_reply_to_user:
                footer += ' en respuesta a %s' % in_reply_to_user
        
        if retweet_by:
            footer += '\nRetweeted by %s' % retweet_by
            
        footer += '</span>'
        
        fav = False
        if tweet.has_key('favorited'): fav = tweet['favorited']
        
        pango_twt = message + interline + footer
        self.model.append([pix, username, datetime, client, pango_twt, tweet['text'],
            tweet['id'], fav, in_reply_to_id, in_reply_to_user, retweet_by, None, direct])
        del pix
        
    def update_user_pic(self, user, pic):
        # Evaluar si es más eficiente esto o cargar toda la lista cada vez
        pix = util.load_avatar(self.mainwin.imgdir, pic)
        iter = self.model.get_iter_first()
        while iter:
            u = self.model.get_value(iter, 1)
            if u == user:
                self.model.set_value(iter, 0, pix)
            iter = self.model.iter_next(iter)
        del pix
        
    def update_tweets(self, arr_tweets):
        if arr_tweets is None:
            self.waiting.stop(error=True)
            self.lblerror.set_markup("<span size='small'>Error intentando actualizar</span>")
            return 0
        else:
            count = util.count_new_tweets(arr_tweets, self.last)
            self.waiting.stop()
            self.lblerror.set_markup("")
            self.model.clear()
            for tweet in arr_tweets:
                self.add_tweet(tweet)
            self.last = arr_tweets
            
            return count
