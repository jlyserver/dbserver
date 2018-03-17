#-*- coding: utf8 -*-

import time
from conf import conf
from cache import cache

from table import *
import json
from sqlalchemy.sql import and_, or_, not_

'''
mobile 手机号码
return: True=手机号存在     False=手机号不存在
'''
def verify_mobile(mobile):
    s = DBSession()
    r = s.query(User).filter(User.mobile == mobile).first()
    s.close()
    return True if r else False
#充值密码 {}=失败  ctx=成功
def find_password(mobile, passwd):
    if not mobile or not passwd:
        return {}
    s = DBSession()
    r = s.query(User).filter(User.mobile == mobile).first()
    if not r:
        s.close()
        return {}
    else:
        s.query(User).filter(User.mobile == mobile).update({User.password:passwd})
        try:
            s.commit()
        except:
            s.close()
            return {}
    uid = r.id
    ctx = get_ctx_info(uid, s=s)
    s.close()
    return ctx
#用户注册 ={} 已经注册或db出错  =ctx{}注册成功
def user_regist(mobile, passwd, sex, s=None):
    f = s
    if not f:
        s = DBSession()
    u = User(mobile=mobile, password=passwd, sex=sex)
    r = s.query(User).filter(User.mobile == mobile).first()
    if r:
        if not f:
            s.close()
        return {}
    r = True
    try:
        s.add(u)
        s.commit()
    except:
        r = False
    if not r:
        if not f:
            s.close()
        return {}
    r = s.query(User).filter(User.mobile == mobile).first()
    uid = r.id
    h  = Hobby(uid)
    st = Statement(uid)
    o  = OtherInfo(uid, mobile=mobile, verify_m=1)
    p  = Picture(uid)
    a  = User_account(id_=uid)
    s.add(h)
    s.add(st)
    s.add(o)
    s.add(p)
    s.add(a)
    res = False
    try:
        s.commit()
        res = True
    except:
        rb = DBSession()
        rb.query(User).filter(User.id == uid).delete(synchronize_session=False)
        rb.query(Hobby).filter(Hobby.id == uid).delete(synchronize_session=False)
        rb.query(Statement).filter(Statement.id == uid).delete(synchronize_session=False)
        rb.query(OtherInfo).filter(OtherInfo.id == uid).delete(synchronize_session=False)
        rb.query(Picture).filter(Picture.id == uid).delete(synchronize_session=False)
        rb.query(User_account).filter(User_account.userid == uid).delete(synchronize_session=False)
        try:
            rb.commit()
        except:
            rb.close()
        res = False
    ctx = {}
    if res:
        ctx = get_ctx_info(uid, s=s)
    if not f:
        s.close()
    return ctx

def query_user_login(mobile, passwd, s=None):
    t = s
    if not s:
        s = DBSession()
    r = {}
    try:
        r = s.query(User).filter(and_(User.mobile == mobile, User.password == passwd)).first()
        r = {} if not r else r.dic_return()
    except:
        r = {}
    if not t:
        s.close()
    return r
#根据用户的uid查询内心独白和个性签名
def query_statement_by_uid(uid, s=None):
    if not uid:
        return {}
    t = s
    if not t:
        s = DBSession()
    r = {}
    try:
        r = s.query(Statement).filter(Statement.id == uid).first()
        r = {} if not r else r.dic_return()
    except:
        r = {}
    if not t:
        s.close()
    return r
#根据用户的uid查询用户的其他信息:qq wx email telephone
def query_otherinfo_by_uid(uid, s=None):
    if not uid:
        return {}
    t = s
    if not s:
        s = DBSession()
    r = {}
    try:
        r = s.query(OtherInfo).filter(OtherInfo.id == uid).first()
        r = {} if not r else r.dic_return()
    except:
        r = {}
    if not t:
        s.close()
    return r
#根据用户的uid查询对应的图片url
def query_pic_by_uid(uid, s=None):
    if not uid:
        return {}
    t = s
    if not t:
        s = DBSession()
    r = {}
    try:
        r = s.query(Picture).filter(Picture.id == uid).first()
        r = {} if not r else r.dic_array()
    except:
        r = {}
    if not t:
        s.close()
    return r

#根据用户uid查询兴趣爱好
def query_hobby_by_uid(uid, s=None):
    h = Hobby(0)
    null = h.dic_array()
    if not uid:
        return null
    t = s
    if not t:
        s = DBSession()
    r = null
    try:
        r = s.query(Hobby).filter(Hobby.id == uid).first()
        r = null if not r else r.dic_array()
    except:
        r = null
    if not t:
        s.close()
    return r
