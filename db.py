#-*- coding: utf8 -*-

import time
import hashlib
from conf import conf
from cache import cache

from table import *
import json
from sqlalchemy.sql import and_, or_, not_
from sqlalchemy import desc

nation_table = {0:'未填', 1:'汉族', 2:'壮族', 3:'满族', 4:'回族', 5:'苗族',
    6:'维吾尔族', 7:'土家族', 8:'彝族', 9:'蒙古族', 10:'藏族',
    11:'布依族', 12:'侗族', 13:'瑶族', 14:'朝鲜族', 15:'白族',
    16:'哈尼族', 17:'哈萨克族', 18:'黎族', 19:'傣族', 20:'畲族',
    21:'傈傈族', 22:'仡佬族', 23:'东乡族', 24:'高山族', 25:'拉祜族',
    26:'水族', 27:'佤族', 28:'纳西族', 29:'羌族', 30:'土族',
    31:'仫佬族', 32:'锡伯族', 33:'柯尔克孜族', 34:'达翰尔族', 35:'景颇族',
    36:'毛南族', 37:'撒拉族', 38:'布朗族', 39:'塔吉克族', 40:'阿昌族',
    41:'普米族', 42:'鄂温克族', 43:'怒族', 44:'京族', 45:'基诺族',
    46:'德昂族', 47:'保安族', 48:'俄罗斯族', 49:'裕固族', 50:'乌孜别克族',
    51:'门巴族', 52:'鄂伦春族', 53:'独龙族', 54:'塔塔尔族', 55:'赫哲族',
    56:'珞巴族'}
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
    rs = {}
    try:
        tok = digest(passwd)
        r = s.query(User).filter(and_(User.mobile == mobile, User.password == tok)).first()
        rs = {} if not r else r.dic_return()
    except:
        rs = {}
    if not rs:
        if not t:
            s.close()
        return rs
    uid = r.id
    ft  = time.localtime()
    now = time.strftime('%Y-%m-%d %H:%M:%S', ft)
    r.last_login = now
    day = rs['last_login'].split(' ')[0]
    nd  = now.split(' ')[0]
    s.commit()
    if day != nd:
        r = s.query(User_account).filter(User_account.id == uid).first()
        if not r:
            u = User_account(uid, 0, conf.free_bean)
            s.add(u)
        else:
            r.free = conf.free_bean
        s.commit()
    
    if not t:
        s.close()
    return rs
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
            r = pt.dic_array()
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
    now = time.localtime()
    now = time.strftime('%Y-%m-%d %H:%M:%S', now)
    if str(r.last_login).split(' ')[0] != now.split(' ')[0]:
        r.last_login = now
        D = {User_account.free:conf.free_bean}
        ra = s.query(User_account).filter(User_account.id == r.id).update(D)
        s.commit()
    c['user'] = r.dic_return()
    c['user']['nation_name'] = nation_table.get(int(c['user']['nation']), '未填')
    
    st = query_statement_by_uid(uid, s=s)
    c['statement'] = st

    o = query_otherinfo_by_uid(uid, s=s)
    c['otherinfo'] = o

    p = query_pic_by_uid(uid, s=s)
    c['pic'] = p

    sex = c['user']['sex']
    df = 'img/default_female.jpg' if sex == 2 else 'img/default_male.jpg'
    if len(c['pic']['arr'][0]) == 0:
       c['pic']['arr'][0] = '%s/%s' % (conf.pic_ip, df)
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
        ctx['user']['nation_name'] = nation_table.get(int(nation), '未填')
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
    if not ids:
        s.close()
        return None
    m = s.query(Statement).filter(Statement.id.in_(ids)).all()
    m_ = {}
    for e in m:
        m_[e.id] = e.dic_return()
    p = s.query(Picture).filter(Picture.id.in_(ids)).all()
    p_ = {}
    for e in p:
        p_[e.id] = e.dic_array()
    D = {}
    for e in r:
        pic = p_.get(e.id)
        st  = m_.get(e.id)
        if not pic or not st:
            continue
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
kind=1 看手机 =2 看微信 =3看qq =4看邮箱号
return: =-1参数不对
'''
def seeother(kind=None, uid=None, cuid=None):
    if not kind or kind not in [1,2,3,4] or not uid or not cuid:
        return {'code':-1, 'msg':'参数错误'}
    fee_table = [0, conf.mobile_fee, conf.wx_fee, conf.qq_fee, conf.email_fee] 
    s = DBSession()
    o = query_otherinfo_by_uid(uid, s=s)
    if not o:
        s.close()
        return {'code':-1, 'msg':'没有此用户'}
    info = [0, o['mobile'],   o['wx'],      o['qq'],       o['email']]
    pub  = [0, o['public_m'], o['public_w'],o['public_q'], o['public_e']]
    vry  = [0, o['verify_m'], o['verify_w'],o['verify_q'], o['verify_e']]
    pub_ = pub[kind]
    vry_ = vry[kind]
    conn = info[kind]
    if len(conn) == 0:
        s.close()
        return {'code':-1, 'msg':'用户未填,不扣豆'}
    ru = s.query(User_account).filter(User_account.id == cuid).first()
    if not ru:
        s.close()
        return {'code':-1, 'msg':'没有此用户'}
    cond = and_(Consume_record.userid == cuid, Consume_record.objid == uid, Consume_record.way == kind+4)
    rc = s.query(Consume_record).filter(cond).first()
    if rc:
        s.close()
        return {'code':0, 'msg':'ok', 'data':{'account': ru.dic_return(), 'conn': conn}}
    else:
        if not pub_:
            s.close()
            return {'code':-1, 'msg':'用户为公开该联系方式'}
        if not vry_:
            s.close()
            return {'code':-1, 'msg':'用户为填写该联系方式'}
            
        fee = fee_table[kind] 
        if ru.free >= fee:
            ru.free = ru.free - fee
            ac = ru.dic_return()
            s.commit()
            s.close()
            return {'code':0, 'msg':'ok', 'data':{'account': ac, 'conn':conn}}
        elif ru.num >= fee:
            ru.num = ru.num - fee
            ac = ru.dic_return()
            c = Consume_record(0, cuid, uid, kind+4, fee)
            s.add(c)
            s.commit()
            s.close()
            return {'code':0, 'msg':'ok', 'data':{'account': ac, 'conn':conn}}
        else:
            s.close()
            return {'code':-1, 'msg':'余额不足'}

def sawother(cuid=None, uid=None, s=None):
    a = {'wx':0, 'qq': 0, 'email': 0, 'mobile':0, 'email1': 0, 'yanyuan':0}
    if not cuid or not uid:
        d = {'code': 0, 'msg': 'ok', 'data': a}
        return d
    f = s
    if not f:
        s = DBSession()
    cuid, uid = int(cuid), int(uid)
    if uid != cuid:
        print('uid=%d cuid=%d' % (uid, cuid))
        rl = s.query(Look).filter(Look.from_id == cuid, Look.to_id == uid).order_by(desc(Look.time_)).all()
        if rl:
            ids = []
            for i in xrange(len(rl)):
                if i > conf.toffset_look_limit :
                    ids.append(rl[i].id)
            if ids:
                s.query(Look).filter(Look.id.in_(ids)).delete(synchronize_session=False)
        l = Look(id_=0, f=cuid, to=uid)
        s.add(l)
        s.commit()
    c = and_(Consume_record.userid == cuid, Consume_record.objid == uid)
    c = and_(c, Consume_record.way != 3, Consume_record.way != 4)
    r = s.query(Consume_record).filter(c).all()
    if not r:
        if not f:
            s.close()
        d = {'code':0, 'msg': 'ok', 'data': a}
        return d
    c_m = {}
    n = 6
    for e in r:
        if n < 1:
            break
        if e.way == 1:
            if a['yanyuan'] == 0:
                n = n-1
            a['yanyuan'] = 1
        elif e.way == 2:
            if a['email1'] == 0:
                n = n-1
            a['email1'] = 1
        elif e.way == 5:
            if a['mobile'] == 0:
                n = n-1
            a['mobile'] = 1
        elif e.way == 6:
            if a['wx'] == 0:
                n = n-1
            a['wx'] = 1
        elif e.way == 7:
            if a['qq'] == 0:
                n = n-1
            a['qq'] = 1
        elif e.way == 8:
            if a['email'] == 0:
                n = n-1
            a['email'] = 1

    if not f:
        s.close()
    return {'code':0, 'msg': 'ok', 'data': a}
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

def write_img(uid=None, first=None, second=None, third=None, kind=None):
    if not uid or not first or not second or not third or not kind:
        return None
    s = DBSession()
    r = s.query(Picture).filter(Picture.id == uid).first()
    if not r or r.count < 1:
        s.close()
        return None
    else:
        src = '%s/%s/%s' % (first, second, third)
        if kind == '1':
            if len(r.url0) and src != r.url0:
                dp = DeprecatedPicture(0, r.url0)
                s.add(dp)
            r.url0 = src
        else:
            r.count = r.count - 1
            if not len(r.url1):
                r.url1 = src
            elif not len(r.url2):
                r.url2 = src
            elif not len(r.url3):
                r.url3 = src
            elif not len(r.url4):
                r.url4 = src
            elif not len(r.url5):
                r.url5 = src
            elif not len(r.url6):
                r.url6 = src
            elif not len(r.url7):
                r.url7 = src
            elif not len(r.url8):
                r.url8 = src
            elif not len(r.url9):
                r.url9 = src
            else:
                s.close()
                return None
        s.commit()
    s.close()
    return True

def delimg(uid=None, src=None):
    if not uid or not src:
        return None
    s = DBSession()
    r = s.query(Picture).filter(Picture.id == uid).first()
    if not r:
        s.close()
        return None
    if r.url0 == src:
        r.url0 = ''
        r.count = r.count + 1
    elif r.url1 == src:
        r.url1, r.url2, r.url3, r.url4, r.url5, r.url6, r.url7, r.url8, r.url9 = r.url2, r.url3, r.url4, r.url5, r.url6, r.url7, r.url8, r.url9, ''
        r.count = r.count + 1
    elif r.url2 == src:
        r.url2, r.url3, r.url4, r.url5, r.url6, r.url7, r.url8, r.url9 = r.url3, r.url4, r.url5, r.url6, r.url7, r.url8, r.url9, ''
        r.count = r.count + 1
    elif r.url3 == src:
        r.url3, r.url4, r.url5, r.url6, r.url7, r.url8, r.url9 = r.url4, r.url5, r.url6, r.url7, r.url8, r.url9, ''
        r.count = r.count + 1
    elif r.url4 == src:
        r.url4, r.url5, r.url6, r.url7, r.url8, r.url9 = r.url5, r.url6, r.url7, r.url8, r.url9, ''
        r.count = r.count + 1
    elif r.url5 == src:
        r.url5, r.url6, r.url7, r.url8, r.url9 = r.url6, r.url7, r.url8, r.url9, ''
        r.count = r.count + 1
    elif r.url6 == src:
        r.url6, r.url7, r.url8, r.url9 = r.url7, r.url8, r.url9, ''
        r.count = r.count + 1
    elif r.url7 == src:
        r.url7, r.url8, r.url9 = r.url8, r.url9, ''
        r.count = r.count + 1
    elif r.url8 == src:
        r.url8, r.url9 = r.url9, ''
        r.count = r.count + 1
    elif r.url9 == src:
        r.url9 = ''
        r.count = r.count + 1
    s.commit()
    s.close()
    return True
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
    ids = [e.to_id for e in a1] if kind == 1 else [e.from_id for e in a1]
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
        d = e.dic_array()
        m_p[e.id] = d['arr'][0]
    N = len(a1)
    for e in a1:
        [t1, t2] = str(e.time_).split(' ')
        k = e.to_id if kind == 1 else e.from_id
        u = m_u.get(k)
        if not u:
            continue
        df = 'img/default_female.jpg' if u['sex'] == 2 else 'img/default_male.jpg'
        df = '%s/%s' % (conf.pic_ip, df)
        p = m_p.get(k)
        p = df if not p else p
        if not u:
            N = N - 1
            continue
        d = {'id':k, 'nick_name':u['nick_name'], 'sex':u['sex'],
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
        if not u:
            N = N - 1
            continue
        p = m_p.get(e.to_id, '')
        df = 'img/default_female.jpg' if u['sex'] == 2 else 'img/default_male.jpg'
        p = df if not p else p
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

'''
kind =1关注 =0取消关注
'''
def sendcare(uid=None, cuid=None, kind=None):
    if not uid or not cuid or not kind:
        return None
    s = DBSession()
    c = and_(Care.from_id == cuid, Care.to_id == uid)
    r = s.query(Care).filter(c).first()
    if not r:
        if kind == 0:
            s.close()
            return True
        else:
            ca = Care(id_=0, f=cuid, to=uid)
            s.add(ca)
            s.commit()
            s.close()
            return True
    if kind == 0:
        s.query(Care).filter(Care.id == r.id).delete(synchronize_session=False)
        s.commit()
        return True
    s.close()
    return True

def yanyuan(uid=None, cuid=None, s=None):
    if not uid or not cuid:
        return None
    if uid == cuid:
        return None
    f = s
    if not f:
        s = DBSession()
    c = and_(Yanyuan.from_id == cuid, Yanyuan.to_id == uid)
    r = s.query(Yanyuan).filter(c).first()
    if r:
        if not f:
            s.close()
        return True
    y = Yanyuan(id_=0, f=cuid, t=uid)
    s.add(y)
    cnt = conf.msg_yanyuan
    e = Email(id_=0, f=cuid, t=uid, c=cnt, k=1)
    s.add(e)
    s.commit()
    if not f:
        s.close()
    return True

def yanyuan_check(uid=None, cuid=None, s=None):
    if not uid or not cuid:
        return None
    if uid == cuid:
        return None
    f = s
    if not f:
        s = DBSession()
    c = and_(Yanyuan.from_id == cuid, Yanyuan.to_id == uid)
    r = s.query(Yanyuan).filter(c).first()
    if not f:
        s.close()
    return True if r else None

#kind=1 收件 !=1 发件
def __mail(kind=1, uid=None, page=None, next_=None, s=None):
    if not uid or not page or next_ < 0:
        return []
    uid, page, next_ = int(uid), int(page), int(next_)
    f = s
    if not f:
        s = DBSession()
    c, d = True, {}
    if kind == 1:
        c = and_(Email.to_id == uid, Email.to_del == 0)
    else:
        c = and_(Email.from_id == uid, Email.from_del == 0)
    r = s.query(Email).filter(c).limit(page).offset(page*next_)
    if not r:
        if not f:
            s.close()
        return []
    m_ids = {}
    ids = []
    if kind == 1:
        for e in r:
            m_ids[e.from_id] = 1
    else:
        for e in r:
            m_ids[e.to_id] = 1
    ids = m_ids.keys()
    if not ids:
        if not f:
            s.close()
        return []
    ru = s.query(User).filter(User.id.in_(ids)).all()
    if not ru:
        if not f:
            s.close()
        return []
    u_m = {}
    for e in ru:
        u_m[e.id] = e.dic_return()

    rp = s.query(Picture).filter(Picture.id.in_(ids)).all()
    p_m = {}
    for e in p_m:
        p_m[e.id] = e.url0

    e_m = {}
    for e in r:
        t = str(e.time_)
        mail = {'read':e.read_, 'id': e.id, 'content': e.content,
                'time': str(e.time_), 'kind': e.kind}
        d = {}
        if kind == 1:
            u = u_m.get(e.from_id)
            if not u:
                continue
            name = '新用户%s'% u['mobile'][-4:] if not u['nick_name'] else u['nick_name']
            sex_name = '男' if u['sex'] == 1 else '女'
            user = {'id': e.from_id, 'name': name, 'sex': u['sex']}
            sex = u['sex']
            df = 'img/default_female.jpg' if sex == 2 else 'img/default_male.jpg'
            src = p_m.get(e.from_id, '')
            if not src:
                src = '%s/%s' % (conf.pic_ip, df)
            user['pic'] = src
            user['sex_name'] = sex_name
            d = {'user': user, 'mail': mail}
        else:
            u = u_m.get(e.to_id)
            if not u:
                continue
            name = '新用户%s'% u['mobile'][-4:] if not u['nick_name'] else u['nick_name']
            user = {'id': e.to_id, 'name': name, 'sex': u['sex']}
            sex_name = '男' if u['sex'] == 2 else '女'
            sex = u['sex']
            df = 'img/default_female.jpg' if sex == 2 else 'img/default_male.jpg'
            src = p_m.get(e.to_id, '')
            if not src:
                src = '%s/%s' % (conf.pic_ip, df)
            user['pic'] = src
            user['sex_name'] = sex_name
            d = {'user': user, 'mail': mail}
        if not e_m.get(t):
            e_m[t] = [d]
        else:
            e_m[t].append(d)
    if not f:
        s.close()

    a = sorted(e_m.keys(), reverse=True)
    D = []
    for e in a:
        for d in e_m[e]:
            D.append(d)
    return D
   
def see_email(eid=None, cuid=None):
    if not eid or not cuid:
        return None
    s = DBSession()
    r = s.query(Email).filter(Email.id == eid).first()
    if not r:
        return True
    r.read_ = 1
    s.commit()
    s.close()
    return True

def email(uid=None, page=None, next_=None, s=None):
    if not uid or not page or next_ < 0:
        return None
    f = s
    if not f:
        s = DBSession()
    in_  = __mail(1, uid, page, next_, s)
    out_ = __mail(2, uid, page, next_, s)
  
    unread = 0
    for e in in_:
        if e['mail']['read'] == 0:
            unread = unread + 1
    c = and_(Email.to_id == uid, Email.to_del == 0)
    ri = s.query(Email).filter(c).count()
    c = and_(Email.from_id == uid, Email.from_del == 0)
    ro = s.query(Email).filter(c).count()
    if not f:
        s.close()
    
    return {'in':in_,'out':out_,'total_in':ri,'totoal_out':ro,'page':page, 'unread':unread}

def latest_conn(uid=None, s=None):
    if not uid:
        return -1, None
    f = s
    if not f:
        s = DBSession()
    uc = and_(User.id == uid, User.valid_state == 0)
    ru = s.query(User).filter(uc).first()
    if not ru:
        if not f:
            s.close()
        return 0, []
    sex = ru.sex 
    c = or_(Email.from_id == uid, Email.to_id == uid)
    c = and_(c, Email.kind == 0)
    r = s.query(Email).filter(c).limit(20)
    if not r:
        if not f:
            s.close()
        return 0, []
    e_m = {}
    for e in r:
        if e.from_id != uid:
            e_m[e.from_id] = 1
        if e.to_id != uid:
            e_m[e.to_id] = 1
    ids = e_m.keys()[:conf.toffset_freq_conn]
    if not ids:
        if not f:
            s.close()
        return 0, []

    r = s.query(User).filter(User.id.in_(ids)).all()
    u_m = {}
    for e in r:
        u_m[e.id] = e
    rp = s.query(Picture).filter(Picture.id.in_(ids)).all()
    p_m = {}
    for e in rp:
        d = e.dic_array()
        p_m[e.id] = d['arr'][0]
    a = []
    for e in u_m:
        name = u_m[e].nick_name
        if not name:
            name = '新用户%s'% u_m[e].mobile[-4:]
        sex = u_m[e].sex
        sex_name = '女' if sex == 2 else '男'
        src = p_m.get(u_m[e].id, '')
        if not src:
            df = 'img/default_female.jpg' if sex == 2 else 'img/default_male.jpg'
            src = '%s/%s' % (conf.pic_ip, df)
        last_login = str(u_m[e].last_login)
        d = {'name': name, 'sex': sex, 'src': src, 'id': u_m[e].id,
            'last_login': last_login, 'sex_name':sex_name }
        a.append(d)
    if not f:
        s.close()
    return 0, a

'''
cuid: 主动发信人id
uid:  收信人id
content: 发信内容
eid: 邮件id, 如果有此eid,表示在此eid基础上回复信件,不收费
kind: 邮件类型 0=普通信件 1=系统信件
return: -1=参数不正确  -2=余额不足 0=成功
'''
def sendemail(uid=None, cuid=None, content=None, eid=None, kind=0, s=None):
    if not uid or not cuid or not content:
        return -1
    if uid == cuid:
        return -1
    f = s
    if not f:
        s = DBSession()
    already = False
    if eid:
        eid = int(eid)
        c = or_(Email.from_del == 0, Email.to_del == 0)
        c1= and_(c, Email.kind == 0)
        ralready = s.quey(Email).filter(Email.id == eid).filter(c1).first()
        if ralready:
            if ralready.from_id in [uid, cuid]:
                already = True
            if ralready.to_id in [uid, cuid]:
                already = True
    if not already:
        ru = s.query(User_account).filter(User_account.id == cuid).first()
        if not ru:
            if not f:
                s.close()
            return -1
        fee = conf.send_email_fee
        if ru.free >= fee:
            ru.free = ru.free - fee
        elif ru.num >= fee:
            ru.num = ru.num - fee
        else:
            if not f:
                s.close()
            return -2

    e = Email(id_=0, f=cuid, t=uid, c=content, k=kind)
    s.add(e)
    s.commit()
    if not f:
        s.close()
    return 0

'''
删除邮件只是将邮件标识为已删除,并未真正删除
'''
def del_email(uid=None, eid=None, s=None):
    if not uid or not eid:
        return None
    f = s
    if not f:
        s = DBSession()
    r = s.query(Email).filter(Email.id == eid).first()
    if not r:
        if not f:
            s.close()
        return True
    if r.from_id == uid:
        r.from_del = 1
        s.commit()
        if not f:
            s.close()
        return True
    if r.to_id == uid:
        r.to_del = 1
        s.commit()
        if not f:
            s.close()
        return True

    if not f:
        s.close()
    return True

def list_dating(sex=None, age1=None, age2=None, loc1=None, loc2=None, page=None, limit=None, next_=None, s=None):
    if loc1:
        if loc1[:2] in ['北京','上海', '天津', '重庆']:
            loc2 = None
    if loc2:
        loc1 = None
    page = conf.toffset_dating_page if not page else int(page)
    limit = conf.toffset_dating_limit if not limit else int(limit)
    next_ = 0 if not next_ else int(next_)
    c = True
    if sex:
        sex = int(sex)
    if sex and sex in [0, 1]:
        c = and_(c, Dating.sex == sex)
    if age1:
        age1 = int(age1)
    if age2:
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
  
    c = and_(c, Dating.valid_state == 0)
    f = s
    if not f:
        s = DBSession()
    n = s.query(Dating).filter(c).count()
    r = s.query(Dating).filter(c).order_by(desc(Dating.time_)).limit(limit).offset(page*next_)
    if not r:
        if not f:
            s.close()
        return {'page':page, 'arr':[], 'total': 0, 'next': next_}
    tmp = {}
    for e in r:
        tmp[e.userid] = 1
    ids = tmp.keys()
    
    ru = []
    if ids:
        ru = s.query(User).filter(User.id.in_(ids)).all()
    p_u = {}
    for e in ru:
        p_u[e.id] = e.dic_return()

    rp = []
    if ids:
        rp = s.query(Picture).filter(Picture.id.in_(ids)).all()
    p_m = {}
    for e in rp:
        p = e.dic_array()
        p_m[e.id] = p['arr'][0]
    a = []
    for e in r:
        u = p_u.get(e.userid)
        if not u:
            n = n-1
            continue
        sex = u['sex']
        t = e.dic_return()
        sjtmap = {0:'约饭',1:'电影',2:'交友',3:'聊天',
                  4:'喝酒',5:'唱歌',6:'其他'}
        t['subject_name'] =  sjtmap.get(e.subject, '其他')
        feemap = {0:'发起人付',1:'AA',2:'男士付款,女士免单',
              3:'视情况而定'}
        objmap = {0:'男士',1:'女士', 2:'男女均可'}
        t['object_name'] = objmap.get(e.object1, '男女均可')
        t['fee_name'] = feemap.get(e.fee, feemap[3])
        t['nick_name'] = u['nick_name']
        t['sex'] = sex
        t['sex_name'] = '男' if sex == 1 else '女'
        t['age'] = u['age']
        t['loc1'] = u['curr_loc1']
        t['loc2'] = u['curr_loc2']
        df = 'img/default_female.jpg' if sex == 2 else 'img/default_male.jpg'
        df = '%s/%s' % (conf.pic_ip, df)
        src = p_m.get(e.userid)
        t['src'] = src if src else df
        a.append(t)
    if not f:
        s.close()
    return {'page':page, 'arr':a, 'total': n, 'next': next_}

'''
我发起的约会
return:  结果个数, 结果列表
'''
def sponsor_dating(uid=None, page=None, limit=None, next_=None,  s=None):
    page = conf.toffset_dating_page if not page else int(page)
    limit = conf.toffset_dating_limit if not limit else int(limit)
    next_ = 0 if not next_ else int(next_)

    if not uid or not uid.isdigit():
        return {'page':page, 'arr':[], 'total': 0, 'next': next_}
   
    f = s
    if not f:
        s = DBSession()
    c = and_(Dating.userid == uid, Dating.valid_state != 2)
    n = s.query(Dating).filter(c).order_by(desc(Dating.time_)).count()
    r = s.query(Dating).filter(c).order_by(desc(Dating.time_)).limit(limit).offset(page*next_)
    if not r:
        if not f:
            s.close()
        return {'page':page, 'arr':[], 'total': 0, 'next': next_}
    tmp = {}
    for e in r:
        tmp[e.userid] = 1
    ids = tmp.keys()
    
    ru = []
    if ids:
        ru = s.query(User).filter(User.id.in_(ids)).all()
    p_u = {}
    for e in ru:
        p_u[e.id] = e.dic_return()

    rp = []
    if ids:
        rp = s.query(Picture).filter(Picture.id.in_(ids)).all()
    p_m = {}
    for e in rp:
        p = e.dic_array()
        p_m[e.id] = p['arr'][0]
    a = []
    for e in r:
        u = p_u.get(e.userid)
        if not u:
            n = n-1
            continue
        sex = u['sex']
        t = e.dic_return()
        sjtmap = {0:'约饭',1:'电影',2:'交友',3:'聊天',
                  4:'喝酒',5:'唱歌',6:'其他'}
        t['subject_name'] =  sjtmap.get(e.subject, '其他')
        feemap = {0:'发起人付',1:'AA',2:'男士付款,女士免单',
              3:'视情况而定'}
        objmap = {0:'男士',1:'女士', 2:'男女均可'}
        t['object_name'] = objmap.get(e.object1, '男女均可')
        t['fee_name'] = feemap.get(e.fee, feemap[3])
        t['nick_name'] = u['nick_name']
        t['sex'] = sex
        t['sex_name'] = '男' if sex == 1 else '女'
        t['age'] = u['age']
        t['loc1'] = u['curr_loc1']
        t['loc2'] = u['curr_loc2']
        df = 'img/default_female.jpg' if sex == 2 else 'img/default_male.jpg'
        df = '%s/%s' % (conf.pic_ip, df)
        src = p_m.get(e.userid)
        t['src'] = src if src else df
        a.append(t)
    if not f:
        s.close()
    return {'page':page, 'arr':a, 'total': n, 'next': next_}

'''
参与的约会
uid: 报名参加人的id
return: 帖子总数, 帖子结果
'''
def participate_dating(uid, page=None, limit=None, next_=None,  s=None):
    page = conf.toffset_dating_page if not page else int(page)
    limit = conf.toffset_dating_limit if not limit else int(limit)
    next_ = 0 if not next_ else int(next_)
    if not uid or not uid.isdigit():
        return {'page':page, 'arr':[], 'total': 0, 'next': next_}
    
    f = s
    if not f:
        s = DBSession()
    n = s.query(Yh_baoming).filter(Yh_baoming.userid == uid).count()
    r = s.query(Yh_baoming).filter(Yh_baoming.userid == uid).order_by(desc(Yh_baoming.time_)).limit(limit).offset(page*next_)
    if not r:
        if not f:
            s.close()
        return {'page':page, 'arr':[], 'total': 0, 'next': next_}
    ids = [e.dating_id for e in  r]
    rd = s.query(Dating).filter(Dating.id.in_(ids)).filter(Dating.valid_state != 2).all()
    if not rd:
        if not f:
            s.close()
        return {'page':page, 'arr':[], 'total': 0, 'next': next_}
    ids = [e.userid for e in rd]
    pu = s.query(Picture).filter(Picture.id.in_(ids)).all()
    p_m = {}
    for e in pu:
        p_m[e.id] = e.dic_array()

    d_m = {}
    for e in rd:
        d_m[e.id] = e.dic_return()
        sex = e.sex
        sex_name = '女' if sex == 0 else '男'
        d_m[e.id]['sex_name'] = sex_name
        df = 'img/default_female.jpg' if sex == 0 else 'img/default_male.jpg'
        src = ''
        p = p_m.get(e.userid)
        if not p or not p['arr'][0]:
            src = '%s/%s' % (conf.pic_ip, df)
        else:
            src = p['arr'][0]
        d_m[e.id]['src'] = src


    a = d_m.values()

    if not f:
        s.close()
    return {'page':page, 'arr':a, 'total': n, 'next': next_}

def create_dating(uid=None, age=18, sjt=6, dt=None,\
        loc1=None, loc2=None, locd='', obj=2, num=1, fee=0, bc='',\
        valid_time=1):
    if not uid or not dt:
        return None
    if not loc1 and not loc2:
        return None
    age, sjt = int(age), int(sjt)
    obj, num, fee = int(obj), int(num), int(fee)
    valid_time = int(valid_time)
    loc1 = loc1 if loc1 else ''
    loc2 = loc2 if loc2 else ''
    s = DBSession()
    r = s.query(User).filter(User.id == uid).first()
    if not r:
        s.close()
        return False
    name = r.nick_name
    sex =  1 if r.sex == 1 else 0
    d = Dating(name=name, uid=uid, age=age, sex=sex, sjt=sjt, dt=dt,\
               loc1=loc1, loc2=loc2, locd=locd, obj=obj, num=num,\
               fee=fee, bc=bc, valid_time=valid_time)
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
    r = s.query(Dating).filter(Dating.id == did).first()
    if not r:
        s.close()
        return True
    if r.userid != uid:
        s.close()
        return True
    r.valid_state = 2
    r.msg = '用户删除'
    try:
        s.commit()
    except:
        s.close()
        msg = 'remove dating did: %s' % str(did)
        print(msg)
        return False
    s.close()
    return True

def detail_dating(uid=None, did=None, s=None):
    if not uid or not did:
        return {}
    f = s
    if not f:
        s = DBSession()
    r = s.query(Dating).filter(Dating.id == did).first()
    if not r:
        if not f:
            s.close()
        return {}
    buchong = r.buchong
    me = True if uid == r.userid else False
    uid1 = r.userid
    D = {}
    u = s.query(User).filter(User.id == uid1).first()
    if not u:
        if not f:
            s.close()
        return {}
    if len(buchong) == 0:
        rs = s.query(Statement).filter(Statement.id == uid1).first()
        if rs:
            buchong = rs.motto if len(rs.content) == 0 else rs.content
    sex = u.sex
    df = 'img/default_female.jpg' if sex == 2 else 'img/default_male.jpg'
    df = '%s/%s' % (conf.pic_ip, df)
    rp = s.query(Picture).filter(Picture.id == uid1).first()
    src = df
    if rp:
        p = rp.dic_array()
        src = df if len(p['arr'][0]) == 0 else p['arr'][0]
    D['src'] = src 
    D['nick_name'] = u.nick_name
    D['sex'] = u.sex
    D['sex_name'] = '男' if u.sex == 1 else '女'
    D['age'] = u.age
    D['height'] = u.height
    D['loc1'] = u.curr_loc1
    D['loc2'] = u.curr_loc2
    D['statement'] = buchong
    D['subject'] = r.subject
    sjtmap = {0:'约饭',1:'电影',2:'交友',3:'聊天',
              4:'喝酒',5:'唱歌',6:'其他'}
    D['subject_name'] =  sjtmap.get(r.subject, '其他')
    D['scan_count'] = r.scan_count + 1
    r.scan_count = r.scan_count + 1
    D['numbers'] = r.numbers
    D['fee'] = r.fee
    feemap = {0:'发起人付',1:'AA',2:'男士付款,女士免单',
              3:'视情况而定'}
    D['fee_name'] = feemap.get(r.fee, feemap[3])
    D['dtime'] = str(r.dtime)
    D['object'] = r.object1
    objmap = {0:'男士',1:'女士', 2:'男女均可'}
    D['object_name'] = objmap.get(r.object1, '男女均可')
    D['loc_detail'] = r.loc_detail
    D['buchong'] = r.buchong
    D['time'] = str(r.time_)
    D['valid_time'] = r.valid_time
    s.commit()
    if not me: 
        D['me'] = 0
        c = and_(Yh_baoming.dating_id == did, Yh_baoming.userid == uid)
        ry = s.query(Yh_baoming).filter(c).all()
        D['already'] = 1 if ry else 0
    else:
        D['me'] = 1
        ry = s.query(Yh_baoming).filter(Yh_baoming.dating_id == did).all()
        if not ry:
            D['baoming'] = []
        else:
            y_u = {}
            for e in ry:
                y_u[e.userid] = e
            ids = y_u.keys()
            ru = s.query(User).filter(User.id.in_(ids)).all()
            u_m = {}
            for e in ru:
                u_m[e.id] = e
            rs = s.query(Statement).filter(Statement.id.in_(ids)).all()
            rs_m = {}
            for e in rs:
                rs_m[e.id] = e
            rp = s.query(Picture).filter(Picture.id.in_(ids)).all()
            p_m = {}
            for e in rp:
                sex = u_m[e.id].sex
                df = 'img/default_female.jpg' if sex == 2 else 'img/default_male.jpg'
                df = '%s/%s' % (conf.pic_ip, df)
                p = e.dic_array()
                src = p['arr'][0]
                src = df if len(src) == 0 else src
                p_m[e.id] = src
            B = []
            degree_map = {0:'保密',1:'高中及以下',2:'中专/大专',3:'本科',
                          4:'研究生',5:'博士及博士后'}
            for e in ru:
                st = rs_m[e.id].content
                if not st:
                    st = rs_m[e.id].motto
                st = '%s...'%st[:40]
                name = '新用户%s' % e.mobile[-4:] if not e.nick_name else e.nick_name
                src = p_m[e.id]
                sex = e.sex
                sex_name = '男' if sex == 1 else '女'
                tm = str(y_u[e.id].time_)
                degree = u_m[e.id].degree
                age = e.age
                height = e.height
                degree_name = degree_map.get(degree, '保密')
                b = {'nick_name': name, 'src': src, 'sex': sex,
                     'sex_name': sex_name, 'time': tm, 'age': age,
                     'height': height, 'degree': degree, 'id': e.id,
                     'degree_name': degree_name, 'statement': st}
                B.append(b)
            D['baoming'] = B
    if not f:
        s.close()
    return D

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
    c = and_(Yh_baoming.dating_id == did, Yh_baoming.userid == uid)
    ry = s.query(Yh_baoming).filter(c).first()
    if ry:
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
    page = conf.toffset_zhenghun_page if not page else int(page)
    limit = conf.toffset_zhenghun_limit if not limit else int(limit)
    next_ = 0 if not next_ else int(next_)
    c = True
    if sex:
        sex = int(sex)
    if sex and sex in [0, 1]:
        c = and_(c, Zhenghun.sex == sex)

    if age1:
        age1 = int(age1)
    if age2:
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
    n = s.query(Zhenghun).filter(c).count()
    r = s.query(Zhenghun).filter(c).order_by(desc(Zhenghun.time_)).limit(limit).offset(page*next_)
    if not r:
        if not f:
            s.close()
        return {'page':page, 'arr':[], 'total': 0, 'next': next_}
    tmp = {}
    for e in r:
        tmp[e.userid] = 1
    ids = tmp.keys()
    ru = []
    if ids:
        ru = s.query(User).filter(User.id.in_(ids)).all()
    p_u = {}
    for e in ru:
        p_u[e.id] = e.dic_return()

    rp = []
    if ids:
        rp = s.query(Picture).filter(Picture.id.in_(ids)).all()
    p_m = {}
    for e in rp:
        p = e.dic_array()
        p_m[e.id] = p['arr'][0]
    a = []

    for e in r:
        u = p_u.get(e.userid)
        if not u:
            n = n-1
            continue
        sex = u['sex']
        t = e.dic_return()
        t['object_name'] = '征MM' if e.object1 == 0 else '征GG'
        t['nick_name'] = u['nick_name']
        t['sex'] = sex
        t['sex_name'] = '男' if sex == 1 else '女'
        t['age'] = u['age']
        df = 'img/default_female.jpg' if sex == 2 else 'img/default_male.jpg'
        df = '%s/%s' % (conf.pic_ip, df)
        src = p_m.get(e.userid)
        t['src'] = src if src else df
        a.append(t)
    if not f:
        s.close()
    return {'page':page, 'arr':a, 'total': n, 'next': next_}


def create_zhenghun(uid=None, loc1=None, \
        loc2=None, v_d=1, title=None, cnt=None, obj1=None):
    err = {'code': -1, 'msg': '参数不对'}
    if not uid or not title or not obj1 or not v_d:
        return err
    if not loc1 and not loc2:
        return err
    if not cnt:
        cnt = ''
    if not loc1:
        loc1 = ''
    if not loc2:
        loc2 = ''
    s = DBSession()
    ru = s.query(User).filter(User.id == uid).first()
    if not ru:
        s.close()
        return err
    name = ru.nick_name if ru.nick_name else '新用户%s'%ru.mobile[-4:]
    age  = ru.age
    sex  = 1 if ru.sex == 1 else 0

    ra = s.query(User_account).filter(User_account.id == uid).first()
    if not ra:
        s.close()
        return err
    if ra.free >= conf.zhenghun_fee:
        ra.free = ra.free - conf.zhenghun_fee
    elif ra.num >= conf.zhenghun_fee:
        ra.num = ra.num - conf.zhenghun_fee
    else:
        s.close()
        return {'code': -1, 'msg': '余额不足'}

    z = Zhenghun(id_=0, uid=uid, name=name, age=age, sex=sex, loc1=loc1,\
                 loc2=loc2, v_d=v_d, title=title, cnt=cnt, obj1=obj1)
    s.add(z)
    try:
        s.commit()
    except:
        msg = 'zhenghun create: failed uid=%s name=%s age=%s sex=%s loc1=%s loc2=%s valid_time=%d title=%s content=%s object1=%d' % (uid, name, age, sex, loc1, loc2, v_d, title, cnt, obj1)
        print(msg)
        s.close()
        return err
    s.close()
    return {'code': 0, 'msg': 'ok'}

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
    if not uid:
        return {'page':page, 'arr':[], 'total': 0, 'next': next_}

    page = conf.toffset_zhenghun_page if not page else int(page)
    limit = conf.toffset_zhenghun_limit if not limit else int(limit)
    next_ = 0 if not next_ else int(next_)

    f = s
    if not f:
        s = DBSession()
    n = s.query(Zhenghun).filter(Zhenghun.userid == uid).count()
    r = s.query(Zhenghun).filter(Zhenghun.userid == uid).order_by(desc(Zhenghun.time_)).limit(limit).offset(page*next_)
    if not r:
        if not f:
            s.close()
        return {'page':page, 'arr':[], 'total': 0, 'next': next_}

    tmp = {}
    for e in r:
        tmp[e.userid] = 1
    ids = tmp.keys()
    ru = []
    if ids:
        ru = s.query(User).filter(User.id.in_(ids)).all()
    p_u = {}
    for e in ru:
        p_u[e.id] = e.dic_return()
    rp = []
    if ids:
        rp = s.query(Picture).filter(Picture.id.in_(ids)).all()
    p_m = {}
    for e in rp:
        p = e.dic_array()
        p_m[e.id] = p['arr'][0]
    a = []

    for e in r:
        u = p_u.get(e.userid)
        if not u:
            n = n-1
            continue
        sex = u['sex']
        t = e.dic_return()
        t['object_name'] = '征MM' if e.object1 == 0 else '征GG'
        t['nick_name'] = u['nick_name']
        t['sex'] = sex
        t['sex_name'] = '男' if sex == 1 else '女'
        t['age'] = u['age']
        df = 'img/default_female.jpg' if sex == 2 else 'img/default_male.jpg'
        df = '%s/%s' % (conf.pic_ip, df)
        src = p_m.get(e.userid)
        t['src'] = src if src else df
        a.append(t)
    if not f:
        s.close()
    return {'page':page, 'arr':a, 'total': n, 'next': next_}

def city_zhenghun(uid=None, page=None, limit=None, next_=None):
    if not uid:
        return {'page':page, 'arr':[], 'total': 0, 'next': next_}
    s = DBSession()
    u = s.query(User).filter(User.id == uid).first()
    if not u:
        s.close()
        return {'page':page, 'arr':[], 'total': 0, 'next': next_}
    loc1 = u.curr_loc1
    loc2 = u.curr_loc2

    r = list_zhenghun(sex=None, loc1=loc1, loc2=loc2, page=page, limit=limit, next_=next_, s=s)
    s.close()
    return r

def detail_zhenghun(zid=None, s=None):
    if not zid:
        return {'code': -1, 'msg': '参数不正确'}
    f = s
    if not f:
        s = DBSession()
    r = s.query(Zhenghun).filter(Zhenghun.id == zid).first()
    if not r:
        if not f:
            s.close()
        return {'code': -1, 'msg': '参数不正确'}
    uid = r.userid
    ru = s.query(User).filter(User.id == uid).first()
    if not ru:
        if not f:
            s.close()
        return {'code': -1, 'msg': '参数不正确'}
    rp = s.query(Picture).filter(Picture.id == uid).first()
    p_u = {}
    if rp:
        p_u[rp.id] = rp.dic_array()
    D = {}
    D['nick_name'] = ru.nick_name if ru.nick_name else '新用户%s' % ru.mobile[-4:]
    D['sex'] = ru.sex
    D['sex_name'] = '男' if ru.sex == 1 else '女'
    D['age'] = ru.age
    D['loc1'] = r.loc1 if r.loc1 else ru.curr_loc1
    D['loc2'] = r.loc2 if r.loc2 else ru.curr_loc2
    D['height'] = ru.height
    D['degree'] = ru.degree
    if r.content:
        cnt = r.content
    else:
        cnt = rs.content if rs.content else rs.motto
    D['content'] =  cnt
    D['scan_count'] = r.scan_count + 1
    r.scan_count = r.scan_count + 1
    D['time'] = str(r.time_).replace('-', '/')
    D['valid_day'] = r.valid_day
    D['title'] = r.title
    D['object'] = r.object1
    D['object_name'] = '征GG' if r.object1 == 0 else '征MM'
    s.commit()

    if not f:
        s.close()
    return D


__all__=['verify_mobile', 'find_password', 'get_ctx_info_mobile_password',
         'user_regist', 'query_user', 'query_user_login', 'get_user_info',
         'update_basic','get_ctx_info', 'edit_statement', 'edit_other',
         'verify_wx_qq_email', 'isee', 'seeme', 'icare', 'list_dating',
         'public_conn','query_new', 'find_users', 'sponsor_dating',
         'participate_dating', 'create_dating', 'remove_dating',
         'detail_dating', 'baoming_dating', 'list_zhenghun', 'write_img',
         'create_zhenghun', 'remove_zhenghun', 'sponsor_zhenghun',
         'city_zhenghun', 'detail_zhenghun',
         'delimg', 'seeother', 'sendemail', 'yanyuan', 'yanyuan_check',
         'email', 'latest_conn', 'sawother', 'del_email']


if __name__ == '__main__':
    r = detail_zhenghun(1)
    print(r)
'''
    r = create_dating(name='123', uid=19, age=18, sex=1, sjt=6, dt='2018-04-06 18:30:00',\
        loc1='四川', loc2='成都', locd='郭家桥西街', obj=2, num=1, fee=0, bc='',\
        valid_time=1)
'''
