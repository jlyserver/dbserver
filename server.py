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
from cache import cache

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
        d = {'code': -1, 'msg':'参数错误'}
        if sex < 1 or limit < 1 or page < 1 or next_ != 0:
            pass
        else:
            t = time.time()
            t = t - conf.toffset_newest*3600*24
            t = time.localtime(t)
            now = time.strftime('%Y-%m-%d %H:%M:%S', t)
            r = query_new(t, sex, limit, page, next_)
            d = {'code':0, 'msg':'ok', 'data':r}
        d = json.dumps(d)
        self.write(d)

class FindHandler(tornado.web.RequestHandler):
    def post(self):
        sex          = self.get_argument('sex', None)
#       sex          = int(sex) if sex else -1
        agemin       = self.get_argument('agemin', None)
#       agemin       = int(agemin) if agemin else -1
        agemax       = self.get_argument('agemax', None)
#       agemax       = int(agemax) if agemax else -1
        cur1         = self.get_argument('cur1',    None)
        cur2         = self.get_argument('cur2',    None)
        ori1         = self.get_argument('ori1',    None)
        ori2         = self.get_argument('ori2',    None)
        degree       = self.get_argument('degree', None)
#       degree       = int(degree) if degree else -1
        salary       = self.get_argument('salary', None)
#       salary       = int(salary) if salary else -1
        xz           = self.get_argument('xingzuo', None)
        sx           = self.get_argument('shengxiao', None)
        limit        = self.get_argument('limit', None)
#       limit        = int(limit) if limit else -1
        page         = self.get_argument('page', None)
#       page         = int(page) if page else -1
        next_        = self.get_argument('next', None)
#       next_        = int(next_) if next_ else -1
        uid          = self.get_argument('uid', None)
        d = {}
        print('sex=', sex, not sex)
        print('agemin=', agemin, not agemin)
        print('agemax=', agemax, not agemax)
        print('cur1=', cur1, not cur1)
        print('cur2=', cur2, not cur2)
        print('ori1=', ori1, not ori1)
        print('ori2=', ori2, not ori2)
        print('degree=', degree, not degree)
        print('salary=', salary, not salary)
        print('xz=', xz, not xz)
        print('sx=', sx, not sx)
        print('limit=', limit, not limit)
        print('page=', page, not page)
        print('next=', next_, not next_)
        print('uid=', uid, not uid)
        usex = get_sex_by_uid(uid=uid)
        c, r, page = find_users(sex, agemin, agemax, cur1, cur2, ori1, ori2,\
                          degree, salary, xz, sx, limit, page, next_)
        d = {'code': 0, 'msg':'ok', 'count':c, 'data':r, 'page': page}
        if usex:
            d['sex'] = usex
        if conf.debug:
            print(d)
        d = json.dumps(d)
        self.write(d)

class EmailHandler(tornado.web.RequestHandler):
    def post(self):
        uid = self.get_argument('uid', None)
        page = self.get_argument('page', None)
        next_ = self.get_argument('next', None)
        d = {} 
        if not uid or not page or not next_:
            d = {'code': -1, 'msg': '参数不正确'}
        else:
            uid, page, next_ = int(uid), int(page), int(next_)
            r = email(uid=uid, page=page, next_=next_)
            if not r:
                d = {'code': -1, 'msg': '参数不正确'}
            else:
                d = {'code': 0, 'msg': 'ok', 'data': r}
        d = json.dumps(d)
        self.write(d)

class SeeEmailHandler(tornado.web.RequestHandler):
    def post(self):
        eid  = self.get_argument('eid', None)
        cuid = self.get_argument('cuid', None)
        d = {} 
        if not eid or not cuid:
            d = {'code': -1, 'msg': '参数不正确'}
        else:
            eid, cuid = int(eid), int(cuid)
            r = see_email(eid=eid, cuid=cuid)
            if not r:
                d = {'code': -1, 'msg': '参数不正确'}
            else:
                d = {'code': 0, 'msg': 'ok'}
        d = json.dumps(d)
        self.write(d)

