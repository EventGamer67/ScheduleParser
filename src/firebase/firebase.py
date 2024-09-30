from typing import List

import firebase_admin
from firebase_admin import messaging, credentials

cred = credentials.Certificate({
    "type": "service_account",
    "project_id": "chronos-29a6e",
    "private_key_id": "436d0e5e7bb202fddbcc16e04116a1d46908945d",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvwIBADANBgkqhkiG9w0BAQEFAASCBKkwggSlAgEAAoIBAQDgQfDY43fvVpOS\ngMUWDLZwtbatCSEmwG7qhEYjqTFHBkHSLOF3ieWmNQddtgwSZ+brQHSUO4y7hDBT\nKBiGauNrnyF9D4o0myk7iJlLQ399Bxfvj5xfjpDk/A7F7GbK1ms0XKVJe2S+BVNt\ndIxgkEJqoNwY+EPFcExfXPx8kH4TUCidiuvzMkpDFey0G17j5zQK/UEZRbvlCWq1\nIQuVXfZPNZ+NzZkLePYnq/rZeZe4V2N3mrWm77x0o0ytfWphwU1nLD4EJ3aaz6yE\no6s2adHlZviZPwPpQ2rITcrG6OcGYoyWDGlJAuCr3NTjYgzpRntSxhadbuEq8EvZ\nMX7aoln1AgMBAAECggEASXcgrRS7niMJHiXkKsiIXd0RlpcWjqjczSP/DECpnYBd\nwLomNLBulKfrnVX9l2wFWI0Zg9QMUwPHhv5sJmDO1ttfL6aPGpO4CsJBocffdHiF\n7VtpGV7Ndc5jEpDSzeE3ZoRxO2TaiGubPJDBSgMIVwESiXWPUhdrVZRTPIVjX/S2\nAwku3Rr3lloLd/QQIel9mrqywlcquPuggWJmKkWuvITUzxjd4yFrGzlq84INTSIz\nnUeOwgb6LDTAgoi1WStee2SmPPaSi+UgLp/PUSZJI9f99O8QYX0naSmjkkOfsHVR\nW7gh8Ksg/TRxL0zHD4EItUkMIfLk0Fmzv9bwnwN4owKBgQD2zoBZdVm0uKYnlSBj\nUesDwlYAaVwTWUL4OpRA8nisThYNXIUkmMnWQ+weF5hVbdkOmjo9YyJsxvmAjPsc\no57pEtt0pp1oYF5gRDGKc7QVqQN/Z/odkkDaJs0T5XQIdUCy3bBSbSAJ6Ih1h6Zq\nbGUkTubUr0gprZyZymMEzQ+XdwKBgQDonGqE3v3zifnYSGE5HBkcHKaLGQXQ3u2h\nFUaJDw8hQg9eWSkPOFrO0sgO059kxc3rp45pfwBWT9Q/88emAsJ8emMR/5liNWoi\n+ux0tIyPA1NA2lsLbbNlwTa61CKc7Md4NMSL8SbKkqOhxYKfToZk0zzKHnp8JDUj\nrhuEeyQM8wKBgQCasji02d9ObWaH7OsOFeyOwKKTQ3bZEdvuJxmB0/lbVt5vpYw2\nsiXgzVYUTonHEkE46+aRT6/mKpl8v+EtxEj4oj830K9dGvpMsLG0rG02Hmf41b1q\nB5/qnONyEyI1ovjYpCe+onOwgjX2JP5kOmjy5xm8OdmrdgxwQPDrs3SQZQKBgQC/\nFm/zA3U/siNLZ/pmfgyqqWavcjjy44/2+pFdWr+lJK2XZktys2r16PZsJ7ETieOm\nKZm2VJykSyQj/VIPsMiwlaH5US5iHVs5rUS+guvNOIAWEMsmUlJDzzv0svxUSbd7\nqm2kQNELLPe7l5O85zdEcLvJlswsW1pEG22Dod11vQKBgQCay090RwmGnPPuaeIe\nBUFyuMPqk7CG6LRPD4DPGCa4OROjLzkNM04DpWALXRr7pZ7K+j4FFJDmO71iB0au\ng4Xi9EOznSOhuiKX0ppTuGVjyzXKy5To9ofNpDaAvYtjtSnOY/21ciZcNJHdga/v\nv29tbfb9SO44oUEwAPUfu85UVw==\n-----END PRIVATE KEY-----\n",
    "client_email": "firebase-adminsdk-ed7hf@chronos-29a6e.iam.gserviceaccount.com",
    "client_id": "110531035167654412505",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-ed7hf%40chronos-29a6e.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
})
firebase_admin.initialize_app(cred)


def send_message_to_topic(title, body, sup):
    registration_tokens = sup.getSubs(sup)

    web_subs = [sub.token for sub in registration_tokens if sub.clientID == 1]
    android_subs = [sub.token for sub in registration_tokens if sub.clientID == 2]
    if len(web_subs) > 0:
        message = messaging.MulticastMessage(
            data={'title': title, 'body': body},
            tokens=web_subs,
        )
        response = messaging.send_each_for_multicast(message)
        print('Successfully sent message web:', response)
    if len(android_subs) > 0:
        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data={'title': title, 'body': body},
            tokens=android_subs,
        )
        response = messaging.send_each_for_multicast(message)
        print('Successfully sent message android:', response)

