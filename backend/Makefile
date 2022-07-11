service_name=first2know
local_image_tag=$(service_name):latest

THIS_FILE := $(lastword $(MAKEFILE_LIST))

dockerbuild:
	docker build -t $(local_image_tag) .

dockerruncron:
	docker run \
		--rm \
		--name $(service_name) \
		$(local_image_tag) \
		make runcron

dockertest:
	docker run \
		--rm \
		--name $(service_name) \
		$(local_image_tag) \
		make test

dockerrunserver:
	docker run \
		-it \
		--rm \
		-p 8000:8000 \
		--name $(service_name) \
		$(local_image_tag) \
		make runserver

runserver:
	LOCAL=true uvicorn $(service_name).server:web_app --host 0.0.0.0 --port 8000

runcron:
	LOCAL=true python3 -m first2know.cron

regenauth:
	LOCAL=true python3 -m first2know.twitter_auth

modaldeploy:
	modal app deploy --name first2know first2know.modal_app:modal_app

test:
	# python3 -m unittest first2know.test
	python3 -m unittest first2know.test.TestScreenshot.test_raw_proxy

list:  # Meta target to list other targets.
	@$(MAKE) -pRrq -f $(THIS_FILE) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$' | xargs
