Background
==========

Motivation
----------
SVInsight was developed to provide an open-source tool for creating social vulnerability indices or SVIs based on user defined study areas and input variables. SVInsight uses two methodologies to create indices based on existing scholarly research: (1) a factor analysis method and (2) a rank method. This tool's purpose is to provide researchers with the ability to quickly create exploratory estimates of vulnerability based on existing and known relationships between socio-demographic variables and a community's sensitivity (a proxy for vulnerability). 


While SVInsight is capable of rapidly producing tailor made estimates of relative vulnerability of a given region for researchers and/or practitioners, it does not replace the in-depth investigation required to definitively define what makes someone more or less vulnerable. Indices created with SVInsight can be used as a starting point for understanding the complex relationship between socio-demographic variables and community characteristics including vulnerability, sensitivity, and adaptive capacity by highlighting prominent geographic disparities. It is further important to note that vulnerability estimates are relative, and calculated scores should be taken in the context of the study area being examined.

This package was specifically written in conjunction with past and ongoing projects at the University of Texas at Austin [2]_ [3]_ [4]_. More detailed information regarding funding sources can be found in the :doc:`Acknowledgements section <../Acknowledgements/acknowledgements>`.


Methodology
-----------

Data Source 
^^^^^^^^^^^
All data comes from the American Community Survey 5-Year Estimates because they contain data at the Census block group and tract level. More information on data quality can be found on their `website <https://www.census.gov/data/developers/data-sets/acs-5year.html>`_. 

Iterative Factor Analysis
^^^^^^^^^^^^^^^^^^^^^^^^^

This methodology is heavily influenced by the original SoVI® [1]_ developed by Dr. Susan Cutter. By utilizing a data reduction methodology, a large subset of American Community Survey 5-Year Estimate variables can be dimensionally reduced and combined into a single index. Both principal component analyses and factor analyses are data reduction techniques that have been utilized to create vulnerability indices. A principal component analysis (PCA) reduces data by creating one or more index variables, or ‘components,’ by using a linear combination (i.e., a weighted average) from a larger set of measured variables. The purpose of a PCA is to determine the optimal number of components, the optimal choice of measured variables for each component, and the optimal weights. A factor analysis (FA) is a model of latent variables. A ‘latent variable’ cannot be directly measured with a single variable. A common example used to describe this is we cannot directly measure something like social anxiety, but we can measure whether someone has a high or low social anxiety based on a set of questions like “I am uncomfortable in large groups” or “ I get nervous talking to strangers.” We utilize a factor analysis approach because it is the data reduction methodology most often associated with creating composite indices, which is our end goal. 

The follow are the steps in the iterative factor analysis approach: 


1. **Scale the data**
    - We standardize the data to a range of 0-1. Since all of the variable have a different scale, this makes each variable have an equal weight going into the analysis.

2. **Conduct Initial Factor Analysis**
    - Inputs for a factor analysis include the number of factors we are attempting to reduce the data down to, the rotation method, and the fitting method. For this first factor analysis, we set the number of factors to the number of variables under investigation (the maximum number of possible factors) in order to determine if there are any variables at the start we can eliminate for having too low of an influence. The rotation method used is varimax, or orthogonal rotation, which maximizes the sum of the variances of the squared loadings. In simpler terms, ‘loadings’ refer to the correlations between variables and factors. With varimax rotation, the resultant factors are uncorrelated with each other. The fitting method we use is minimum residual (‘minres’).

3. **Calculate Eigenvalues**
    -With our initial factors, we need to determine which ones are significant and which can be removed. If we stopped here, we would have reduced X variables to X factors, (i.e., we wouldn’t have reduced anything). Our goal is to find the weakest factors to eliminate so that while we are eliminating data, we maintain the highest level of reported variance in our final factors.
    -The first step in doing this is calculating the eigenvalues, which is defined as a measure of how much of the common variance of the observed variables a factor explains. A factor with an eigenvalue greater than or equal to 1 explains more variance than a single observed variable and is therefore beneficial. This is known as the Kaiser Criterion. The number of factors whose eigenvalues is greater than 1 now becomes our new number of factors.

4. **Recompute Factor Analysis based on Kaiser Criterion**
    - Similar to step 2, we run the factor analysis again with the new optimized number of factors.

5. **Calculate Loading Factors**
    - The loading factor is the correlation coefficient for the variable and factor. It shows the variance explained by the variable on that particular factor. This will become the weight of the variable on that factor. Various standards exist on what makes a significant loading factor. For the sake of this research, we identify any loading factor that is greater than 0.5 or less than -0.5 is significant.

