#-*- coding: utf8 -*-

import time
from conf import conf
from cache import cache

from table import *
import json
from sqlalchemy.sql import and_, or_, not_

def user_regist(name, passwd):
    s = DBSession()
    u = User(name=name, password=passwd)
    r = True
    try:
        s.add(u)
        s.commit()
    except:
        r = False
    s.close()
    return r

def query_user_login(name, passwd):
    s = DBSession()
    r = {}
    try:
        r = s.query(User).filter(and_(User.nick_name == name, User.password == passwd)).first()
        r = {} if not r else r.dic_return()
    except:
        r = {}
    s.close()
    return r
#根据用户的uid查询内心独白和个性签名
def query_statement_by_uid(uid):
    if not uid:
        return {}
    s = DBSession()
    r = {}
    try:
        r = s.query(Statement).filter(Statement.id == uid).first()
        r = {} if not r else r.dic_return()
    except:
        r = {}
    s.close()
    return r
#根据用户的uid查询用户的其他信息:qq wx email telephone
def query_otherinfo_by_uid(uid):
    if not uid:
        return {}
    s = DBSession()
    r = {}
    try:
        r = s.query(OtherInfo).filter(OtherInfo.id == uid).first()
        r = {} if not r else r.dic_return()
    except:
        r = {}
    s.close()
    return r
#根据用户的uid查询对应的图片url
def query_pic_by_uid(uid):
    if not uid:
        return {}
    s = DBSession()
    r = {}
    try:
        r = s.query(Picture).filter(Picture.id == uid).first()
        r = {} if not r else r.dic_array()
    except:
        r = {}
    s.close()
    return r

#根据用户uid查询兴趣爱好
def query_hobby_by_uid(uid):
    h = Hobby(0)
    null = h.dic_array()
    if not uid:
        return null
    s = DBSession()
    r = null
    try:
        r = s.query(Hobby).filter(Hobby.id == uid).first()
        r = null if not r else r.dic_array()
    except:
        r = null
    return r

def get_user_info(uid):
    h = Hobby(0)
    null = h.dic_array()
    if not uid:
        return {'statement':{}, 'otherinfo':{}, 'pic': {}, 'hobby': null}
    statement = query_statement_by_uid(uid)
    otherinfo = query_otherinfo_by_uid(uid)
    pic       = query_pic_by_uid(uid)
    hobby     = query_hobby_by_uid(uid)
    return {'statement':statement, 'otherinfo':otherinfo, 'pic': pic,\
            'hobby': hobby}

def get_ctx_info(name, password):
    c = {}
    u = query_user_login(name, password)
    if not u:
        return {}
    c['user'] = u
    
    uid = u['id']
    s = query_statement_by_uid(uid)
    c['statement'] = s

    o = query_otherinfo_by_uid(uid)
    c['otherinfo'] = o

    p = query_pic_by_uid(uid)
    c['pic'] = p

    h = query_hobby_by_uid(uid)
    c['hobby'] = h

    return c
