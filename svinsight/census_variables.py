
def setup_census_variables():
    # set instances of Census variables 
    # {'NAME':{'num':['vars'], 'den':['vars']}}
    QAGEDEP = {'QAGEDEP':
                    {'num':['B01001_026E', 'B01001_003E', 'B01001_020E',
                        'B01001_021E', 'B01001_022E', 'B01001_023E', 'B01001_024E',
                        'B01001_025E', 'B01001_027E', 'B01001_044E', 'B01001_045E',
                        'B01001_046E', 'B01001_047E', 'B01001_048E', 'B01001_049E'], 
                    'den':['B01001_001E'],
                    'description':'Percent of population under the age of 5 or over the age of 65'}}
    QFEMALE = {'QFEMALE':
                    {'num':['B01001_026E'], 
                    'den':['B01001_001E'],
                    'description':'Percent of population that is female'}}
    MEDAGE = {'MEDAGE':
                    {'num':['B01002_001E'], 
                    'den':[1],
                    'description':'Median age'}}
    QBLACK = {'QBLACK':
                    {'num':['B03002_004E'], 
                    'den':['B03002_001E'],
                    'description':'Percent of population that is non-Hispanic Black/African-American'}}
    QNATIVE = {'QNATIVE':
                    {'num':['B03002_005E'], 
                    'den':['B03002_001E'],
                    'description':'Percent of population that is non-Hispanic Native American'}}
    QASIAN = {'QASIAN':
                    {'num':['B03002_006E'], 
                    'den':['B03002_001E'],
                    'description':'Percent of population that is non-Hispanic Asian'}}
    QHISPC = {'QHISPC':
                    {'num':['B03002_012E'], 
                    'den':['B03002_001E'],
                    'description':'Percent of population that is Hispanic'}}
    QFAM = {'QFAM':
                    {'num':['B11005_005E'], 
                    'den':['B11005_003E'],
                    'description':'Percent of families where only one spouse is present in the household'}}
    PPUNIT = {'PPUNIT':
                    {'num':['B25010_001E'], 
                    'den':[1],
                    'description':'People per unit, or average household size'}}
    QFHH = {'QFHH':
                    {'num':['B11001_006E'], 
                    'den':['B11001_001E'],
                    'description':'Percent of households with Female householder and no spouse present'}}
    QEDLESHI = {'QEDLESHI':
                    {'num':['B15003_002E', 'B15003_003E', 'B15003_004E',
                            'B15003_005E', 'B15003_006E', 'B15003_007E', 'B15003_008E',
                            'B15003_009E', 'B15003_010E', 'B15003_011E', 'B15003_012E',
                            'B15003_013E', 'B15003_014E', 'B15003_015E', 'B15003_016E'],
                    'den':['B15003_001E'],
                    'description':'Percent of population over the age of 25 with less than a high school diploma (or equivalent)'}}
    QCVLUN = {'QCVLUN':
                    {'num':['B23025_005E'],
                    'den':['B23025_003E'],
                    'description':'Percent of civilian population over the age of 15 that is unemployed'}}
    QRICH = {'QRICH':
                    {'num':['B19001_017E'],
                        'den':['B19001_001E'],
                    'description':'Percent of households earning over $200,000 annually'}}
    QSSBEN = {'QSSBEN':
                    {'num':['B19055_002E'],
                    'den':['B19055_001E'],
                    'description':'Percent of houseolds with social security income'}}
    PERCAP = {'PERCAP':
                    {'num':['B19301_001E'],
                    'den':[1],
                    'description':'Per capita income in the past 12 months'}}
    QRENTER = {'QRENTER':
                    {'num':['B25003_003E'],
                    'den':['B25003_001E'],
                    'description':'Percent of households that are renters'}}
    QUNOCCHU = {'QUNOCCHU':
                    {'num':['B25002_003E'],
                    'den':['B25002_001E'],
                    'description':'Percent of housing units that are unoccupied'}}
    QMOHO = {'QMOHO':
                    {'num':['B25024_010E'],
                    'den':['B25024_001E'],
                    'description':'Percent of housing unts that are mobile homes'}}
    MDHSEVAL = {'MDHSEVAL':
                    {'num':['B25077_001E'],
                    'den':[1],
                    'description':'Median housing value'}}
    MDGRENT = {'MDGRENT':
                    {'num':['B25064_001E'],
                    'den':[1],
                    'description':'Median gross rent'}}
    QPOVTY = {'QPOVTY':
                    {'num':['B17021_002E'],
                    'den':['B17021_001E'],
                    'description':'Percent of population whose income in the past 12 months was below the poverty level'}}
    QNOAUTO = {'QNOAUTO':
                    {'num':['B25044_003E', 'B25044_010E'],
                    'den':['B25044_001E'],
                    'description':'Percent of households without access to a car'}}
    QNOHLTH = {'QNOHLTH':
                    {'num':['B27001_005E', 'B27001_008E', 'B27001_011E', 'B27001_014E', 
                            'B27001_017E', 'B27001_020E', 'B27001_023E', 'B27001_026E', 
                            'B27001_029E', 'B27001_033E', 'B27001_036E', 'B27001_039E', 
                            'B27001_042E', 'B27001_045E', 'B27001_048E', 'B27001_051E', 
                            'B27001_054E', 'B27001_057E'],
                    'den':['B27001_001E'],
                    'description':'Percent of population without health insurance'}}
    QESL = {'QESL':
                    {'num':['B16004_007E', 'B16004_008E', 'B16004_012E', 'B16004_013E', 
                            'B16004_017E', 'B16004_018E', 'B16004_022E', 'B16004_023E', 
                            'B16004_029E', 'B16004_030E', 'B16004_034E', 'B16004_035E', 
                            'B16004_039E', 'B16004_040E', 'B16004_044E', 'B16004_045E', 
                            'B16004_051E', 'B16004_052E', 'B16004_056E', 'B16004_057E', 
                            'B16004_061E', 'B16004_062E', 'B16004_066E', 'B16004_067E'],
                    'den':['B16004_001E'],
                    'description':'Percent of population who speaks English "not well" or "not at all" '}}
    QFEMLBR = {'QFEMLBR':
                    {'num':['C24010_038E'],
                    'den':['C24010_001E'],
                    'description':'Percent of the civilian employed population over the age of 16 that is female'}}
    QSERV = {'QSERV':
                    {'num':['C24010_019E', 'C24010_055E'],
                    'den':['C24010_001E'],
                    'description':'Percent of the civilian employed population that has a service occupation'}}
    QEXTRCT = {'QEXTRCT':
                    {'num':['C24010_032E', 'C24010_068E'],
                    'den':['C24010_001E'],
                    'description':'Percent of the civilian employed population that has a construction and extraction occupation'}}
    

    # all variable equation dictionaries in a list
    all_vars_eqs_list = [QAGEDEP, QFEMALE, MEDAGE, QBLACK,
                        QNATIVE, QASIAN, QHISPC, QFAM,
                        PPUNIT, QFHH, QEDLESHI, QCVLUN, 
                        QRICH, QSSBEN, PERCAP, QRENTER,
                        QUNOCCHU, QMOHO, MDHSEVAL, MDGRENT,
                        QPOVTY, QNOAUTO, QNOHLTH, QESL,
                        QFEMLBR, QSERV, QEXTRCT]
    
    # all variable equation dictionaries in dictionary
    all_vars_eqs = {}
    for d in all_vars_eqs_list:
        all_vars_eqs.update(d)

    # all unique Census variables
    all_vars = list(set(value for name, dict in all_vars_eqs.items() for key1, value1 in dict.items() if key1 != 'description' for value in value1))       
    all_vars.remove(1)

    return all_vars_eqs, all_vars


