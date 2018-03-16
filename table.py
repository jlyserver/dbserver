#-*- coding: utf8 -*-

import time

from sqlalchemy import Column, String, Integer, Date, TIMESTAMP, create_engine
from sqlalchemy.sql import and_, or_, not_
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import sys
reload(sys)
sys.path.append('..')

from conf import conf

# 初始化数据库连接:
mysql_url = 'mysql+mysqlconnector://' + str(conf.mysql_user) + ':%s@%s:'%(conf.mysql_password, conf.mysql_host) + str(conf.mysql_port) + '/' + conf.mysql_db
engine = create_engine(mysql_url, encoding=conf.mysql_encode)
# 创建DBSession类型:
DBSession = sessionmaker(bind=engine)
Base = declarative_base()

###########################################
class User(Base):
    __tablename__ = conf.table_user

    def __init__(self, id_=0, name='', password='', mobile='',
            sex=0, aim=0, age=18,\
            m=0, xz=0, sx=0, blood=0, salary=0, wt=50, ht=160, de=0, \
            na='汉族', cl1='', cl2='', ori1='', ori2='', t=None):
        self.id       = id_
        self.nick_name= name
        self.password = password
        self.mobile   = mobile
        self.sex      = sex
        self.aim      = aim
        self.age      = age
        self.marriage = m
        self.xingzuo  = xz
        self.shengxiao= sx
        self.blood    = blood
        self.salary   = salary
        self.weight   = wt
        self.height   = ht
        self.degree   = de
        self.nation   = na
        self.curr_loc1= cl1
        self.curr_loc2= cl2
        self.ori_loc1 = ori1
        self.ori_loc2 = ori2
        if not t:
            t       = time.localtime()
            now     = time.strftime('%Y-%m-%d %H:%M:%S', t)
            self.regist_time = now
        else:
            self.regist_time = t

    id                = Column(Integer, primary_key=True)
    nick_name         = Column(String(16))
    password          = Column(String(16))
    mobile            = Column(String(16))
    sex               = Column(Integer)
    aim               = Column(Integer)
    age               = Column(Integer)
    marriage          = Column(Integer) 
    xingzuo           = Column(Integer)
    shengxiao         = Column(Integer)
    blood             = Column(Integer)
    salary            = Column(Integer)
    weight            = Column(Integer)
    height            = Column(Integer)
    degree            = Column(Integer)
    nation            = Column(String(6))
    curr_loc1         = Column(String(8))
    curr_loc2         = Column(String(8))
    ori_loc1          = Column(String(8))
    ori_loc2          = Column(String(8))
    regist_time       = Column(TIMESTAMP)

    def dic_return(self):
        return { 'id':       self.id,          'nick_name': self.nick_name, 
                 'mobile':    self.mobile,
                 'sex':       self.sex,
                 'aim':      self.aim,         'age':       self.age,
                 'marriage': self.marriage,    'xingzuo':   self.xingzuo,
                 'shengxiao':self.shengxiao,   'blood':     self.blood,
                 'salary':   self.salary,
                 'weight':   self.weight,      'height':    self.height,
                 'degree':   self.degree,      'nation':    self.nation,
                 'curr_loc1':self.curr_loc1,   'curr_loc2': self.curr_loc2, 
                 'ori_loc1': self.ori_loc1,    'ori_loc2':  self.ori_loc2,
                 'regist_time': str(self.regist_time)}
    def dic_return2(self):
        return { 'id':       self.id,          'nick_name': self.nick_name,
                 'sex':      self.sex,         'age':       self.age,
                 'height':   self.height,      'degree':    self.degree}

###########################################
class Statement(Base):
    __tablename__ = conf.table_statement
    def __init__(self, id_=0, motto='', stat=''):
        self.id         = id_
        self.motto      = motto
        self.content    = stat
    id                = Column(Integer, primary_key=True)
    motto             = Column(String(128))
    content           = Column(String(1024))
    def dic_return(self):
        return {'id': self.id, 'motto': self.motto, 'content': self.content}
    def dic_default(self, id_=0):
        self.id = id_
        return {'id': self.id, 'motto': self.motto, 'content': self.content}