class LatestConnHandler(tornado.web.RequestHandler):
    def post(self):
        uid = self.get_argument('uid', None)
        d = {}
        if not uid:
            d = {'code': -1, 'msg': '参数不正确'}
        else:
            uid = int(uid)
            n, r = latest_conn(uid=uid)       
            if n < 0:
                d = {'code': -1, 'msg': '参数不正确'}
            else:
                d = {'code': 0, 'msg': 'ok', 'data': r}
        d = json.dumps(d)
        self.write(d)

class SendEmailHandler(tornado.web.RequestHandler):
    def post(self):
        uid  = self.get_argument('uid', None)
        cuid = self.get_argument('cuid',None)
        cnt  = self.get_argument('content', None)
        eid  = self.get_argument('eid', '')
        kind = self.get_argument('kind', None)
        d = {} 
        if not uid or not cuid or not cnt: 
            d = {'code': -1, 'msg': '参数不正确'}
        elif uid == cuid:
            d = {'code': -1, 'msg': '自己不用给自己发信'}
        else:
            if kind:
                kind = int(kind)
            else:
                kind = 0
            r = sendemail(uid=uid,cuid=cuid,content=cnt,eid=eid,kind=kind)
            if r == -1:
                d = {'code': -1, 'msg': '参数不正确'}
            elif r == -2:
                d = {'code': -1, 'msg': '余额不足'}
            else:
                d = {'code': 0, 'msg': 'ok'}
        d = json.dumps(d)
        self.write(d)
    
class DelEmailHandler(tornado.web.RequestHandler):
    def post(self):
        uid  = self.get_argument('uid', None)
        eid  = self.get_argument('eid',None)
        d = {} 
        if not uid or not eid: 
            d = {'code': -1, 'msg': '参数不正确'}
        else:
            uid, eid = int(uid), int(eid)
            r = del_email(uid=uid, eid=eid)
            if not r:
                d = {'code': -1, 'msg': '参数不正确'}
            else:
                d = {'code': 0, 'msg': 'ok'}
        d = json.dumps(d)
        self.write(d)

class YanyuanHandler(tornado.web.RequestHandler):
    def post(self):
        uid  = self.get_argument('uid', None)
        cuid = self.get_argument('cuid',None)
        d = {} 
        if not uid or not cuid: 
            d = {'code': -1, 'msg': '参数不正确'}
        elif uid == cuid:
            d = {'code': -1, 'msg': '自己不用给自己发眼缘'}
        else:
            r = yanyuan(uid=uid, cuid=cuid)
            if not r:
                d = {'code': -1, 'msg': '参数不正确'}
            else:
                d = {'code': 0, 'msg': 'ok'}
        d = json.dumps(d)
        self.write(d)

class YanyuanCheckHandler(tornado.web.RequestHandler):
    def post(self):
        uid  = self.get_argument('uid', None)
        cuid = self.get_argument('cuid',None)
        d = {} 
        if not uid or not cuid: 
            d = {'code': -1, 'msg': '参数不正确'}
        elif uid == cuid:
            d = {'code': -1, 'msg': '自己不用给自己发眼缘'}
        else:
            r = yanyuan_check(uid=uid, cuid=cuid)
            if not r:
                d = {'code': -1, 'msg': '参数不正确'}
            else:
                d = {'code': 0, 'msg': 'ok', 'data':{'yanyuan':1}}
        d = json.dumps(d)
        self.write(d)

class GuanzhuCheckHandler(tornado.web.RequestHandler):
    def post(self):
        uid  = self.get_argument('uid', None)
        cuid = self.get_argument('cuid',None)
        kind = self.get_argument('kind', None)
        d = {} 
        if not uid or not cuid or not kind: 
            d = {'code': -1, 'msg': '参数不正确'}
        elif uid == cuid:
            d = {'code': -1, 'msg': '自己不用关注自己'}
        else:
            r = guanzhu_check(uid=uid, cuid=cuid, kind=kind)
            if not r:
                d = {'code': -1, 'msg': '参数不正确'}
            else:
                d = {'code': 0, 'msg': 'ok', 'data':r}
        d = json.dumps(d)
        self.write(d)

