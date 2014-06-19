import sqlite3
import subprocess
import CalendarCredentials

# Radio stations we can play through mplayer
STATIONS = [
   {'name':'BBC Radio 1', 'url':'http://bbc.co.uk/radio/listen/live/r1.asx'},
   {'name':'BBC Radio 2', 'url':'http://bbc.co.uk/radio/listen/live/r2.asx'},
   {'name':'Capital FM', 'url':'http://ms1.capitalinteractive.co.uk/fm_high'},
   {'name':'Kerrang Radio', 'url':'http://tx.whatson.com/icecast.php?i=kerrang.aac.m3u'},
   {'name':'Magic 105.4', 'url':'http://tx.whatson.com/icecast.php?i=magic1054.aac.m3u'},
   {'name':'Smooth Radio', 'url':'http://media-ice.musicradio.com/SmoothUK.m3u'},
   {'name':'XFM', 'url':'http://media-ice.musicradio.com/XFM.m3u'},
   {'name':'BBC Radio London', 'url':'http://bbc.co.uk/radio/listen/live/bbclondon.asx'},
   {'name':'BBC Radio Surrey', 'url':'http://bbc.co.uk/radio/listen/live/bbcsurrey.asx'},
]

class Settings:
   # Database connection details
   DB_NAME='settings.db'
   TABLE_NAME='settings'

   # Our default settings for when we create the table
   DEFAULTS= [
      ('volume','85'), # Volume
      ('station','0'), # Radio station to play
      ('radio_delay','10'), # Delay (secs) to wait for radio to start
      ('snooze_length','5'), # Time (mins) to snooze for
      ('max_brightness','15'), # Maximum brightness
      ('min_brightness','1'), # Minimum brightness
      ('brightness_timeout','20'), # Time (secs) after which we should revert to auto-brightness
      ('menu_timeout','20'), # Time (secs) after which an un-touched menu should close
      ('wakeup_time','105'), # Time (mins) before event that alarm should be triggered
      ('manual_alarm',''), # Manual alarm time (default not set)
      ('calendar',CalendarCredentials.CALENDAR), # Calendar to gather events from
   ]

   def __init__(self):
      self.conn = sqlite3.connect(self.DB_NAME, check_same_thread=False)
      self.c = self.conn.cursor()

   def setup(self):
      # This method called once from alarmpi main class
      # Check to see if our table exists, if not then create and populate it
      r = self.c.execute('SELECT COUNT(*) FROM sqlite_master WHERE type="table" AND name=?;',(self.TABLE_NAME,))
      if self.c.fetchone()[0]==0:
         self.firstRun()

      # Set the volume on this machine to what we think it should be 
      self.setVolume(self.getInt('volume'))

   def firstRun(self):
      print "Running first-time SQLite set-up"
      self.c.execute('CREATE TABLE '+self.TABLE_NAME+' (name text, value text)')
      self.c.executemany('INSERT INTO '+self.TABLE_NAME+' VALUES (?,?)',self.DEFAULTS)
      self.conn.commit()

   def get(self,key):
      self.c.execute('SELECT * FROM '+self.TABLE_NAME+' WHERE name=?',(key,))
      r = self.c.fetchone()
      if r is None:
         raise Exception('Could not find setting %s' % (key))
      return r[1]

   def getInt(self,key):
      try:
         return int(self.get(key))
      except ValueError:
         print "Could not fetch %s as integer, value was [%s], returning 0" % (key,self.get(key))
         return 0

   def set(self,key,val):
      self.get(key) # So we know if it doesn't exist

      if key=="volume":
         self.setVolume(val)

      self.c.execute('UPDATE '+self.TABLE_NAME+' SET value=? where name=?',(val,key,))
      self.conn.commit()

   def setVolume(self,val):
      subprocess.Popen("/usr/local/bin/vol %s" % (val), stdout=subprocess.PIPE, shell=True)
      print "Volume adjusted to %s" % (val)

   def __del__(self):
      self.conn.close()
