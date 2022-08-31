from flask import render_template, request, redirect, url_for, flash, abort, session, jsonify, Blueprint
import json
import os.path
from .db_conn import MongoDBConnection
from werkzeug.utils import secure_filename

bp = Blueprint('urlshort', __name__)
mongo = MongoDBConnection()

@bp.route('/')
def home():
    return render_template('home.html', codes=session.keys())


@bp.route('/your-url', methods=['GET', 'POST'])
def your_url():
    if request.method == 'POST':
        with mongo:
            collection = mongo.connection.urlshortener.urlshorts
            if collection.find_one({"shortname": request.form['code']}):
                flash(
                    'That short name has already been taken. Please select another name.')
                return redirect(url_for('urlshort.home'))
            else:
                if 'url' in request.form.keys():
                    url = {
                        "shortname": request.form['code'],
                        "url": request.form['url']
                    }
                    collection.insert_one(url)
                else:
                    # its a file
                    f = request.files['file']
                    full_name = request.form['code'] + \
                        secure_filename(f.filename)
                    f.save(
                        '/home/alex/projects/url-shortener/urlshort/static/user_files/' + full_name)
                    url = {
                        "shortname": request.form['code'],
                        "file": full_name
                    }
                    collection.insert_one(url)
                session[request.form['code']] = True

        # urls = {}
        # if os.path.exists('urls.json'):
        #     with open('urls.json') as urls_file:
        #         urls = json.load(urls_file)

        # if request.form['code'] in urls:
        #     flash('That short name has already been taken. Please select another name.')
        #     return redirect(url_for('urlshort.home'))

        # if 'url' in request.form.keys():
        #     urls[request.form['code']] = {'url': request.form['url']}
        # else:
        #     # its a file
        #     f = request.files['file']
        #     full_name = request.form['code'] + secure_filename(f.filename)
        #     f.save('/home/alex/url-shortener/urlshort/static/user_files/' + full_name)
        #     urls[request.form['code']] = {'file': full_name}

        # with open('urls.json', 'w') as url_file:
        #     json.dump(urls, url_file)
        #     session[request.form['code']] = True

        return render_template('your_url.html', code=request.form['code'])
    else:
        # redirects to homepage
        return redirect(url_for('urlshort.home'))


@bp.route('/<string:code>')
def redirect_to_url(code):
    with mongo:
        collection = mongo.connection.urlshortener.urlshorts
        link = collection.find_one({"shortname": code})
        if link:
            if 'url' in link:
                return redirect(link['url'])
            else:
                return redirect(url_for('static', filename='user_files/' +
                                        link['file']))

    # if os.path.exists('urls.json'):
    #     with open('urls.json') as urls_file:
    #         urls = json.load(urls_file)
    #         if code in urls.keys():
    #             if 'url' in urls[code].keys():
    #                 return redirect(urls[code]['url'])
    #             else:
    #                 return redirect(url_for('static', filename='user_files/' +
    #                                         urls[code]['file']))
    return abort(404)

@bp.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


@bp.route('/api')
def session_api():
    return jsonify(list(session.keys()))
