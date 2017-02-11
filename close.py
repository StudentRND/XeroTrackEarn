from xero import Xero
from xero.auth import PrivateCredentials
import json
import time
import sys
from datetime import datetime
import logging

class Accounting:
    def __init__(self):
        with open('config.json') as config_file:
            self.config = json.load(config_file)
        with open('keys/privatekey.pem', 'r') as keyfile:
            rsa_key = keyfile.read()
        credentials = PrivateCredentials(self.config['consumer_key'], rsa_key)
        self.xero = xero = Xero(credentials)

    def _getTrackingValues(self):
        if not(hasattr(self, 'cached_tracking')):
            self.cached_tracking = self.xero.trackingcategories.filter(Name=self.config['tracking'])[0]['Options']
        return {i['Name']: i['TrackingOptionID'] for i in self.cached_tracking if i['Status'] == 'ACTIVE'}

    def _getBalance(self, as_at, account, tracking):
        print "Querying {} for {}".format(account, tracking)
        time.sleep(1)
        r = self.xero.reports.get('BalanceSheet', params={
            'date': as_at,
            'standardLayout': True,
            'trackingOptionID1': self._getTrackingValues()[tracking]
        })[0]['Rows']

        sr = [i['Rows'] for i in r if 'Rows' in i and len(i['Rows']) > 0]
        sr = [j for i in sr for j in i]
        sr = [i['Cells'] for i in sr]

        a = {i[0]['Value']: i[1]['Value'] for i in sr}
        return a[account] if account in a else float(0)

    def _getTrackingBalance(self, as_at, account):
        all_balance = {i: self._getBalance(as_at, account, i) for i in self._getTrackingValues().keys()}
        return {x: float(y) for x, y in all_balance.iteritems() if y != 0}

    def _createAje(self, at, balances):
        lines = [[{
                'LineAmount': balance,
                'Description': 'To earn revenue from {}'.format(tracking),
                'AccountCode': self.config['unearned']['code'],
                'Tracking': { 'TrackingCategory': {
                    'Name': self.config['tracking'],
                    'Option': tracking
                }}
            },{
                'LineAmount': balance*-1,
                'Description': 'To earn revenue from {}'.format(tracking),
                'AccountCode': self.config['earned']['code'],
                'Tracking': { 'TrackingCategory': {
                    'Name': self.config['tracking'],
                    'Option': tracking
                }}
            }] for tracking, balance in sorted(balances.iteritems())]
        lines = [j for i in lines for j in i]
        self.xero.manualjournals.put({
            'Narration': 'To recognize earned revenue',
            'Date': datetime.strptime(at, '%Y-%m-%d'),
            'JournalLines': lines
        })

    def close(self, at):
        balances = self._getTrackingBalance(at, self.config['unearned']['name'])
        if len(balances) > 0:
            print "\n\nTracking Balance for {} as at {}".format(self.config['unearned']['name'], at)
            print "\n"
            for tracking, balance in sorted(balances.iteritems()):
                print "{:20}: {:>10.2f}".format(tracking, balance)

            print "\n\nCreating AJE..."
            self._createAje(at, balances)
        else:
            print "\n\nZero balance"


a = Accounting()
a.close(sys.argv[1])
