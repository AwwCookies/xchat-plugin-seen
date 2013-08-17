# THIS IS A XChat/HexChat PLUGIN #
# MAKE SURE TO NEVER LOAD MORE THAN ONE COPY #
##########################################
__module_author__ = 'Aww'
__module_name__ = 'Seen Database'
__module_version__ = '1.1.0'
__module_description__ = 'Seen Database made with sqlite3 and Python'
##########################################
import sqlite3, xchat, datetime, os
class Seen:
    def __init__(self):
        # Auto Delete after database size gets bigger than <some size>
        # self.max_size = (1024 * 1024) * 1024
        if os.name != "posix":
            self.dbconnection = sqlite3.connect(xchat.get_info("xchatdir") + "\\seen.db")
        else:
            self.dbconnection = sqlite3.connect(xchat.get_info("xchatdir") + "/seen.db")
        self.curs = self.dbconnection.cursor()
        self.curs.execute("CREATE TABLE IF NOT EXISTS seen (nick TEXT UNIQUE, msg TEXT)")

    def commit(self, word = None, word_eol = None, userdata = None):
        self.dbconnection.commit()

    def on_unload(self, userdata = None):
        self.dbconnection.commit()
        self.dbconnection.close()

    def parse(self, word, word_eol, userdata = None):
        tempdata = word_eol[0].replace('!', ' ', 1).split()
        data = {
            "Nick": tempdata[0].lstrip(':'),
            "Host": tempdata[1],
            "Type": tempdata[2],
            "Channel": tempdata[3],
            "Message": ' '.join(tempdata[4:]).replace(':', '', 1)
        }
        self.update(data)

    def update(self, data):
        now = datetime.datetime.now().strftime("%B %d, %Y at %I:%M %p %Z")
        msg = "%s was last seen on channel %s on %stheir last message was: %s" % (
            data["Nick"], data["Channel"], now, data["Message"].replace('"', "'"))
        try:
            self.curs.execute('REPLACE INTO seen (nick, msg) VALUES ("%s", "%s")' % (data["Nick"], msg))
        except sqlite3.OperationalError:
            print "ERROR(seen.py - sqlite3.OperationalError): Someone said something funny :-/"

    def lastseen(self, word, word_eol, userdata = None):
        found = False
        if word[1] == '-w':
            if len(word) > 2:
                for nick in self.curs.execute("SELECT * FROM seen WHERE nick LIKE '%s'" % word[2]):
                    xchat.prnt(nick[1])
                    found = True
                if not found:
                    print "%s was not found in the database." % word[2]
            else:
                xchat.prnt("/seen <nick>")
                xchat.prnt("Example: /seen Aww")
        else:
            if len(word) > 1:
                for nick in self.curs.execute("SELECT * FROM seen WHERE nick='%s'" % word[1]):
                    xchat.prnt(nick[1])
                    found = True
                if not found:
                    print "%s was not found in the database." % word[1]
            else:
                xchat.prnt("/seen <nick>")
                xchat.prnt("Example: /seen Aww")

    def info(self, word = None, word_eol = None, userdata = None):
        for response in self.curs.execute("SELECT Count(*) FROM seen"):
            num_of_entrys = response[0]
            break
        if os.name != "posix":
            db_size = os.path.getsize(xchat.get_info("xchatdir") + "\\seen.db")
            db_file = xchat.get_info("xchatdir") + "\\seen.db"
            if os.path.exists(xchat.get_info("xchatdir") + "/seen.db-journal"):
                temp_db_size = os.path.getsize(xchat.get_info("xchatdir") + "\\seen.db-journal")
            else:
                temp_db_size = 0
            temp_db_file = xchat.get_info("xchatdir") + "\\seen.db-journal"
        else:
            db_size = os.path.getsize(xchat.get_info("xchatdir") + "/seen.db")
            if os.path.exists(xchat.get_info("xchatdir") + "/seen.db-journal"):
                temp_db_size = os.path.getsize(xchat.get_info("xchatdir") + "/seen.db-journal")
            else:
                temp_db_size = 0
            db_file = xchat.get_info("xchatdir") + "/seen.db"
            temp_db_file = xchat.get_info("xchatdir") + "/seen.db-journal"
        xchat.prnt(
            "13Seen database info: \n13Size: %.2fKB \n13Temp Size: %.2fKB "
            "\n13Entries: %d \n13File: %s\n13Temp File: %s" % (
            float(db_size)/1024.0, float(temp_db_size/1024.0), int(num_of_entrys), db_file, temp_db_file))

seen = Seen()
xchat.hook_unload(seen.on_unload)
xchat.hook_server("PRIVMSG", seen.parse)
xchat.hook_command("seen", seen.lastseen)
xchat.hook_command("seen->info", seen.info)
xchat.hook_command("seen->commit", seen.commit)
xchat.prnt("%s version %s by %s has been loaded." % (__module_name__, __module_version__, __module_author__))
seen.info();
# xchat.prnt("04Note: NEVER LOAD THIS MORE THEN ONCE! IF YOU NEED TO RELOAD IT MAKE SURE TO UNLOAD IT FIRST!!")
