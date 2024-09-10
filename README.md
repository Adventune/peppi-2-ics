# Peppi2ICS

Exporting tool to export current term timetable from Peppi into an ICS. Pair for
example with
[bulk edit calendar events](https://bulkeditcalendarevents.com/index.html) to
get clean timetables into Google calendar.

> [!WARNING]
> This is not tested in any way. It was solely coded based on what I saw in my
> Peppi environment. I don't know if this extends to other environments
> (I study in Oulu university, others might not work :shrug:). There are
> probably some cases where an error is thrown or something else goes wrong.

## Dependecies

- Python 3
- Pipenv

## Usage

- Install dependecies with `pipenv install`.
- Run with `python3 main.py`.
- Provide the curl command once prompted.
- Use the outputted `Peppi2ICS.ics` in any way you see fit.

### Curl command

To authenticate to Peppi (and to get the URL params) I lazily used the curl from
the browser. To get it (on firefox):

- Navigate to your "HOPS" and select `Enrolments`-tab.
- `CTRL+shift+E` to open devtools.
- Filter URLs with `enrollment`.
- Reload the page.
- Right click the only appearing request (if multiple just find the request that
  returns the page source).
- Select `Copy Value` > `Copy As cURL` and paste to the program.
  - You should read the source of anything that asks you to do this!!
