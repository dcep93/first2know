service_name=first2know
local_image_tag=$(service_name):latest

THIS_FILE := $(lastword $(MAKEFILE_LIST))

dockerbuild:
	docker build -t $(local_image_tag) .

dockerexec: dockerbuild
	docker run \
		-it \
		--rm \
		--name $(service_name) \
		$(local_image_tag) \
		make $(ARGS)

oneoff:
	python3 -u -m first2know.oneoff

server:
	uvicorn app:app --loop asyncio --host 0.0.0.0 --port 8080

cron:
	python3 -u -m first2know.cron

twitter_auth:
	python3 -m first2know.twitter_auth

test:
	python3 -m unittest first2know.test
	# python3 -m unittest first2know.test.TestScreenshot.test_raw_proxy

list:  # Meta target to list other targets.
	@$(MAKE) -pRrq -f $(THIS_FILE) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$' | xargs
