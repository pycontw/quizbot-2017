ALL: help

help:
	@echo 'make <command>'
	@echo ''
	@echo 'commands:'
	@echo '  sync-data    Upload data files to production.'

sync-data:
	scp ./sources.zip deploy@tw.pycon.org:~
	scp ./tickets.zip deploy@tw.pycon.org:~
	ssh deploy@tw.pycon.org sudo mv '~/sources.zip' /var/www/quizbot-2017/
	ssh deploy@tw.pycon.org sudo mv '~/tickets.zip' /var/www/quizbot-2017/
