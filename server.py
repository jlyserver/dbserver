#-*- coding: utf-8 -*-

import tornado.httpserver
import tornado.ioloop
import tornado.web
import tornado.options
import hashlib
import os.path
import json
import time
import datetime
import re
from tornado.options import define, options
from conf import conf
from db import *

define("port", default=conf.sys_port, help="run on the given port", type=int)

class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("mobile")
    def get_role(self):
        return int(self.get_secure_cookie("role"))

class IndexDataTestHandler(tornado.web.RequestHandler):
    def post(self):
        e = {'name':'夏天未迁', 'sex':'男', 'age': '22岁', 'height': '165cm','degree': '本科', 'state': '简单的我，简单的生活，简单的交友，我的世界如此简单简单的我，简单的生活，简单的交友，我的世界如此简单', 'img':'img/img1.jpg'}
        D = {'new_male': [ e for i in xrange(4) ], \
             'new_female': [ e for i in xrange(4) ], \
             'find': [e for i in xrange(8) ]}
        a = json.dumps(D)
        self.write(a)
        
class IndexDataHandler(tornado.web.RequestHandler):
    def post(self):
        t = time.time()
        t = t - conf.toffset_newest*3600*24
        t = time.localtime(t)
        now = time.strftime('%Y-%m-%d %H:%M:%S', t)
        c = {'regist_time': now}
        new = query_user(**c)
       
        other = query_user(**{})
        r = {'new': new, 'other':other}
        cnt = json.dumps(r)
        self.write(cnt)

class IndexNewHandler(tornado.web.RequestHandler):
    def post(self):
        sex   = int(self.get_argument('sex',   0))
        limit = int(self.get_argument('limit', 0))
        page  = int(self.get_argument('page',  0))
        next_ = int(self.get_argument('next',  0))
        if sex < 1 or limit < 1 or page < 1 or next_ != 0:
            d = {'code': -1, 'msg':'error', 'data':{}}
            d = json.dumps(d)
            self.write(d)
        else:
            t = time.time()
            t = t - conf.toffset_newest*3600*24
            t = time.localtime(t)
            now = time.strftime('%Y-%m-%d %H:%M:%S', t)
            r = query_new(t, sex, limit, page, next_)
            d = {'code':0, 'msg':'ok', 'data':r}
            print('sex=%d'%sex)
            print(d)
            d = json.dumps(d)
            self.write(d)

class FindHandler(tornado.web.RequestHandler):
    def post(self):
        sex          = int(self.get_argument('sex',     -1))
        agemin       = int(self.get_argument('agemin',  -1))
        agemax       = int(self.get_argument('agemax',  -1))
        cur1         = self.get_argument('cur1',    None)
        cur2         = self.get_argument('cur2',    None)
        ori1         = self.get_argument('ori1',    None)
        ori2         = self.get_argument('ori2',    None)
        degree       = int(self.get_argument('degree', -1))
        salary       = int(self.get_argument('salary', -1))
        xz           = self.get_argument('xingzuo', None)
        sx           = self.get_argument('shengxiao', None)
        limit        = int(self.get_argument('limit', -1))
        page         = int(self.get_argument('page', -1))
        next_        = int(self.get_argument('next', -1))
        if agemin > agemax:
            agemin, agemax = agemax, agemin
        c, r = find_users(sex, agemin, agemax, cur1, cur2, ori1, ori2,\
                          degree, salary, xz, sx, limit, page, next_)
        print(r)
        if not r:
            d = {'code': -1, 'msg':'error', 'data':{}}
            d = json.dumps(d)
            self.write(d)
        else:
            d = {'code': 0, 'msg':'ok', 'count':c, 'data':r}
            d = json.dumps(d)
            self.write(d)

class CtxHandler(tornado.web.RequestHandler):
    def post(self):
        uid = self.get_argument('uid', None)
        if not uid:
            r = {'code': -1, 'data': {}, 'msg': 'cookie is invalid'}
            r = json.dumps(r)
            self.write(r)
        else:
            d = get_ctx_info(uid)
            if not d:
                r = {'code': -1, 'data': {}, 'msg': 'no user exist'}
                r = json.dumps(r)
                self.write(r)
            else:
                r = {'code': 0, 'data': d, 'msg': 'ok'}
                r = json.dumps(r)
                self.write(r)
