# Sentiment Stockticker Dashboard
## Table of contents
* [General info](#general-info)
* [Getting started](#getting-started)


## General info
This "Sentiment Stockticker Dashboard"-Project deals with the topic of sentiment analysis and was written in the context of the lecture "Projektrealisierung" in the course WWI18DSB Wirtschaftsinformatik Data Science at DHBW Mannheim. 
The contributors (GitHub name) to this project were 
* Anabel Lilja (anabellilja)
* Bjarne Gerdes (bjarnege)
* Johannes Deufel (Johannes998)
* Nina Mergelsberg (NinaM98) and 
* Simone Marx (SimoneMarx)

### Objective and approach
The goal of this project involves the development of machine learning models that generate recommendations for capital investments based on current news data. These recommendations are comprehensive and take into account a wide variety of factors. In order to give customers a comprehensible overview of how investment recommendations are calculated, both the price fluctuations of the investments and an individually calculated ranking score are shown. 

In addition to the technical development of the models, the preparation of various economic and project-specific analyses is a primary focus of this project.

### Task distribution in the team
The distribution of tasks over the process of the project is as follows: 

| Contributor | Task | Points |
| ------------------ | ------------------ | ------------------ |
| Anabel Lilja |  - Entwicklung des Projektvorgehens, der Risikoanalyse und des SLA <br> - Verwaltung des Backlogs und der Reihenfolge der Aufgabenpakete <br> - Ausarbeitung des Projektberichts| 100 Points |
| Bjarne Gerdes | - Datengewinnung und -aufbereitung, <br> - Entwicklung und Evaluierung  des Vorhersagemodells <br> - Evaluierung der Backendarchitektur <br> - Ausarbeitung des Projektberichts| 100 Points |
| Johannes Deufel | - Entwicklung des Frontend <br> - Anbindung des Modells an das Frontend <br> - Entwicklung und Durchführung der WI-Aspekte <br> - Ausarbeitung des Projektberichts| 100 Points |
| Nina Mergelsberg | - Status Reports <br> - Aktualisierung der Kosten-, Zeit- und Projektplan-Übersichten <br> - Entwicklung und Durchführung der wirtschaftlichen Analysen <br> - Ausarbeitung des Projektberichts| 100 Points |
| Simone Marx | - Entwicklung und Durchführung der wirtschaftlichen Analysen <br> - Einhaltung der Scrum-Richtlinien <br> - Organisation und Moderation der Scrum-Meetings <br> - Ausarbeitung des Projektberichts| 100 Points |

### Live Demo 

A minimal demo of the project can be opened by clicking on the image below.

[![Watch the video](https://s20.directupload.net/images/210728/d7fwv4xi.jpg)](https://drive.google.com/file/d/1ep7TTYouwLP-sfdzqeHSb4nZ5SeAHMlo/view)

## Getting started 
#### Required programs
The required programs that have to be installed on our computer should be:
* docker
* docker-compose
* python
* git

### How to set it up
Before the code can be executed, the following commands must be executed from the top hierarchy level:
```
git clone https://github.com/bjarnege/wwi18dsb-projektrealisierung.git
python getting-started.py
docker-compose build ./src/docker-compose.yml
docker-compose up ./src/docker-compose.yml -d
```


### Access 
The data will filtered, labeled according to their sentiment and can be accessed with PgAdmin at 
```
localhost:1337
```

Additionally the database can be accessed under 
```
localhost:1234
``` 
with the user ***admin*** and the password ***password***