#更新个人中心中用户的基本信息
def update_basic(nick_name=None, aim=None, age=None,\
        marriage=None, xingzuo=None, shengxiao=None, blood=None,\
        weight=None, height=None, degree=None, nation=None,\
        cur_loc1=None, cur_loc2=None, ori_loc1=None, ori_loc2=None,\
        motto=None, *hobby, **ctx):
    if not ctx or not ctx.get('user'):
        return None
    uid = ctx['user'].get('id')
    if not uid:
        return None
    u = {}
    if nick_name:
        u[User.nick_name] = nick_name
        ctx['user']['nick_name'] = nick_name
    if aim:
        u[User.aim] = aim
        arr = [u'未填', u'交友', u'征婚', u'聊天']
        i = 0 if int(aim) < 0 or int(aim) >= len(arr) else int(aim)
        ctx['user']['aim'] = arr[i]
    if age:
        u[User.age] = int(age)
        ctx['user']['age'] = int(age)
    if marriage:
        u[User.marriage] = marriage
        arr = [u'保密', u'单身', u'非单身', u'已婚', u'丧偶']
        i = 0 if int(marriage) < 0 or int(marriage) >= len(arr) else int(marriage)
        ctx['user']['marriage'] = arr[i]
    xz = [u'未填', u'白羊座', u'金牛座', u'双子座', u'巨蟹座', u'狮子座',
         u'处女座', u'天秤座', u'天蝎座', u'射手座', u'摩羯座', u'水瓶座', 
         u'双鱼座']
    if xingzuo:
        u[User.xingzuo] = xingzuo
        i = int(xingzuo)
        i = 0 if i < 0 or i >= len(xz) else i
        ctx['user']['xingzuo'] = xz[i]
    sx = [u'未填', u'鼠', u'牛', u'虎', u'兔', u'龙', u'蛇', u'马',
          u'羊', u'猴', u'鸡', u'狗', u'猪']
    if shengxiao:
        u[User.shengxiao] = shengxiao
        i = int(shengxiao)
        i = 0 if i < 0 or i >= len(sx) else i
        ctx['user']['shengxiao'] = sx[i]
    bd = [u'未填', 'A', 'B', 'AB', 'O']
    if blood:
        u[User.blood] = blood
        i = int(blood)
        i = 0 if i < 0 or i >= len(bd) else i
        ctx['user']['blood'] = bd[i]
    if weight:
        u[User.weight] = int(weight)
        ctx['user']['weight'] = int(weight)
    if height:
        u[User.height] = int(height)
        ctx['user']['height'] = int(height)
    xl=[u'保密',   u'高中及以下', u'中专/大专', u'本科',
        u'研究生', u'博士及博士后']
    if degree:
        u[User.degree] = degree
        i = int(degree)
        i = 0 if i < 0 or i >= len(xl) else i
        ctx['user']['degree'] = xl[i]
    if nation:
        u[User.nation] = nation
        ctx['user']['nation'] = nation
    if cur_loc1:
        u[User.curr_loc1] = cur_loc1
        ctx['user']['curr_loc1'] = cur_loc1
    if cur_loc2:
        u[User.curr_loc2] = cur_loc2
        ctx['user']['curr_loc2'] = cur_loc2
    if ori_loc1:
        u[User.ori_loc1] = ori_loc1
        ctx['user']['ori_loc1'] = ori_loc1
    if ori_loc2:
        u[User.ori_loc2] = ori_loc2
        ctx['user']['ori_loc2'] = ori_loc2
    h = {Hobby.pashan:'0',   Hobby.sheying:'0', Hobby.yinyue:'0',
         Hobby.dianying:'0', Hobby.lvyou: '0',  Hobby.youxi: '0',
         Hobby.jianshen:'0', Hobby.meishi: '0', Hobby.paobu: '0',
         Hobby.guangjie:'0', Hobby.changge:'0', Hobby.tiaowu:'0',
         Hobby.puke: '0',    Hobby.majiang:'0', Hobby.wanggou:'0',
         Hobby.kanshu:'0' }
    hc = Hobby(uid)
    for e in hobby:
        if e == u'爬山':
            h[Hobby.pashan], hc.pashan = '1', '1'
        if e == u'摄影':
            h[Hobby.sheying], hc.sheying = '1', '1'
        if e == u'音乐':
            h[Hobby.yinyue], hc.yinyue  = '1', '1'
        if e == u'电影':
            h[Hobby.dianying], hc.dianying = '1', '1'
        if e == u'旅游':
            h[Hobby.lvyou], hc.lvyou = '1', '1'
        if e == u'游戏':
            h[Hobby.youxi], hc.youxi = '1', '1'
        if e == u'健身':
            h[Hobby.jianshen], hc.jianshen = '1', '1'
        if e == u'美食':
            h[Hobby.meishi], hc.meishi = '1', '1'
        if e == u'跑步':
            h[Hobby.paobu], hc.paobu = '1', '1'
        if e == u'逛街':
            h[Hobby.guangjie], hc.guangjie = '1', '1'
        if e == u'唱歌':
            h[Hobby.changge], hc.changge = '1', '1'
        if e == u'跳舞':
            h[Hobby.tiaowu], hc.tiaowu = '1', '1'
        if e == u'扑克':
            h[Hobby.puke], hc.puke = '1', '1'
        if e == u'麻将':
            h[Hobby.majiang], hc.majiang = '1', '1'
        if e == u'网购':
            h[Hobby.wanggou], hc.wanggou = '1', '1'
        if e == u'看书':
            h[Hobby.kanshu], hc.kanshu = '1', '1'
    ctx['hobby'] = hc.dic_array()
    s = DBSession() 

    if u:
        try:
            ru = s.query(User).filter(User.id == uid).update(u)
            s.commit()
        except Exception, e:
            return None
    r  = s.query(Statement).filter(Statement.id == uid).first()
    motto = '' if not motto else motto
    if not r:
        st = Statement(uid, motto, '')
        s.add(st)
        try:
            s.commit()
        except Exception, e:
            return None
    else:
        st = {Statement.motto: motto}
        r = s.query(Statement).filter(Statement.id == uid).update(st)
        s.commit()
    if ctx.get('statement'):
        ctx['statement']['motto'] = motto
    else:
        ctx['statement'] = {'id': uid, 'motto': motto, 'content':''}
    r  = s.query(Hobby).filter(Hobby.id == uid).first()
    if not r:
        s.add(hc)
    else:
        rh = s.query(Hobby).filter(Hobby.id == uid).update(h)
    s.commit()
    return ctx