# # set instances of Census variables 
# # {'NAME':{'num':['vars'], 'den':['vars']}}
# self.QAGEDEP = {'QAGEDEP':
#                 {'num':['B01001_026E', 'B01001_003E', 'B01001_020E',
#                     'B01001_021E', 'B01001_022E', 'B01001_023E', 'B01001_024E',
#                     'B01001_025E', 'B01001_027E', 'B01001_044E', 'B01001_045E',
#                     'B01001_046E', 'B01001_047E', 'B01001_048E', 'B01001_049E'], 
#                 'den':['B01001_001E']}}
# self.QFEMALE = {'QFEMALE':
#                 {'num':['B01001_026E'], 
#                  'den':['B01001_001E']}}
# self.MEDAGE = {'MEDAGE':
#                 {'num':['B01002_001E'], 
#                 'den':[1]}}
# self.QBLACK = {'QBLACK':
#                 {'num':['B03002_004E'], 
#                 'den':['B03002_001E']}}
# self.QNATIVE = {'QNATIVE':
#                 {'num':['B03002_005E'], 
#                  'den':['B03002_001E']}}
# self.QASIAN = {'QASIAN':
#                 {'num':['B03002_006E'], 
#                 'den':['B03002_001E']}}
# self.QHISPC = {'QHISPC':
#                 {'num':['B03002_012E'], 
#                 'den':['B03002_001E']}}
# self.QFAM = {'QFAM':
#                 {'num':['B11005_005E'], 
#                 'den':['B11005_003E']}}
# self.PPUNIT = {'PPUNIT':
#                 {'num':['B25010_001E'], 
#                 'den':[1]}}
# self.QFHH = {'QFHH':
#                 {'num':['B11001_006E'], 
#                 'den':['B11001_001E']}}
# self.QEDLESHI = {'QEDLESHI':
#                 {'num':['B15003_002E', 'B15003_003E', 'B15003_004E',
#                         'B15003_005E', 'B15003_006E', 'B15003_007E', 'B15003_008E',
#                         'B15003_009E', 'B15003_010E', 'B15003_011E', 'B15003_012E',
#                         'B15003_013E', 'B15003_014E', 'B15003_015E', 'B15003_016E'],
#                 'den':['B15003_001E']}}
# self.QCVLUN = {'QCVLUN':
#                 {'num':['B23025_005E'],
#                  'den':['B23025_003E']}}
# self.QRICH = {'QRICH':
#                 {'num':['B19001_017E'],
#                  'den':['B19001_001E']}}
# self.QSSBEN = {'QSSBEN':
#                 {'num':['B19055_002E'],
#                  'den':['B19055_001E']}}
# self.PERCAP = {'PERCAP':
#                 {'num':['B19301_001E'],
#                  'den':[1]}}
# self.QRENTER = {'QRENTER':
#                 {'num':['B25003_003E'],
#                  'den':['B25003_001E']}}
# self.QUNOCCHU = {'QUNOCCHU':
#                 {'num':['B25002_003E'],
#                  'den':['B25002_001E']}}
# self.QMOHO = {'QMOHO':
#                 {'num':['B25024_010E'],
#                  'den':['B25024_001E']}}
# self.MDHSEVAL = {'MDHSEVAL':
#                 {'num':['B25077_001E'],
#                  'den':[1]}}
# self.MDGRENT = {'MDGRENT':
#                 {'num':['B25064_001E'],
#                  'den':[1]}}
# self.QPOVTY = {'QPOVTY':
#                 {'num':['B17021_002E'],
#                  'den':['B17021_001E']}}
# self.QNOAUTO = {'QNOAUTO':
#                 {'num':['B25044_003E', 'B25044_010E'],
#                  'den':['B25044_001E']}}
# self.QNOHLTH = {'QNOHLTH':
#                 {'num':['B27001_005E', 'B27001_008E', 'B27001_011E', 'B27001_014E', 
#                         'B27001_017E', 'B27001_020E', 'B27001_023E', 'B27001_026E', 
#                         'B27001_029E', 'B27001_033E', 'B27001_036E', 'B27001_039E', 
#                         'B27001_042E', 'B27001_045E', 'B27001_048E', 'B27001_051E', 
#                         'B27001_054E', 'B27001_057E'],
#                  'den':['B27001_001E']}}
# self.QESL = {'QESL':
#                 {'num':['B16004_007E', 'B16004_008E', 'B16004_012E', 'B16004_013E', 
#                         'B16004_017E', 'B16004_018E', 'B16004_022E', 'B16004_023E', 
#                         'B16004_029E', 'B16004_030E', 'B16004_034E', 'B16004_035E', 
#                         'B16004_039E', 'B16004_040E', 'B16004_044E', 'B16004_045E', 
#                         'B16004_051E', 'B16004_052E', 'B16004_056E', 'B16004_057E', 
#                         'B16004_061E', 'B16004_062E', 'B16004_066E', 'B16004_067E'],
#                  'den':['B16004_001E']}}
# self.QFEMLBR = {'QFEMLBR':
#                 {'num':['C24010_038E'],
#                  'den':['C24010_001E']}}
# self.QSERV = {'QSERV':
#                 {'num':['C24010_019E', 'C24010_055E'],
#                  'den':['C24010_001E']}}
# self.QEXTRCT = {'QEXTRCT':
#                 {'num':['C24010_032E', 'C24010_068E'],
#                  'den':['C24010_001E']}}



