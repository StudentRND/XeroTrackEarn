XeroTrackEarn is a utility to help us add manual journals to Xero to earn revenue across
a tracking category.

You'll need a Xero app to use it: populate the keys folder as described
[here](https://developer.xero.com/documentation/api-guides/create-publicprivate-key),
then register your app [here](https://app.xero.com/Application/).

Copy config.json to config.json.sample, and configure your tracking category of choice as
well as unearned and earned revenue accounts, and your Xero consumer key. You will need
to specify both the account name and code, because the API is inconsistent.

Run `python close.py YYYY-MM-DD`, where YYYY-MM-DD represents the date you'd like your
revenue earned. The program will get your unearned account balance across the tracking
regions, display the balance, and then automatically generate a draft manual journal.

If it all looks good, go ahead and post the journal in Xero! Your revenue is earned!

(Note that this will NOT earn any revenue without a tracking category option. If your
unearned liability account is still showing a balance at the date you specified, run
an account transactions report, and set the Tracking option to Uncategorized.)
