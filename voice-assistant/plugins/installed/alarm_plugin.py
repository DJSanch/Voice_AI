import re
from plugins.base_plugin import BasePlugin


class AlarmPlugin(BasePlugin):

    name = "Alarm Plugin"
    version = "1.0"



    def __init__(self, alarm):

        self.alarm = alarm



    def can_handle(self, command):

        return "alarm" in command.lower()



    def handle(self, command):

        text = command.lower()


        match = re.search(
            r'(\d{1,2})[: ](\d{2})',
            text
        )


        if not match:

            return (
                "What time should I set the alarm for?"
            )



        hour = int(match.group(1))
        minute = int(match.group(2))


        if "pm" in text and hour < 12:
            hour += 12


        if "am" in text and hour == 12:
            hour = 0


        alarm_time = (
            f"{hour:02d}:{minute:02d}"
        )


        return self.alarm.set_alarm(
            alarm_time
        )