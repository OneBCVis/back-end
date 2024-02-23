test:
	cd stream
	pwd
	pip3 install virtualenv
	pip3 install -r stream/tests/requirements.txt
	cd stream && \
		python3 -m venv venv && \
		python3 -m pytest -s tests/unit  -v -c tests/pytest.ini
