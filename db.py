#-*- coding: utf8 -*-

import time
import hashlib
from conf import conf
from cache import cache

from table import *
import json
from sqlalchemy.sql import and_, or_, not_
from sqlalchemy import desc

def digest(word):
    m2 = hashlib.md5()
    line = '%s%s' % (word, conf.digest_salt)
    m2.update(line)
    token = m2.hexdigest()
    return token

'''
mobile 手机号码
return: True=手机号存在     False=手机号不存在
'''
def verify_mobile(mobile):
    s = DBSession()
    r = s.query(User).filter(User.mobile == mobile).first()
    s.close()
    return True if r else False
#找回密码 {}=失败  ctx=成功
def find_password(mobile, passwd):
    if not mobile or not passwd:
        return {}
    s = DBSession()
    r = s.query(User).filter(User.mobile == mobile).first()
    if not r:
        s.close()
        return {}
    else:
        tok = digest(passwd)
        s.query(User).filter(User.mobile == mobile).update({User.password:tok})
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
    tok = digest(passwd)
    name = u'新用户%s' % mobile[-4:]
    u = User(mobile=mobile, name=name, password=tok, sex=sex)
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
    st = Statement(uid, motto='未填', stat='未填')
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
        rb.query(User_account).filter(User_account.id == uid).delete(synchronize_session=False)
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
        tok = digest(passwd)
        r = s.query(User).filter(and_(User.mobile == mobile, User.password == tok)).first()
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
        if not r:
            stm = Statement(id_=uid, motto='未填', stat='未填')
            s.add(stm)
            s.commit()
            r = stm.dic_return()
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
        if not r:
            ru = s.query(User).filter(User.id == uid).first()
            if ru:
                oi = OtherInfo(id_=uid, mobile=ru.mobile, verify_m=1)
            else:
                oi = OtherInfo(id_=uid)
            s.add(oi)
            r = oi.dic_return()
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
        if not r:
            pt = Picture(id_=uid)
            s.add(pt)
            s.commit()
            r = pt.dic_return()
    except:
        r = {}
    if not t:
        s.close()
    return r

#根据用户uid查询兴趣爱好
def query_hobby_by_uid(uid, s=None):
    if not uid:
        return {}
    t = s
    if not t:
        s = DBSession()
    try:
        r = s.query(Hobby).filter(Hobby.id == uid).first()
        r = {} if not r else r.dic_array()
        if not r:
            hob = Hobby(id_=uid)
            s.add(hob)
            s.commit()
            r = hob.dic_array()
    except:
        r = {}
    if not t:
        s.close()
    return r
def query_account_by_uid(uid, s=None):
    if not uid:
        return {}
    t = s
    if not t:
        s = DBSession()
    try:
        r = s.query(User_account).filter(User_account.id == uid).first()
        r = {} if not r else r.dic_return()
        if not r:
            ao = User_account(id_=uid)
            s.add(ao)
            s.commit()
            r = ao.dic_return()
    except:
        r = {}
    if not t:
        s.close()
    return r

def get_user_info(uid, s=None):
    if not uid:
        return None
    f = s
    if not f:
        s = DBSession()
    statement = query_statement_by_uid(uid, s=s)
    otherinfo = query_otherinfo_by_uid(uid, s=s)
    pic       = query_pic_by_uid(uid, s=s)
    hobby     = query_hobby_by_uid(uid, s=s)
    account   = query_account_by_uid(uid, s=s)
    if not f:
        s.close()
    return {'statement':statement, 'otherinfo':otherinfo, 'pic': pic,
            'hobby': hobby, 'account': account}
'''
根据uid获得用户的信息:
  user:{} //见user表
  statement: {} //见statement表
  otherinfo: {} //见otherinfo表
  pic: {} //见picture表
  hobby: {} //见hobby表
  account: {} //见account表
'''
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