class CtxHandler(tornado.web.RequestHandler):
    def post(self):
        uid = self.get_argument('uid', None)
        d = {'code': -1, 'msg': '参数不正确'}
        if uid:
            uid = int(uid)
            r = get_ctx_info(uid)
            if r:
                d = {'code': 0, 'data': r, 'msg': 'ok'}
        d = json.dumps(d)
        self.write(d)

class LoginHandler(tornado.web.RequestHandler):
    def post(self):
        mobile = self.get_argument('mobile', None)
        passwd = self.get_argument('password', None)
        d = {'code': -1, 'msg': '参数错误'}
        if not mobile or not passwd:
            pass
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

class WxLoginHandler(tornado.web.RequestHandler):
    def post(self):
        nick_name = self.get_argument('nick_name', '')
        sex       = self.get_argument('sex', '1')
        unionid   = self.get_argument('unionid', '')
        src       = self.get_argument('src', '')
        if conf.debug:
            print('nick_name=%s' % nick_name)
            print('sex=%s'%sex)
            print('unionid=%s'%unionid)
        d = {'code': -1, 'msg': '参数错误'}
        if not unionid:
            pass
        else:
            r = wx_login_and_regist(unionid=unionid, sex=sex, nick_name=nick_name, src=src)
            if conf.debug:
                print('r=', r)
            if r:
                d = {'code': 0, 'msg': 'ok', 'data':r}
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
        uid          = self.get_argument('uid', None)
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
        cur_loc1     = self.get_argument('curr_loc1',  None)
        cur_loc2     = self.get_argument('curr_loc2',  None)
        ori_loc1     = self.get_argument('ori_loc1',  None)
        ori_loc2     = self.get_argument('ori_loc2',  None)
        motto        = self.get_argument('motto',     None)
        hobby        = self.get_argument('hobby',     '') 
        d = {'code': -1, 'msg': '参数不正确'}
        if not uid:
            pass
        else:
            if conf.debug:
                print('hobby=%s' % hobby)
            if hobby:
                h = []
                try:
                    h = json.loads(hobby)
                except:
                    h = []
                hobby = h
            r = update_basic(uid, nick_name, aim, age, marriage, xingzuo,\
                       shengxiao, blood, weight, height, degree, nation, \
                  cur_loc1, cur_loc2, ori_loc1, ori_loc2, motto, *hobby)
            if conf.debug:
                print('cur_loc1=%s cur_loc2=%s ori_loc1=%s ori_loc2=%s', (cur_loc1, cur_loc2, ori_loc1, ori_loc2))
            if not r:
                d = {'code': -1, 'msg': '编辑失败'}
            else:
                d = {'code': 0, 'msg': '编辑成功', 'data': r}
        d = json.dumps(d)
        self.write(d)

class StatementEditHandler(tornado.web.RequestHandler):
    def post(self):
        uid       = self.get_argument('uid', None)
        cnt       = self.get_argument('content', None)
        d = {'code': -1, 'msg': '参数错误'}
        if not uid or not cnt:
            pass
        else:
            r = edit_statement(uid, cnt)
            if r:
                d = {'code': 0, 'msg': '编辑成功'}
        d = json.dumps(d)
        self.write(d)

class OtherEditHandler(tornado.web.RequestHandler):
    def post(self):
        uid       = self.get_argument('uid', None)
        salary    = self.get_argument('salary', None)
        work      = self.get_argument('work', None)
        car       = self.get_argument('car', None)
        house     = self.get_argument('house', None)
        mobile    = self.get_argument('mobile', None)
        wx        = self.get_argument('wx', None)
        qq        = self.get_argument('qq', None)
        email     = self.get_argument('email', None)

        d = {'code': -1, 'msg': '参数错误'}
        if not uid:
            pass
        elif not salary and not work and not car and not house:
            pass
        else:
            r = edit_other(uid, salary, work, car, house,\
                    mobile, wx, qq, email)
            if r:
                d = {'code': 0, 'msg': '编辑成功', 'data': r}
        d = json.dumps(d)
        self.write(d)

