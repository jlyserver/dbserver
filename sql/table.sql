/*用户基本表*/
create table if not exists user
(
    id int unsigned primary key auto_increment,
    nick_name varchar(16),
    password  varchar(32) not null,
    mobile    varchar(16),
    sex tinyint default 0, /*0=unknown 1=male  2=female */
    aim tinyint default 0, /*0=未填 1=交友 2=征婚 3=聊天*/
    age int unsigned default 0,             /*年龄*/
    marriage tinyint default 0,/*0=未填 1=单身 2=离异 3=丧偶 */
    xingzuo  tinyint default 0, /*0=未填 1~12依次顺排星座*/
    shengxiao tinyint default 0, /*0=未填1~12依次顺排生肖*/
    blood tinyint default 0, /*0=未填 1=A 2=B 3=AB 4=O */
    salary tinyint default 0, /*月薪 0=未填 1=2000以下 2=2000~5000 3=5000~10000 4=10000~20000 5=20000~50000 6=50000以上*/
    weight int unsigned default 0, /*体重, 单位: kg*/
    height int unsigned default 0, /*身高, 单位: cm*/
    degree int default 0, /*0=保密 1=高中及以下 2=中专/大专 3=本科 4=研究生 5=博士及博士后 */
    nation tinyint default 0, /*民族 0=未填 1~56百度民族顺序*/
    curr_loc1 varchar(8) default '', /*现在所在省(直辖市)*/
    curr_loc2 varchar(8) default '', /*现在所在市(区)*/
    ori_loc1  varchar(8) default '', /*籍贯所在省(直辖市)*/
    ori_loc2  varchar(8) default '', /*籍贯所在市(区)*/
    state tinyint default 0, /*征友状态 0=征友进行中 1=找到意中人*/
    regist_time timestamp default CURRENT_TIMESTAMP not null,
    last_login  timestamp,
    valid_state tinyint not null default 0, /*状态 0=合法 1=被禁止*/
    msg varchar(32) default '' /*被禁止的原因*/
) engine=InnoDB, charset=utf8;

/*座右铭和内心独白表*/
create table if not exists statement
(
    id int unsigned primary key,
    motto varchar(128) default '',  /*座右铭*/
    content varchar(1024) default ''/*内心独白*/
) engine=InnoDB, charset=utf8;

create table if not exists otherinfo
(
    id int unsigned primary key,
    salary tinyint default 0, /*月薪 0=未填 1=2000以下 2=2000~5000 3=5000~10000 4=10000~20000 5=20000~50000 6=50000以上*/
    work tinyint default 0, /*0=未填 1=学生 2=老师 3=工程师 4=商务人士 5=个体老板 6=白领人士 7=其他*/
    house tinyint default 0, /*0=未填 1=已购 2=未购 3=需要时购*/
    car tinyint default 0, /*0=未填 1=已购 2=未购 3=需要时购*/
    mobile varchar(16) default '', /*电话*/
    verify_m tinyint default 0, /*0=未验证 1=已验证*/
    public_m tinyint default 0, /*0=公开 1=未公开*/
    fee_m    int unsigned default 1, /*查看手机需要多少豆*/

    email varchar(64) default '', /*邮箱*/
    verify_e tinyint default 0, /*0=未验证 1=已验证*/
    public_e tinyint default 0, /*0=公开 1=未公开*/
    fee_e    int unsigned default 1, /*查看email需要多少豆*/

    wx varchar(32) default '', /*微信*/
    verify_w tinyint default 0, /*0=未验证 1=已验证*/
    public_w tinyint default 0, /*0=公开 1=未公开*/
    fee_w    int unsigned default 1, /*查看微信需要多少豆*/
    
    qq varchar(16) default '', /*qq*/
    verify_q tinyint default 0, /*0=未验证 1=已验证*/
    public_q tinyint default 0, /*0=公开 1=未公开*/
    fee_q    int unsigned default 1, /*查看qq需要多少豆*/
    fee_sendemail int unsigned default 1 /*发邮件需要多少豆*/
) engine=InnoDB, charset=utf8;