###########################################
class OtherInfo(Base):
    __tablename__ = conf.table_otherinfo
    def __init__(self, id_, salary=0, work=0, house=0, car=0,\
                mobile='', verify_m=0, public_m=1, email='', \
                verify_e=0, public_e=1, wx='', verify_w=0, \
                public_w=1, qq='', verify_q=0, public_q=1):
        self.id          = id_
        self.salary      = salary
        self.work        = work
        self.house       = house
        self.car         = car
        self.mobile      = mobile
        self.verify_m    = verify_m
        self.public_m    = public_m
        self.email       = email
        self.verify_e    = verify_e
        self.public_e    = public_e
        self.wx          = wx
        self.verify_w    = verify_w
        self.public_w    = public_w
        self.qq          = qq
        self.verify_q    = verify_q
        self.public_q    = public_q

    id           = Column(Integer, primary_key=True)
    salary       = Column(Integer)
    work         = Column(Integer)
    house        = Column(Integer)
    car          = Column(Integer)
    mobile       = Column(String(16))
    verify_m     = Column(Integer)
    public_m     = Column(Integer)
    
    email        = Column(String(64))
    verify_e     = Column(Integer)
    public_e     = Column(Integer)

    wx           = Column(String(32))
    verify_w     = Column(Integer)
    public_w     = Column(Integer)

    qq           = Column(String(16))
    verify_q     = Column(Integer)
    public_q     = Column(Integer)
    
    def dic_return(self):
        return {'id':      self.id,         'salary':     self.salary,
                'work':    self.work,       'house':      self.house,
                'car':     self.car,        'mobile':     self.mobile,
                'verify_m':self.verify_m,   'public_m':   self.public_m,
                'email':   self.email,      'verify_e':   self.verify_e,
                'public_e':self.public_e,   'wx':         self.wx,
                'verify_w':self.verify_w,   'public_w':   self.public_w,
                'qq':      self.qq,         'verify_q':   self.verify_q,
                'public_q':self.public_q }

###########################################
class Picture(Base):
    __tablename__ = conf.table_picture
    def __init__(self, id_=0, c=9, u0='', u1='', u2='', u3='', u4='',\
            u5='', u6='', u7='', u8='', u9=''):
        self.id     = id_
        self.count  = c
        self.url0   = u0
        self.url1   = u1
        self.url2   = u2
        self.url3   = u3
        self.url4   = u4
        self.url5   = u5
        self.url6   = u6
        self.url7   = u7
        self.url8   = u8
        self.url9   = u9
    id           = Column(Integer, primary_key=True)
    count        = Column(Integer)
    url0         = Column(String(64))
    url1         = Column(String(64))
    url2         = Column(String(64))
    url3         = Column(String(64))
    url4         = Column(String(64))
    url5         = Column(String(64))
    url6         = Column(String(64))
    url7         = Column(String(64))
    url8         = Column(String(64))
    url9         = Column(String(64))
    def dic_return(self):
        return {'id':   self.id,     'count': self.count, \
                'url0': self.url0,   'url1':  self.url1,  \
                'url2': self.url0,   'url3':  self.url1,  \
                'url4': self.url0,   'url5':  self.url1,  \
                'url6': self.url0,   'url7':  self.url1,  \
                'url8': self.url0,   'url9':  self.url1}
    def dic_array(self):
        a = [self.url0, self.url1, self.url2, self.url3, self.url4,\
             self.url5, self.url6, self.url7, self.url8, self.url9]
        return {'id':   self.id,     'count': self.count,  'arr': a}
    def dic_default(self, id_=0):
        self.id = id_
        a = ['' for i in xrange(self.count+1) ]
        return {'id':   self.id,     'count': self.count,  'arr': a}


