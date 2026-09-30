import datetime
from zoneinfo import ZoneInfo

def execute(**kwargs):
    eastern_time = datetime.datetime.now(ZoneInfo("America/New_York"))
    
    hour = int(eastern_time.strftime("%I"))
    rest_of_time = eastern_time.strftime("%M %p")
    
    return f"The current time is {hour}:{rest_of_time}."