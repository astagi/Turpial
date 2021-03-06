# -*- coding: utf-8 -*-

# PyQT account form view for Turpial
#
# Author:  Carlos Guerrero (aka guerrerocarlos)
# Started: Sep 11, 2011

import logging
from PyQt4 import QtGui
from PyQt4.QtWebKit import *

from turpial.ui.html import HtmlParser
from turpial.ui.qt.htmlview import HtmlView

log = logging.getLogger('PyQt4')

class AccountForm(QtGui.QDialog):
    def __init__(self, parent, plist, user=None, pwd=None, protocol=None):
        super(AccountForm,self).__init__()
        
        self.accwin = parent
        self.htmlparser = HtmlParser(None)
        self.setWindowTitle('Create Account')
        self.resize(290, 200)
        self.finished.connect(self.__close)
        
        self.container = HtmlView()
        self.container.page().setLinkDelegationPolicy(QWebPage.DelegateAllLinks)
        self.container.page().linkClicked.connect(self.__link_request)
        self.container.page().loadStarted.connect(self.__load_request)
        self.layout = QtGui.QVBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.addWidget(self.container)
        self.setLayout(self.layout)
        
        page = self.htmlparser.account_form(plist)
        self.container.setHtml(page)
        self.show()
        self.working = False
        
    def __close(self, event=None):
        self.hide()


    def __load_request(self): 
        try:
            url = self.container.page().mainFrame().documentElement().findAll('#query')[0].attribute("src")
        except:
            url = ""
        self.__action_request(url)

    def __link_request(self,url):
        self.__action_request(str(url.toString()))

    def __action_request(self,url):
        print url

        action = url.split(':')[1]
        try:
            args = url.split(':')[2].split('-%&%-')
        except IndexError:
            args = []
        
        if action == "//close":
            self.__close()
        elif action == "//save_account":
            self.working = True
            print "mandando a guardar"
            self.accwin.save_account(args[0], args[1], args[2])
            self.done_login()
            print "terminado de guardar"
    
    def cancel_login(self, message):
        self.container.execute("cancel_login('" + msg + "');")
    
    def done_login(self):
        self.hide()
