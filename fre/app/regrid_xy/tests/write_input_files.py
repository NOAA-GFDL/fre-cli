import numpy as np
import xarray as xr


def gridspec():

    sn = "standard_name"
    data = {}

    # dictionary with components and data
    components = {"atm": ["atmosphere", "C96_mosaic"],
                  "lnd": ["land", "C96_mosaic"],
                  "ocn": ["ocean", "ocn_mosaic"],
                  "ocn_topog": ["notused", "ocean_topog"]
                  }

    for comp, [compp, fname] in components.items():
        # mosaic_dir
        data[f"{comp}_mosaic_dir"] = xr.DataArray("./", attrs={sn: f"directory storing {compp} mosaic"})
        # mosaic_file
        data[f"{comp}_mosaic_file"] = xr.DataArray(f"{fname}.nc", attrs={sn: f"{compp} mosaic filename"})
        # mosaic_variable
        data[f"{comp}_mosaic"] = xr.DataArray(fname, attrs={sn: f"{compp} mosaic name"})

    # exchange files
    aXo_files = ["C96_mosaic_tile1Xocean_mosaic_tile1.nc"] * 6
    aXl_files = [f"C96_mosaic_tile1XC96_mosaic_tile{i}.nc" for i in range(1, 7)]
    lXo_files = ["C96_mosaic_tile1Xocean_mosaic_tile1.nc"] * 6

    # exchange components with data
    xcomponents = {"aXo": ["atmXocn_exchange_grid_file", aXo_files],
                   "aXl": ["atmXlnd_exchange_grid_file", aXl_files],
                   "lXo": ["lndXocn_exchange_grid_file", lXo_files]
                   }

    # exchange file variable
    for xcomp, [attr, thefiles] in xcomponents.items():
        data[f"{xcomp}_file"] = xr.DataArray(thefiles, attrs={sn: attr}, dims=[f"nfile_{xcomp}"])

    # write
    xr.Dataset(data).to_netcdf("grid_spec.nc")


def mosaic():

    data = {}

    # mosaic variable
    data["mosaic"] = xr.DataArray("C96_mosaic", attrs={"standard_name": "grid_mosaic_spec",
                                                       "children": "gridtiles",
                                                       "contact_regions": "contacts",
                                                       "grid_descriptor": ""}
                                  )

    # gridlocation variable
    data["gridlocation"] = xr.DataArray("./", attrs={"standard_name": "grid_file_location"})

    # gridfiles variable
    gridfiles_list = [f"C96_grid.tile{i}.nc" for i in range(1, 7)]
    data["gridfiles"] = xr.DataArray(gridfiles_list, dims=["ntiles"])

    # gridtiles variable
    gridtiles_list = [f"tile{i}" for i in range(1, 7)]
    data["gridtiles"] = xr.DataArray(gridtiles_list, dims=["ntiles"])

    # contacts variable
    contactslist = ["C96_mosaic:tile1::C96_mosaic:tile2",
                    "C96_mosaic:tile1::C96_mosaic:tile3",
                    "C96_mosaic:tile1::C96_mosaic:tile5",
                    "C96_mosaic:tile1::C96_mosaic:tile6",
                    "C96_mosaic:tile2::C96_mosaic:tile3",
                    "C96_mosaic:tile2::C96_mosaic:tile4",
                    "C96_mosaic:tile2::C96_mosaic:tile6",
                    "C96_mosaic:tile3::C96_mosaic:tile4",
                    "C96_mosaic:tile3::C96_mosaic:tile5",
                    "C96_mosaic:tile4::C96_mosaic:tile5",
                    "C96_mosaic:tile4::C96_mosaic:tile6",
                    "C96_mosaic:tile5::C96_mosaic:tile6"
                    ]

    # contacts variable
    data["contacts"] = xr.DataArray(contactslist,
                                    attrs={"standard_name": "grid_contact_spec",
                                           "contact_type": "boundary",
                                           "alignment": "true",
                                           "contact_index": "contact_index",
                                           "orientation": "orient"},
                                    dims=["ncontact"]
                                    )

    # contact_index variable
    contact_indexlist = [
        "192:192,1:192::1:1,1:192",
        "1:192,192:192::1:1,192:1",
        "1:1,1:192::192:1,192:192",
        "1:192,1:1::1:192,192:192",
        "1:192,192:192::1:192,1:1",
        "192:192,1:192::192:1,1:1",
        "1:192,1:1::192:192,192:1",
        "192:192,1:192::1:1,1:192",
        "1:192,192:192::1:1,192:1",
        "1:192,192:192::1:192,1:1",
        "192:192,1:192::192:1,1:1",
        "192:192,1:192::1:1,1:192"
    ]

    data["contact_index"] = xr.DataArray(contact_indexlist,
                                         attrs={"standard_name": "starting_ending_point_index_of_contact"},
                                         dims=["ncontact"]
                                         )

    # write
    xr.Dataset(data).to_netcdf("C96_mosaic.nc")


def grid():

    for i in range(1, 7):

        data = {}

        # tile variable
        data["tile"] = xr.DataArray(f"tile{i}", attrs={"standard_name": "grid_tile_spec",
                                                       "geometry": "spherical",
                                                       "north_pole": "0.0 90.0",
                                                       "projection": "cube_gnomonic",
                                                       "discretization": "logically_rectangular",
                                                       "conformal": "False"}
                                    )

        # generate x, y grid values
        xvalues = np.arange(0, 361, 1, dtype=np.float64)
        yvalues = np.arange(-90, 91, 1, dtype=np.float64)
        x, y = np.meshgrid(xvalues, yvalues)

        # x variable
        data["x"] = xr.DataArray(x, dims=["nyp", "nxp"], attrs={"standard_name": "geographic_longitude",
                                                                "units": "degree_east"}
                                 )

        # y variable
        data["y"] = xr.DataArray(y, dims=["nyp", "nxp"], attrs={"standard_name": "geographic_longitude",
                                                                "units": "degree_north"}

                                 )

        # area variable
        area_values = np.zeros((90, 360), dtype=np.float64)
        data["area"] = xr.DataArray(area_values, dims=["ny", "nx"])

        # write data
        xr.Dataset(data).to_netcdf(f"C96_grid.tile{i}.nc")


def all():

    gridspec()
    mosaic()
    grid()
