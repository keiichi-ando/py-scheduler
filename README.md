# Python3.9 Flask in Docker

Docker template

`Apache + Python3.9 + Flask (wsgi) SPA + apscheduler`

## ref

- [Docker + Python + Flask で API サーバーを構築してみる](http://unalus.com/wp/2019/11/22/docker-python-flask%E3%81%A7api%E3%82%B5%E3%83%BC%E3%83%90%E3%83%BC%E3%82%92%E6%A7%8B%E7%AF%89%E3%81%97%E3%81%A6%E3%81%BF%E3%82%8B/)
- [Flask-Login を使用してアプリケーションに認証を追加する方法](https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login-ja)
- [Flask に SPA バックエンドを全て任せたい話 - Qiita](https://qiita.com/ytkj/items/ab67a1cee3cbfc42254d)
- [APScheduler の使い方（初心者向け）](https://programgenjin.hatenablog.com/entry/2019/04/01/093005)
- [Python で自動ジョブを実行する(APScheduler) ](https://qiita.com/svfreerider/items/32ecd91d402b05fb8b9a)
- [入門者必読、vue.js の状態管理 Vuex がわかる](https://reffect.co.jp/vue/understaind-vue-basic)

## TODO

---

## pip install

コンテナ起動後に実行

```bash
pipenv install --dev
cd src
npm install && npm run build
```

## waitress serve

```bash
# with auto reload
hupper -m serve_waitress.py

#without auto reload
python serve_waitress.py
```