###########################################
class Hobby(Base):
    __tablename__ = conf.table_hobby
    def __init__(self, id_, ps=0, sy=0, yy=0, dy=0, ly=0, \
                 yx=0, js=0, ms=0, pb=0, gj=0, cg=0, \
                 tw=0, pk=0, mj=0, wg=0, ks=0):
        self.id       = id_
        self.pashan   = ps
        self.sheying  = sy
        self.yinyue   = yy
        self.dianying = dy
        self.lvyou    = ly
        self.youxi    = yx
        self.jianshen = js
        self.meishi   = ms
        self.paobu    = pb
        self.guangjie = gj
        self.changge  = cg
        self.tiaowu   = tw
        self.puke     = pk
        self.majiang  = mj
        self.wanggou  = wg
        self.kanshu   = ks
    id           = Column(Integer, primary_key=True)
    pashan       = Column(Integer)
    sheying      = Column(Integer)
    yinyue       = Column(Integer)
    dianying     = Column(Integer)
    lvyou        = Column(Integer)
    youxi        = Column(Integer)
    jianshen     = Column(Integer)
    meishi       = Column(Integer)
    paobu        = Column(Integer)
    guangjie     = Column(Integer)
    changge      = Column(Integer)
    tiaowu       = Column(Integer)
    puke         = Column(Integer)
    majiang      = Column(Integer)
    wanggou      = Column(Integer)
    kanshu       = Column(Integer)
    
    def dic_return(self):
        return {'id':        self.id,      'pashan':     self.pashan, \
                'sheying':   self.sheying, 'yinyue':     self.yinyue, \
                'dianying':  self.dianying,'lvyou':      self.lvyou, \
                'youxi':     self.youxi,   'jianshen':   self.jianshen, \
                'meishi':    self.meishi,  'paobu':      self.paobu,    \
                'guangjie':  self.guangjie,'changge':    self.changge,  \
                'tiaowu':    self.tiaowu,  'puke':       self.puke,     \
                'majiang':   self.majiang, 'wanggou':    self.wanggou,  \
                'kanshu':    self.kanshu}
    def dic_array(self):
        a = []
        d = {'id': self.id}
        a.append(['爬山', int(self.pashan)])
        a.append(['摄影', int(self.sheying)])
        a.append(['音乐', int(self.yinyue)])
        a.append(['电影', int(self.dianying)])
        a.append(['旅游', int(self.lvyou)])
        a.append(['游戏', int(self.youxi)])
        a.append(['健身', int(self.jianshen)])
        a.append(['美食', int(self.meishi)])
        a.append(['跑步', int(self.paobu)])
        a.append(['逛街', int(self.guangjie)])
        a.append(['唱歌', int(self.changge)])
        a.append(['跳舞', int(self.tiaowu)])
        a.append(['扑克', int(self.puke)])
        a.append(['麻将', int(self.majiang)])
        a.append(['网购', int(self.wanggou)])
        d['arr'] = a
        flag = 0
        for e in a:
            if e[1] == 1:
                flag = 1
                break
        d['arr_flag'] = flag
        return d
###########################################

class Email(Base):
    __tablename__ = conf.table_email
    def __init__(self, id_=0, f=0, t=0, c='', t_=None):
        if not t_:
            t_   = time.localtime()
            now  = time.strftime('%Y-%m-%d %H:%M:%S', t_)
            self.time_ = now
        else:
            self.time_ = t_
        self.id      = id_
        self.from_id = f
        self.to_id   = t
        self.content = c

    id           = Column(Integer, primary_key=True)
    from_id      = Column(Integer)
    to_id        = Column(Integer)
    content      = Column(String(96))
    time_        = Column(TIMESTAMP)
    def dic_return(self):
        return {'id': self.id,        'from_id': self.from_id,
                'to_id': self.to_id,  'content': self.content,
                'time': self.time_}
###########################################

class Money_record(Base):
    __tablename__ = conf.table_money_record
    def __init__(self, id_=0, uid=0, oid=0, way=0, num=0, t=None):
        if not t:
            t    = time.localtime()
            now  = time.strftime('%Y-%m-%d %H:%M:%S', t)
            self.time_ = now
        else:
            self.time_ = t
        self.id       = id_
        self.user_id  = uid
        self.objid    = oid
        self.way      = way
        self.num      = num
    id           = Column(Integer, primary_key=True)
    user_id      = Column(Integer)
    objid        = Column(Integer)
    way          = Column(Integer)
    num          = Column(Integer)
    time_        = Column(TIMESTAMP)
    def dic_return(self):
        return {'id':   self.id,     'user_id': self.user_id,
                'objid': self.objid, 'way':  self.way, 
                'num':     self.num, 'time': self.time_}
##########################################################

class User_account(Base):
    __tablename__ = conf.table_user_account
    def __init__(self, id_=0, uid=0, num=0):
        self.id     = id_
        self.userid = uid
        self.num    = num
    id           = Column(Integer, primary_key=True)
    userid       = Column(Integer)
    num          = Column(Integer)
    def dic_return(self):
        return {'id': self.id,   'userid': self.userid, 'num': self.num}
###########################################################

class Look(Base):
    __tablename__ = conf.table_look
    def __init__(self, id_=0, f=0, to=0, t=None):
        self.id       = id_
        self.from_id  = f
        self.to_id    = to
        if not t:
            t    = time.localtime()
            now  = time.strftime('%Y-%m-%d %H:%M:%S', t)
            self.time_ = now
        else:
            self.time_ = t
    id           = Column(Integer, primary_key=True)
    from_id      = Column(Integer)
    to_id        = Column(Integer)
    time_        = Column(TIMESTAMP)
    def dic_return(self):
        return {'id': self.id,  'from_id':self.from_id,
                'to_id': self.to_id, 'time': self.time_}


__all__=['DBSession', 'User', 'Statement', 'OtherInfo', 'Picture', 'Hobby',
         'Email', 'Money_record', 'User_account', 'Look']
'''
'''
if __name__ == '__main__':
    s = DBSession()
    a = User_account(id_=0, uid=1)
    try:
        s.add(a)
        s.commit()
    except:
        print('error')
    s.close()