class LoginHandler(tornado.web.RequestHandler):
    def post(self):
        mobile = self.get_argument('mobile', None)
        passwd = self.get_argument('password', None)
        if not mobile or not passwd:
            r = {'code': -1, 'msg': 'mobile or password is null'}
            d = json.dumps(r)
            self.write(d)
        else:
            r = query_user_login(mobile, passwd)
            if not r:
                d = {'code': -1, 'msg': 'not exist'}
            else:
                uid = r['id']
                info = get_user_info(uid)
                info['user'] = r
                d = {'code': 0, 'msg': 'ok', 'data': info}
            d = json.dumps(d)
            self.write(d)
#注册发送验证码
class VerifyHandler(tornado.web.RequestHandler):
    def post(self):
        mobile = self.get_argument('mobile', None)
        if not mobile:
            d = {'code':-1, 'msg':'电话号码不正确'}
            d = json.dumps(d)
            self.write(d)
        else:
            r = verify_mobile(mobile)
            d = {}
            #注册
            if not r:
                d = {'code': 0, 'msg':'手机号不存在'}#表示可以注册
            else:
                d = {'code': -1, 'msg':'手机号已存在'}#表示不可以注册
            d = json.dumps(d)
            self.write(d)
            self.finish()
#验证手机发送验证码
class VerifyMobileHandler(tornado.web.RequestHandler):
    def post(self):
        mobile = self.get_argument('mobile', None)
        uid    = self.get_argument('uid',    None)
        p = '^(1[356789])[0-9]{9}$'
        d = {}
        if not uid or not mobile or not re.match(p, mobile):
            d = {'code':-1, 'msg':'invalid parameters'}
        else:
            ctx = merge_mobile(uid, mobile)
            if not ctx:
                d = {'code': -1, 'msg':'invalid parameters'}
            else:
                d = {'code': 0, 'msg': 'ok', 'data':ctx}
        d = json.dumps(d)
        self.write(d)

class FindVerifyHandler(tornado.web.RequestHandler):
    def post(self):
        mobile = self.get_argument('mobile', None)
        if not mobile:
            d = {'code':-1, 'msg':'电话号码为空'}
            d = json.dumps(d)
            self.write(d)
        else:
            r = verify_mobile(mobile)
            d = {}
            if not r:
                d = {'code': -1, 'msg':'手机号不存在'}#表示不可以找回
            else:
                d = {'code': 0, 'msg':'手机号已存在', 'data':r}#表示可以找回
            d = json.dumps(d)
            self.write(d)

class FindPasswordHandler(tornado.web.RequestHandler):
    def post(self):
        mobile = self.get_argument('mobile', None)
        passwd = self.get_argument('password', None)
        d = {}
        if not mobile or not passwd:
            d = {'code':-1, 'msg':'手机号和密码不能为空'}
        else:
            r = find_password(mobile, passwd)
            if not r:
                d = {'code': -1, 'msg': '手机号不存在'}
            else:
                d = {'code': 0, 'msg': '重置密码成功', 'data':r}
        d = json.dumps(d)
        self.write(d)


class RegistHandler(tornado.web.RequestHandler):
    def post(self):
        mobile = self.get_argument('mobile', None)
        passwd = self.get_argument('password', None)
        sex    = int(self.get_argument('sex', 0))
        p = '^(1[356789])[0-9]{9}$'
        if not mobile or not re.match(p, mobile) or not passwd or sex not in [1,2]:
            d = {'code':-1, 'msg':'参数错误'}
            d = json.dumps(d)
            self.write(d)
            self.finish()
        else:
            d = {}
            r = user_regist(mobile, passwd, sex)
            if not r:
                d = {'code':-2, 'msg':'该号码已被注册过了'}
            else:
                d = {'code': 0, 'msg':'注册成功', 'data':r}
            d = json.dumps(d)
            self.write(d)
            self.finish()

class BasicEditHandler(tornado.web.RequestHandler):
    def post(self):
        ctx          = self.get_argument('ctx', None)
        nick_name    = self.get_argument('nick_name', None)
        aim          = self.get_argument('aim',       None)
        age          = self.get_argument('age',       None)
        marriage     = self.get_argument('marriage',  None)
        xingzuo      = self.get_argument('xingzuo',   None)
        shengxiao    = self.get_argument('shengxiao', None)
        blood        = self.get_argument('blood',     None)
        weight       = self.get_argument('weight',    None)
        height       = self.get_argument('height',    None)
        degree       = self.get_argument('degree',    None)
        nation       = self.get_argument('nation',    None)
        cur_loc1     = self.get_argument('cur_loc1',  None)
        cur_loc2     = self.get_argument('cur_loc2',  None)
        ori_loc1     = self.get_argument('ori_loc1',  None)
        ori_loc2     = self.get_argument('ori_loc2',  None)
        motto        = self.get_argument('motto',     None)
        hobby        = self.get_argument('hobby',     []) 
        if hobby:
            h = []
            try:
                h = json.loads(hobby)
            except:
                h = []
            hobby = h
        c = {}
        try:
            c = json.loads(ctx)
        except:
            c = {}
        ctx = c
        if not ctx:
            r = {'code':-1, 'msg': '没有找到对应的用户'}
            r = json.dumps(r)
            self.write(r)
        else:
            r = update_basic(nick_name, aim, age, marriage, xingzuo,\
                       shengxiao, blood, weight, height, degree, nation, \
                  cur_loc1, cur_loc2, ori_loc1, ori_loc2, motto, *hobby, **ctx)
            if not r:
                r = {'code': -1, 'msg': '编辑失败'}
            else:
                r = {'code': 0, 'msg': '编辑成功', 'data': r}
            r = json.dumps(r)
            self.write(r)

