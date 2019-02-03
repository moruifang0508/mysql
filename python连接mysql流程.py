# -*- coding: utf-8 -*-
import os

#在python3中连接mysql使用PyMySQL,而在python2中使用MySQLdb
#如果PyMySQL库还没有安装，需要预先用pip安装：pip3 install PyMySQL
import pymysql


import time
import random
import pdb
import sys

conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='admin', db='mrf', charset='utf8')
cursor = conn.cursor()

# get all attributes existing in the img_labels
img_attrs = ['type', 'color']

# create 3 tables: users, user_label, img_label

# add users
user_dict = {'user1' : 'password',
             'user2' : 'password',
             'user3' : 'password',
             }
for key, value in user_dict.items():
    temp_sql = "select Id from users where username='{}';".format(key)
    cursor.execute(temp_sql)
    rows = cursor.fetchall()
    if len(rows)==0:
        temp_sql = "insert into users(username, passwd) values ('{}', '{}');".format(key, value)
        cursor.execute(temp_sql)

        #本人添加，因为对数据修改后要确定，才能修改成功
        conn.commit()

    else:
        print("User: {} has already existed. Skip this user.".format(key))


# select all existing users, then will randomly distribute the images to them
temp_sql = "select Id from users"
cursor.execute(temp_sql)
rows = cursor.fetchall()
userId = [row[0] for row in rows]

# get img_list, and initialize the distribution
img_names_file = '/home/lyc/Desktop/multi-label/train.lst'
img_list = []
for line in open(img_names_file):
    line = line.strip()
    img_list.append(line)

# add items into table img_label
imglabel_sql = "INSERT INTO img_label(image_name, data_source) VALUES"
n = 0
for line in img_list:
    n += 1
    if(n % 100 == 0):
        print('Writing {}th image:{} to database.'.format(n, line))
    line = line.split()
    #只取表示图片路径的最后一项
    line = line[-1].split('/')
    imgname = line.pop()
    data_source = '/'.join(line)
    imglabel_sql += " ('{}', '{}'),".format(imgname, data_source)
imglabel_sql = imglabel_sql[:-1] + ';'
#print("imglabel_sql : {}\n".format(imglabel_sql))
#pdb.set_trace()
try:
    effect_row = cursor.execute(imglabel_sql)
    conn.commit()
    print("successfully insert imglabel_sql, total {}itmes.".format(n))
except:
    conn.rollback()
    print('database insert exception when insert imglabel_sql')

# get the Id in img_label according to image_name and its source
userlabel_sql = "select Id from img_label"
cursor.execute(userlabel_sql)
rows = cursor.fetchall()

#pdb.set_trace()
# add items into tabel user_label
userlabel_sql = "insert into user_label(userid, imgid, attr) values"
n = 0
for row in rows:
    imgId = row[0]
    for img_attr in img_attrs:
        n += 1
        userId_random = random.choice(userId)
        userlabel_sql += " ('{:d}', '{:d}', '{}'),".format(userId_random, imgId, img_attr)
userlabel_sql = userlabel_sql[:-1] + ';'
#print("userlabel_sql : {}\n".format(userlabel_sql))
try:
    effect_row = cursor.execute(userlabel_sql)
    conn.commit()
    print("successfully insert userlabel_sql")
except:
    conn.rollback()
    print('database insert exception when insert userlabel_sql')

conn.close()
