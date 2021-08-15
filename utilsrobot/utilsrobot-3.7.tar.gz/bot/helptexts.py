#================================================================================================================================
warnhelpp = """
Here is The help of Warns Module
Admin COmmands
 - /warn <userid> | <reason> or /warn <reason> in reply to a message: warn a user
 - /removelastwarn: remove the last warn that a user has received
 - /getwarns: list the warns that a user has received
 - /resetwarns: reset all warns that a user has received
 - /setwarnmode <kick/ban/mute>: set the warn mode for the chat
"""

blacklisthelpp = """
 - /addblacklist <trigger> : blacklists the trigger
 - /rmblacklist <trigger> : stop blacklisting a certain blacklist trigger
 - /listblacklist: list all active blacklist filters
 - /geturl: View the current blacklisted urls
 - /addurl <urls>: Add a domain to the blacklist. The bot will automatically parse the url.
 - /delurl <urls>: Remove urls from the blacklist.
**Example:**
 - /addblacklist the admins suck: This will remove "the admins suck" everytime some non-admin types it
 - /addurl bit.ly: This would delete any message containing url "bit.ly"
"""

ruless = """
Here is the help for the Rules module:
Admin Commands :-
 - /setrules <rules>: set the rules for this chat
 - /clearrules: clears the rules for this chat
Normal User Commands :-
 - /rules: get the rules for this chat
"""

welcomehelpp = """
Here is the help for the Welcome module:

Admin Commands:
 - /savewelcome <text>: Set a new welcome message. Supports markdown and fillings.
 - /welcome : See Your Current Welcome Message
 - /clearwelcome : Clears Your Current Welcome Message
"""

filterrhelp = """
Here is the help for the Filters module:

 • /filters: List all active filters saved in the chat.

Admin only:-
 • /savefilter <keyword> <reply message>: Add a filter to this chat. The bot will now reply that message whenever 'keyword'is mentioned. If you reply to a sticker with a keyword, the bot will reply with that sticker. NOTE: all filter keywords are in lowercase.
 • /stop <filter keyword>: Stop that filter.

Chat creator only:-
 • /removeallfilters: Remove all chat filters at once.
"""

promotehelpp = """
**Here is the help for the Promote Module**

• /promote `<reply to user/userid/username>`
    **Promote the user in the chat.**

• /demote `<reply to user/userid/username>`
    **Demote the user in the chat.**
"""

banhelpp = """
**Here is the help for the Bans Module**

• /ban `<reply to user/userid/username> <reason>`
    **Ban the user from the chat.**

• /unban `<reply to user/userid/username> <reason>`
    **Unban the user from the chat.**
"""

kickhelpp = """
**Here is the help for the Kick Module**

• /kick `<reply to user/userid/username> <reason>`
    **Kick the user from the chat.**
"""

pinhelpp = """
**Here is the help for the Pin/Unpin Module**

• /pin `<reply to message>`
    **Pin the message in the chat**
    **For Loud pin use (`/pin loud`).**

• /unpin `<reply to message>`
    **Unpin the message in the chat**
    **For Unpinning All Messages Use (`/unpin all`).**

"""
purgehelpp = """
**Here is the help for the Purge Module**

• /purge `<reply to message>`
    **Purge all messages from the replied message.**

• /del `<reply to message>`
    **Deletes The Replied Message.**
"""
notesshelp = """
Here is the help for the Notes module:

 • `#<notename>`: To Get The Note
 • /notes : list all saved notes in this chat
 
Admins only:
 • /save <notename> <reply message> :  save the replied message as a note with name notename
 • /clear <notename>: clear note with this name
 
 Chat Creator Only:
 • /removeallnotes: removes all notes from the group
 
 Note: Note names are case-insensitive, and they are automatically converted to lowercase before getting saved.
 """
lockktypes = """
Available message types to lock/unlock are: 
- `all` 
- `msg` 
- `media`
- `sticker`
- `gif`
- `game`
- `inline`
- `poll`
- `invite`
- `pin`
- `info`
"""

lockhelpp = """Here is The Help For Notes Module 

Do stickers annoy you? or want to avoid people sharing links? or pictures? You're in the right place!

The locks module allows you to lock away some common items in the telegram world; the bot will automatically delete them!

Admin commands:
- /lock <item>: Lock one or more items. Now, only admins can use this type!
- /unlock <item>: Unlock one or more items. Everyone can use this type again!
- /locktypes: Show the list of all lockable items."""

antifloodhelpp= """
Antiflood allows you to take action on users that send more than x messages in a row.
Exceeding the set flood will result in restricting that user.
This will mute users if they send more than 10 messages in a row, bots are ignored.
 - /flood: Get the current flood control setting
**Admins only:**
 - /setfloodlimit <int/'off'>: enables or disables flood control
Example: /setflood 10
 - /setfloodmode <ban/kick/mute/tban/tmute> <value>: Action to perform when user have exceeded flood limit. ban/kick/mute/tmute/tban
**Note:**
Value must be filled for tban and tmute
It can be:
5m = 5 minutes
6h = 6 hours
3d = 3 days
1w = 1 week
"""

#==========================================================================
