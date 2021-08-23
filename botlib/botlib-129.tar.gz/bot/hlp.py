# This file is placed in the Public Domain.


from obj import Object, keys, get

def __dir__():
    return ("hlp",)

cmds = "cfg,cmd,dlt,dne,dpl,flt,fnd,ftc,log,met,mre,nck,ops,rem,req,rss,slg,tdo,thr,upt"

h = Object()
h.cfg = "cfg <key=val> sets a irc configuration value, no val shows the config content"
h.cmd = "cmd shows list of commands"
h.dlt = "dlt <userhost> deletes a user"
h.dne = "dne <match> flags a todo item as done"
h.dpl = "rss <url> sets rss items to display"
h.flt = "flt shows a list of bots"
h.ftc = "ftc fetches rss feeds"
h.hlp = "hlp <command> shows help text"
h.met = "met <userhost> introduces a user"
h.mre = "mre shows next batch in cache"
h.nck = "nick <nickname> changes nickname"
h.ops = "ops gives operator status"
h.rem = "rem <match> removes feed"
h.req = "req shows request to the prosecutor"
h.rss = "rss <url> adds a rss item"
h.slg = "slg shows referennce"
h.thr = "lists running threads"
h.upt = "display uptime"

def hlp(event):
    if not event.rest:
        event.reply("hlp <%s>" % "|".join(keys(h)))
        return
    event.reply(get(h, event.args[0], None) or "no help found")