# # # Set CENSUS variables LIST (OLD WAY)
# # self.QAGEDEP_vars = ['B01001_001E', 'B01001_026E', 'B01001_003E', 'B01001_020E',
# #                     'B01001_021E', 'B01001_022E', 'B01001_023E', 'B01001_024E',
# #                     'B01001_025E', 'B01001_027E', 'B01001_044E', 'B01001_045E',
# #                     'B01001_046E', 'B01001_047E', 'B01001_048E', 'B01001_049E'] 
# # self.QFEMALE_vars = ['B01001_001E', 'B01001_026E']
# # self.MEDAGE_vars = ['B01002_001E']
# # self.QBLACK_vars = ['B03002_001E','B03002_004E']
# # self.QNATIVE_vars = ['B03002_001E', 'B03002_005E']
# # self.QASIAN_vars = ['B03002_001E', 'B03002_006E']
# # self.QHISPC_vars = ['B03002_001E', 'B03002_012E']
# # self.QFAM_vars = ['B11005_003E', 'B11005_005E']
# # self.PPUNIT_vars = ['B25010_001E']
# # self.QFHH_vars = ['B11001_001E', 'B11001_006E']
# # self.QEDLESHI_vars = ['B15003_001E', 'B15003_002E', 'B15003_003E', 'B15003_004E',
# #                         'B15003_005E', 'B15003_006E', 'B15003_007E', 'B15003_008E',
# #                         'B15003_009E', 'B15003_010E', 'B15003_011E', 'B15003_012E',
# #                         'B15003_013E', 'B15003_014E', 'B15003_015E', 'B15003_016E'] 
# # self.QCVLUN_vars = ['B23025_003E', 'B23025_005E']
# # self.QRICH_vars = ['B19001_001E', 'B19001_017E']
# # self.QSSBEN_vars = ['B19055_001E', 'B19055_002E']
# # self.PERCAP_vars = ['B19301_001E']
# # self.QRENTER_vars = ['B25003_001E', 'B25003_003E']
# # self.QUNOCCHU_vars = ['B25002_001E', 'B25002_003E']
# # self.QMOHO_vars = ['B25024_001E', 'B25024_010E']
# # self.MDHSEVAL_vars = ['B25077_001E']
# # self.MDGRENT_vars = ['B25064_001E']
# # self.QPOVTY_vars = ['B17021_001E', 'B17021_002E']
# # self.QNOAUTO_vars = ['B25044_001E', 'B25044_003E', 'B25044_010E']
# # self.QNOHLTH_vars = ['B27001_001E', 'B27001_005E', 
# #                     'B27001_008E', 'B27001_011E', 'B27001_014E', 'B27001_017E', 
# #                     'B27001_020E', 'B27001_023E', 'B27001_026E', 'B27001_029E',
# #                     'B27001_033E', 'B27001_036E', 'B27001_039E', 'B27001_042E', 
# #                     'B27001_045E', 'B27001_048E', 'B27001_051E', 'B27001_054E', 
# #                     'B27001_057E']
# # self.QESL_vars = ['B16004_007E' , 'B16004_008E', 'B16004_012E', 'B16004_013E', 
# #                     'B16004_017E', 'B16004_018E', 'B16004_022E', 'B16004_023E', 
# #                     'B16004_029E', 'B16004_030E', 'B16004_034E', 'B16004_035E', 
# #                     'B16004_039E', 'B16004_040E', 'B16004_044E', 'B16004_045E', 
# #                     'B16004_051E', 'B16004_052E', 'B16004_056E', 'B16004_057E', 
# #                     'B16004_061E', 'B16004_062E', 'B16004_066E', 'B16004_067E',
# #                     'B16004_001E']
# # self.QFEMLBR_vars = ['C24010_001E', 'C24010_038E']
# # self.QSERV_vars = ['C24010_001E', 'C24010_019E', 'C24010_055E']
# # self.QEXTRCT_vars = ['C24010_001E', 'C24010_032E', 'C24010_068E']

