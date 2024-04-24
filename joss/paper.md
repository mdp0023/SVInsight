---
title: 'SVInsight: A Python Package for calculating Social Vulnerability Indices'
tags:
  - Python
  - Vulnerability
  - Census
  - Demographics
  - Social Vulnerability Index
  - Census
  - SVI
  - Hazards
  - Factor Analysis

authors:
  - name: Matthew Preisser
    orcid: 0000-0002-5149-3744
    equal-contrib: true
    affiliation: "1" # (Multiple affiliations must be quoted)
  - name: Paola Passalacqua
    orcid: 0000-0002-4763-7231
    equal-contrib: true # (This is how you can denote equal contributions between multiple authors)
    affiliation: 1
    - name: R. Patrick Bixler
    orcid: 0000-0003-0515-0967
    equal-contrib: true # (This is how you can denote equal contributions between multiple authors)
    affiliation: 2
affiliations:
 - name: Maseeh Department of Civil, Architectural and Environmental Engineering
   index: 1
 - name: LBJ School of Public Affairs
   index: 2

date: 24 Arpil 2024
bibliography: paper.bib

---

# Summary

A community's exposure to environmental hazards, their sensitivity to such events, and their ability to respond (adaptive capacity) are influenced by their social, political, cultural, economic, and demographic information [@Smit_2006; @Cutter_2010; @Fatemi_2017]. Understanding the interconnected relationships among exposure, sensitivity, and adaptive capacity is important to estimate the degree to which stakeholders can mitigate environmental hazards [@Smit_2006]. Social Vulnerability Indices, or SVIs, are built on social and demographic data to serve as proxies for these interconnected variables. Numerous SVIs exist including SoVI trademark&reg; from The University of South Carolina's Hazards Vulnerability & Resilience Institute [@Cutter_2003], the Center for Disease Control [@Flanagan_2011], and the United Nations Development Program [@UNDP_2010]. In this paper, we present an open-source Python package, *SVInsight*, which provides an accessible workflow to calculate various exploratory social vulnerability indices that are specific to a given study area.


# Statement of need
Generic social vulnerabilities for large regions can be lacking in their ability to identify at risk populations [@Tate_2012; Nelson_2015; @Tellman_2020]. Furthermore, vulnerability indices are not created equally, and users, researchers, and developers should clearly state the objectives and structure of their index in order to accurately present their findings [@Bakkensen_2016], which may not be possible if they were not involved in creating the index. *SVInsight* is an accessible and open-source tool to quickly calculate SVIs for a user defined region using either custom or a research supported pre-set list of social and demographic variables. *SVInsight* calculates SVIs built on data from the Census Bureau's 5-Year American Community Survey using the two leading methods for calculating such metrics: a composite score using a data reduction methodology [@Cutter_2003] and a ranking method [@Flanagan_2011]. The work done leading up to the creation of the *SVInsight* Python package was and continues to be a part of numerous vulnerability and hazard related research efforts [Bixler_2021a; Preisser_2022; Preisser_2023].


# Background 




# Functionality and Ease of Use 

*SVInsight* automates the entire SVI creation process. The entire workflow can be completed in only 5 lines code:

  - `project = svi(project_name, file_path, api_key, geoids)`: Initializes an SVI project and creates the necessary file structure for all of the intermediary files that might be of interest to users 
  - `project.boundaries_data(boundary, year)`: Extracts the appropriate Census geographic boundaries for the project area
  - `project.census_data(boundary, year)`: Extracts the raw Census data and fills missing holes as needed
  - `project.configure_variables(config_file)`: Configures the specific SVI run
  - `project.calculate_svi(config_file, boundary, year)`: Calculates both SVI estimates (Factor Analysis and Rank Methods)




# Figures

Figures can be included like this:
![Caption for example figure.\label{fig:example}](figure.png){ width=80% }
and referenced from text using \autoref{fig:example}.

Figure sizes can be customized by adding an optional second parameter:
![Caption for example figure.](figure.png){ width=20% }

# Acknowledgements
This work was supported in part by the National Science Foundation Graduate Research Fellowship (grant no. DGE-1610403), Future Investigators in NASA Earth and Space Science and Technology (NASA FINESST, grant no. 21-EARTH21-0264), Planet Texas 2050, a research grand challenge at the University of Texas at Austin, and the U.S. Department of Energy, Office of Science, Biological and Environmental Research Program’s South-East Texas Urban Integrated Field Laboratory under Award Number DE-SC0023216.


# References