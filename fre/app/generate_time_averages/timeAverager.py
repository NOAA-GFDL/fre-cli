''' core class structure for this module.'''
import logging

fre_logger = logging.getLogger(__name__)

class timeAverager:
    '''
    abstract base class for generating time averages + related statistical quantities
    this class must be inherited by another for functionality.
    '''
    pkg: str
    var: str
    unwgt: bool
    avg_type: str

    def __init__(self, pkg, var, unwgt, avg_type):
        ''' init method '''
        fre_logger.info('__init__ called')
        # arg_list = [ pkg, var, unwgt, avg_type ] # TODO
        arg_list = [ pkg, unwgt, avg_type ]
        if all( arg is None for arg in arg_list ):
            fre_logger.debug('except maybe var, all args None')
            self.pkg = None
            self.var = var
            self.unwgt = False
            self.avg_type = "all"
        else:
            fre_logger.debug('except maybe var, no args None')
            self.pkg = pkg
            self.var = var
            self.unwgt = unwgt
            self.avg_type = avg_type


    def __repr__(self):
        ''' return text representation of object '''
        return f'{type(self).__name__}( pkg = {self.pkg}, \
                               unwgt = {self.unwgt}, \
                               var = {self.var}, \
                               avg_type = {self.avg_type})'

    def var_has_time_units(self, an_nc_var = None):
        ''' checks if variable's units are of time '''
        try:
            fre_logger.debug('looking at units for netCDF variable %s', an_nc_var)
            var_units = an_nc_var.units
            units_is_time = False
            units_is_time = any( [ var_units == 'seconds' ,  'seconds since' in var_units ,
                                   var_units == 'minutes' ,  'minutes since' in var_units ,
                                   var_units == 'hours'   ,  'hours since'   in var_units ,
                                   var_units == 'days'    ,  'days since'    in var_units ,
                                   var_units == 'months'  ,  'months since'  in var_units ,
                                   var_units == 'years'   ,  'years since'   in var_units  ] )
            return units_is_time
        except AttributeError:
            fre_logger.warning('variable does not have units')
            fre_logger.warning('PROBABLY not time.')
            return False

        # TODO
        #def var_has_time_dims(self, an_nc_var=None):
        #try:
        #    var_dims=an_nc_var.dimensions
        #for dim in an_nc_var.dimensions:
        #    if dim ==




    def generate_timavg(self, infile=None, outfile=None):
        '''# this is a hint: this is to be defined by classes inheriting from the abstract one
        this function is never to be fully defined here by design.'''
        raise NotImplementedError()
