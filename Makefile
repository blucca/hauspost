.DEFAULT_GOAL := run
.PHONY: run demo hosted provision stop logs

run demo hosted provision stop logs:
	$(MAKE) -C track_2b $@
