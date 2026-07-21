install :
	pip install -r requirements.txt

run : 
	python3 Fly-in.py $(SRC)

clean :
	rm -rf __pycache__
	rm -rf .mypy_cache

lint:
	flake8 .
	mypy . \
		--warn-return-any \
		--warn-unused-ignores \
		--ignore-missing-imports \
		--disallow-untyped-defs \
		--check-untyped-defs