/*用户的图片表*/
create table if not exists picture
(
    id int unsigned primary key,
    count smallint default 9, /*还能上传多少张图片*/  
    url0 varchar(64) default '', /*头像图片*/
    url1 varchar(64) default '',
    url2 varchar(64) default '',
    url3 varchar(64) default '',
    url4 varchar(64) default '',
    url5 varchar(64) default '',
    url6 varchar(64) default '',
    url7 varchar(64) default '',
    url8 varchar(64) default '',
    url9 varchar(64) default '' 
) engine=InnoDB, charset=utf8;

create table if not exists deprecated_picture
(
  id int unsigned primary key auto_increment,
  src varchar(64) default ''
) engine=InnoDB, charset=utf8;

/*兴趣爱好*/
create table if not exists hobby
(
    id int unsigned primary key, /*用户的id*/
    pashan   tinyint default 0, /*爬山 0=喜欢 1=不喜欢*/
    sheying  tinyint default 0, /*摄影 0=喜欢 1=不喜欢*/
    yinyue   tinyint default 0, /*音乐 0=喜欢 1=不喜欢*/
    dianying tinyint default 0, /*电影 0=喜欢 1=不喜欢*/
    lvyou    tinyint default 0, /*旅游 0=喜欢 1=不喜欢*/
    youxi    tinyint default 0, /*游戏 0=喜欢 1=不喜欢*/
    jianshen tinyint default 0, /*健身 0=喜欢 1=不喜欢*/
    meishi   tinyint default 0, /*美食 0=喜欢 1=不喜欢*/
    paobu    tinyint default 0, /*跑步 0=喜欢 1=不喜欢*/
    guangjie tinyint default 0, /*逛街 0=喜欢 1=不喜欢*/
    changge  tinyint default 0, /*唱歌 0=喜欢 1=不喜欢*/
    tiaowu   tinyint default 0, /*跳舞 0=喜欢 1=不喜欢*/
    puke     tinyint default 0, /*扑克 0=喜欢 1=不喜欢*/
    majiang  tinyint default 0, /*麻将 0=喜欢 1=不喜欢*/
    wanggou  tinyint default 0, /*网购 0=喜欢 1=不喜欢*/
    kanshu   tinyint default 0  /*看书 0=喜欢 1=不喜欢*/
) engine=InnoDB, charset=utf8;

/*发送email*/
create table if not exists email
(
    id int unsigned primary key auto_increment,
    from_id int unsigned not null,
    to_id   int unsigned not null,
    content varchar(512),
    kind     tinyint unsigned default 0, /** =0邮件消息 =1眼缘消息 =关注消息**/   
    from_del tinyint unsigned default 0, /** =1 发送方已删除 **/
    to_del   tinyint unsigned default 0, /** =1 接收方已删除 **/
    read_    tinyint unsigned default 0, /** =0 未读 =1已读  **/
    time_ timestamp default CURRENT_TIMESTAMP
) engine=InnoDB, charset=utf8;

/*发送yanyuan*/
create table if not exists yanyuan
(
    id int unsigned primary key auto_increment,
    from_id int unsigned not null,
    to_id   int unsigned not null,
    time_ timestamp default CURRENT_TIMESTAMP
) engine=InnoDB, charset=utf8;

/*用户消费记录*/
create table if not exists consume_record
(
    id int unsigned primary key auto_increment,
    userid int unsigned not null,
    objid  int unsigned not null, /*userid 帖子id 或邮件id or user id*/
    way tinyint unsigned not null,/*1=发送眼缘 2=发信 3=约会帖 4=征婚帖 
                                    5=查看手机 6=查看微信 7=查看QQ 8=查看邮箱号*/
    num int unsigned not null, /*发生个数 1个=0.1元*/
    time_ timestamp default CURRENT_TIMESTAMP
) engine=InnoDB, charset=utf8;

/*充值记录*/
create table if not exists add_record
(
    id int unsigned primary key auto_increment,
    userid int unsigned not null,  /*用户id*/
    way tinyint unsigned not null, /*0=微信支付 1=支付宝*/
    num int unsigned not null, /*发生个数 1个=0.1元*/
    time_ timestamp default CURRENT_TIMESTAMP
) engine=InnoDB, charset=utf8;

