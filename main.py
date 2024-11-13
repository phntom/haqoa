import logging

from haqoa.logs import logging_setup
from haqoa import alert

logger = logging.getLogger(__name__)

if __name__ == '__main__':

    logging_setup(logger)

    alert.run()

    # alert.background_notification_listener({'threatId': '0', 'instance': '1544803905', 'title': 'ירי רקטות וטילים', 'type': '0', 'alertTitle': 'b2efe33c-790c-4f69-92ef-a6e9701c826c', 'language': 'iw-IL', 'citiesIds': '5000702,5000703,5000710,5000711,5000712,5000718,5000719,5000727,5000730,5000732,5000733,5000734,5000738,5000739,5000745,5000754,5000755,5000761,5000780,5001849,5001853,5001860,5001861,5001863,5001870,5001961,5002011', 'id': '169945', 'time': '2024-11-06T21:00:26+0200', 'formatting': '[{"style":[]}]', 'msgId': '21982', 'desc': 'היכנסו למרחב המוגן ושהו בו 10 דקות'})
    # alert.background_notification_listener({'threatId': '8', 'instance': '1544803905', 'title': 'Hostile aerial vehicle infiltrating Israel airspace - The event has ended', 'type': '0', 'alertTitle': '167452', 'language': 'iw-IL', 'citiesIds': '5000983,5000985,5000986,5000992,5000993,5000998,5001131,5001137,5001138,5001150,5001183,5001216,5001230,5001242,5001243,5001253,5001271,5001304,5001336,5001337,5001338,5001347,5001351,5001389,5001396,5001397,5001404,5001405,5001414,5001415,5001423,5001424,5001433,5001448,5001458,5001459,5001461,5001462,5001469,5001470,5001479,5001480,5001489,5001490,5001499,5001500,5001520,5001544,5001545,5001562,5001563,5001570,5001581,5001582,5001583,5001592,5001593,5001878,5001928,5002023,5002192', 'id': '167452', 'time': '2024-10-30T18:30:29+0200', 'formatting': '[{"style":[]}]', 'buttonText': 'For all guidelines', 'buttonUri': 'https://www.oref.org.il/12754-en/Pakar.aspx', 'desc': 'Following the report of an alert that was activated due to the infiltration of a hostile aerial vehicle into Israel airspace - the incident has ended. \n '})
    # alert.background_notification_listener({'threatId': '0', 'instance': '1544803905', 'title': 'ירי רקטות וטילים', 'type': '0', 'alertTitle': 'f23b4f4a-2267-46e5-a9d4-539fb126a915', 'language': 'iw-IL', 'citiesIds': '5001637', 'id': '164170', 'time': '2024-10-31T10:38:34+0300', 'formatting': '[{"style":[]}]', 'msgId': '21982', 'desc': 'היכנסו למרחב המוגן ושהו בו 10 דקות'})
    # alert.background_notification_listener({'threatId': '5', 'instance': '1544803905', 'title': 'חדירת כלי טיס עוין', 'type': '0', 'alertTitle': 'c2913eb2-f95d-4b77-ac1f-2c5310c83a34', 'language': 'iw-IL', 'citiesIds': '5001499,5001544', 'id': '167508', 'time': '2024-10-31T10:30:59+0300', 'formatting': '[{"style":[]}]', 'msgId': '21988', 'desc': 'היכנסו מיד למרחב המוגן ושהו בו למשך 10 דקות, אלא אם ניתנה התרעה נוספת'})
