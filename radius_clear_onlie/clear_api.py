from flask import Flask, jsonify, request, abort,render_template
from flask_httpauth import HTTPBasicAuth
import pymysql

region_codes = {
    '金华': '4013',
    '永康': '4040',
    '东阳': '4006',
    '浦江': '4005',
    '兰溪': '4005',
    '武义': 'wuyi',
    '义乌': 'yiwu3',
    '磐安': '4039',
    '嘉兴': '4002',
    '嘉兴乡镇': 'jxxz',
    '平湖': '4029',
    '海宁': '4012',
    '桐乡': '4038',
    '海盐': 'hyhezuoqu',
    '嘉善': '4034',
    '湖州': '4001',
    '湖州郊区': 'hzjq',
    '南浔': 'nxhzq',
    '长兴': 'changxing1',
    '安吉': 'anji',
    '德清': 'deqing3',
    '丽水': 'lishuihzq',
    '龙泉': 'longquan',
    '缙云': 'jinyun',
    '青田': 'qingtian',
    '遂昌': 'suichang',
    '松阳': 'songyang',
    '云和': 'yunhe',
    '庆元': 'qingyuan',
    '莲都': 'liandu',
    '景宁': 'jn001',
    '衢州': 'quzhou',
    '常山': 'chanshan',
    '江山': 'js001',
    '龙游': 'longyou',
    '开化': 'kaihua1',
    '衢江': 'qujiang',
    '柯城': 'qzkchzq',
    '宁波': 'ningbo',
    '鄞州': 'yinzhou9',
    '北仑': 'BEICANG',
    '江北': 'jiangbei2',
    '余姚': 'yuyao',
    '镇海': 'zhenhai',
    '奉化': 'fenghua3',
    '象山': 'xiangshan',
    '宁海': 'ninghai',
    '慈溪': 'cixi',
    '镇海炼化': 'zhenhailianhua',
    '绍兴': 'sxhzq',
    '新昌': 'xinchang',
    '绍兴县': 'sxx001',
    '诸暨': 'zhuji',
    '嵊州': 'shengzhougd',
    '上虞': 'sy001',
    '温州': 'wenzhou',
    '苍南': 'cn01',
    '永嘉': 'yongjia',
    '文成': 'wencheng',
    '平阳': 'pingyang',
    '泰顺': 'taishun',
    '瑞安': 'ruian001',
    '洞头': 'dongtou',
    '乐清': 'yueqing',
    '舟山': 'zsfgs',
    '普陀': 'putuo',
    '岱山': 'daishan',
    '嵊泗': 'shengsi',
    '普陀山': 'putuoshan',
    '台州': 'TZHZQ',
    '天台': 'tiantai',
    '温岭': 'wenling3',
    '黄岩': 'huangyan',
    '玉环': 'yuhuan',
    '仙居': 'xianju',
    '三门': 'sanmen',
    '临海': 'linhai001'
}
#获得一个数据库连接
def connect_to_db():
    connection = pymysql.connect(host='127.0.0.1',
                                 user='root',
                                 password='671200jyc',
                                 db='radius',
                                 port=3306,
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection
# def connect_to_db():
#     connection = pymysql.connect(host='30.254.4.10',
#                                  user='mysql',
#                                  password='Hzlsc6hHy7',
#                                  db='radius',
#                                  port=3306,
#                                  charset='utf8mb4',
#                                  cursorclass=pymysql.cursors.DictCursor)
#     return connection
#一个地区用户的计数
def get_online_users_count(region_name):
    org_code = region_codes.get(region_name)
    if not org_code:
        print(f"Invalid region name: {region_name}")
        return

    connection = connect_to_db()
    with connection.cursor() as cursor:
        sql = "SELECT COUNT(*) as count FROM ua_broadband_user_online WHERE org_code LIKE %s"
        cursor.execute(sql, (org_code,))
        result = cursor.fetchone()
    connection.close()
    return result['count']

#查看某个地区的所有在线用户
def get_users_by_region(region_name, limit=50, offset=0):
    org_code = region_codes.get(region_name)
    if not org_code:
        print(f"Invalid region name: {region_name}")
        return
    connection = connect_to_db()
    with connection.cursor() as cursor:
        sql = "SELECT login_name,bras_addr,bras_name,framed_addr,mac_name,memo,start_date,update_date,status FROM radius.ua_broadband_user_online WHERE org_code = %s LIMIT %s OFFSET %s"
        cursor.execute(sql, (org_code, limit, offset))
        users = cursor.fetchall()
    connection.close()
    return users


#清除某一个地区在线表
def delete_online_users(region_name):
    org_code = region_codes.get(region_name)
    if not org_code:
        return {"success": False, "message": f"Invalid region name: {region_name}"}
    else:
        connection = connect_to_db()
        with connection.cursor() as cursor:
            sql = "DELETE FROM ua_broadband_user_online WHERE org_code = %s"
            cursor.execute(sql, (org_code,))
            connection.commit()
        connection.close()
        return {"success": True, "message": f"已删除{region_name}地区所有用户，地区码为{org_code}"}


#删除某个用户
def delete_online_user(login_name):
    connection = connect_to_db()
    with connection.cursor() as cursor:
        sql = "DELETE FROM ua_broadband_user_online WHERE login_name = %s"
        affected_rows = cursor.execute(sql, (login_name,))
        connection.commit()
    connection.close()

    if affected_rows == 0:
        return {"success": False, "message": f"User with login_name {login_name} not found"}
    else:
        return {"success": True, "message": f"Deleted user with login_name: {login_name}"}

#确认用户是否在线
def check_user_online(login_name):
    connection = connect_to_db()
    with connection.cursor() as cursor:
        sql = "SELECT * FROM ua_broadband_user_online WHERE login_name = %s"
        cursor.execute(sql, (login_name,))
        result = cursor.fetchone()
    connection.close()
    return result is not None,result




auth = HTTPBasicAuth()

# 用户名和密码的验证函数
@auth.verify_password
def verify_password(username, password):
    # 这里您可以从数据库或其他来源验证用户名和密码
    if username == 'admin' and password == '671200jyc':
        return True
    return False

app = Flask(__name__)

@app.route('/api/online_users_count', methods=['GET'])
@auth.login_required
def api_online_users_count():
    region_name = request.args.get('region_name')
    count = get_online_users_count(region_name)
    return jsonify(count=count)

@app.route('/api/users_by_region', methods=['GET'])
@auth.login_required
def api_users_by_region():
    region_name = request.args.get('region_name')
    limit = int(request.args.get('limit', 50))
    offset = int(request.args.get('offset', 0))
    users = get_users_by_region(region_name, limit, offset)
    return jsonify(users=users)



@app.route('/api/check_user_online', methods=['GET'])
@auth.login_required
def api_check_user_online():
    login_name = request.args.get('login_name')
    is_user_online, detail = check_user_online(login_name)
    return jsonify(is_user_online=is_user_online, detail=detail)


@app.route('/user_management')
@auth.login_required
def user_management():
    return render_template('user_management.html',region_codes=region_codes)

@app.route('/user_search')
@auth.login_required
def user_search():
    return render_template('user_search.html',region_codes=region_codes)

@app.route('/api/delete_region_users', methods=['POST'])
@auth.login_required
def api_delete_online_users():
    if not auth.username() == 'admin':  # 只有 admin 用户才有权限执行删除操作
        abort(403)

    region_name = request.form.get('region_name')
    reslut = delete_online_users(region_name)

    return jsonify(reslut)


@app.route('/api/delete_online_user', methods=['POST'])
@auth.login_required
def api_delete_online_user():
    if not auth.username() == 'admin':  # 只有 admin 用户才有权限执行删除操作
        abort(403)

    login_name = request.form.get('login_name')
    result = delete_online_user(login_name)

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True)