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

1. 取得題目檔 ``sources.zip``，放在專案根目錄內（不需解壓縮）。
2. 在根目錄建立 ``.env`` 檔案，用來指定專案環境變數。檔案格式類似一般用來 source 的 Bash 檔，使用 `python-dotenv`_ 管理，參見文檔了解可用格式。
3. 在環境變數 ``DATABASE_URL`` 指定資料庫路徑。資料庫路徑資訊由 `dj-database-url`_ 管理，參見文檔了解可用參數。

.. _`python-dotenv`: https://github.com/theskumar/python-dotenv
.. _`dj-database-url`: https://github.com/kennethreitz/dj-database-url


設定開發環境
------------

開發環境用 pipenv_ 管理。先在系統安裝 pipenv 後，在 project root 執行::

    pipenv install

進入 pipenv shell（類似用 virtualenv 的 activate）::

    pipenv shell

安裝所有 dependencies（包含開發用工具）::

    pipenv install --dev

.. _pipenv: http://docs.pipenv.org


常用指令
=========

若需用 pipenv 管理的 venv 執行指令，直接在原本的指令前面加上 ``pipenv run`` 即可。或者，一旦用 ``pipenv shell`` 進入該環境的 shell 後，就可以直接正常執行，不需加上前綴。

資料庫 schema 同步::

    python -m quizzler.migrations


本地檢視 RestructuredText 文件::

    restview 文件路徑