def query_account_by_uid(uid, s=None):
    a = User_account()
    null = a.dic_return()
    if not uid:
        return null
    t = s
    if not t:
        s = DBSession()
    try:
        r = s.query(User_account).filter(User_account.id == uid).first()
        r = null if not r else r.dic_return()
    except:
        r = null
    if not t:
        s.close()
    return r

def get_user_info(uid):
    if not uid:
        return None
    s = DBSession()
    statement = query_statement_by_uid(uid, s=s)
    otherinfo = query_otherinfo_by_uid(uid, s=s)
    pic       = query_pic_by_uid(uid, s=s)
    hobby     = query_hobby_by_uid(uid, s=s)
    s.close()
    return {'statement':statement, 'otherinfo':otherinfo, 'pic': pic,
            'hobby': hobby}

def get_ctx_info(uid, s=None):
    c = {}
    if not uid:
        return c
    f = s
    if not f:
        s = DBSession()
    r = s.query(User).filter(User.id == uid).first()
    if not r:
        if not f:
            s.close()
        return {}
    c['user'] = r.dic_return()
    
    st = query_statement_by_uid(uid, s=s)
    c['statement'] = st

    o = query_otherinfo_by_uid(uid, s=s)
    c['otherinfo'] = o

    p = query_pic_by_uid(uid, s=s)
    c['pic'] = p

    h = query_hobby_by_uid(uid, s=s)
    c['hobby'] = h

    a = query_account_by_uid(uid, s=s)
    c['account'] = a
    if not f:
        s.close()
    return c
def get_ctx_info_mobile_password(mobile, password, s=None):
    f = s
    if not f:
        s = DBSession()
    r = query_user_login(mobile, password, s=s)
    if not r:
        if not f:
            s.close()
        return False
    uid = r['id']
    r = get_ctx_info(uid, s=s)
    return r

def merge_uids(uid, uidsrc, s=None):
    if not uidsrc or not uid:
        return False
    f = s
    if not f:
        s = DBSession()
    ol_ = s.query(OtherInfo).filter(OtherInfo.id == uid).first()
    or_ = s.query(OtherInfo).filter(OtherInfo.id == uidsrc).first()
    if not or_:
        if not f:
            s.close()
        return False
    ol_.mobile = or_.mobile
    ol_.verify_m = 1
    ol_.public_m = 1

    if not ol_.wx:
        ol_.wx = or_.wx
        ol_.verify_w = or_.verify_w
        ol_.public_w = or_.public_w
    else:
        if ol_.verify_w == 0 and or_.wx and or_.verify_w == 1:
            ol_.wx = or_.wx
            ol_.verify_w = or_.verify_w
            ol_.public_w = or_.public_w
    if not ol_.qq:
        ol_.qq = or_.qq
        ol_.verify_q = or_.verify_q
        ol_.public_q = or_.public_q
    else:
        if ol_.verify_q == 0 and or_.qq and or_.verify_q == 1:
            ol_.qq = or_.qq
            ol_.verify_q = or_.verify_q
            ol_.public_q = or_.public_q
    s.query(User).filter(User.id == uidsrc).delete(synchronize_session=False)
    s.query(OtherInfo).filter(OtherInfo.id == uidsrc).delete(synchronize_session=False)
    s.query(Statement).filter(Statement.id == uidsrc).delete(synchronize_session=False)
    s.query(Hobby).filter(Hobby.id == uidsrc).delete(synchronize_session=False)
    s.query(Picture).filter(Picture.id == uidsrc).delete(synchronize_session=False)
    s.commit()
    ctx = get_ctx_info(uid, s=s)
    if not f:
        s.close()
    return ctx

