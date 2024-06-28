VERSION := $(shell git describe --abbrev=0)
OWNER := "ETH-NEXUS"
REPO := "dcc"

all: build_mac build_linux clean

clean:
	@rm -rf build dcc.spec

build_mac:
	@pipenv run pyinstaller --name dcc --onefile dcc.py --distpath ./dist/mac

build_linux:
	@rm -rf build dist/linux dcc.spec
	@docker build . -f Dockerfile.linux -t pyinstaller_linux
	@docker run --rm -it -v .:/src pyinstaller_linux sh -c 'pyinstaller --name dcc --onefile dcc.py --distpath /src/dist/linux'

gh:
	@docker build . -f Dockerfile.gh -t gh

release: all gh
	@mkdir -p releases
	@docker run --rm -it -v .:/src tar czf /src/releases/$(REPO)-$(VERSION).tar.gz /src/dist
	-@docker run --rm -it -v .:/src gh sh -c 'gh release delete $(VERSION)'
	-@docker run --rm -it -v .:/src gh sh -c 'gh api \
		--method POST \
		-H "Accept: application/vnd.github+json" \
		-H "X-GitHub-Api-Version: 2022-11-28" \
		/repos/$(OWNER)/$(REPO)/releases \
		-f "tag_name=$(VERSION)" \
		-f "target_commitish=main" \
		-f "name=$(VERSION)" \
		-f "body=Release bundle of $(REPO)" \
		-F "draft=false" \
		-F "prerelease=false" \
		-F "generate_release_notes=false"'
	@docker run --rm -it -v .:/src gh sh -c 'gh release upload $(VERSION) /src/releases/$(REPO)-$(VERSION).tar.gz'

run: 
	@dist/dcc/dcc