#-*- coding: utf-8 -*-
import ConfigParser

class Picconf():
    def __init__(self, name):
        p = ConfigParser.ConfigParser()
        p.read(name)
        self.sys_ip      = p.get('sys', 'sys_ip')
        self.sys_port    = p.getint('sys', 'sys_port')

        self.redis_ip       = p.get('redis', 'redis_ip')
        self.redis_port     = p.getint('redis', 'redis_port')
        self.redis_db       = p.getint('redis', 'redis_db')
        self.redis_password = p.get('redis', 'redis_password')
        self.redis_timeout  = p.getint('redis', 'redis_timeout')

        self.mysql_user      = p.get('mysql', 'mysql_user')
        self.mysql_password  = p.get('mysql', 'mysql_password')
        self.mysql_host      = p.get('mysql', 'mysql_host')
        self.mysql_port      = p.getint('mysql', 'mysql_port')
        self.mysql_db        = p.get('mysql', 'mysql_db')
        self.mysql_encode    = p.get('mysql', 'mysql_encode')

        self.toffset_newest  = p.getint('toffset', 'newest')
        self.toffset_count   = p.getint('toffset', 'count')
        self.toffset_new_male= p.getint('toffset', 'new_male')
        self.toffset_new_female = p.getint('toffset', 'new_female')
        self.toffset_isee_limit = p.getint('toffset', 'isee_limit')
        self.toffset_seeme_limit= p.getint('toffset', 'seeme_limit')
        self.toffset_icare_limit= p.getint('toffset', 'icare_limit')
        self.toffset_dating_page= p.getint('toffset', 'dating_page')
        self.toffset_dating_limit = p.getint('toffset', 'dating_limit')
        self.toffset_freq_conn  = p.getint('toffset', 'freq_conn')
        self.toffset_zhenghun_page = p.getint('toffset', 'zhenghun_page')
        self.toffset_zhenghun_limit= p.getint('toffset', 'zhenghun_limit')
        self.toffset_look_limit  = p.getint('toffset', 'look_limit')

        self.page            = p.getint('find', 'page')
        self.limit           = p.getint('find', 'limit')

        self.digest_salt     = p.get('digest', 'digest_salt')

        self.table_user      = p.get('table', 'table_user')
        self.table_statement = p.get('table', 'table_statement')
        self.table_otherinfo = p.get('table', 'table_otherinfo')
        self.table_picture   = p.get('table', 'table_picture')
        self.table_hobby     = p.get('table', 'table_hobby')
        self.table_email     = p.get('table', 'table_email')
        self.table_yanyuan   = p.get('table', 'table_yanyuan')
        self.table_consume_record = p.get('table', 'table_consume_record')
        self.table_add_record     = p.get('table', 'table_add_record')
        self.table_user_account = p.get('table', 'table_user_account')
        self.table_look         = p.get('table', 'table_look')
        self.table_care         = p.get('table', 'table_care')
        self.table_dating       = p.get('table', 'table_dating')
        self.table_yh_baoming   = p.get('table', 'table_yh_baoming')
        self.table_zhenghun     = p.get('table', 'table_zhenghun')

        self.pic_ip             = p.get('pic', 'pic_ip')
        self.postfix            = p.get('pic', 'postfix')

        self.mobile_fee         = p.getint('fee', 'mobile_fee')
        self.wx_fee             = p.getint('fee', 'wx_fee')
        self.qq_fee             = p.getint('fee', 'qq_fee')
        self.email_fee          = p.getint('fee', 'email_fee')
        self.send_email_fee     = p.getint('fee', 'send_email_fee')
        self.yanyuan_fee        = p.getint('fee', 'yanyuan_fee')
        self.yuehui_fee         = p.getint('fee', 'yuehui_fee')
        self.zhenghun_fee       = p.getint('fee', 'zhenghun_fee')
        self.timeout_fee        = p.getint('fee', 'timeout_fee')
        self.free_bean          = p.getint('fee', 'free_bean')

        self.dating_fee_1       = p.getint('fee', 'dating_fee_1')
        self.dating_fee_2       = p.getint('fee', 'dating_fee_2')
        self.dating_fee_3       = p.getint('fee', 'dating_fee_3')
        self.dating_fee_4       = p.getint('fee', 'dating_fee_4')
        self.dating_fee_5       = p.getint('fee', 'dating_fee_5')
        self.dating_fee_6       = p.getint('fee', 'dating_fee_6')
        self.dating_fee_7       = p.getint('fee', 'dating_fee_7')

        self.zhenghun_fee_1     = p.getint('fee', 'zhenghun_fee_1')
        self.zhenghun_fee_2     = p.getint('fee', 'zhenghun_fee_2')
        self.zhenghun_fee_3     = p.getint('fee', 'zhenghun_fee_3')
        self.zhenghun_fee_4     = p.getint('fee', 'zhenghun_fee_4')



        self.msg_yanyuan        = p.get('msg', 'msg_yanyuan')
        self.yanyuan_reject     = p.get('msg', 'yanyuan_reject')
        self.yanyuan_accept     = p.get('msg', 'yanyuan_accept')

        self.debug              = p.getint('debug', 'debug')
    def dis(self):
        print(self.port)

conf    = Picconf('./conf.txt')

if __name__ == "__main__":
    conf.dis()