class SeeOtherHandler(tornado.web.RequestHandler):
    def post(self):
        kind = int(self.get_argument('kind', 0))
        uid  = self.get_argument('uid', None)
        cuid = self.get_argument('cuid', None)
        d = {'code': -1, 'msg':'参数不正确'}
        if kind not in [1,2,3,4] or not uid or not cuid:
            d = {'code': -1, 'msg':'参数不正确'}
        else:
            uid, cuid = int(uid), int(cuid)
            d = seeother(kind=kind, uid=uid, cuid=cuid)
        d = json.dumps(d)
        self.write(d)

class SawOtherHandler(tornado.web.RequestHandler):
    def post(self):
        uid  = self.get_argument('uid', None)
        cuid = self.get_argument('cuid', None)
        d = {'code': -1, 'msg':'参数不正确'}
        if not uid or not cuid:
            d = {'code': -1, 'msg':'参数不正确'}
        else:
            d = sawother(uid=uid, cuid=cuid)
        d = json.dumps(d)
        self.write(d)


class VerifyOtherHandler(tornado.web.RequestHandler):
    def post(self):
        kind = int(self.get_argument('kind', 0))
        uid  = self.get_argument('uid',  None)
        num  = self.get_argument('num',  None)
        d = {'code':-1, 'msg':'参数错误'}
        if not uid or not kind or not num:
            pass
        else:
            r = verify_wx_qq_email(uid, num, kind)
            if r:
                d = {'code': 0, 'msg': '验证成功', 'data': r}
        d = json.dumps(d)
        self.write(d)

class ImgHandler(tornado.web.RequestHandler):
    def post(self):
        uid = self.get_argument('uid', None)
        f   = self.get_argument('f',   None)
        s   = self.get_argument('s',   None)
        t   = self.get_argument('t',   None)
        k   = self.get_argument('k',   None)
        d = {'code': -1, 'msg': '参数不正确'}
        if not uid or not f or not s or not t or not k:
            d = {'code': -1, 'msg': '参数不正确'}
        else:
            r = write_img(uid=uid, first=f, second=s, third=t, kind=k)
            if r:
               d = {'code': 0, 'msg': 'ok'}
        d = json.dumps(d)
        self.write(d)
        self.finish()
            
class DelImgHandler(tornado.web.RequestHandler):
    def post(self):
        uid = self.get_argument('uid', None)
        src = self.get_argument('src', None)
        d = {'code': -1, 'msg': '参数不正确'}
        if not uid or not src:
            d = {'code': -1, 'msg': '参数不正确'}
        else:
            r = delimg(uid=uid, src=src)
            if r:
                d = {'code': 0, 'msg': 'ok'}
        d = json.dumps(d)
        self.write(d)
            

class PublicHandler(tornado.web.RequestHandler):
    def post(self):
        uid       = self.get_argument('uid', None)
        kind      = self.get_argument('kind', None)
        action    = self.get_argument('action', None)
        if not uid or not kind or not action:
            r = {'code': -1, 'msg':'参数不正确'}
            r = json.dumps(r)
            self.write(r)
        else:
            kind, action = int(kind), int(action)
            r = public_conn(uid, kind, action)
            if not r:
                r = {'code': -1, 'msg': '参数错误'}
            else:
                r = {'code': 0, 'msg': 'ok'}
            r = json.dumps(r)
            self.write(r)

class ISeeHandler(tornado.web.RequestHandler):
    def post(self):
        uid = self.get_argument('uid', None)
        if not uid:
            d = {'code': -1, 'msg':'参数不正确'}
            d = json.dumps(d)
            self.write(d)
        else:
            uid = int(uid)
            n, r = isee(uid)
            if n >= 0:
                d = {'code': 0, 'msg':'ok', 'data': {'count':n, 'data':r}}
            else:
                d = {'code': -2, 'msg': '请先登录'}
            d = json.dumps(d)
            self.write(d)

class SeeMeHandler(tornado.web.RequestHandler):
    def post(self):
        uid = self.get_argument('uid', None)
        if not uid:
            d = {'code': -1, 'msg':'参数不正确'}
            d = json.dumps(d)
            self.write(d)
        else:
            uid = int(uid)
            n, r = seeme(uid)
            if n >= 0:
                d = {'code': 0, 'msg':'ok', 'data': {'count':n, 'data':r}}
            else:
                d = {'code': -2, 'msg': '请先登录'}
            d = json.dumps(d)
            self.write(d)

