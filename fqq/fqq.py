#!/usr/bin/env python
# coding=utf8
'''
Fqq
Copyright © 2015 Cubarco

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included
in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''

import urllib
import urllib2
import qr
import time
import random
import json
import sys
import socket
import os
# import threading

from cookielib import CookieJar, Cookie


class Fqq():
    STEP1_URL = 'https://ui.ptlogin2.qq.com/cgi-bin/login' \
        '?daid=164&target=self&style=16&mibao_css=m_webqq&appid=501004106&' \
        'enable_qlogin=0&no_verifyimg=1&' \
        's_url=http%3A%2F%2Fw.qq.com%2Fproxy.html' \
        '&f_url=loginerroralert&strong_login=1&login_state=10&t=20131024001'
    QRCODE_URL = 'https://ssl.ptlogin2.qq.com/ptqrshow' \
        '?appid=501004106&e=0&l=M&s=5&d=72&v=4'
    QR_STATUS_URL = 'https://ssl.ptlogin2.qq.com/ptqrlogin' \
        '?webqq_type=10&remember_uin=1&login2qq=1&aid=501004106' \
        '&u1=http%3A%2F%2Fw.qq.com%2Fproxy.html%3Flogin2qq%3D1%26' \
        'webqq_type%3D10&ptredirect=0&ptlang=2052&daid=164&from_ui=1' \
        '&pttype=1&dumy=&fp=loginerroralert&action=0-0-143245' \
        '&mibao_css=m_webqq&t=undefined&g=1&js_type=0&js_ver=10140' \
        '&login_sig=&pt_randsalt=0'
    GET_VFWEBQQ_URL = 'http://s.web2.qq.com/api/getvfwebqq' \
        '?ptwebqq={}&clientid={}&psessionid=&t={}'
    LOGIN2_URL = 'http://d.web2.qq.com/channel/login2'
    GET_USER_FRIENDS_URL = 'http://s.web2.qq.com/api/get_user_friends2'
    GET_GROUP_INFO_EXT2_URL = 'http://s.web2.qq.com/api/get_group_info_ext2' \
        '?gcode={}&vfwebqq={}&t={}'
    GET_DISCU_INFO_URL = 'http://d.web2.qq.com/channel/get_discu_info?did={}' \
        '&vfwebqq={}&clientid={}&psessionid={}&t={}'
    POLL2_URL = 'http://d.web2.qq.com/channel/poll2'

    S_REFERER_URL = 'http://s.web2.qq.com/proxy.html' \
        '?v=20130916001&callback=1&id=1'
    D_REFERER_URL = 'http://d.web2.qq.com/proxy.html' \
        '?v=20110331002&callback=1&id=3'

    def __init__(self):
        random.seed(time.time())
        self.msg_id = random.randint(20000, 50000)
        self.client_id = random.randint(20000000, 90000000)
        self.friends = {}
        self.groups = {}
        self.discus = {}
        self._cj = CookieJar()
        self._opener = urllib2.build_opener(
            urllib2.HTTPCookieProcessor(self._cj)
        )
        self._opener.addheaders = [
            ('User-agent',
             'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.11 ' +
             '(KHTML, like Gecko) Chrome/23.0.1271.6 Safari/537.11')
        ]

    def hash(self, uin, ptwebqq):
        N = [0] * 4
        for t in range(len(ptwebqq)):
            N[t % 4] ^= ord(ptwebqq[t])
        U = ["EC", "OK"]
        V = [0] * 4
        V[0] = int(uin) >> 24 & 255 ^ ord(U[0][0])
        V[1] = int(uin) >> 16 & 255 ^ ord(U[0][1])
        V[2] = int(uin) >> 8 & 255 ^ ord(U[1][0])
        V[3] = int(uin) & 255 ^ ord(U[1][1])
        U = [0] * 8
        for T in range(8):
            if T % 2 == 0:
                U[T] = N[T >> 1]
            else:
                U[T] = V[T >> 1]
        N = ["0", "1", "2", "3", "4", "5", "6", "7",
             "8", "9", "A", "B", "C", "D", "E", "F"]
        V = ""
        for T in range(len(U)):
            V += N[U[T] >> 4 & 15]
            V += N[U[T] & 15]
        return V

    def http_req(self, url, ref=None, data=None, timeout=None):
        if ref:
            self._opener.addheaders.append(('Referer', ref))
        ret = self._opener.open(url, data=data, timeout=timeout)
        if ref:
            self._opener.addheaders.pop(1)

        return ret.read()

    def login(self):
        # set cookie
        self.http_req(self.STEP1_URL)
        pgv_info = "ssid=s%d" % random.randint(1e9, 1e10)
        pgv_pvid = str(random.randint(1e9, 1e10))
        ck = Cookie(version=0, name='pgv_info', value=pgv_info, port=None,
                    port_specified=False, domain='qq.com',
                    domain_specified=True, domain_initial_dot=False, path='/',
                    path_specified=True, secure=False, expires=None,
                    discard=True, comment=None, comment_url=None,
                    rest={'HttpOnly': None}, rfc2109=False)
        self._cj.set_cookie(ck)
        ck = Cookie(version=0, name='pgv_pvid', value=pgv_pvid, port=None,
                    port_specified=False, domain='qq.com',
                    domain_specified=True, domain_initial_dot=False, path='/',
                    path_specified=True, secure=False, expires=None,
                    discard=True, comment=None, comment_url=None,
                    rest={'HttpOnly': None}, rfc2109=False)
        self._cj.set_cookie(ck)

        # fetch qrcode image and print as ascii code
        r = self.http_req(self.QRCODE_URL)
        qr.qr_printraw(r)

        # check qrcode status
        while True:
            time.sleep(2)
            qr_status_ret = self.http_req(self.QR_STATUS_URL)
            if qr_status_ret.find("http") >= 0:
                print "verified!"
                break
            if qr_status_ret.find("二维码认证中") >= 0:
                print 'verifying.'
            if qr_status_ret.find("二维码已失效") >= 0:
                print "expired."
                r = self.http_req(self.QRCODE_URL)
                os.system("clear")
                qr.qr_printraw(r)

        # checksig
        checksig_url = qr_status_ret.split(',')[2].strip("''")
        self.http_req(checksig_url)

        cookiedict = {i.name: i.value for i in self._cj}
        self.ptwebqq = cookiedict['ptwebqq']

        # get vfwebqq
        url = self.GET_VFWEBQQ_URL.format(self.ptwebqq, self.client_id,
                                          int(time.time()))
        vfwebqq_ret = json.loads(self.http_req(url, ref=self.S_REFERER_URL))

        if vfwebqq_ret['retcode'] != 0:
            sys.exit(-1)

        self.vfwebqq = vfwebqq_ret['result']['vfwebqq']

        # login2, fetch login token
        login2_post_data = (
            ("r=%7B%22ptwebqq%22%3A%22{}%22%2C%22clientid%22%3A{}%2C" +
             "%22psessionid%22%3A%22%22%2C%22status%22%3A%22hidden%22%7D")
            .format(self.ptwebqq, self.client_id))
        login_ret = json.loads(self.http_req(self.LOGIN2_URL,
                                             ref=self.D_REFERER_URL,
                                             data=login2_post_data))

        if login_ret['retcode'] != 0:
            sys.exit(-1)

        self.uin = str(login_ret['result']['uin'])
        self.psessionid = login_ret['result']['psessionid']
        self.hash_digests = self.hash(self.uin, self.ptwebqq)
        # vfwebqq = login_ret['result']['vfwebqq']

    def get_user_friends(self):
        # get user friends
        get_user_friends_data = (
            "r=%7B%22vfwebqq%22%3A%22{}%22%2C%22hash%22%3A%22{}%22%7D"
            .format(self.vfwebqq, self.hash_digests)
        )

        ret = self.http_req(self.GET_USER_FRIENDS_URL,
                            ref=self.S_REFERER_URL,
                            data=get_user_friends_data)

        userfriends = json.loads(ret)

        if userfriends['retcode'] != 0:
            return False

        results = userfriends['result']
        marknames = {i['uin']: i['markname'] for i in results['marknames']}
        for friend in results['info']:
            uin = friend['uin']
            nick = friend['nick']
            markname = marknames.get(uin, None)

            self.friends[uin] = {
                'pnick': markname if markname else nick,
                'nick': nick,
                'markname': markname
            }

        return True

    def get_group_info_ext(self, gcode):
        url = self.GET_GROUP_INFO_EXT2_URL.format(str(gcode), self.vfwebqq,
                                                  int(time.time()))
        ret = self.http_req(url, ref=self.S_REFERER_URL)

        groupexts = json.loads(ret)

        if groupexts['retcode'] != 0:
            return False

        results = groupexts['result']

        self.groups.setdefault(gcode, {})
        self.groups[gcode]['gid'] = results['ginfo']['gid']
        self.groups[gcode]['name'] = results['ginfo']['name']

        marknames = {i['muin']: i['card'] for i in results['cards']}
        self.groups[gcode].setdefault('members', {})
        for member in results['minfo']:
            uin = member['uin']
            nick = member['nick']
            markname = marknames.get(uin, None)

            self.groups[gcode]['members'][uin] = {
                'pnick': markname if markname else nick,
                'nick': nick,
                'markname': markname
            }

        return True

    def get_discu_info(self, did):
        url = self.GET_DISCU_INFO_URL.format(did, self.vfwebqq, self.client_id,
                                             self.psessionid, int(time.time()))
        ret = self.http_req(url, ref=self.D_REFERER_URL)

        discuinfos = json.loads(ret)

        if discuinfos['retcode'] != 0:
            return False

        results = discuinfos['result']

        self.discus.setdefault(did, {})
        self.discus[did]['name'] = results['info']['discu_name']
        self.discus[did].setdefault('members', {})
        for member in results['mem_info']:
            uin = member['uin']
            nick = member['nick']
            self.discus[did]['members'][uin] = {
                'nick': nick
            }

    def get_gname_by_gcode(self, gcode):
        for i in range(3):
            if gcode not in self.groups:
                self.get_group_info_ext(gcode)
            else:
                break
        return self.groups[gcode]['name']

    def get_dname_by_did(self, did):
        for i in range(3):
            if did not in self.discus:
                self.get_discu_info(did)
            else:
                break
        return self.discus[did]['name']

    def get_nick_by_uin(self, uin):
        if uin in self.friends:
            return self.friends[uin]['pnick']

        for group in self.groups.values:
            if uin in group['members']:
                return group['members'][uin]['nick']

        for discu in self.discus.values:
            if uin in discu['members']:
                return discu['members'][uin]['nick']

        return str(uin)

    def get_nick_by_uin_gcode(self, uin, gcode):
        if gcode not in self.groups:
            self.get_group_info_ext(gcode)

        if uin in self.groups[gcode]['members']:
            return self.groups[gcode]['members'][uin]['pnick']

        return str(uin)

    def get_nick_by_uin_did(self, uin, did):
        if did not in self.discus:
            self.get_discu_info(did)

        if uin in self.discus[did]['members']:
            return self.discus[did]['members'][uin]['nick']

        return str(uin)

    def send_group_msg_by_uin(self, group_uin, msg):
        url = 'http://d.web2.qq.com/channel/send_qun_msg2'
        post_dict = {"group_uin": int(group_uin),
                     "content": ("[\"" + msg +
                                 "\",[\"font\",{\"name\":\"宋体\",\"size\":10"
                                 ",\"style\":[0,0,0],\"color\":\"000000\"}]]"),
                     "face": 579,
                     "clientid": self.client_id,
                     "msg_id": self.msg_id,
                     "psessionid": self.psessionid
                     }
        self.msg_id += 1
        print self.http_req(url, ref=self.D_REFERER_URL,
                            data='r=' + urllib.quote(json.dumps(post_dict)))

    def content2string(self, contents):
        line = ""
        for content in contents:
            if isinstance(content, list):
                if (content[0] == 'cface' or
                        content[0] == 'face' or
                        content[0] == 'offpic'):
                    line += '[sticker]'
            elif isinstance(content, unicode):
                line += content
            else:
                print content
        return line

    def dispatcher(self, results):
        for result in results:
            poll_type = result['poll_type']
            value = result['value']
            if poll_type == 'group_message':
                # TODO dispatch group_message
                gname = self.get_gname_by_gcode(value['group_code'])
                nick = self.get_nick_by_uin_gcode(value['send_uin'],
                                                  value['group_code'])
                line = self.content2string(value['content'])
                print u'[GROUP {}] {}: {}'.format(
                    gname, nick, line)
            elif poll_type == 'discu_message':
                # TODO dispatch discus message
                dname = self.get_dname_by_did(value['did'])
                nick = self.get_nick_by_uin_did(value['send_uin'],
                                                value['did'])
                line = self.content2string(value['content'])
                print u'[DISCUS {}] {}: {}'.format(
                    dname, nick, line)
            elif poll_type == 'message':
                # TODO dispatch message
                line = self.content2string(value['content'])
                nick = self.get_nick_by_uin(value['from_uin'])
                print u'[PRIV] {}: {}'.format(
                    nick, line)
            elif poll_type == 'buddies_status_change':
                pass
            elif poll_type == 'kick_message':
                return False, result['value']['reason']
            else:
                print 'Unhandled poll type: ' + result['poll_type']
                print result
        return True, None

    def loop(self):
        post_data = (
            ("r=%7B%22ptwebqq%22%3A%22{}%22%2C%22clientid%22%3A{}%2C" +
             "%22psessionid%22%3A%22{}%22%2C%22key%22%3A%22%22%7D")
            .format(self.ptwebqq, self.client_id, self.psessionid)
        )

        while True:
            try:
                ret = self.http_req(self.POLL2_URL, ref=self.D_REFERER_URL,
                                    data=post_data, timeout=5)
            except urllib2.URLError, e:
                print "error: %s" % e
                continue
            except socket.timeout:
                print 'timeout'
                continue

            print ret
            if ret:
                poll = json.loads(ret)

            if poll['retcode'] == 116:
                # update tokens
                self.ptwebqq = poll['p']
                self.hash_digests = self.hash(self.uin, self.ptwebqq)
                post_data = (
                    ("r=%7B%22ptwebqq%22%3A%22{}%22%2C%22clientid%22%3A"
                     "{}%2C%22psessionid%22%3A%22{}%22%2C%22"
                     "key%22%3A%22%22%7D")
                    .format(self.ptwebqq, self.client_id, self.psessionid)
                )
                continue
            elif poll['retcode'] != 0:
                print poll
                continue

            s, e = self.dispatcher(poll['result'])
            if s:
                time.sleep(1)
            else:
                print e
                return False


if __name__ == '__main__':
    fqq = Fqq()
    fqq.login()
    fqq.get_user_friends()
    print 'user friends infomation fetched.'
    fqq.loop()
