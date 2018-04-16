import os
import hello as flaskr
import unittest
import tempfile
import pdb
import json

from bs4 import BeautifulSoup

'''
0  test_get_homepage(self):
20 test_post_message(self): 
20 test_delete_message(self):
15 test_page(self):
20 test_sort(self):
15 test_filter(self):
10 test_filter_then_page(self):
'''


class FlaskrTestCase(unittest.TestCase):

    def setUp(self):
        flaskr.app.testing = True
        self.app = flaskr.app.test_client()

    def tearDown(self):
        pass

    def check_html(self, html, messages):
        soup = BeautifulSoup(html, 'html.parser')
        mlist = soup.find('ol', attrs={'id':"messageList"})
        assert mlist

        mtags = mlist.find_all('li', attrs={'class':'message'})
        assert len(mtags) >= len(messages)
        for mtag, message in zip(mtags, messages):
            assert message[0] in mtag.find('div', attrs={'class':'content'}).text
            assert message[1] in mtag.find('div', attrs={'class':'content'}).text
            assert message[3] in mtag.find('div', attrs={'class':'rightbottom'}).text

    def test_get_homepage(self):
        #http://flask.pocoo.org/docs/0.12/api/#response-objects
        flaskr.messages = [["rilak", "gg", 1, "0"], ['rilak2', 'wanna sleep', 0, 'no']]
        rv = self.app.get('/', follow_redirects=True)
        assert rv.status_code == 200

        html = rv.data.decode('utf8')
        self.check_html(html, flaskr.messages)

    def test_post_message(self):
        flaskr.messages = [["rilak", "gg", 1, "0"], ['rilak2', 'wanna sleep', 0, 'no']]
        rv = self.app.post('/add', data=dict(
            from_user   = "mocha",
            new_message = "go to work!"
        ), follow_redirects=True)

        data = rv.data.decode('utf8')
        soup = BeautifulSoup(data, 'html.parser')

        mtext = soup.find('div', attrs={'class':'content'}).text
        assert 'mocha' in mtext
        assert 'go to work!' in mtext

        for i in range(10):
            rv = self.app.post('/add', data=dict(
                from_user   = "temp",
                new_message = "temp"
            ), follow_redirects=True)

        ids = [m[2] for m in flaskr.messages]
        assert len(ids) == len(set(ids))

    def test_delete_message(self):
        flaskr.messages = []

        rv = self.app.post('/add', data=dict(
            from_user   = "mocha",
            new_message = "go to work!"
        ), follow_redirects=True)

        rv = self.app.post('/add', data=dict(
            from_user   = "rilak",
            new_message = "I forget the deadline...."
        ), follow_redirects=True)
        html = rv.data.decode('utf8')
        soup = BeautifulSoup(html, 'html.parser')
        a_tag = soup.find('a', attrs={'class':'close'})
        href = a_tag.get('href', '')
        mid = href[href.find('(')+1:href.find(')')]
        if mid.isdigit():
            mid = int(mid)
        #the first message
        
        d = {'index':mid}
        rv = self.app.delete('/delete', data=json.dumps(d))
        assert rv.status_code == 200

        rv = self.app.get('/')
        html = rv.data.decode('utf8')
        assert 'rilak' not in html

    def test_page(self):
        flaskr.messages = [[str(i), str(i), i, "0"] for i in range(13, 0, -1)]
        rv = self.app.get('/?page=0', follow_redirects=False)
        assert rv.status_code == 302
        assert 'page=1' in rv.headers['location']

        rv = self.app.get('/?page=-42', follow_redirects=False)
        assert rv.status_code == 302
        assert 'page=1' in rv.headers['location']

        rv = self.app.get('/?page=TEST!', follow_redirects=False)
        assert rv.status_code == 302
        assert 'page=1' in rv.headers['location']

        rv = self.app.get('/?page=42', follow_redirects=False)
        assert rv.status_code == 302
        assert 'page=3' in rv.headers['location']

        rv = self.app.get('/?page=2', follow_redirects=True)
        html = rv.data.decode('utf8')
        self.check_html(html, flaskr.messages[5:10])

        rv = self.app.get('/?page=3', follow_redirects=True)  
        html = rv.data.decode('utf8')
        self.check_html(html, flaskr.messages[10:])

    def test_sort(self):
        rilak   = ['2rilak', '3', 1, '1']
        hortune = ['1hortune', '22', 1, '3']
        mocha   = ['3mocha', '111', 1, '2']
        flaskr.messages = [ rilak, hortune, mocha ]

        rv = self.app.get('/?sort=user', follow_redirects=True)
        assert rv.status_code == 200
        html = rv.data.decode('utf8')
        self.check_html(html, [ hortune, rilak, mocha ])

        rv = self.app.get('/?sort=r_user', follow_redirects=True)
        assert rv.status_code == 200
        html = rv.data.decode('utf8')
        self.check_html(html, [ mocha, rilak, hortune ])

        rv = self.app.get('/?sort=r_len', follow_redirects=True)
        assert rv.status_code == 200
        html = rv.data.decode('utf8')
        self.check_html(html, [ mocha, hortune, rilak ])

        rv = self.app.get('/?sort=len', follow_redirects=True)
        assert rv.status_code == 200
        html = rv.data.decode('utf8')
        self.check_html(html, [ rilak, hortune, mocha ])

        rv = self.app.get('/?sort=time', follow_redirects=True)
        assert rv.status_code == 200
        html = rv.data.decode('utf8')
        self.check_html(html, [ rilak, mocha, hortune ])

        rv = self.app.get('/?sort=r_time', follow_redirects=True)
        assert rv.status_code == 200
        html = rv.data.decode('utf8')
        self.check_html(html, [ hortune, mocha, rilak ])

    def test_filter(self):
        rilak1  = ['卍 rilak 卍', 'GG', 1, '1']
        rilak2  = ['hortune', '乂 rilak 乂', 2, '2']
        hortune = ['hortune', 'hortune', 3, '3']
        null    = ['', '', '', '']
        flaskr.messages = [rilak1, rilak2, hortune, rilak2, rilak1]

        rv = self.app.get('/?filter=rilak', follow_redirects=True)
        assert rv.status_code == 200
        html = rv.data.decode('utf8')
        assert html.count('rilak') == 4
        assert html.count('GG') == 2
        assert html.count('hortune') == 2
       
        rv = self.app.get('/?filter=hortune', follow_redirects=True)
        assert rv.status_code == 200
        html = rv.data.decode('utf8')
        assert html.count('卍 rilak 卍') == 0
        assert html.count('乂 rilak 乂') == 2
        assert html.count('hortune') == 4

        rv = self.app.get('/?filter=hortune乂', follow_redirects=True)
        assert rv.status_code == 200
        html = rv.data.decode('utf8')
        assert html.count('卍 rilak 卍') == 0
        assert html.count('乂 rilak 乂') == 0
        assert html.count('hortune') == 0

        rv = self.app.get('/?filter=卍GG', follow_redirects=True)
        assert rv.status_code == 200
        html = rv.data.decode('utf8')
        assert html.count('卍 rilak 卍') == 0
        assert html.count('乂 rilak 乂') == 0
        assert html.count('hortune') == 0

    def test_filter_then_page(self):
        rilak_m1 = ['rilak', 'hey', 1, '0']
        rilak_m2 = ['hortune', 'rilak87', 1, '0']
        mocha_m  = ['mocha', 'mocha', 1, '0']

        flaskr.messages = [ rilak_m1, rilak_m2, mocha_m, rilak_m1, rilak_m1, rilak_m2, mocha_m]

        rv = self.app.get('/?filter=mocha&page=2&sort=', follow_redirects=False)
        assert rv.status_code == 302
        assert 'page=1' in rv.headers['location']

        rv = self.app.get('/?filter=rilak&page=1&sort=', follow_redirects=False)
        assert rv.status_code == 200
        html = rv.data.decode('utf8')
        self.check_html(html, [ rilak_m1, rilak_m2, rilak_m1, rilak_m1, rilak_m2])


if __name__ == '__main__':
    unittest.main()