6. **Calculate Variance Statistics**
    -The variance statistics for each factor that we are interested in tracking are the SS Loadings, Proportion Variance, Cumulative Variance, and Ratio of Variance.
        + *SS Loadings:* The sum of the squared loadings for the factor. If a factor’s SS loading is greater than 1 it is worth keeping.
        + *Proportion Variance:* The proportion of the variance that a factor accounts for. The first factor will have the highest proportion, due to our rotation earlier, and subsequent factors will have a decreasing proportion of explained variance.
        + *Cumulative Variance:* The cumulative sum of the variance that is explained with each factor. The overall cumulative variance is how much of the original system’s variables are explained with this new reduced dimensionality. This is incredibly important because it shows us how much of the original data’s variance we are losing. If we are losing too much, then we need to reconsider how many factors we have reduced down to. If it is too close to 100% then we can theoretically reduce down more.
        + *Ratio of Variance:* Ratio of proportion of variance to cumulative variance.

7. **Determine Significant Variables**
    -Any variable whose loading factor is greater than 0.5 or less than -0.5  at any point is significant and therefore needs to be included in the analysis. Any variable that is not significant in any factor can be eliminated. With the new dataset we can again re-run the factor analysis until only the variables that are significantly contributing to at least one factor are included.

8. **Begin Iterative Loop**
    - With the newly created list of variables that have a significant contribution to at least a single factor, we can eliminate those that are not contributing and re-run the factor analysis without it. This process is repeated until every variable is significantly contributing to at least one factor.

9. **Compose the Final Index**
    -We first recalculate the final loadings and then for each factor, multiply the loading by the ratio of variance to scale the data. Therefore, factor 1 is rated higher than factor 2, factor 2 is rated higher than 3, and so on. From this, we can examine each factor to see which is the largest source of ‘vulnerability’ within the composite index (i.e., what is contributing the most). We create the composite index by adding each factor value together to calculate the unscaled composite index. The final composite index is minmax scaled so that the most vulnerable block group has a composite index of 1 and the least as a composite index of 0.

The purpose of the factor analysis and composite score index in the scope of social vulnerability is to determine which variables are most distinguishable across the study area. The variables with the highest variability are likely to influence the index the most and therefore they must be taken into context of the study area. For example, in Austin, TX a variable that is highly variant across the city is the percent of population that identifies as Hispanic. If this trait contributes to social vulnerability, then our index is working properly to identify areas of higher vulnerability. However, if we discovered that this trait does not contribute to social vulnerability, we cannot include it in this workflow because we are unintentionally weighting the index incorrectly. That is why it is *imperative that indices are developed through collaborations with local experts* to identify which variables are likely contributing to vulnerability. 



Rank Method
^^^^^^^^^^^
Another commonly employed method to estimate social vulnerability is a ranking method, which was popularized by the `Center for Disease Control's Social Vulnerability Index <https://www.atsdr.cdc.gov/placeandhealth/svi/index.html>`_ [5]_. This method is a more simplified way to produce an index for a given area. Each variable of interest is sorted from high to low and ranked. For each location within the study area, the ranks are summed so that locations with a higher overall rank have a greater vulnerability score. In our method, the final summed ranks are also minmax scaled so that the most vulnerable block group has a composite index of 1 and the least as a composite index of 0.


.. _variables:

Variables
---------
SVInsight comes with a standard set of 27 variables which come from the original principal component analysis method, SoVI®. We omit two variables from the original list of 29 due to data availability issues for all of the years and geographic boundaries of interest (the percentage of the population living in nursing facilities, and the number of hospitals per capita). It is important to note that the CDC SVI uses a list of 16 variables that are similar to those from the SoVI® method. Determining which or how many variables to use depends completely on the study area and objectives of the researcher/practitioner and can greatly influence the estimates. Special consideration must be taken to determine the most appropriate set of variables to use.

The variables, there definitions, and the American Community Survey 5-Year Estimate sources can be found below:


+ QAGDDEP: Percent of population under the age of 5 or over the age of 65
    - ['B01001_001E', 'B01001_026E', 'B01001_003E', 'B01001_020E', 'B01001_021E', 'B01001_022E', 'B01001_023E', 'B01001_024E', 'B01001_025E', 'B01001_027E', 'B01001_044E', 'B01001_045E', 'B01001_046E', 'B01001_047E', 'B01001_048E', 'B01001_049E']

+ QFEMALE: Percent of population that is female
    - ['B01001_001E', 'B01001_026E']

+ MEDAGE: Median age
    - ['B01002_001E']

+ QBLACK: Percent of population that is non-Hispanic Black/African-American
    - ['B03002_001E', 'B03002_004E']

+ QNATIVE: Percent of population that is non-Hispanic Native American
    - ['B03002_001E', 'B03002_005E']

+ QASIAN: Percent of population that is non-Hispanic Asian
    - ['B03002_001E', 'B03002_006E']

+ QHISPC: Percent of population that is Hispanic
    - ['B03002_001E', 'B03002_012E']