/*用户的账户余额*/
create table if not exists user_account
(
    id int unsigned primary key, /*用户id*/
    num    int unsigned not null,/*余额总计 单位个 1个=0.1元*/
    free   int unsigned default 0 /*每日免费个数 单位个  1个=0.1元*/
) engine=InnoDB, charset=utf8;

/*我看过谁 谁看过我*/
create table if not exists look
(
    id int unsigned primary key auto_increment,
    from_id int unsigned not null,  /*主动看的用户id*/
    to_id   int unsigned not null,  /*被动看的用户id*/
    time_ timestamp default CURRENT_TIMESTAMP
) engine=InnoDB, charset=utf8;

/*我关注的*/
create table if not exists care
(
    id int unsigned primary key auto_increment,
    from_id int unsigned not null,  /*主动关注的用户id*/
    to_id   int unsigned not null,  /*被动关注的用户id*/
    time_ timestamp default CURRENT_TIMESTAMP
) engine=InnoDB, charset=utf8;

/*约会帖子*/
create table if not exists dating
(
    id int unsigned primary key auto_increment,
    userid  int unsigned not null,  /*发起人id*/
    nick_name varchar(16),          /*发起人昵称*/
    age  tinyint unsigned not null, /*发起人年龄*/
    sex  tinyint unsigned not null, /*发起人性别 0=女 1=男*/
    subject tinyint unsigned not null, /* 0=约饭 1=电影 2=交友 3=聊天
                                      4=喝酒 5=唱歌 6=其他*/
    dtime timestamp not null,      /*约会时间*/
    loc1  varchar(8) not null,     /*约会地点 省(直辖市)*/
    loc2  varchar(8) not null,     /*约会地点 市(区) */
    loc_detail varchar(64),        /*约会详细地点*/
    object1 tinyint unsigned not null, /*0=男士 1=女士 2=男女均可*/
    numbers int unsigned not null, /*约会人数*/
    fee tinyint unsigned not null, /*0=发起人付 1=AA 2=男士付款,女士免单 3=视情况而定*/
    buchong varchar(160),  /*约会补充*/
    valid_time tinyint unsigned not null, /*报名有效期限 单位天*/
    time_ timestamp default CURRENT_TIMESTAMP,
    scan_count int unsigned not null default 0, /*帖子浏览次数*/
    valid_state tinyint not null default 0, /*0=帖子有效 1=被禁止 2=被删除*/
    msg varchar(32) /*被禁止的原因*/
) engine=InnoDB, charset=utf8;

/*约会报名表*/
create table if not exists yh_baoming
(
    id int unsigned primary key auto_increment,
    dating_id  int unsigned not null,  /*帖子id*/
    userid int unsigned not null,  /*报名人id*/
    time_ timestamp default CURRENT_TIMESTAMP
) engine=InnoDB, charset=utf8;


/*征婚帖子*/
create table if not exists zhenghun
(
    id int unsigned primary key auto_increment,
    userid  int unsigned not null,  /*发起人id*/
    nick_name varchar(16),          /*发起人昵称*/
    age  tinyint unsigned not null, /*发起人年龄*/
    sex  tinyint unsigned not null, /*发起人性别 0=女 1=男*/
    loc1  varchar(8) not null,     /*征婚地点 省(直辖市)*/
    loc2  varchar(8) not null,     /*征婚地点 市(区) */
    time_ timestamp default CURRENT_TIMESTAMP, /*发帖时间*/
    valid_day int unsigned not null, /*报名有效期限 单位天 <= 365 */
    title varchar(64), /*帖子标题*/
    content varchar(800), /*帖子内容*/
    object1 tinyint not null, /*=0征GG =1征MM*/
    scan_count int unsigned default 0, /*浏览次数*/
    valid_state tinyint not null default 0, /*0=帖子有效 1=被禁止 2=用户删除*/
    msg varchar(32) /*被禁止的原因*/
) engine=InnoDB, charset=utf8;
