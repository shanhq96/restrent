from flask import *
import rentdata
import userinfo

app = Flask(__name__)


@app.route('/')
def app_index():
    return render_template("main.html")

@app.route('/test')
def app_test():
    return render_template("test.html")


def get_return_response(data2return):
    """获取封装着返回数据的response"""
    response = make_response(data2return)
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'POST'
    response.headers['Access-Control-Allow-Headers'] = 'x-requested-with,content-type'
    return response

if __name__ == '__main__':
    app.register_blueprint(rentdata.__getblueprint__(), url_prefix='/rentdata')
    app.register_blueprint(userinfo.__getblueprint__(), url_prefix='/userinfo')
    app.run(host='0.0.0.0')
