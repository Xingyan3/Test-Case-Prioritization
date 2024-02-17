CC=gcc
CFLAGS=-fprofile-arcs	-ftest-coverage	-Wno-return-type	-g
TARGET=totinfo
SOURCE=totinfo.c
LIBS=-lm

all:	$(TARGET)

$(TARGET):	$(SOURCE)
	$(CC)	$(CFLAGS)	-o	$(TARGET)	$(SOURCE)	$(LIBS)

clean:
	rm	-f	$(TARGET)	$(TARGET).gcno	$(TARGET).gcda