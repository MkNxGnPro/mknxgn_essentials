import time, threading, datetime
from essentials import tokening


EVERY_SECOND = "second"
EVERY_MINUTE = "minute"
EVERY_HOUR = "hour"
EVERY_DAY = "day"
EVERY_WEEK = "week"
EVERY_MONTH = "month"
EVERY_YEAR = "year"

SECOND = "second"
MINUTE = "minute"
HOUR = "hour"
DAY = "day"

def wait_X_Y_and_do(count, function=None, unit_type=SECOND, args=None, keep_open=False):

    def wait(function, count, unit_type, args):
        if unit_type == SECOND:
            pass
        elif unit_type == MINUTE:
            count = count * 60
        elif unit_type == HOUR:
            count = count * 3600
        elif unit_type == DAY:
            count = count * 86400
        else:
            raise ValueError("You didn't pass a comprehendable unit_type")

        time.sleep(count)

        function(*args)

    threading.Thread(target=wait, args=[function, count, unit_type, args], daemon=not keep_open).start()


class EventListener:
    def __init__(self, viaDate=True):
        self.events = {}
        self.viaDate = viaDate
        if viaDate:
            self.start_time = datetime.datetime.now()
            self.second = self.start_time.second
            self.minute = self.start_time.minute
            self.week = self.start_time.isocalendar()[1]
            self.hour = self.start_time.hour
            self.day = self.start_time.day
            self.month = self.start_time.month
            self.year = self.start_time.year
            threading.Thread(target=self.__Checker__, daemon=True).start()
        else:
            self.seconds = 0
            self.minutes = 0
            self.hours = 0
            self.days = 0
            self.weeks = 0
            self.years = 0
            threading.Thread(target=self.__Waiter__, daemon=True).start()

    def __Waiter__(self):
        threading.Thread(target=self.__EventCaller__, args=[EVERY_SECOND], daemon=True).start()
        while True:
            time.sleep(1)
            self.seconds += 1
            threading.Thread(target=self.__EventCaller__, args=[EVERY_SECOND], daemon=True).start()
            if self.seconds == 60:
                self.minutes += 1
                self.seconds = 0
                threading.Thread(target=self.__EventCaller__, args=[EVERY_MINUTE], daemon=True).start()
            if self.minutes == 60:
                self.minutes = 0
                self.hours += 1
                threading.Thread(target=self.__EventCaller__, args=[EVERY_HOUR], daemon=True).start()
            if self.hours == 24:
                self.hours = 0
                self.days += 1
                threading.Thread(target=self.__EventCaller__, args=[EVERY_DAY], daemon=True).start()
            if self.days == 7:
                self.days = 0
                self.weeks += 1
                threading.Thread(target=self.__EventCaller__, args=[EVERY_WEEK], daemon=True).start()
            if self.weeks == 52:
                self.weeks = 0
                self.years += 1
                threading.Thread(target=self.__EventCaller__, args=[EVERY_YEAR], daemon=True).start()

    def __Checker__(self):
        threading.Thread(target=self.__EventCaller__, args=[EVERY_SECOND], daemon=True).start()
        while True:
            currentTime = datetime.datetime.now()
            time.sleep(0.50)
            if currentTime.second != self.second:
                self.second = currentTime.second
                threading.Thread(target=self.__EventCaller__, args=[EVERY_SECOND], daemon=True).start()

            if currentTime.minute != self.minute:
                self.minute = currentTime.minute
                threading.Thread(target=self.__EventCaller__, args=[EVERY_MINUTE], daemon=True).start()

            if currentTime.hour != self.hour:
                self.hour = currentTime.hour
                threading.Thread(target=self.__EventCaller__, args=[EVERY_HOUR], daemon=True).start()

            if currentTime.day != self.day:
                self.day = currentTime.day
                threading.Thread(target=self.__EventCaller__, args=[EVERY_DAY], daemon=True).start()

            if currentTime.isocalendar()[1] != self.week:
                self.week = currentTime.isocalendar()[1]
                threading.Thread(target=self.__EventCaller__, args=[EVERY_WEEK], daemon=True).start()

            if currentTime.month != self.month:
                self.month = currentTime.month
                threading.Thread(target=self.__EventCaller__, args=[EVERY_MONTH], daemon=True).start()

            if currentTime.year != self.year:
                self.year = currentTime.year
                threading.Thread(target=self.__EventCaller__, args=[EVERY_YEAR], daemon=True).start()

    def __EventCaller__(self, calling_type):
        for event in self.events:
            event = self.events[event]
            if event.type == calling_type:
                event.run(calling_type)

    def RegisterEvent(self, every_x, action):
        tk = tokening.CreateToken(6, self.events)
        self.events[tk] = Event(every_x, action, tk)
        return self.events[tk]

    def RemoveEvent(self, eventHandle):
        try:
            del self.events[eventHandle.id]
        except:
            time.sleep(0.5)
            del self.events[eventHandle.id]

class Event:
    def __init__(self, per, action, ids):
        self.action = action
        self.type = per
        self.runs = 0
        self.id = ids

    def run(self, calling_type):
        self.runs += 1
        threading.Thread(target=self.action, args=[calling_type, datetime.datetime.now()], daemon=True).start()
        