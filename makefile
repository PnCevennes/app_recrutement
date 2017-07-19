HOST=0.0.0.0
PORT=8000
VENV=venv
WORKERS=4

superv:
	@/bin/bash -c "screen -S superv -d -m python3 supervision/supervisiond.py"

develop:
	@/bin/bash -c "source ../$(VENV)/bin/activate&&python server.py runserver -d -r -h $(HOST) -p $(PORT)"


prod:
	@/bin/bash -c "source ../$(VENV)/bin/activate&&gunicorn --daemon --pid="tizoutis.pid" --error-log ../errors.log -w $(WORKERS) -b '$(HOST):$(PORT)' -n 'tizoutis' server:app"&&echo "Serveur activé sur '$(HOST):$(PORT)'"


prod-stop:
	@kill `cat tizoutis.pid`&&echo "Terminé."


shell:
	@/bin/bash -c "source ../$(VENV)/bin/activate&&python server.py shell"
