"""
Export your current terms and schedule from Peppi to ICS
"""

from datetime import datetime

import requests
from bs4 import BeautifulSoup as bs

cookies = {
    "COOKIE_SUPPORT": "true",
    "GUEST_LANGUAGE_ID": "fi_FI",
}


def main():
    """
    Export your current terms and schedule from Peppi to ICS
    """

    curl = input("Enter the curl command copied from the browser: ")
    curl_parts = curl.split(" ")

    # Get the needed values from the curl command

    # URL
    url = curl_parts[1].replace("'", "")
    # Get the server name from the url
    server_name = url.split("/")[2]

    # Cookies
    for part in curl_parts:
        if "_shibsession" in part:
            cookie = part.split("=")
            cookies[cookie[0]] = cookie[1].replace("'", "").replace(";", "")
        if "JSESSIONID" in part:
            cookies["JSESSIONID"] = part.split("=")[1].replace("'", "").replace(";", "")

    # Check if the cookies are set
    if len(cookies) < 3:
        print("Cookies are not set correctly")
        return

    # Get the terms from Peppi
    terms = get_terms(url)

    if len(terms) == 0:
        print("No terms found")
        return

    print("Terms found:")
    for term in terms:
        print(" - " + term)

    reservations = []
    for term in terms:
        # Get reservations and add them to the list of reservations
        reservations.append(get_reservations(term, server_name))
    # Flatten the list of reservations
    events = [event for reservation in reservations for event in reservation]
    ics_content = create_ics(events)

    with open("Peppi2ICS.ics", "w") as f:
        f.write(ics_content)

    print("ICS file created successfully")


def get_terms(url):
    """
    Get all the terms from Peppi
    """

    response = requests.get(
        url,
        cookies=cookies,
    )

    if "Authentication Request" in response.text:
        print("Authentication failed")
        return []

    soup = bs(response.content, "html.parser")
    terms = []
    # id enrolled_active to get all the courses
    for tr in soup.find(id="enrolled-active").find("tbody").find_all("tr"):
        tds = tr.find_all("td")
        # If td 0 has a div with class rejected, the term is not active and skipped
        if tds[0].find("div", class_="rejected"):
            continue
        terms.append(tds[1].text)

    return terms


def get_reservations(term, server_name):
    """
    Get reservations for a specific term
    """
    response = requests.get(
        f"https://{server_name}/delegate/realization-info?term={term}",
        cookies=cookies,
    )

    soup = bs(response.content, "html.parser")

    # Find all tr with class "reservation-education-group-*"
    reservations = soup.find_all(
        "tr", class_=lambda x: x and x.startswith("reservation-education-group-")
    )

    parsed_reservations = []

    # Parse the reservations
    for reservation in reservations:
        title = reservation.find_all("td")[0].text.strip().split(" " + term)[0]
        group = reservation.find_all("td")[3].text.strip()
        location = (
            reservation.find_all("td")[4]
            .text.strip()
            .replace("        ", "")
            .replace("    ", "")
        )
        group_type = "L" if "Lue" in group else "E"
        time = reservation.find_all("td")[1].text.strip()
        # parse dd.mm.yyyy hh:mm - hh:mm
        start_date = datetime.strptime(time.split(" - ")[0].strip(), "%d.%m.%Y %H.%M")
        end_date = datetime.strptime(time.split(" - ")[1].strip(), "%H.%M")

        parsed_reservations.append(
            {
                "term": term,
                "title": title,
                "group": group,
                "location": location,
                "group_type": group_type,
                "start_date": start_date,
                "end_date": end_date,
            }
        )

    return parsed_reservations


def create_ics(events):
    """
    Create ICS file from the events
    """
    ics_content = "BEGIN:VCALENDAR\nVERSION:2.0\nPRODID:-//Adventune//Peppi2ICS//EN\n"

    for event in events:
        # Correcting the end date by taking the date from 'start_date' and the time from 'end_time'
        end_date = event["start_date"].replace(
            hour=event["end_date"].hour, minute=event["end_date"].minute
        )

        # Formatting dates in the ICS format
        start_date_str = event["start_date"].strftime("%Y%m%dT%H%M%S")
        end_date_str = end_date.strftime("%Y%m%dT%H%M%S")
        uid = f"{start_date_str}{event['term']}{event['group']}"
        dtstamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        summary = f"{event['group_type']}: {event['title']} - {event['group']} - {event['term']}"

        # Adding event data to ICS content
        ics_content += f"""BEGIN:VEVENT
UID:{uid}
DTSTAMP:{dtstamp}
DTSTART:{start_date_str}
DTEND:{end_date_str}
SUMMARY:{summary}
LOCATION:{event['location']}
DESCRIPTION:Group Type: {event['group_type']}
END:VEVENT
"""

    ics_content += "END:VCALENDAR"
    return ics_content


if __name__ == "__main__":
    main()
