#!/usr/bin/env python
# coding=utf8

import logging

import qr
import fqq


def buddy_msg_handler(f, bundle):
    f.send_buddy_msg_by_uin(
        bundle['uin'],
        '[Autoreply] QQ sucks, switch to XXX and save your ass.'
    )

if __name__ == '__main__':
    f = fqq.Fqq()
    f.logger.setLevel(logging.INFO)
    f.set_qr_handler(lambda x: qr.qr_printraw(x))
    f.add_buddy_msg_handler(buddy_msg_handler)
    f.login()
    f.get_user_friends()
    f.loop()
