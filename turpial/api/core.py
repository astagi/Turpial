# -*- coding: utf-8 -*-

'''Minimalistic and agnostic core for Turpial'''
#
# Author: Wil Alvarez (aka Satanas)
# Mar 06, 2011

import Queue
import logging
import traceback

from turpial.api.protocols.twitter import twitter
from turpial.api.protocols.identica import identica
from turpial.api.interfaces.post import Response
from turpial.config import PROTOCOLS

from turpial.api.models import Account

PROTOCOLS = {
    'twitter': twitter.Main(),
    'identica': identica.Main(),
}

class Core:
    '''Turpial core'''
    def __init__(self):
        self.queue = Queue.Queue()
        logging.basicConfig(level=logging.DEBUG)
        self.log = logging.getLogger('Core')
        self.log.debug('Started')
        self.accounts = {}
        
    def register_account(self, username, password, protocol, remember):
        self.log.debug('Registering account %s' % username)
        aid = "%s-%s" % (username, protocol)
        account = Account()
        account.username = username
        account.password = password
        #TODO: Validate protocol
        account.protocol = protocol
        self.accounts[aid] = account
        
    def login(self):
        for aid, acc in self.accounts.iteritems():
            self.log.debug('Authenticating %s' % acc)
            try:
                rtn = PROTOCOLS[acc.protocol].auth(acc.username, acc.password)
            except TurpialException, exc:
                
            except Exception, exc:
                
            print rtn
            
    
    
        
