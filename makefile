.PHONY : clean build 

clean :
	rm -r build
	rm -r dist
	rm *.spec


build :
	@./compile