#更新个人中心中用户的基本信息
#return ctx
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
        u[User.aim] = int(aim)
        ctx['user']['aim'] = int(aim)
    if age:
        u[User.age] = int(age)
        ctx['user']['age'] = int(age)
    if marriage:
        u[User.marriage] = int(marriage)
        ctx['user']['marriage'] = int(marriage)
    if xingzuo:
        u[User.xingzuo] = int(xingzuo)
        ctx['user']['xingzuo'] = int(xingzuo)
    if shengxiao:
        i = int(shengxiao)
        u[User.shengxiao] = i
        ctx['user']['shengxiao'] = i
    if blood:
        i = int(blood)
        u[User.blood] = i
        ctx['user']['blood'] = i
    if weight:
        u[User.weight] = int(weight)
        ctx['user']['weight'] = int(weight)
    if height:
        u[User.height] = int(height)
        ctx['user']['height'] = int(height)
    if degree:
        i = int(degree)
        u[User.degree] = i
        ctx['user']['degree'] = i
    if nation:
        u[User.nation] = int(nation)
        ctx['user']['nation'] = int(nation)
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
    h = {Hobby.pashan:0,   Hobby.sheying:0, Hobby.yinyue:0,
         Hobby.dianying:0, Hobby.lvyou: 0,  Hobby.youxi: 0,
         Hobby.jianshen:0, Hobby.meishi: 0, Hobby.paobu: 0,
         Hobby.guangjie:0, Hobby.changge:0, Hobby.tiaowu:0,
         Hobby.puke: 0,    Hobby.majiang:0, Hobby.wanggou:0,
         Hobby.kanshu:0 }
    hn = len(hobby)
    h[Hobby.pashan]   = hobby[0] if 0 < hn else 0
    h[Hobby.sheying]  = hobby[1] if 1 < hn else 0
    h[Hobby.yinyue]   = hobby[2] if 2 < hn else 0
    h[Hobby.dianying] = hobby[3] if 3 < hn else 0
    h[Hobby.lvyou]    = hobby[4] if 4 < hn else 0
    h[Hobby.youxi]    = hobby[5] if 5 < hn else 0
    h[Hobby.jianshen] = hobby[6] if 6 < hn else 0
    h[Hobby.meishi]   = hobby[7] if 7 < hn else 0
    h[Hobby.paobu]    = hobby[8] if 8 < hn else 0
    h[Hobby.guangjie] = hobby[9] if 9 < hn else 0
    h[Hobby.changge]  = hobby[10] if 10 < hn else 0
    h[Hobby.tiaowu]   = hobby[11] if 11 < hn else 0
    h[Hobby.puke]     = hobby[12] if 12 < hn else 0
    h[Hobby.majiang]  = hobby[13] if 13 < hn else 0
    h[Hobby.wanggou]  = hobby[14] if 14 < hn else 0
    h[Hobby.kanshu]   = hobby[15] if 15 < hn else 0

    s = DBSession() 
    if u:
        ru = s.query(User).filter(User.id == uid).update(u)
    motto = '' if not motto else motto
    st = {Statement.motto: motto}
    s.query(Statement).filter(Statement.id == uid).update(st)
    if ctx.get('statement'):
        ctx['statement']['motto'] = motto
    else:
        ctx['statement'] = {'id': uid, 'motto': motto, 'content':''}
    rh = s.query(Hobby).filter(Hobby.id == uid).update(h)
    try:
        s.commit()
    except:
        s.close()
        return None
    r = s.query(Hobby).filter(Hobby.id == uid).first()
    ctx['hobby'] = r.dic_array() if r else {}
    s.close()
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

    s = DBSession()
    s.query(Statement).filter(Statement.id == uid).update(su)
    try:
        s.commit()
    except:
        s.close()
        return None
    ctx['statement']['content'] = cnt
    s.close()
    return ctx

def edit_other(salary=None, work=None, car=None, house=None, **ctx):
    if not salary and not work and not car and not house:
        return None
    if not ctx:
        return None
    uid = ctx['user'].get('id')
    if not uid:
        return None
    ou  = {}
    if salary:
        ou[OtherInfo.salary] = salary
        ctx['otherinfo']['salary'] = salary
    if work:
        ou[OtherInfo.work]  = work 
        ctx['otherinfo']['work'] = work
    if car:
        ou[OtherInfo.car] = car
        ctx['otherinfo']['car'] = car
    if house:
        ou[OtherInfo.house] = house 
        ctx['otherinfo']['house'] = house

    s = DBSession()
    s.query(OtherInfo).filter(OtherInfo.id == uid).update(ou)
    s.commit()
    s.close()
    return ctx
