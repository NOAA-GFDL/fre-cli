# Makefile created by mkmf 2022.01.00


.DEFAULT:
	-echo $@ does not exist.
all: a.out
SRC =
OBJ =
clean: neat
	-rm -f .a.out.cppdefs $(OBJ) a.out

neat:
	-rm -f $(TMPFILES)

TAGS: $(SRC)
	etags $(SRC)

tags: $(SRC)
	ctags $(SRC)

a.out: $(OBJ)
	$(LD) $(OBJ) -o a.out  $(LDFLAGS)

