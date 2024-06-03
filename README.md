Overview
========

Bringing back humans on the Moon for extended periods of time, and sending them eventually to Mars, requires a thorough multidsciplinary work on assessing systems architectures for permanent surface bases. The primary focus of this work is to provide performance assessment models for the extraction and the processing of lunar/martian soil and martian atmosphere for the in-situ production of propellant and essential resources for the crew and infrastructures (O2/H2O). The key figures of merit are comprised of power requirements, thermal management requirements, system mass, and resources consumption/production rates. These In-Situ Resources Utilization (ISRU) models will eventually be integrated with power, thermal, ECLSS, habitats,... models to assess optimal systems configuration for permanent lunar/martian bases within a Multi-Disciplinary Analysis Optimization (MDAO) framework.

# ISRU modeling effort

Three main processes have been studied for regolith processing (lunar soil):

- Hydrogene reduction of Ilmenite ([H2_Plant.py](https://github.com/Antoine-Marin-Git/ISRU_Moon_Mars/tree/master/H2_Plant.py))
- Carbothermal reduction of Silica ([CH4_Plant.py](https://github.com/Antoine-Marin-Git/ISRU_Moon_Mars/tree/master/CH4_Plant.py))
- Drying of wet regolith/ice in Permanently Shadowed Regions (PSR) ([LADI_Dryer.py](https://github.com/Antoine-Marin-Git/ISRU_Moon_Mars/tree/master/LADI_Dryer.py))

And Sabatier reactions have been implemented to reduce martian CO2 into usable H2O ([Mars_Atmo_Processing.py](https://github.com/Antoine-Marin-Git/ISRU_Moon_Mars/tree/master/Mars_Atmo_Processing.py)).

The regolith extraction phase aswell must be taken into account as it is a crucial step in the overall processing chain ([Extraction_Rovers.py](https://github.com/Antoine-Marin-Git/ISRU_Moon_Mars/tree/master/Extraction_Rovers.py)). Additionally, an electrolyzer model is implemented to perform separately water electrolysis if needed ([Electrolyzer.py](https://github.com/Antoine-Marin-Git/ISRU_Moon_Mars/tree/master/Electrolyzer.py)).