'''
num:  微信号或qq号或email
kind: =1验证微信 =2验证qq =3验证email
ctx:  用户的上下文, 包括uid
return: 成功=ctx  失败=None
'''
def verify_wx_qq_email(num, kind, **ctx):
    if not num or not kind or not ctx:
        return None
    uid = None
    try:
        uid = ctx['user']['id']
    except:
        uid = None
    if not uid:
        return None
    D = {}
    try:
        if kind == 1:
            D = {OtherInfo.wx: num, OtherInfo.verify_w:1}
            ctx['otherinfo']['wx'] = num
            ctx['otherinfo']['verify_w'] = 1
        elif kind == 2:
            D = {OtherInfo.qq: num, OtherInfo.verify_q:1}
            ctx['otherinfo']['qq'] = num
            ctx['otherinfo']['verify_q'] = 1
        else:
            D = {OtherInfo.email: num, OtherInfo.verify_e:1}
            ctx['otherinfo']['email'] = num
            ctx['otherinfo']['verify_e'] = 1
    except:
        return None
    s = DBSession()
    s.query(OtherInfo).filter(OtherInfo.id == uid).update(D)
    try:
        s.commit()
    except:
        s.close()
        return None
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

def public_conn(kind, action, **ctx):
    if not ctx:
        return None
    #手机 qq wx email
    if kind not in [1, 2, 3, 4] or action not in [0, 1]:
        return None
    uid = ctx['user'].get('id')
    if not uid:
        return None
    ou  = {}
    if kind == 1:
        ctx['otherinfo']['public_m'] = action
        ou[OtherInfo.public_m] = action
        if ctx['otherinfo']['verify_m'] == 0:
            return None
    elif kind == 2:
        ctx['otherinfo']['public_w'] = action
        ou[OtherInfo.public_w] = action
        if ctx['otherinfo']['verify_w'] == 0:
            return None
    elif kind == 3:
        ctx['otherinfo']['public_q'] = action
        ou[OtherInfo.public_q] = action
        if ctx['otherinfo']['verify_q'] == 0:
            return None
    elif kind == 4:
        ctx['otherinfo']['public_e'] = action
        ou[OtherInfo.public_e] = action
        if ctx['otherinfo']['verify_e'] == 0:
            return None
    s = DBSession()
    if ou:
        try:
            s.query(OtherInfo).filter(OtherInfo.id == uid).update(ou)
            s.commit()
        except:
            s.close()
            return None
    s.close()
    return ctx

'''
kind: =1我看过谁 =2谁看过我  
'''
def see(uid, kind, s=None):
    if not uid:
        return None, None
    f = s
    limit = 0
    if not f:
        s = DBSession()
    if kind == 1:
        limit = conf.toffset_isee_limit
        r = s.query(Look).filter(Look.from_id == uid).order_by(desc(Look.time_))
    elif kind == 2:
        limit = conf.toffset_seeme_limit
        r = s.query(Look).filter(Look.to_id == uid).order_by(desc(Look.time_))
    else:
        if not f:
            s.close()
        return None, None
    if not r:
        if not f:
            s.close()
        return 0, [] 
    a1, a2, n = [], [], 0
    for e in r:
        if n > limit:
            a2.append(e.id)
        else:
            a1.append(e)
        n = n + 1
    if a2:
        s.query(Look).filter(Look.id.in_(a2)).delete(synchronize_session=False)
        s.commit()
    m_a1_t = {}
    ids = [e.to_id for e in a1]
    if not ids:
        if not f:
            s.close()
        return 0, [] 
    r = s.query(User).filter(User.id.in_(ids)).all()
    m_u = {}
    for e in r:
        m_u[e.id] = e.dic_return()
    r = s.query(Picture).filter(Picture.id.in_(ids)).all()
    m_p = {}
    for e in r:
        m_p[e.id] = e.url0
    N = len(a1)
    for e in a1:
        [t1, t2] = str(e.time_).split(' ')
        u = m_u.get(e.to_id)
        p = m_p.get(e.to_id, '')
        if not u:
            N = N - 1
            continue
        d = {'id':e.to_id, 'nick_name':u['nick_name'], 'sex':u['sex'],
             'age': u['age'], 'curr_loc1':u['curr_loc1'],
             'curr_loc2':u['curr_loc2'], 'src': p, 'time':t2}
        if not m_a1_t.get(t1):
            m_a1_t[t1] = [d]
        else:
            m_a1_t[t1].append(d)
    a = sorted(m_a1_t.keys(), reverse=True)
    D = [{'date': e, 'arr':m_a1_t[e]} for e in a]
    if not f:
        s.close()
    N = N if N > 0 else 0
    return len(a1), D

'''
谁看过我, 超过toffset_isee_limit的人数的取最近toffset_isee_limit个人
uid: 主动看的人的id
'''
def isee(uid, s=None):
    n, r = see(uid, 1, s)
    return n, r