def merge_mobile(uid, mobile, s=None):
    f = s
    if not f:
        s = DBSession()
    r = s.query(User).filter(User.mobile == mobile).first()
    if not l or not r:
        if not f:
            s.close()
        return False
    ctx = merge_uids(uid, r['id'], s=s)
    if not f:
        s.close()
    return ctx

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
'''
按条件查找
sex:       1=男 2=女
agemin:    年龄区间最小
agemax:    年龄区间最大
cur1:      当前居住省(直辖市)
cur2:      当前居住市(直辖市区)
ori1:      籍贯所在省(直辖市)
ori2:      籍贯所在市(直辖市区)
degree:    学历  0=保密 1=高中及以下 2=中专/大专
                 3=本科 4=研究生     5=博士及博士后
salary:    薪资  0=未填 1=2000以下    2=2000~5000   3=5000~10000
                        4=10000~20000 5=20000~50000 6=50000以上
xz:        星座  0=未填 1~12依次顺排星座 1=白羊座 2=金牛座 3=双子座
sx:        生肖  0=未填 1~12依次顺排生肖 1=鼠 2=牛 3=虎...12=猪
limit:     一次最多取limit个
page:      一个页面最多能展示page个
next_:     分页, 0=第一页 1=第二页
'''
def find_users(sex=None,  agemin=None, agemax=None, cur1=None, cur2=None,\
               ori1=None, ori2=None,   degree=None, salary=None,\
               xz=None,   sx=None, limit=8, page=12, next_=0):
    limit = 8 if limit < 1 else limit
    page  = 12 if page < 1 else page
    next_ = 0 if next_ < 1 else next_
    s = DBSession()
    t = s.query(User)
    if sex and sex in [1,2]:
        t = t.filter(User.sex == sex)
    if agemin and agemin >= 18:
        t = t.filter(User.age >= agemin)
    if agemax and agemax >= 18:
        t = t.filter(User.age <= agemax)
    if cur1:
        t = t.filter(User.curr_loc1 == cur1)
    if cur2:
        t = t.filter(User.curr_loc2 == cur2)
    if ori1:
        t = t.filter(User.ori_loc1 == ori1)
    if ori2:
        t = t.filter(User.ori_loc2 == ori2)
    if degree and degree in [0, 1, 2, 3, 4, 5]:
        t = t.filter(User.degree == degree)
    if salary and salary in [0, 1, 2, 3, 4, 5]:
        t = t.filter(User.salary == salary)
    if xz and xz in [i for i in xrange(13)]:
        t = t.filter(User.xingzuo == xz)
    if sx and sx in [i for i in xrange(13)]:
        t = t.filter(User.shengxiao == sx)
    if salary and salary in [i for i in xrange(7) if i > 0]:
        t = t.filter(User.salary == salary)
    count = t.count()
    r = t.limit(limit).offset(page*next_)

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
    arr = [D[e] for e in D] if D else []
    return count, arr


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

#充值
def recharge(uid, num, s=None):
    if not uid or not num or num < 0:
        return False
    f = s
    if not f:
        s = DBSession()
    u = s.query(User_account).filter(User_account.id == uid).first()
    if not u:
        if not f:
            s.close()
        return False
    u.num = u.num + num
    r = Money_record(uid=uid, num=num, way=0)
    s.add(r)
    s.commit()
    if not f:
        s.close()
    return True

'''
写一条交易记录
uid:  发生交易时用户的id
objid:发生交易时对象id， 当充值时，忽略objid
way:  发生交易类型 0=充值 1=发送眼缘 2=发信 3=约会帖 4=征婚帖
num:  发生交易金额 1个=一个示爱豆, 0.1元
'''
def write_record(uid, objid, way, num, s=None):
    if not uid or not way or way not in [0,1,2,3,4] or not num or num < 1:
        return False
    f = s
    if not f:
        s = DBSession() 
    r = Money_record(uid=uid, oid=objid, way=way, num=num)
    s.add(r)
    s.commit()
    if not f:
        s.close()
    return True

'''
send_email: 发送邮件
fid:        发送方的uid
tid:        接收方的uid
cnt:        发送邮件的内容
return:     成功=True 失败=False
'''
def send_email(fid, tid, cnt, s=None):
    if not fid or not tid or not cnt:
        return False
    f = s
    if not f:
        s = DBSession()
    e = Email(f=fid, t=tid, c=cnt)
    s.add(e)
    s.commit()
    if not f:
        s.close()
    return True
'''
根据uid获得邮件
t:      0=收件箱  非0=发件箱
uid:    用户id
limit:  一次请求最多返回limit个邮件
page:   一页最多展示page个邮件
next_:  第next_页开始, 下标从0开始
return:  []数组
'''
def get_email_by_uid(uid, limit, page, next_, t=0, s=None):
    if not uid or not limit or not page or not next_:
        return []

    f = s
    if not f:
        s = DBSession()
    r = None
    if t == 0:
        r = s.query(Email).filter(Email.to_id == uid).limit(limit).offset(page*next_)
    else:
        r = s.query(Email).filter(Email.from_id == uid).limit(limit).offset(page*next_)
    if not f:
        s.close()
    return [] if not r else [e.dic_return() for e in r]

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

__all__=['verify_mobile', 'find_password', 'get_ctx_info_mobile_password',
         'user_regist', 'query_user', 'query_user_login', 'get_user_info',
         'update_basic','get_ctx_info', 'edit_statement', 'edit_other',
         'publish_conn','query_new', 'find_users']

if __name__ == '__main__':
    r = user_regist('17313615918', '123', 1)
    print(r)
