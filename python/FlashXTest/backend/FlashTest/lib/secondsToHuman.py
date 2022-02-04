def convert(seconds):
  """
  Takes a number of seconds and returns a human-readable conversion.
  
  Input of s <= 59 seconds will yield a string of the form "s seconds".
  Higher values will yield a string of the form "mm:ss", "hh:mm:ss",
  or "dd:hh:mm:ss" - whichever is appropriate for the given input.
  """

  # round seconds to nearest second
  iseconds = int(round(seconds))

  SECONDS_IN_DAY = 86400
  SECONDS_IN_HOUR = 3600
  SECONDS_IN_MINUTE = 60

  daysStr    = ""
  hoursStr   = ""
  minutesStr = ""
  secondsStr = ""

  days = iseconds // SECONDS_IN_DAY
  if (days):
    daysStr = ("%2d" % days).replace(" ","0")
    iseconds -= (days * SECONDS_IN_DAY)

  hours = iseconds // SECONDS_IN_HOUR
  if (hours or days):
    hoursStr = ("%2d" % hours).replace(" ","0")
    iseconds -= (hours * SECONDS_IN_HOUR)

  minutes = iseconds // SECONDS_IN_MINUTE
  if (minutes or hours or days):
    minutesStr = ("%2d" % minutes).replace(" ","0")
    iseconds -= (minutes * SECONDS_IN_MINUTE)

  if (minutes or hours or days):
    secondsStr = ("%2d" % iseconds).replace(" ","0")
    l = [daysStr, hoursStr, minutesStr, secondsStr]
    conversionStr = ":".join([str for str in l if len(str) > 0])
  elif seconds == 1:
    conversionStr = "1 second"
  elif seconds < 9.5:
    conversionStr = "%8.6f seconds" % seconds
  else:
    conversionStr = "%s seconds" % iseconds

  return conversionStr