class ICareHandler(tornado.web.RequestHandler):
    def post(self):
        uid = self.get_argument('uid', None)
        if not uid:
            d = {'code': -1, 'msg':'参数不正确'}
            d = json.dumps(d)
            self.write(d)
        else:
            uid = int(uid)
            n, r = icare(uid)
            if n >= 0:
                d = {'code': 0, 'msg':'ok', 'data': {'count':n, 'data':r}}
            else:
                d = {'code': -2, 'msg': '请先登录'}
            d = json.dumps(d)
            self.write(d)

class SendCareHandler(tornado.web.RequestHandler):
    def post(self):
        uid = self.get_argument('uid', None)
        cuid= self.get_argument('cuid',None)
        kind= self.get_argument('kind', None)
        d = {}
        if not uid or not cuid or not kind:
            d = {'code': -1, 'msg':'参数不正确'}
        else:
            uid, cuid, kind = int(uid),int(cuid),int(kind)
            r = sendcare(uid=uid, cuid=cuid, kind=kind)
            if not r:
                d = {'code': 0, 'msg':'ok'}
            else:
                d = {'code': -1, 'msg': '请先登录'}
        d = json.dumps(d)
        self.write(d)

class ListDatingHandler(tornado.web.RequestHandler):
    def post(self):
        sex      = self.get_argument('sex', None)
        age1     = self.get_argument('age1', None)
        age2     = self.get_argument('age2', None)
        loc1     = self.get_argument('loc1', None)
        loc2     = self.get_argument('loc2', None)
        page     = self.get_argument('page', None)
        limit    = self.get_argument('limit', None)
        next_    = self.get_argument('next', None)
        r = list_dating(sex=sex, age1=age1, age2=age2, loc1=loc1, loc2=loc2, page=page, limit=limit, next_=next_)
        d = {'code':0, 'msg':'ok', 'data':r}
        d = json.dumps(d)
        self.write(d)

class CreateDatingHandler(tornado.web.RequestHandler):
    def post(self):
        uid        = self.get_argument('uid', None)
        age        = int(self.get_argument('age', 18))
        sjt        = self.get_argument('sjt', None)
        dt         = self.get_argument('dt', None)
        loc1       = self.get_argument('loc1', '')
        loc2       = self.get_argument('loc2', '')
        locd       = self.get_argument('locd', None)
        obj        = self.get_argument('obj', None)
        num        = self.get_argument('num', 1)
        fee        = self.get_argument('fee', 0)
        bc         = self.get_argument('bc', '')
        vt         = self.get_argument('vt', 1)
        d = {'code': 0, 'msg': 'ok'}
        if not uid or not sjt or not obj:
            d = {'code':-1, 'msg':'参数不全'}
        if not loc1 and not loc2:
            d = {'code': -1, 'msg':'参数不全'}
        if d['code'] == 0:
            r = create_dating(uid=uid, age=age, sjt=sjt,\
                    dt=dt, loc1=loc1, loc2=loc2, locd=locd, obj=obj, num=num,\
                    fee=fee, bc=bc, valid_time=vt)
            if not r:
                d = {'code': -1, 'msg':'创建失败'}
        d = json.dumps(d)
        self.write(d)

class RemoveDatingHandler(tornado.web.RequestHandler):
    def post(self):
        uid    = self.get_argument('uid', None)
        did    = self.get_argument('did', None)
        d = {'code': 0, 'msg':'ok'}
        if not did or not uid:
            d = {'code': -1, 'msg': '参数不正确'}
        if d['code'] == 0:
            r = remove_dating(uid=uid, did=did)
            if not r:
                d = {'code': -1, 'msg': '删除失败'}
        d = json.dumps(d)
        self.write(d)

class ParticipateDatingHandler(tornado.web.RequestHandler):
    def post(self):
        uid   = self.get_argument('uid', None)
        limit = int(self.get_argument('limit', 0))
        page  = int(self.get_argument('page', 0))
        next_ = int(self.get_argument('next', 0))
        d = {'code': 0, 'msg': 'ok'}
        if not uid:
            d = {'code': -1, 'msg': '参数不正确'}
        if d['code'] == 0:
            r = participate_dating(uid, limit=limit, page=page, next_=next_)
            d = {'code': 0, 'msg':'ok', 'data':r}
        d = json.dumps(d)
        self.write(d)

