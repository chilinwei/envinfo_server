# all the imports
import os, uuid
import datastore, sendmail
from datetime import datetime
from flask import Flask, request, render_template

app = Flask(__name__) # create the application instance

# convert timestamp to datetime format
def TSConvert(_str):
    return datetime.strftime(datetime.strptime(_str,"%Y%m%d%H%M%S%f"),"%Y-%m-%d %H:%M:%S.%f")

# web api show envdata
@app.route('/')
def show_envdata():
    conn = datastore.conn()
    cur = conn.cursor()
    cur.execute('select id, uid, dt, ts, ax, ay, az, light, temp, humi, volts from env order by id desc limit 100')
    envdata = cur.fetchall()
    cur.close()
    conn.close()
    # print envdata
    return render_template('show_envdata.html', data=envdata)

# web api insert envdate
@app.route('/addenvdata/<uid>', methods=['POST'])
def add_envdata(uid):
    try:
        add_envdata = ("INSERT INTO `env` "
        "(`uid`,`dt`,`ts`,`ax`,`ay`,`az`,`light`,`temp`,`humi`,`volts`) "
        "VALUES (%(uid)s, %(dt)s, %(ts)s, %(ax)s, %(ay)s, %(az)s, %(light)s, %(temp)s, %(humi)s, %(volts)s)")

        _data = request.get_json()
        _data['uid'] = uid

        if _data.has_key('ts'):
            _ts = _data['ts']
            _data['dt'] = TSConvert(_ts)
        else:
            _data['ts'] = datetime.strftime(datetime.now(), '%Y%m%d%H%M%S%f')
            _data['dt'] = datetime.now()

        if _data.has_key('ax'):
            pass
        else:
            _data['ax'] = -999

        if _data.has_key('ay'):
            pass
        else:
            _data['ay'] = -999

        if _data.has_key('az'):
            pass
        else:
            _data['az'] = -999

        if _data.has_key('light'):
            pass
        else:
            _data['light'] = -999

        if _data.has_key('temp'):
            pass
        else:
            _data['temp'] = -999

        if _data.has_key('humi'):
            pass
        else:
            _data['humi'] = -999

        if _data.has_key('volts'):
            pass
        else:
            _data['volts'] = -999

        # print _data

        conn = datastore.conn()
        cur = conn.cursor()
        cur.execute(add_envdata, _data)
        conn.commit()
        cur.close()
        conn.close()

        return 'success'
    except Exception as e:
        print(e)
    
# web api upload photo
@app.route('/uploader/<uid>', methods = ['POST'])
def upload_file(uid):
    try:
        fn = str(uuid.uuid4().hex)+'.jpg'
        f = request.files['file']

        _add_sql = ("insert into `files` (`uid`, `dt`, `ts`, `filename`) "
        "values (%(uid)s,%(dt)s,%(ts)s,%(fn)s) ")

        _add_data = {
            'uid': uid,
            'dt': datetime.strftime(datetime.now(), '%Y-%m-%d %H:%M:%S.%f'),
            'ts': datetime.strftime(datetime.now(), '%Y%m%d%H%M%S%f'),
            'fn': fn
        }
        # print _add_data
        # save photo
        f.save(os.path.join(app.root_path,'photo',fn))
        # record file name
        conn = datastore.conn()
        cur = conn.cursor()
        cur.execute(_add_sql, _add_data)
        conn.commit()
        cur.close()
        conn.close()

        return 'success'
    except Exception as e:
        print(e)