#按条件召回用户信息
def query_user(**cond):
    sex = cond.get('sex', None)
    age = cond.get('age', None)
    curl = cond.get('curr_loc', None)
    ori  = cond.get('ori_loc', None)
    degree = cond.get('degree', None)
    xz  = cond.get('xingzuo', None)
    nation = cond.get('nation', None)
    regist_time = cond.get('regist_time', None)
    s = DBSession()
    c = True
    if sex:
        c = and_(c, User.sex == sex)
    if age:
        a1, a2 = age.split(',')
        c = and_(c, User.age >= int(a1), User.age <= int(a2))
    if curl:
        l1, l2 = curl.split(',')
        c = and_(c, User.curr_loc1 == l1, User.curr_loc2 == l2)
    if ori:
        o1, o2 = ori.split(',')
        c = and_(c, User.ori_loc1 == o1, User.ori_loc2 == o2)
    if degree:
        c = and_(c, User.degree == degree)
    if xz:
        c = and_(c, User.xingzuo == xz)
    if nation:
        c = and_(c, User.nation == nation)
    if regist_time:
        c = and_(c, User.regist_time >= regist_time)
    r = []
    try:
        r = s.query(User).filter(c).limit(conf.toffset_count)
    except:
        r = []
    male = []
    female = []
    for e in r:
        if e.sex == '0':
            male.append(e)
        elif e.sex == '1':
            female.append(e)
    male = male[: conf.toffset_new_male]
    female = female[: conf.toffset_new_female]

    mids = [e.id for e in male]
    fids = [e.id for e in female]
    ids  = mids + fids
    cnt  = s.query(Statement).filter(Statement.id.in_(mids)).all()
    pic  = s.query(Picture).filter(Picture.id.in_(mids)).all()
    s.close()
    cnt_map = {}
    for e in cnt:
        cnt_map[e.id] = e
    pic_map = {}
    for e in pic:
        pic_map[e.id] = e
    result = []
    for e in male:
        motto = cnt_map.get(e.id, '')
        mid   = e.dic_return2()
        mid['motto'] = motto if not motto else motto.motto
        pic_url = pic_map.get(e.id, '')
        mid['pic_url'] = pic_url if not pic_url else pic_url.url0
        result.append(mid)
    for e in female:
        motto = cnt_map.get(e.id, '')
        mid   = e.dic_return2()
        mid['motto'] = motto if not motto else motto.motto
        pic_url = pic_map.get(e.id, '')
        mid['pic_url'] = pic_url if not pic_url else pic_url.url0
        result.append(mid)
    return result