class SponsorDatingHandler(tornado.web.RequestHandler):
    def post(self):
        uid   = self.get_argument('uid', None)
        limit = self.get_argument('limit', None)
        page  = self.get_argument('page', None)
        next_ = self.get_argument('next', None)
        d = {'code': 0, 'msg': 'ok'}
        if not uid:
            d = {'code': -1, 'msg': '参数不正确'}
        if d['code'] == 0:
            r = sponsor_dating(uid, limit=limit, page=page, next_=next_)
            d = {'code': 0, 'msg':'ok', 'data':r}
        d = json.dumps(d)
        self.write(d)

class DetailDatingHandler(tornado.web.RequestHandler):
    def post(self):
        did      = self.get_argument('did', None)
        uid      = self.get_argument('cuid', None)
        d = {}
        if not did or not uid:
            d = {'code':-1, 'msg':'参数不全'}
        else:
            uid, did = int(uid), int(did)
            r = detail_dating(uid=uid, did=did)
            if not r:
                d = {'code':-1, 'msg': '参数不对'}
            else:
                d = {'code':0, 'msg': 'ok', 'data':r}
        d = json.dumps(d)
        self.write(d)
        self.finish()

class BaomingDatingHandler(tornado.web.RequestHandler):
    def post(self):
        did      = self.get_argument('did', None)
        uid      = self.get_argument('uid', None)
        d = {}
        if not uid or not did:
            d = {'code':-1, 'msg':'参数不全'}
        else:
            r = baoming_dating(uid=uid, did=did)
            if not r:
                d = {'code':-1, 'msg': '参数不对'}
            else:
                d = {'code':0, 'msg': '报名成功'}
        d = json.dumps(d)
        self.write(d)
        self.finish()

class ListZhenghunHandler(tornado.web.RequestHandler):
    def post(self):
        sex      = self.get_argument('sex', None)
        age1     = self.get_argument('age1', None)
        age2     = self.get_argument('age2', None)
        loc1     = self.get_argument('loc1', None)
        loc2     = self.get_argument('loc2', None)
        page     = self.get_argument('page', None)
        limit    = self.get_argument('limit', None)
        next_    = self.get_argument('next', None)
        r = list_zhenghun(sex, age1, age2, loc1, loc2, page, limit, next_)
        d = {'code': 0, 'msg': 'ok', 'data': r}
        d = json.dumps(d)
        self.write(d)

class CreateZhenghunHandler(tornado.web.RequestHandler):
    def post(self):
        uid       = self.get_argument('uid', None)
        loc1      = self.get_argument('loc1', None)
        loc2      = self.get_argument('loc2', None)
        v_d       = self.get_argument('valid_day', None)
        title     = self.get_argument('title', None)
        cnt       = self.get_argument('content', None)
        obj1      = self.get_argument('object', None)
        d = {'code': -1, 'msg': '参数不对'}
        if not uid or not title or not obj1:
            d = {'code': -1, 'msg': '参数不对'}
        else:
            d = create_zhenghun(uid=uid,loc1=loc1, loc2=loc2, v_d=v_d,\
                    title=title, cnt=cnt, obj1=obj1)
        d = json.dumps(d)
        self.write(d)
        
#我发起的征婚
class SponsorZhenghunHandler(tornado.web.RequestHandler):
    def post(self):
        uid  = self.get_argument('uid', None)
        page = self.get_argument('page', None)
        limit= self.get_argument('limit', None)
        next_= self.get_argument('next', None)
        d = {'code': -1 , 'msg': '参数不正确'}
        if uid:
            r = sponsor_zhenghun(uid, page, limit, next_) 
            d = {'code': 0, 'msg': 'ok', 'data': r}
        d = json.dumps(d)
        self.write(d)

