============================
PyCon Taiwan 2017 猜謎機器人
============================

詳細規劃見 `spec.rst`。


專案設定
=============

需求
---------

* Python 3.6+
* PostgreSQL 9.3+


建立需要檔案
------------

註：專案根目錄即本檔案所在目錄。

1. 取得題目檔 ``sources.zip`` 與註冊資料 ``tickets.zip``，放在專案根目錄內（不需解壓縮）。

2. 在根目錄建立 ``.env`` 檔案，用來指定專案環境變數。檔案格式類似一般用來 source 的 Bash 檔，使用 `python-dotenv`_ 管理，參見文檔了解可用格式。

3. 在 ``.env`` 檔案中寫入需要的環境變數：
    * ``DATABASE_URL`` 指定資料庫路徑。資料庫路徑資訊由 `dj-database-url`_ 管理，參見文檔了解可用參數。
    * ``DJANGO_SECRET_KEY`` 指定 Django 需要的 secret key。
    * ``DJANGO_SETTINGS_MODULE`` 指定 Django 的設定檔路徑。本地端應設定成 ``webapi.fbbot.settings.local``。
    * ``FACEBOOK_ACCESS_TOKEN`` 與 ``FACEBOOK_VERIFY_TOKEN`` 指定 Facebook Messenger bot 需要的認證資訊。
    * ``LINE_ACCESS_TOKEN`` 與 ``LINE_CHANNEL_SECRET`` 指定 LINE bot 需要的認證資訊。

.. _`python-dotenv`: https://github.com/theskumar/python-dotenv
.. _`dj-database-url`: https://github.com/kennethreitz/dj-database-url


設定開發環境
------------

開發環境用 pipenv_ 管理。先在系統安裝 pipenv 後，在 project root 執行以下指令，安裝專案所需 dependencies（包含開發用工具）::

    pipenv install --dev

.. _pipenv: http://docs.pipenv.org


常用指令
=========

若需用 pipenv 管理的 virtualenv 執行指令，直接在原本的指令前面加上 ``pipenv run`` 即可。例如下面的指令可進入專案 virtualenv 的 Python interactive shell::

    pipenv run python

為精簡起見，以下的指令一律省略 ``pipenv run`` 前綴。

資料庫 schema 同步::

    python -m quizzler.migrations


本地檢視 RestructuredText 文件::

    restview 文件路徑


執行 dev web server::

    python webapi/manage.py runserver