class StatementEditHandler(tornado.web.RequestHandler):
    def post(self):
        ctx       = self.get_argument('ctx', None)
        cnt       = self.get_argument('content', None)
        if not ctx or not cnt:
            r = {'code': -1, 'msg':'failed!', 'data': {}}
            r = json.dumps(r)
            self.write(r)
        else:
            d = {}
            try:
                d = json.loads(ctx)
            except:
                d = {}
            if not d:
                r = {'code': -1, 'msg':'failed!', 'data': {}}
                r = json.dumps(r)
                self.write(r)
            else:
                r = edit_statement(cnt, **d)
                if not r:
                    r = {'code': -1, 'msg': '编辑失败'}
                else:
                    r = {'code': 0, 'msg': '编辑成功', 'data': r}
                r = json.dumps(r)
                self.write(r)

class OtherEditHandler(tornado.web.RequestHandler):
    def post(self):
        ctx       = self.get_argument('ctx', None)
        salary    = self.get_argument('salary', None)
        work      = self.get_argument('work', None)
        car       = self.get_argument('car', None)
        house     = self.get_argument('house', None)
        if not ctx:
            r = {'code': -1, 'msg':'invalid', 'data': {}}
            r = json.dumps(r)
            self.write(r)
        elif not salary and not work and not car and not house:
            r = {'code': -1, 'msg':'noneed', 'data': {}}
            r = json.dumps(r)
            self.write(r)
        else:
            d = {}
            try:
                d = json.loads(ctx)
            except:
                d = {}
            if not d:
                r = {'code': -1, 'msg':'invalid', 'data': {}}
                r = json.dumps(r)
                self.write(r)
            else:
                r = edit_other(salary, work, car, house, **d)
                if not r:
                    r = {'code': -1, 'msg': '编辑失败'}
                else:
                    r = {'code': 0, 'msg': '编辑成功', 'data': r}
                r = json.dumps(r)
                self.write(r)
            
class PublishHandler(tornado.web.RequestHandler):
    def post(self):
        ctx       = self.get_argument('ctx', None)
        kind      = self.get_argument('kind', None)
        action    = self.get_argument('action', None)
        if not ctx or not kind or not action:
            r = {'code': -1, 'msg':'invalid', 'data': {}}
            r = json.dumps(r)
            self.write(r)
        else:
            d = {}
            try:
                d = json.loads(ctx)
            except:
                d = {}
            if not d:
                r = {'code': -1, 'msg':'invalid', 'data': {}}
                r = json.dumps(r)
                self.write(r)
            else:
                r = publish_conn(kind, action, **d)
                if not r:
                    r = {'code': -1, 'msg': '编辑失败'}
                else:
                    r = {'code': 0, 'msg': '编辑成功', 'data': r}
                r = json.dumps(r)
                self.write(r)


if __name__ == "__main__":
    tornado.options.parse_command_line()
    settings = {
        "cookie_secret": "bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E=",
        "xsrf_cookies": False,
        "debug":True}
    handler = [
       #('/indexdata', IndexDataHandler),
        ('/ctx', CtxHandler),
        ('/indexdata', IndexDataTestHandler),
        ('/login', LoginHandler),
        ('/regist', RegistHandler),
        ('/verify', VerifyHandler),
        ('/verify_mobile', VerifyMobileHandler),
        ('/find_verify', FindVerifyHandler),
        ('/find_password', FindPasswordHandler),
        ('/basic_edit', BasicEditHandler), 
        ('/statement_edit', StatementEditHandler),
        ('/other_edit', OtherEditHandler),
       #('/publish', PublishHandler),
        ('/new', IndexNewHandler),
        ('/find', FindHandler),
              ]
    application = tornado.web.Application(handler, **settings)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