class CityZhenghunHandler(tornado.web.RequestHandler):
    def post(self):
        uid  = self.get_argument('uid', None)
        page = self.get_argument('page', None)
        limit= self.get_argument('limit', None)
        next_= self.get_argument('next', None)
        d = {'code': -1 , 'msg': '参数不正确'}
        if uid:
            r = city_zhenghun(uid=uid, page=page, limit=limit, next_=next_)
            d = {'code': 0, 'msg': 'ok', 'data': r}
        d = json.dumps(d)
        self.write(d)

class DetailZhenghunHandler(tornado.web.RequestHandler):
    def post(self):
        zid = self.get_argument('zid', None)
        d = {'code': -1 , 'msg': '参数不正确'}
        if zid:
            d = detail_zhenghun(zid=zid)
        d = json.dumps(d)
        self.write(d)

class RemoveZhenghunHandler(tornado.web.RequestHandler):
    def post(self):
        zid = self.get_argument('zid', None)
        uid = self.get_argument('uid', None)
        d = {'code': -1 , 'msg': '参数不正确'}
        if zid and uid:
            r = remove_zhenghun(zid=zid, uid=uid)
            if r:
                d = {'code': 0, 'msg': 'ok'}
        d = json.dumps(d)
        self.write(d)

class EmailUnReadHandler(tornado.web.RequestHandler):
    def post(self):
        d = {'code': -1, 'msg': '参数错误'}
        uid = self.get_argument('uid', None)
        if not uid:
            pass
        else:
            n = email_unread(uid=uid)
            d = {'code': 0, 'msg': 'ok', 'data': n}
        d = json.dumps(d)
        self.write(d)

class YanYuanReplyHandler(tornado.web.RequestHandler):
    def post(self):
        cuid = self.get_argument('cuid', None)
        uid  = self.get_argument('uid', None)
        eid  = self.get_argument('eid', None)
        kind = self.get_argument('kind', None)
        d = {'code': -1, 'msg': '参数错误'}
        if not cuid or not uid or not eid  or not kind:
            pass
        else:
            r = yanyuan_reply(cuid, uid, eid, kind)
            if r:
                d = {'code': 0, 'msg': 'ok'}
        d = json.dumps(d)
        self.write(d)


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
        ('/seeother', SeeOtherHandler),
        ('/sawother', SawOtherHandler),
        ('/verify_other', VerifyOtherHandler),
        ('/img', ImgHandler),
        ('/delimg', DelImgHandler),
        ('/public', PublicHandler),
        ('/isee', ISeeHandler),
        ('/seeme', SeeMeHandler),
        ('/icare', ICareHandler),
        ('/sendcare', SendCareHandler),
        ('/guanzhu_check', GuanzhuCheckHandler),
        ('/new', IndexNewHandler),
        ('/find', FindHandler),
        ('/email', EmailHandler),
        ('/see_email', SeeEmailHandler),
        ('/latest_conn', LatestConnHandler),
        ('/sendemail', SendEmailHandler),
        ('/del_email', DelEmailHandler),
        ('/yanyuan', YanyuanHandler),
        ('/yanyuan_check', YanyuanCheckHandler),
        ('/list_dating', ListDatingHandler),
        ('/create_dating', CreateDatingHandler),
        ('/detail_dating', DetailDatingHandler),
        ('/remove_dating', RemoveDatingHandler),
        ('/participate_dating', ParticipateDatingHandler),
        ('/sponsor_dating', SponsorDatingHandler),
        ('/baoming_dating', BaomingDatingHandler),
        ('/list_zhenghun', ListZhenghunHandler),
        ('/create_zhenghun', CreateZhenghunHandler),
        ('/remove_zhenghun', RemoveZhenghunHandler),
        ('/sponsor_zhenghun', SponsorZhenghunHandler),
        ('/city_zhenghun', CityZhenghunHandler),
        ('/detail_zhenghun', DetailZhenghunHandler),
        ('/email_unread', EmailUnReadHandler),
        ('/wxlogin', WxLoginHandler),
        ('/yanyuan_reply', YanYuanReplyHandler),
              ]
    application = tornado.web.Application(handler, **settings)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.PeriodicCallback(update_free_fee, 60000).start()
    tornado.ioloop.IOLoop.instance().start()
