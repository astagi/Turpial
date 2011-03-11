# -*- coding: utf-8 -*-

'''Minimalistic and agnostic core for Turpial'''
#
# Author: Wil Alvarez (aka Satanas)
# Mar 06, 2011

import os
import Queue
import logging
import gettext
import traceback

from turpial.config import PROTOCOLS
from turpial.api.interfaces.post import Response
from turpial.api.protocols.twitter import twitter
from turpial.api.protocols.identica import identica
from turpial.api.interfaces.http import TurpialException
from turpial.api.models import Account, ProfileResponse, ErrorResponse

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
        
        # Initialize gettext
        gettext_domain = 'turpial'
        # Definicion de localedir en modo desarrollo
        if os.path.isdir(os.path.join(os.path.dirname(__file__), '..', 'i18n')):
            localedir = os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'i18n'))
            trans = gettext.install(gettext_domain, localedir)
            self.log.debug('Locale Dir %s' % localedir)
        else:
            trans = gettext.install(gettext_domain)
        
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
        response = ProfileResponse()
        for aid, acc in self.accounts.iteritems():
            self.log.debug('Authenticating %s' % acc)
            try:
                rtn = PROTOCOLS[acc.protocol].auth(acc.username, acc.password)
                response.add(rtn)
            except TurpialException, exc:
                self.log.debug('%s' % exc.msg)
                return ErrorResponse(exc.msg)
            except Exception, exc:
                print traceback.print_exc()
                self.log.debug('Authentication Error')
                return ErrorResponse(_('Authentication Error'))
        return response
