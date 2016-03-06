import time

from flask import render_template, request, redirect
from sqlite3 import connect
from . import app, _settings


@app.route('/', methods=['POST', 'GET'])
def index():

    if request.method == 'POST':
        if request.form['long_url']:
            assigned_word = assign_word_to_url(request.form['long_url'])
            if assigned_word:
                return render_template('short_url.html',
                                       short_url=assigned_word,
                                       url_root = _settings.SERVER_NAME)
            else:
                return render_template('error_page.html',
                                       error_message=2)

    return render_template('index.html')


@app.route('/<path:path>')
def redirect_short_url(path):
    original_url = get_original_url(path)
    if original_url:
        return redirect(original_url)

    return render_template('error_page.html', error_message=1)


def get_unused_word(original_url):
    conn = connect(_settings.WORDS_DATABASE)
    cursor = conn.execute("""SELECT WORD FROM wordlist
                               WHERE URL='{0}'
                               """.format(original_url))
    for row in cursor:
        return row[0]

    # if this url is registered before,
    #  then we use same word and just update time_stamp
    cursor = conn.execute("""SELECT WORD FROM wordlist
                                WHERE instr('{0}',WORD)>0 and
                                TIME_STAMP is NULL LIMIT 1;
                                """.format(original_url))

    # if it finds any word then returns
    for row in cursor:
        return row[0]

    # if did not find word then goes for finding an unused word
    cursor = conn.execute("""SELECT WORD FROM wordlist
                                WHERE TIME_STAMP is NULL LIMIT 1;
                                """.format(original_url))
    for row in cursor:
        return row[0]

    # if there is not any unused word then find the eldest one
    cursor = conn.execute("""SELECT WORD FROM wordlist
                                ORDER BY TIME_STAMP LIMIT 1;
                                """.format(original_url))
    for row in cursor:
        return row[0]

    # happens in a case when database is empty!
    return None


def assign_word_to_url(original_url):
    conn = connect(_settings.WORDS_DATABASE)
    try:
        time_stamp = time.time()
        url_word = get_unused_word(original_url)
        conn.execute("""UPDATE wordlist SET
                            URL='{0}',
                            TIME_STAMP={1}
                            WHERE WORD='{2}'
                         """.format(original_url,
                                    time_stamp,
                                    url_word))

        conn.commit()
        conn.close()
        return url_word
    except Exception as err:
        return None


def get_original_url(short_url_word):
    conn = connect(_settings.WORDS_DATABASE)
    try:
        cursor = conn.execute("""SELECT URL FROM wordlist
                                    WHERE WORD='{0}';
                               """.format(short_url_word))
        original_url = cursor.fetchone()[0]
        conn.close()
        if original_url:
            return original_url
        else:
            return None
    except Exception:
        return None
