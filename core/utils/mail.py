"""
Envoi de mails
"""
import threading

from flask_mail import Message

from server import get_app, db, mail


def _send_async(app, msg, groups):
    # TODO utiliser backends authentif pour gérer les envois mails

    from core.auth.backends import get_members_mails
    with app.app_context():
        for mail_addr in get_members_mails(groups):
            msg.add_recipient(mail_addr)
        mail.send(msg)


def send_mail(
        groups, subject, msg_body,
        add_dests=None, sendername='recrutement'):
    '''
    envoie un mail aux administrateurs de l'application
    '''
    if add_dests is None:
        add_dests = []

    # supprimer chaines vides dans listes email
    add_dests = list(filter(lambda x: len(x), add_dests))

    app = get_app()
    if not app.config['SEND_MAIL']:
        return

    dests = add_dests

    msg = Message(
        '[%s] %s' % (sendername, subject),
        sender=app.config['MAIL_SENDER'],
        recipients=dests)
    msg.body = msg_body

    thr = threading.Thread(target=_send_async, args=[app, msg, groups])
    thr.start()