'''
谁看过我, 超过toffset_seeme_limit的人数的取最近toffset_seeme_limit个人
uid: 被动看的人的id
'''
def seeme(uid, s=None):
    n, r = see(uid, 2, s)
    return n, r

def icare(uid, s=None):
    if not uid:
        return None, None
    limit = conf.toffset_icare_limit
    f = s
    if not f:
        s = DBSession()
    r = s.query(Care).filter(Care.from_id == uid).order_by(desc(Care.time_))
    if not r:
        if not f:
            s.close()
        return 0, []

    a1, a2, n = [], [], 0
    for e in r:
        if n > limit:
            a2.append(e.id)
        else:
            a1.append(e)
        n = n + 1
    if a2:
        s.query(Care).filter(Care.id.in_(a2)).delete(synchronize_session=False)
        s.commit()
    m_a1_t = {}
    ids = [e.to_id for e in a1]
    if not ids:
        if not f:
            s.close()
        return 0, []
    r = s.query(User).filter(User.id.in_(ids)).all()
    m_u = {}
    for e in r:
        m_u[e.id] = e.dic_return()
    r = s.query(Picture).filter(Picture.id.in_(ids)).all()
    m_p = {}
    for e in r:
        m_p[e.id] = e.url0
    N = len(a1)
    for e in a1:
        [t1, t2] = str(e.time_).split(' ')
        u = m_u.get(e.to_id)
        p = m_p.get(e.to_id, '')
        if not u:
            N = N - 1
            continue
        d = {'id':e.to_id, 'nick_name':u['nick_name'], 'sex':u['sex'],
             'age': u['age'], 'curr_loc1':u['curr_loc1'],
             'curr_loc2':u['curr_loc2'], 'src': p, 'time':t2}
        if not m_a1_t.get(t1):
            m_a1_t[t1] = [d]
        else:
            m_a1_t[t1].append(d)
    a = sorted(m_a1_t.keys(), reverse=True)
    D = [{'date': e, 'arr':m_a1_t[e]} for e in a]
    if not f:
        s.close()
    N = N if N > 0 else 0
    return N, D

def list_dating(sex=None, age1=None, age2=None, loc1=None, loc2=None, page=None, limit=None, next_=None, s=None):
    page = conf.toffset_dating_page if not page else int(page)
    limit = conf.toffset_dating_limit if not limit else int(limit)
    next_ = 0 if not next_ else int(next_)
    c = True
    if sex and sex in ['0', '1']:
        c = and_(c, Dating.sex == sex)
    if age1 and age1.isdigit():
        age1 = int(age1)
    if age2 and age2.isdigit():
        age2 = int(age2)
    if age1:
        if age2:
            if age1 > age2:
                c = and_(c, Dating.age >= age2, Dating.age <=age1)
            else:
                c = and_(c, Dating.age >= age1, Dating.age <=age2)
        else:
            c = and_(c, Dating.age >= age1)
    else:
        if age2:
            c = and_(c, Dating.age <= age2)
    if loc1:
        c = and_(c, Dating.loc1 == loc1)
    if loc2:
        c = and_(c, Dating.loc2 == loc2)
   
    f = s
    if not f:
        s = DBSession()
    n = s.query(Dating).filter(c).count()
    r = s.query(Dating).filter(c).limit(limit).offset(page*next_)
    ids = [e.id for e in r]
    ru = []
    if ids:
        ru = s.query(Picture).filter(Picture.id.in_(ids)).all()
    p_m = {}
    for e in ru:
        p_m[e.id] = e.url0
    a = []
    for e in r:
        t = e.dic_return()
        df = 'img/default_female.jpg' if e.sex == 0 else 'img/default_male.jpg'
        t['src'] = p_m.get(e.id, df)
        a.append(t)
    if not f:
        s.close()
    return n, a

'''
我发起的约会
return:  结果个数, 结果列表
'''
def sponsor_dating(uid=None, page=None, limit=None, next_=None,  s=None):
    if not uid or not uid.isdigit():
        return None, None
    page = conf.toffset_dating_page if not page else int(page)
    limit = conf.toffset_dating_limit if not limit else int(limit)
    next_ = 0 if not next_ else int(next_)
   
    f = s
    if not f:
        s = DBSession()
    r = s.query(Dating).filter(Dating.userid == uid).limit(limit).offset(page*next_)
    ids = [e.id for e in r]
    ru = []
    if ids:
        ru = s.query(Picture).filter(Picture.id.in_(ids)).all()
    p_m = {}
    for e in ru:
        p_m[e.id] = e.url0
    a = []
    for e in r:
        t = e.dic_return()
        df = 'img/default_female.jpg' if e.sex == 0 else 'img/default_male.jpg'
        src = df if len(p_m.get(e.userid, '')) == 0 else p_m[e.userid]
        t['src'] = src
        a.append(t)

    return len(a), a