# # nested list of all variables
# # self.all_vars = [self.QAGEDEP_vars, self.QFEMALE_vars, self.MEDAGE_vars, self.QBLACK_vars,
# #                  self.QNATIVE_vars, self.QASIAN_vars, self.QHISPC_vars, self.QFAM_vars,
# #                  self.PPUNIT_vars, self.QFHH_vars, self.QEDLESHI_vars, self.QCVLUN_vars, 
# #                  self.QRICH_vars, self.QSSBEN_vars, self.PERCAP_vars, self.QRENTER_vars,
# #                  self.QUNOCCHU_vars, self.QMOHO_vars, self.MDHSEVAL_vars, self.MDGRENT_vars,
# #                  self.QPOVTY_vars, self.QNOAUTO_vars, self.QNOHLTH_vars, self.QESL_vars,
# #                  self.QFEMLBR_vars, self.QSERV_vars, self.QEXTRCT_vars]

# # # Flatten the nested list self.all_vars
# # self.all_vars = [var for sublist in self.all_vars for var in sublist]

# # all variable equation dictionaries in a list
# self.all_vars_eqs_list = [self.QAGEDEP, self.QFEMALE, self.MEDAGE, self.QBLACK,
#                  self.QNATIVE, self.QASIAN, self.QHISPC, self.QFAM,
#                  self.PPUNIT, self.QFHH, self.QEDLESHI, self.QCVLUN, 
#                  self.QRICH, self.QSSBEN, self.PERCAP, self.QRENTER,
#                  self.QUNOCCHU, self.QMOHO, self.MDHSEVAL, self.MDGRENT,
#                  self.QPOVTY, self.QNOAUTO, self.QNOHLTH, self.QESL,
#                  self.QFEMLBR, self.QSERV, self.QEXTRCT]

# # all variable equation dictionaries in dictionary
# self.all_vars_eqs = {}
# for d in self.all_vars_eqs_list:
#     self.all_vars_eqs.update(d)

# # all unique Census variables
# self.all_vars = list(set(var for sublist in [list(value.values()) for value in self.all_vars_eqs.values()] for inner_list in sublist for var in inner_list))
# self.all_vars.remove(1)
