default: dist/dcc/dcc

clean:
	@rm -rf build dist

dist/dcc/dcc: clean
	@pyinstaller dcc.py

run: 
	@dist/dcc/dcc