'''
参与的约会
uid: 报名参加人的id
return: 帖子总数, 帖子结果
'''
def participate_dating(uid, page=None, limit=None, next_=None,  s=None):
    if not uid or not uid.isdigit():
        return 0, None
    page = conf.toffset_dating_page if not page else int(page)
    limit = conf.toffset_dating_limit if not limit else int(limit)
    next_ = 0 if not next_ else int(next_)
    
    f = s
    if not f:
        s = DBSession()
    r = s.query(Yh_baoming).filter(Yh_baoming.userid == uid).limit(limit).offset(page*next_)
    if not r:
        if not f:
            s.close()
        return 0, []
    ids = [e.dating_id for e in  r]
    rd = s.query(Dating).filter(Dating.id.in_(ids)).all()
    if not rd:
        if not f:
            s.close()
        return 0, []
    d_m = {}
    for e in rd:
        d_m[e.id] = e.dic_return()

    a = [d_m[e] for e in d_m]

    if not f:
        s.close()
    return n, a

def create_dating(name=None, uid=None, age=18, sex=0, sjt=6, dt=None,\
        loc1=None, loc2=None, locd='未填', obj=2, num=1, fee=0, bc='无',\
        valid_time=1, t=None):
    if not name or not uid or not dt:
        return None
    if not loc1 and not loc2:
        return None
    loc1 = loc1 if loc1 else ''
    loc2 = loc2 if loc2 else ''
    if not t:
        t = time.localtime()
        t = time.strftime('%Y-%m-%d %H:%M:%S', t)
    d = Dating(name=name, uid=uid, age=age, sex=sex, sjt=sjt, dt=dt,\
               loc1=loc1, loc2=loc2, locd=locd, obj=obj, num=num,\
               fee=fee, bc=bc, valid_time=valid_time, t=t)
    s = DBSession()
    s.add(d)
    try:
        s.commit()
    except:
        s.close()
        m = d.dic_return()
        msg = 'creating dating failed: %s' % m
        print(msg)
        return False
    return True
        
def remove_dating(uid=None, did=None):
    if not uid or not did:
        return None
    s = DBSession()
    r = s.query(Dating).filter(and_(Dating.id == did, Dating.userid == uid)).all()
    if not r:
        s.close()
        return True
    s.query(Dating).filter(Dating.id == did).delete(synchronize_session=False)
    try:
        s.commit()
    except:
        s.close()
        msg = 'remove dating did: %s' % str(did)
        print(msg)
        return False
    s.close()
    return True

def detail_dating(did=None, s=None):
    if not did:
        return None
    f = s
    if not f:
        s = DBSession()
    r = s.query(Dating).filter(Dating.id == did).first()
    if not r:
        if not f:
            s.close()
        return None
    uid1 = r.userid
    ry = s.query(Yh_baoming).filter(Yh_baoming.dating_id == did).first()
    bm = [e.userid for e in ry]
    rp = s.query(Picture).filter(Picture.id == uid1).first()
    a = r.dic_return()
    df = 'img/default_female.jpg' if r.sex == 0 else 'img/default_male.jpg'
    a['src'] = df if not rp.url0 else rp.url0
    a['baoming'] = bm
    if not f:
        s.close()
    return a

def baoming_dating(uid=None, did=None, s=None):
    if not uid or not did:
        return None
    f = s
    if not f:
        s = DBSession()
    r = s.query(Dating).filter(Dating.id == did).first()
    if not r:
        if not f:
            s.close()
        return None
    if r.userid == uid:
        if not f:
            s.close()
        return None
    b = Yh_baoming(0, did, uid)
    s.add(b)
    try:
        s.commit()
    except:
        print('date baoming: failed uid=%s did=%s' % (str(uid), str(did)))
        if not f:
            s.close()
        return None
    if not f:
        s.close()
    return True

