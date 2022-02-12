import time
import datetime
import pytz
import pytz_convert


class TimeManager:

  def __init__(self,tz=None):

    if(tz == None):
      from time import gmtime, strftime
      tz = pytz.timezone("utc")
      self.timezone_name = tz.zone
      timezone = time.strftime("%z", time.gmtime())
      self.offset_string = timezone
    else:
      tz = pytz.timezone(tz)
      self.timezone_name = tz.zone



  def date(self, year=2000, month=1, day=1, timezone_name=None):
    if not timezone_name:
      timezone_name = self.timezone_name
    d  = datetime.datetime(year, month, day, tzinfo=pytz.UTC)
    tz = pytz.timezone(timezone_name)
    d=tz.normalize(d)
    offset_hour = int(str(d)[-5:-3])
    offset_min = int(str(d)[-2:])
    d = d + datetime.timedelta(hours=offset_hour, minutes=offset_min)
    return d

  def datetime(self, year=2000, month=1, day=1, hour=0, min=0, sec=0, timezone_name=None):
    if not timezone_name:
      timezone_name = self.timezone_name
    d  = datetime.datetime(year, month, day, hour, min, sec, tzinfo=pytz.UTC)
    tz = pytz.timezone(timezone_name)
    d=tz.normalize(d)
    offset_hour = int(str(d)[-5:-3])
    offset_min = int(str(d)[-2:])
    d = d + datetime.timedelta(hours=offset_hour, minutes=offset_min)
    return d

  def format_as_canonical_utc(self, time, date_only=False, msec=False):
    if msec:
      if date_only:
        full = time.strftime("%a %b %d %Y GMT")
      else:
        full = time.strftime("%a %b %d %Y %I:%M:%S.%f %p GMT")
    else:
      if date_only:
        full = time.strftime("%a %b %d %Y GMT")
      else:
        full = time.strftime("%a %b %d %Y %I:%M:%S %p GMT")
    return full


  def format_as_canonical(self, time, date_only=False, tz=None, msec=False):
  #Wed Sep 15 1965 00:00:00 GMT-0700 (Pacific Daylight Time)
    if time.tzinfo == None:
      if msec:
        full = time.strftime("%a %b %d %Y %I:%M:%S.%f %p")
      else:
        full = time.strftime("%a %b %d %Y %I:%M:%S %p")
      return full

    if not tz:
      tz = self.timezone_name
      time = time.astimezone(pytz.timezone(tz))
    if tz==pytz.UTC:
      return self.format_as_canonical_utc(time, msec)
    else:
      if msec:
        full = time.strftime("%a %b %d %Y %I:%M:%S.%f %p %Z")
      else:
        full = time.strftime("%a %b %d %Y %I:%M:%S %p %Z")
      return full

  def format_as_iso_utc(self, time, msec=False):
    full = time.isoformat()
    if(msec):
      return full + "Z"
    dot_index = full.find(".")
    if dot_index < 0:
      return full + "Z"
    return full[0:19] +"Z"

  def format_as_iso(self, time, tz=None, msec=False):
    if not tz:
      tz = self.timezone_name

    time = datetime.datetime.utcfromtimestamp(time.timestamp())
    #utc_dt = time.astimezone(self.timezone.tzinfo)
    if tz==pytz.UTC: return self.format_as_iso_utc(time, msec)

  def get_current_time(self):
    return datetime.now()

  def format_datetime(dt, tz):
    utc_dt = dt.astimezone(tz)
    return utc_dt.strftime("%Y-%m-%dT%H:%M:%SZ")