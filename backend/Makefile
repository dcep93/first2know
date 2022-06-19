service_name=first2know
local_image_tag=$(service_name):latest

THIS_FILE := $(lastword $(MAKEFILE_LIST))

dockerbuild:
	docker build -t $(local_image_tag) .

dockerrun:
	docker run \
		--rm \
		--name $(service_name) \
		$(local_image_tag)

dockerrunserver:
	docker run \
		--rm \
		-p 8000:8000 \
		$(local_image_tag) \
		uvicorn $(service_name).server:web_app --host 0.0.0.0 --port 8000

list:  # Meta target to list other targets.
	@$(MAKE) -pRrq -f $(THIS_FILE) : 2>/dev/null | awk -v RS= -F: '/^# File/,/^# Finished Make data base/ {if ($$1 !~ "^[#.]") {print $$1}}' | sort | egrep -v -e '^[^[:alnum:]]' -e '^$@$$' | xargs