def list_zhenghun(sex=None, age1=None, age2=None, loc1=None, loc2=None, page=None, limit=None, next_=None, s=None):
    page = conf.toffset_dating_page if not page else int(page)
    limit = conf.toffset_dating_limit if not limit else int(limit)
    next_ = 0 if not next_ else int(next_)
    c = True
    if sex and sex in ['0', '1']:
        c = and_(c, Zhenghun.sex == sex)
    if age1 and age1.isdigit():
        age1 = int(age1)
    if age2 and age2.isdigit():
        age2 = int(age2)
    if age1:
        if age2:
            if age1 > age2:
                c = and_(c, Zhenghun.age >= age2, Zhenghun.age <=age1)
            else:
                c = and_(c, Zhenghun.age >= age1, Zhenghun.age <=age2)
        else:
            c = and_(c, Zhenghun.age >= age1)
    else:
        if age2:
            c = and_(c, Zhenghun.age <= age2)
    if loc1:
        c = and_(c, Zhenghun.loc1 == loc1)
    if loc2:
        c = and_(c, Zhenghun.loc2 == loc2)

    f = s
    if not f:
        s = DBSession()
    r = s.query(Zhenghun).filter(c).limit(limit).offset(page*next_).order_by(desc(Zhenghun.time_))
    if not r:
        if not f:
            s.close()
        return 0, []
    ids = [e.userid for e in r]
    rp = s.query(Picture).filter(Picture.id.in_(ids)).all()
    if not rp:
        if not f:
            s.close()
        return 0, []
    p_m = {}
    for e in rp:
        p_m[e.id] = e.url0
    a = []
    for e in r:
        t = e.dic_return()
        df = 'img/default_female.jpg' if e.sex == 0 else 'img/default_male.jpg'
        src = df if len(p_m.get(e.userid,'')) == 0 else p_m[e.userid]
        t['src'] = src
        a.append(t)
    if not f:
        s.close()
    n = len(a)
    return n, a

def create_zhenghun(uid=None, name=None, age=None, sex=None, loc1=None, \
        loc2=None, v_d=1, title=None, cnt=None, obj1=None):
    if not uid or not name or not age or not sex or not title or not obj1:
        return None
    if not loc1 and not loc2:
        return None
    s = DBSession()
    z = Zhenghun(0, uid, name, age, sex, loc1, loc2,
                 None, v_d, title, cnt, obj1)
    s.add(z)
    try:
        s.commit()
    except:
        msg = 'zhenghun create: failed uid=%s name=%s age=%s sex=%s loc1=%s loc2=%s valid_time=%d title=%s content=%s object1=%d' % (uid, name, age, sex, loc1, loc2, v_d, title, content, object1)
        print(msg)
        s.close()
        return None
    s.close()
    return True

def remove_zhenghun(zid=None):
    if not zid:
        return None
    s = DBSession()
    s.query(Zhenghun).filter(Zhenghun.id == zid).delete(synchronize_session=False)
    try:
        s.commit()
    except:
        s.close()
        print('zhenghun remove: failed zid=%s' % str(zid))
        return None
    s.close()
    return True

def sponsor_zhenghun(uid=None, page=None, limit=None, next_=None,  s=None):
    if not uid or not uid.isdigit():
        return None, None

    page = conf.toffset_zh_page if not page else int(page)
    limit = conf.toffset_zh_limit if not limit else int(limit)
    next_ = 0 if not next_ else int(next_)

    f = s
    if not f:
        s = DBSession()
    r = s.query(Zhenghun).filter(Zhenghun.userid == uid).limit(limit).offset(page*next_)
    if not r:
        if not f:
            s.close()
        return 0, []
    rp = s.query(Picture).filter(Picture.id == uid).first()
    sex = r.sex
    src = 'img/default_female.jpg' if sex == 0 else 'img/default_male.jpg'
    if rp and len(rp.url0) > 0:
        src = rp.url0
    a = []
    for e in r:
        t = e.dic_return()
        t['src'] = src
        a.append(t)
    if not f:
        s.close()
    return len(a), a


__all__=['verify_mobile', 'find_password', 'get_ctx_info_mobile_password',
         'user_regist', 'query_user', 'query_user_login', 'get_user_info',
         'update_basic','get_ctx_info', 'edit_statement', 'edit_other',
         'verify_wx_qq_email', 'isee', 'seeme', 'icare', 'list_dating',
         'public_conn','query_new', 'find_users', 'sponsor_dating',
         'participate_dating', 'create_dating', 'remove_dating',
         'detail_dating', 'baoming_dating', 'list_zhenghun',
         'create_zhenghun', 'remove_zhenghun', 'sponsor_zhenghun']


if __name__ == '__main__':
    n, r = list_dating()
    print(r)
'''
    r = user_regist('17313615918', '123', 1)
    print(r)
'''
