HOST=0.0.0.0
PORT=8000
VENV=venv
WORKERS=4


develop:
	@/bin/bash -c "source ../$(VENV)/bin/activate&&python server.py runserver -d -r -h $(HOST) -p $(PORT)"


prod:
	@/bin/bash -c "source ../$(VENV)/bin/activate&&gunicorn --daemon --error-log ../errors.log -w $(WORKERS) -b '$(HOST):$(PORT)' -n 'tizoutis' server:app"&&echo "Serveur activé sur '$(HOST):$(PORT)'"


prod-stop:
	@kill `ps xo'%p %a'|grep "[t]izoutis"|cut -d' ' -f2`&&echo "Terminé"


shell:
	@/bin/bash -c "source ../$(VENV)/bin/activate&&python server.py shell"
