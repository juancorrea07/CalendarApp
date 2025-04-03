from dataclasses import dataclass, field
from datetime import datetime, date, time
from typing import ClassVar

from app.services.util import generate_unique_id, date_lower_than_today_error, event_not_found_error, \
    reminder_not_found_error, slot_not_available_error

@dataclass

class Reminder:
    EMAIL: ClassVar[str] = "email"
    SYSTEM: ClassVar[str] = "system"
    date_time: datetime
    type: str = EMAIL

    def __str__(self)-> str:
        return f"Reminder on {self.date_time} of type {self.type}"

@dataclass
class Event:
    title: str
    description: str
    date_: date
    start_at: time
    end_at: time

    reminders: list[Reminder] = field(default_factory=list)
    id: str = field(default_factory=generate_unique_id)

    def add_reminder(self, date_time: datetime, reminder_type: str = Reminder.EMAIL):
        reminder = Reminder(date_time=date_time, type=reminder_type)
        self.reminders.append(reminder)

    def delete_reminder(self, reminder_index: int):
        if 0 <= reminder_index < len(self.reminders):
            self.reminders.pop(reminder_index)
        else:
            reminder_not_found_error()

    def __str__(self):
        return f"ID: {self.id} Event title: {self.title} Description: {self.description} Time: {self.start_at} - {self.end_at}"


class Day:

    def __init__(self,date_: date):
        self.date_: date_
        self.slots: dict[time, str | None]= {}

    def _init_slots(self):
        hour = 0
        minute = 0
        while hour < 24:
            current_time = time(hour, minute)
            self.slots[current_time] = None

            minute += 15
            if minute == 60:
                minute = 0
                hour += 1

    def add_event(self, event_id: str, start_at: time, end_at: time):
        current_hour = start_at.hour
        current_minute = start_at.minute

        while (current_hour, current_minute) < (end_at.hour, end_at.minute):
            current_time = time(current_hour, current_minute)

            if self.slots.get(current_time) is not None:
                slot_not_available_error()
                return

            current_minute += 15
            if current_minute == 60:
                current_minute = 0
                current_hour += 1

        current_hour = start_at.hour
        current_minute = start_at.minute

        while (current_hour, current_minute) < (end_at.hour, end_at.minute):
            current_time = time(current_hour, current_minute)
            self.slots[current_time] = event_id

            current_minute += 15
            if current_minute == 60:
                current_minute = 0
                current_hour += 1

    def delete_event(self, event_id: str):
        deleted = False
        for slot, saved_id in self.slots.items():
            if saved_id == event_id:
                self.slots[slot] = None
                deleted = True
        if not deleted:
            event_not_found_error()

    def update_event(self, event_id: str, start_at: time, end_at: time):
        for slot in self.slots:
            if self.slots[slot] == event_id:
                self.slots[slot] = None

        for slot in self.slots:
            if start_at <= slot < end_at:
                if self.slots[slot]:
                    slot_not_available_error()
                else:
                    self.slots[slot] = event_id