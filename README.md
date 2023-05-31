# Welcome to Electricity Consumption Retriever!

Retrieve home consumption data from companies Endesa and Holaluz, store them in a database and plot them via Grafana.

![Grafana Image](https://github.com/sofisofa/electricity-consumption-retriever/blob/main/Screensh-Grafana.png)

### Introduction
This is project started as a learning exercise and for personal usage, but if you live in Spain this repository may be also for you. The electricity consumption data of your home is retrieved from the companies Holaluz [^1] and Endesa [^2] [^3], is stored in a PostgreSQL database and can then be plotted using Grafana. Both PostgreSQL and Grafana images are ran via Docker. Grafana is provisioned with the database and a dashboard similar to the image above.

A big shout out to [@trocotronic](https://github.com/trocotronic) and their [edistribucion API](https://github.com/trocotronic/edistribucion), which has been used in this project.


### Installation
1. Clone the repository:
```bash
git clone https://github.com/sofisofa/electricity-consumption-retriever.git
```

2. Install dependencies:
```bash
poetry install
```

3. Create .env and .env.prod files, for test and usage respectively. See the .env-template file for more info.


4. Run the desired scripts or functions as explained in Usage instructions.


5. Go to htpps://localhost:3000 to see your consumption data plotted in your Grafana dashboard.


### Usage
Change to the local folder where you have cloned the repo and run the following instructions in terminal.

* Build the Grafana docker image:
    ```bash
    make buildProdGrafana
    ```

* Initialize the PostgreSQL database (first time only):
    ```bash
    make initDb
    ```
  
* Once the database is initialized, you can update it:
    ```bash 
    make updateDb
    ```
  This will also start the containers for the PostgreSQL database and Grafana.


* Take down the containers:
    ```bash 
    make prodDown
    ```

* Run the tests:
    ```bash
    make tests
    ```

----

 [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

----
[^1]: Holaluz API has become obsolete since February 2023, due to changes to the Holaluz website. It will be updated soon.

[^2]: Refer to [this web](https://www.endesa.com/es/blog/blog-de-endesa/luz/comercializadora-distribuidora-diferencias) to see if e-Distribución is the company protviding electricity to the region you live in.

[^3]: You need to be registered in at least one of the websites (https://www.edistribucion.com/ , https://www.holaluz.com/).
