/*用户基本表*/
create table if not exists user
(
    id int unsigned primary key auto_increment,
    nick_name varchar(16) unique,
    password  varchar(16) not null,
    sex tinyint default 0, /*0=unknown 1=male  2=female */
    aim tinyint default 0, /*0=未填 1=交友 2=征婚 3=聊天*/
    age int unsigned default 0,             /*年龄*/
    marriage tinyint default 0,/*0=保密 1=单身 2=非单身 3=已婚 4=丧偶 */
    xingzuo  tinyint default 0, /*0=unknown 1~12依次顺排星座*/
    shengxiao tinyint default 0, /*0=unknown 1~12依次顺排生肖*/
    blood tinyint default 0, /*0=unknown 1=A 2=B 3=AB 4=O */
    weight int unsigned default 0, /*体重, 单位: kg*/
    height int unsigned default 0, /*身高, 单位: cm*/
    degree int default 0, /*0=保密 1=高中及以下 2=中专/大专 3=本科 4=研究生 5=博士及博士后 */
    nation varchar(6) default '未填', /*民族*/
    curr_loc1 varchar(8) default '', /*现在所在省(直辖市)*/
    curr_loc2 varchar(8) default '', /*现在所在市(区)*/
    ori_loc1  varchar(8) default '', /*籍贯所在省(直辖市)*/
    ori_loc2  varchar(8) default '', /*籍贯所在市(区)*/
    regist_time timestamp default CURRENT_TIMESTAMP not null
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

    email varchar(64) default '', /*邮箱*/
    verify_e tinyint default 0, /*0=未验证 1=已验证*/
    public_e tinyint default 0, /*0=公开 1=未公开*/

    wx varchar(32) default '', /*微信*/
    verify_w tinyint default 0, /*0=未验证 1=已验证*/
    public_w tinyint default 0, /*0=公开 1=未公开*/
    
    qq varchar(16) default '', /*qq*/
    verify_q tinyint default 0, /*0=未验证 1=已验证*/
    public_q tinyint default 0  /*0=公开 1=未公开*/
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
