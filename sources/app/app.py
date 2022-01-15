from flask import Flask, Blueprint, jsonify, render_template, flash, redirect, request, url_for
from .settings import *
from .models import User
from flask_login import current_user, login_required

from datetime import datetime, timedelta, timezone

from dateutil.relativedelta import relativedelta

from icalendar import Calendar

from icalevents.icalevents import events

import urllib

def fetchICAL(url):
    f = urllib.request.urlopen(url)
    myfile = f.read()
    return myfile


def getValues():
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    return str(current_time)

def is_inbetween(start, end, event_start, event_end):
    return (start < event_start < end) \
                or (start < event_end < end) \
                or (event_start < start and end < event_end)

def find_sessions_inbetween(events, start, end):
    events_inbetween = []
    for event in events:

        # ignore full day events
        if isinstance(event['DTSTART'].dt, datetime):
            # test if event in range
            if is_inbetween(start, end, event['DTSTART'].dt, event['DTEND'].dt):
                #print("append")
                # append events in range to the return
                events_inbetween.append(event)

            # if event is returning
            if 'RRULE' in event:
                repeatInformation = has_repeating_event_inbetween(event, start, end)
                #print(repeatInformation)
                if repeatInformation[0]:
                   events_inbetween.append(event)
                #if ("WEEKLY" in event['RRULE']):
                #    print("Weekly")
                #print(display_events([event]))
    return events_inbetween

def has_incremental_repeat(event, start, end, increment, until):
    """checks if a reoccuring date with a fixed increment is in the scope of start and end

    Args:
        event ([type]): [description]
        start ([type]): [description]
        end ([type]): [description]
        increment (time): [description]
        until (time): [description]

    Returns:
        Array: [bool: if it Occures, start, end: when it occures]
    """
    i = 0
    # check if there is a reoccuring event
    while (not event['DTSTART'].dt + i*increment > until) \
        and (not event['DTSTART'].dt + i*increment > end):
        # print(event['DTSTART'].dt + timedelta(7*weeks_iterated), start)
        if is_inbetween(start, end, event['DTSTART'].dt + i * i*increment, event['DTEND'].dt + i*increment):
            #print("found it")
            return [True, event['DTSTART'].dt + i*increment, event['DTEND'].dt + i*increment]
        #print (start - (event['DTSTART'].dt + timedelta(7*weeks_iterated)))
        i += 1
    return [False, 0, 0]

def has_repeating_event_inbetween(event, start, end):
    repeatInformation = [False, 0, 0]
    # ignore future returning events
    if (event['DTSTART'].dt < end):
        rrule = event['RRULE']
        if 'YEARLY' in rrule["FREQ"]:
            pass
        elif 'MONTHLY' in rrule["FREQ"]:
            if "UNTIL" in rrule:
                repeatInformation = has_incremental_repeat(event, start, end, relativedelta(months=1), rrule["UNTIL"][0])
        elif 'WEEKLY' in rrule["FREQ"]:
            if "UNTIL" in rrule:
                repeatInformation = has_incremental_repeat(event, start, end, timedelta(7), rrule["UNTIL"][0])
    return repeatInformation

def display_ievents(events):
    output = ""
    for event in events:
        print(event.description)
        print(event.end)
        print(str(event))
    #    output += event.to_ical().decode() + "\n - . - . - \n \n"
    #return output

def generate_instruction_table(start, end, events):
    color_table = {"Timetable > Gremien":"255 0 124", "Timetable > Job":"255 60 0", "Timetable > Jobs":"255 60 0", "Timetable > Events":"0 100 5", "Timetable > Freunde":"210 255 0", "Timetable > Stundenplan":"0 40 130"}
    output = ""
    if not events:
        output = "14400000 5 5 10"
    else:
        events.sort(key=lambda e: e.start)
        #start = datetime.now(tz=timezone(timedelta(0)))
        for i in range(len(events)):
            # write action before event
            if i == 0:
                duration = events[0].start - start
                duration_in_milliseconds = duration.total_seconds() * 1000
                output += "{:.0f}".format(duration_in_milliseconds) + " 5 5 10<br>"
            else:
                duration = events[i].start - events[i-1].end
                duration_in_milliseconds = duration.total_seconds() * 1000
                if duration_in_milliseconds >= 1:
                    output += "{:.0f}".format(duration_in_milliseconds) + " 5 5 10<br>"

            # write action while event
            duration = events[i].end - events[i].start
            duration_in_milliseconds = duration.total_seconds() * 1000
            output += "{:.0f}".format(duration_in_milliseconds) + " " + color_table[events[i].description] + "<br>"

            # find next event
            if i < len(events) - 1:
                j = i + 1
                # skip events that start inbetween
                while events[j].start < events[i].end:
                    j+=1
                # write action after event
                duration = events[j].start - events[i].end
                duration_in_milliseconds = duration.total_seconds() * 1000
                if duration_in_milliseconds >= 1:
                    output += "{:.0f}".format(duration_in_milliseconds) + " 5 5 10<br>"
                i = j - 1
            else:
                # write action after event
                duration = end - events[i].end
                duration_in_milliseconds = duration.total_seconds() * 1000
                if duration_in_milliseconds >= 1:
                    output += "{:.0f}".format(duration_in_milliseconds) + " 5 5 10<br>"
    return output

def display_events(events):
    output = ""
    for event in events:
        output += event.to_ical().decode() + "\n - . - . - \n \n"
    print(output)

main = Blueprint('main', __name__, url_prefix=SITE_ROOT)

@main.route('/')
def index():
    site = "<p>CalDOVE Provider is running...</p>"

    cal = Calendar.from_ical(fetchICAL("https://ics.teamup.com/feed/kspxzt6i8jabqw7icn/0.ics"))

    sessions = [e for e in cal.walk('vevent')]
    span_events = []
    # ignore full day events
    for event in sessions:
        if isinstance(event['DTSTART'].dt, datetime):
            event['DESCRIPTION'] = event['CATEGORIES']
            span_events.append(event)

    cal = Calendar()
    for event in span_events:
        cal.add_component(event)


    #display_events(span_events)

    today = datetime.now(tz=timezone(timedelta(0)))
    tommorrow =  today + timedelta(hours=24)

    sessions = events(string_content=cal.to_ical(), start=today, end=tommorrow)

    #sessions = find_sessions_inbetween(sessions, today, tommorrow+timedelta(2))

    site += "<div id=\"data\">" + generate_instruction_table(today, tommorrow, sessions) + "</div>"

    return site


@main.route('/protected')
@login_required
def protected():
    return 'Hello, World!'

@main.route('/users')
def users():
    return jsonify([ (u.username, u.email) for u in User.query.all() ])


