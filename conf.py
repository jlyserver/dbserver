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

        self.digest_salt     = p.get('digest', 'digest_salt')

        self.table_user      = p.get('table', 'table_user')
        self.table_statement = p.get('table', 'table_statement')
        self.table_otherinfo = p.get('table', 'table_otherinfo')
        self.table_picture   = p.get('table', 'table_picture')
        self.table_hobby     = p.get('table', 'table_hobby')
        self.table_email     = p.get('table', 'table_email')
        self.table_consume_record = p.get('table', 'table_consume_record')
        self.table_add_record     = p.get('table', 'table_add_record')
        self.table_user_account = p.get('table', 'table_user_account')
        self.table_look         = p.get('table', 'table_look')
        self.table_care         = p.get('table', 'table_care')
    def dis(self):
        print(self.port)

conf    = Picconf('./conf.txt')

if __name__ == "__main__":
    conf.dis()