+ QFAM: Percent of families where only one spouse is present in the household
    - ['B11005_003E', 'B11005_005E']

+ PPUNIT: People per unit, or average household size
    - ['B25010_001E']

+ QFHH: Percent of households with Female householder and no spouse present
    - ['B11001_001E', 'B11001_006E']

+ QEDLESHI: Percent of population over the age of 25 with less than a high school diploma (or equivalent)
    - ['B15003_001E', 'B15003_002E', 'B15003_003E', 'B15003_004E', 'B15003_005E', 'B15003_006E', 'B15003_007E', 'B15003_008E', 'B15003_009E', 'B15003_010E', 'B15003_011E', 'B15003_012E', 'B15003_013E', 'B15003_014E', 'B15003_015E', 'B15003_016E']

+ QCVLUN: Percent of civilian population over the age of 15 that is unemployed
    - ['B23025_003E', 'B23025_005E']

+ QRICH: Percent of households earning over $200,000 annually (inversely related to vulnerability)
    - ['B19001_001E', 'B19001_017E']

+ QSSBEN: Percent of households with social security income
    - ['B19055_001E', 'B19055_002E']

+ PERCAP: Per capita income in the past 12 months (inversely related to vulnerability)
    - ['B19301_001E']

+ QRENTER: Percent of households that are renters
    - ['B25003_001E', 'B25003_003E']

+ QUNOCCHU: Percent of housing units that are unoccupied
    - ['B25002_001E', 'B25002_003E']

+ QMOHO: Percent of housing units that are mobile homes
    - ['B25024_001E', 'B25024_010E']

+ MDHSEVAL: Median housing value (inversely related to vulnerability)
    - ['B25077_001E']

+ MDGRENT: Median gross rent
    - ['B25064_001E']

+ QPOVTY: Percent of population whose income in the past 12 months was below the poverty level
    - ['B17021_001E', 'B17021_002E']

+ QNOAUTO: Percent of households without access to a car
    - ['B25044_001E', 'B25044_003E', 'B25044_010E']

+ QNOHLTH: Percent of population without health insurance
    - ['B27001_001E', 'B27001_005E', 'B27001_008E', 'B27001_011E', 'B27001_014E', 'B27001_017E', 'B27001_020E', 'B27001_023E', 'B27001_026E', 'B27001_029E', 'B27001_033E', 'B27001_036E', 'B27001_039E', 'B27001_042E', 'B27001_045E', 'B27001_048E', 'B27001_051E', 'B27001_054E', 'B27001_057E']

+ QESL: Percent of population who speaks English "not well" or "not at all"
    - ['B16004_001E', 'B16004_007E', 'B16004_008E', 'B16004_012E', 'B16004_013E', 'B16004_017E', 'B16004_018E', 'B16004_022E', 'B16004_023E', 'B16004_029E', 'B16004_030E', 'B16004_034E', 'B16004_035E', 'B16004_039E', 'B16004_040E', 'B16004_044E', 'B16004_045E', 'B16004_051E', 'B16004_052E', 'B16004_056E', 'B16004_057E', 'B16004_061E', 'B16004_062E', 'B16004_066E', 'B16004_067E']

+ QFEMLBR: Percent of the civilian employed population over the age of 16 that is female
    - ['C24010_001E', 'C24010_038E']

+ QSERV: Percent of the civilian employed population that has a service occupation
    - ['C24010_001E', 'C24010_019E', 'C24010_055E']

+ QEXTRCT: Percent of the civilian employed population that has a construction and extraction occupation
    - ['C24010_001E', 'C24010_032E', 'C24010_068E']






References
----------

.. [1] Cutter, S. L., Boruff, B. J., & Shirley, W. L. (2012). Social vulnerability to environmental hazards. In Hazards vulnerability and environmental justice (pp. 143-160). Routledge.

.. [2] Bixler, R. P., Yang, E., Richter, S. M., & Coudert, M. (2021). Boundary crossing for urban community resilience: A social vulnerability and multi-hazard approach in Austin, Texas, USA. International Journal of Disaster Risk Reduction, 66, 102613.

.. [3] Preisser, M., Passalacqua, P., Bixler, R. P., & Hofmann, J. (2022). Intersecting near-real time fluvial and pluvial inundation estimates with sociodemographic vulnerability to quantify a household flood impact index. Hydrology and Earth System Sciences, 26(15), 3941-3964.

.. [4] Preisser, M., Passalacqua, P., Bixler, R. P., & Boyles, S. (2023). A network-based analysis of critical resource accessibility during floods. Frontiers in Water, 5, 1278205.

.. [5] Flanagan, B. E., Gregory, E. W., Hallisey, E. J., Heitgerd, J. L., & Lewis, B. (2011). A social vulnerability index for disaster management. Journal of homeland security and emergency management, 8(1), 0000102202154773551792.