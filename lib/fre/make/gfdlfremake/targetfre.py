class fretarget:
    """
    Class: Stores information about the target
    """
    def __init__(self,t):
        """
        Brief: Sets up information about the target and handles errors
        Note: The default target is prod
        Param:
            - self the fretarget object
            - t The target string
        """
        self.target = t # The target string

        ## Split the target string
        targ = self.target.split('-')
        self.makeline_add = ""
        self.debug = False
        self.repro = False
        self.prod = False

        ## Parse the target string for prod, repro, and debug.  Set up what to add to the
        ## make line during compile when using mkmf builds
        for target in targ:
            if target == "debug":
                targ = target.upper()
                self.makeline_add = self.makeline_add + targ + "=on "
                self.debug = True
            elif target == "prod":
                targ = target.upper()
                self.makeline_add = self.makeline_add + targ + "=on "
                self.prod = True
            elif target == "repro":
                targ = target.upper()
                self.makeline_add = self.makeline_add + targ + "=on "
                self.repro = True

            ## Check to see if openmp is included in the target and add that to the makeline add string
            if target == "openmp":
                targ = target.upper()
                self.makeline_add = self.makeline_add + targ + "=on "
                self.openmp = True
            else:
                self.openmp = False

        ## Check to make sure only one of the prod, debug, repro are used
        errormsg = "You can only list one mutually exclusive target, but your target '"+self.target+"' lists more than one of the following targets: \n debug \n prod \n repro"
        if self.debug:
            try:
                if self.repro or self.prod == True:
                    raise ValueError(errormsg)
            except ValueError:
                raise
        elif self.repro:
            try:
                if self.prod == True:
                    raise ValueError(errormsg)
            except ValueError:
                raise
        else:
            try:
                if self.prod == False:
                    raise ValueError("Your target '"+self.target+"' needs to include one of the following: prod, repro, debug")
            except ValueError:
                raise

    def gettargetName(self):
        """
        Brief: Returns the name of the target
        Param:
            - self The fretarget object
        """
        return self.target

    def getmakeline_add(self):
        """
        Brief: Returns the makeline_add
        Param:
            - self The fretarget object
        """
        return self.makeline_add
