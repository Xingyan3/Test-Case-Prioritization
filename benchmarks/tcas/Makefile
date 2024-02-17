CC=gcc
CFLAGS=-fprofile-arcs	-ftest-coverage	-Wno-return-type	-g
TARGET=tcas
SOURCE=tcas.c

all:	$(TARGET)

$(TARGET):	$(SOURCE)
	$(CC)	$(CFLAGS)	-o	$(TARGET)	$(SOURCE)

clean:
	rm	-f	$(TARGET)	$(TARGET).gcno	$(TARGET).gcda