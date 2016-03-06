"""
This is a tool to read a wordlist text file, clean up and
store it in a sqlite file.
"""
import re
import sys
import sqlite3
import os.path


def cleanup_wordlist(wlist):
    lowered_list = [w.lower() for w in wlist]
    ret_list = []
    for w_item in lowered_list:
        cleaned_item = re.sub('[^a-z0-9.]', '', w_item)

        # make a suitable list for executemany
        # only unique words are allowed
        if (cleaned_item,) not in ret_list:
            ret_list.append((cleaned_item,))

    return ret_list

if len(sys.argv) == 3 and os.path.isfile(sys.argv[1]):
    words_file = open(sys.argv[1], 'r')
    words_list = words_file.readlines()

    conn = sqlite3.connect('{0}/words.db'.format(sys.argv[2]))
    try:
        conn.execute("DROP TABLE IF EXISTS wordlist;")
        conn.execute('''CREATE TABLE wordlist
                       (WORD TEXT PRIMARY KEY   NOT NULL,
                        URL TEXT,
                        TIME_STAMP NUMBER
                       );
        ''')
        conn.executemany("INSERT INTO wordlist ('WORD') VALUES (?)",
                         cleanup_wordlist(words_list))
        conn.commit()

    except sqlite3.OperationalError as err:
        print (err.message)

    conn.close()
    print ("Finished!")
else:
    print ("""
    Syntax : {0} <input_wordlist_text_file> <output_path_for_sqlite_file>

    Example: {0} wordlist.txt /opt/test_app/dbase/
    """.format(sys.argv[0]))