'''
t:     在t时间之后注册的
sex:   0=unknown  1=male 2=female
limit: 一次最多取limit个
page:  一页有多少个
next_: 第几页, 实际上是(next_+1)*limit个, next_从0开始
'''
def query_new(t, sex, limit, page, next_):
    s = DBSession()
    r = s.query(User).filter(User.sex == sex).filter(User.regist_time >= t).limit(limit).offset(page*next_)
    ids = [e.id for e in r]
    m = s.query(Statement).filter(Statement.id.in_(ids)).all()
    m_ = {}
    for e in m:
        m_[e.id] = e.dic_return()
    p = s.query(Picture).filter(Picture.id.in_(ids)).all()
    p_ = {}
    for e in p:
        p_[e.id] = e.dic_array()
    D = {}
    pic_default = Picture()
    st_defautl = Statement()
    for e in r:
        pic = p_.get(e.id, pic_default.dic_default(e.id))
        st  = m_.get(e.id, st_defautl.dic_default(e.id))
        D[e.id] = {'user':e.dic_return2(), 'pic':pic, 'statement':st}
    s.close()
    return [D[e] for e in D] if D else []

def edit_statement(cnt, **ctx):
    if not ctx:
        return None
    if not ctx.get('user'):
        return None
    uid = ctx['user'].get('id')
    if not uid:
        return None
    su = {Statement.content:cnt}
    sc = Statement(uid, motto='', stat=cnt)
    sc.content = cnt

    s = DBSession()
    r = s.query(Statement).filter(Statement.id == uid).first()
    if not r:
        s.add(sc)
        s.commit()
        ctx['statement'] = {'id': uid, 'motto':'', 'content':cnt}
    else:
        s.query(Statement).filter(Statement.id == uid).update(su)
        s.commit()
        ctx['statement']['content'] = cnt
    s.close()
    return ctx

def edit_other(mobile=None, email=None, wx=None, qq=None, **ctx):
    if not mobile and not email and not wx and not qq:
        return None
    if not ctx:
        return None
    uid = ctx['user'].get('id')
    if not uid:
        return None
    ou  = {}
    oc  = OtherInfo(uid)
    if mobile:
        oc.mobile = ou[OtherInfo.mobile] = mobile
    if email:
        oc.email  = ou[OtherInfo.email]  = email
    if wx:
        oc.wx     = ou[OtherInfo.wx] = wx
    if qq:
        oc.qq     = ou[OtherInfo.qq] = qq

    s = DBSession()
    r = s.query(OtherInfo).filter(OtherInfo.id == uid).first()
    if not r:
        s.add(oc)
        s.commit()
        ctx['otherinfo'] = oc.dic_return()
    else:
        ctx['otherinfo'] = r.dic_return()
        s.query(OtherInfo).filter(OtherInfo.id == uid).update(ou)
        s.commit()
        ctx['otherinfo']['wx'] = wx if wx else ''
        ctx['otherinfo']['qq'] = qq if qq else ''
        ctx['otherinfo']['mobile'] = mobile if mobile else ''
        ctx['otherinfo']['email'] = email if email else ''
    s.close()
    return ctx

def publish_conn(kind, action, **ctx):
    if not kind or not action or not ctx:
        return None
    #手机 qq wx email
    if kind not in ['1', '2', '3', '4'] or action not in ['0', '1']:
        return None
    uid = ctx['user'].get('id')
    if not uid:
        return None
    ou  = {}
    s = DBSession()
    r = s.query(OtherInfo).filter(OtherInfo.id == uid).first()
    if not r:
        return None
    l = r.dic_return()
    l = json.dumps(l)
    l = json.loads(l)
    ctx['otherinfo'] = l
    if kind == '1':
        ctx['otherinfo']['public_m'] = action
        ou[OtherInfo.public_m] = action
    elif kind == '2':
        ctx['otherinfo']['public_q'] = action
        ou[OtherInfo.public_q] = action
    elif kind == '3':
        ctx['otherinfo']['public_w'] = action
        ou[OtherInfo.public_w] = action
    elif kind == '4':
        ctx['otherinfo']['public_e'] = action
        ou[OtherInfo.public_e] = action
    s.query(OtherInfo).filter(OtherInfo.id == uid).update(ou)
    s.commit()
    s.close()
    return ctx

__all__=['user_regist', 'query_user', 'query_user_login', 'get_user_info',
         'update_basic','get_ctx_info', 'edit_statement', 'edit_other',
         'publish_conn','query_new']

if __name__ == '__main__':
    r = query_new('2017-12-01 00:00:00', 1, 5, 5, 0)
    print(r)
