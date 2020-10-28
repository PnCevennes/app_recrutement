HOST=0.0.0.0
PORT=8000
VENV=venv
WORKERS=2
BSH=/bin/bash -c

develop:
	@$(BSH) "pipenv run python server.py runserver -d -r -h $(HOST) -p $(PORT)"


prod:
	@$(BSH) "pipenv run gunicorn --daemon --pid="tizoutis.pid" --error-log ../errors.log -w $(WORKERS) -b '$(HOST):$(PORT)' -n 'tizoutis' wsgi:app"&&echo "Serveur activé sur '$(HOST):$(PORT)'"


prod-stop:
	@kill `cat tizoutis.pid`&&echo "Terminé."


shell:
	@$(BSH) "pipenv run python server.py shell"
