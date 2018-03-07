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
            d = json.dumps(d)
            self.write(d)

class CtxHandler(tornado.web.RequestHandler):
    def post(self):
        name     = self.get_argument('username', None)
        password = self.get_argument('password', None)
        if not name or not password:
            r = {'code': -1, 'data': {}, 'msg': 'cookie is invalid'}
            r = json.dumps(r)
            self.write(r)
        else:
            d = get_ctx_info(name, password)
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
        name   = self.get_argument('username', None)
        passwd = self.get_argument('password', None)
        if not name or not passwd:
            r = {'code': -1, 'msg': 'username or password is null'}
            d = json.dumps(r)
            self.write(d)
        else:
            r = query_user_login(name, passwd)
            if not r:
                d = {'code': -1, 'msg': 'not exist'}
            else:
                uid = r['id']
                info = get_user_info(uid)
                info['user'] = r
                d = {'code': 0, 'msg': 'success', 'data': info}
            d = json.dumps(d)
            self.write(d)

class RegistHandler(tornado.web.RequestHandler):
    def post(self):
        name   = self.get_argument('username', None)
        passwd = self.get_argument('password', None)
        if not name or not passwd:
            self.write('-1')
        else:
            r = self.__regist(name, passwd)
            if not r:
                self.write('-1')
            else:
                self.write('0')
            self.finish()
    def __regist(self, name, passwd):
        r = user_regist(name, passwd)
        return r

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
        mobile    = self.get_argument('mobile', None)
        email     = self.get_argument('email', None)
        wx        = self.get_argument('wx', None)
        qq        = self.get_argument('qq', None)
        if not ctx:
            r = {'code': -1, 'msg':'invalid', 'data': {}}
            r = json.dumps(r)
            self.write(r)
        elif not mobile and not email and not wx and not qq:
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
                r = edit_other(mobile, email, wx, qq, **d)
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
        ('/basic_edit', BasicEditHandler), 
        ('/statement_edit', StatementEditHandler),
        ('/other_edit', OtherEditHandler),
       #('/publish', PublishHandler),
        ('/new', IndexNewHandler),
              ]
    application = tornado.web.Application(handler, **settings)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
